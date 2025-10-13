// Speech Emotion Recognition - Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    const audioPreview = document.getElementById('audioPreview');
    const audioPlayer = document.getElementById('audioPlayer');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const uploadForm = document.getElementById('uploadForm');

    // File upload handling
    function handleFileSelect(file) {
        if (file && file.type.startsWith('audio/')) {
            // Show file info
            fileName.textContent = file.name;
            fileInfo.style.display = 'flex';
            uploadArea.style.display = 'none';
            
            // Enable analyze button
            analyzeBtn.disabled = false;
            
            // Create audio preview
            const audioURL = URL.createObjectURL(file);
            audioPlayer.src = audioURL;
            audioPreview.style.display = 'block';
            
            // Add visual feedback
            analyzeBtn.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
        } else {
            showError('Please select a valid audio file.');
        }
    }

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // Click to upload
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });

    // Remove file
    removeFile.addEventListener('click', function(e) {
        e.stopPropagation();
        resetUpload();
    });

    // Reset upload area
    function resetUpload() {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
        audioPreview.style.display = 'none';
        analyzeBtn.disabled = true;
        analyzeBtn.style.background = '#cbd5e0';
        
        // Clean up audio URL
        if (audioPlayer.src) {
            URL.revokeObjectURL(audioPlayer.src);
            audioPlayer.src = '';
        }
    }

    // Form submission with loading state
    uploadForm.addEventListener('submit', function(e) {
        if (!fileInput.files[0]) {
            e.preventDefault();
            showError('Please select an audio file first.');
            return;
        }

        // Show loading state
        analyzeBtn.disabled = true;
        analyzeBtn.querySelector('span').textContent = 'Analyzing...';
        loadingSpinner.style.display = 'block';
        
        // Add loading animation to button
        analyzeBtn.style.background = 'linear-gradient(45deg, #cbd5e0, #a0aec0)';
    });

    // Error handling
    function showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
        `;
        
        // Style the error notification
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fed7d7;
            color: #c53030;
            padding: 15px 20px;
            border-radius: 8px;
            border: 1px solid #feb2b2;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        `;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 300);
        }, 5000);
    }

    // Add CSS animations for notifications
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .error-notification {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);

    // Add smooth scrolling for better UX
    function smoothScrollTo(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }

    // Add keyboard accessibility
    uploadArea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });

    // Add focus styles for accessibility
    uploadArea.setAttribute('tabindex', '0');
    uploadArea.setAttribute('role', 'button');
    uploadArea.setAttribute('aria-label', 'Upload audio file');

    // Add ARIA labels for screen readers
    analyzeBtn.setAttribute('aria-label', 'Analyze emotion from uploaded audio file');
    fileInput.setAttribute('aria-label', 'Select audio file for emotion analysis');

    // Add success animation for results
    function animateResult() {
        const resultSection = document.querySelector('.result-section');
        if (resultSection) {
            resultSection.style.animation = 'slideInUp 0.6s ease-out';
            
            // Animate confidence bar
            const confidenceFill = document.querySelector('.confidence-fill');
            if (confidenceFill) {
                const width = confidenceFill.style.width;
                confidenceFill.style.width = '0%';
                setTimeout(() => {
                    confidenceFill.style.width = width;
                }, 500);
            }
        }
    }

    // Check if we have results and animate them
    if (document.querySelector('.result-section')) {
        setTimeout(animateResult, 100);
    }

    // Add file size validation
    function validateFileSize(file) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            showError('File size too large. Please select a file smaller than 50MB.');
            return false;
        }
        return true;
    }

    // Update file handling to include size validation
    const originalHandleFileSelect = handleFileSelect;
    handleFileSelect = function(file) {
        if (file && file.type.startsWith('audio/')) {
            if (validateFileSize(file)) {
                originalHandleFileSelect(file);
            } else {
                resetUpload();
            }
        } else {
            showError('Please select a valid audio file.');
        }
    };

    // Add progress indicator for long uploads
    function showProgress() {
        const progressDiv = document.createElement('div');
        progressDiv.className = 'upload-progress';
        progressDiv.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <span class="progress-text">Uploading and analyzing...</span>
        `;
        
        progressDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            text-align: center;
            min-width: 300px;
        `;
        
        document.body.appendChild(progressDiv);
        
        // Animate progress bar
        const progressFill = progressDiv.querySelector('.progress-fill');
        progressFill.style.cssText = `
            width: 0%;
            height: 4px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 2px;
            transition: width 2s ease-out;
        `;
        
        setTimeout(() => {
            progressFill.style.width = '100%';
        }, 100);
        
        return progressDiv;
    }

    // Enhanced form submission with progress
    const originalFormSubmit = uploadForm.addEventListener;
    uploadForm.addEventListener('submit', function(e) {
        if (!fileInput.files[0]) {
            e.preventDefault();
            showError('Please select an audio file first.');
            return;
        }

        // Show progress indicator
        const progressDiv = showProgress();
        
        // Show loading state
        analyzeBtn.disabled = true;
        analyzeBtn.querySelector('span').textContent = 'Analyzing...';
        loadingSpinner.style.display = 'block';
        analyzeBtn.style.background = 'linear-gradient(45deg, #cbd5e0, #a0aec0)';
        
        // Clean up progress indicator after form submission
        setTimeout(() => {
            if (progressDiv && progressDiv.parentNode) {
                progressDiv.parentNode.removeChild(progressDiv);
            }
        }, 3000);
    });
});
