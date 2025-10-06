// Audio Recording JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const startBtn = document.getElementById('startRecording');
    const stopBtn = document.getElementById('stopRecording');
    const playBtn = document.getElementById('playRecording');
    const analyzeBtn = document.getElementById('analyzeRecording');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const recordingTimer = document.getElementById('recordingTimer');
    const timerDisplay = document.getElementById('timerDisplay');
    const audioVisualization = document.getElementById('audioVisualization');
    const audioCanvas = document.getElementById('audioCanvas');
    const recordingPlayback = document.getElementById('recordingPlayback');
    const recordedAudio = document.getElementById('recordedAudio');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Recording state
    let mediaRecorder;
    let audioChunks = [];
    let audioBlob;
    let recordingStartTime;
    let timerInterval;
    let audioContext;
    let analyser;
    let microphone;
    let animationId;

    // Initialize audio context
    function initAudioContext() {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
    }

    // Start recording
    startBtn.addEventListener('click', async function() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Initialize audio context if not already done
            if (!audioContext) {
                initAudioContext();
            }
            
            // Set up media recorder
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            // Set up audio visualization
            microphone = audioContext.createMediaStreamSource(stream);
            microphone.connect(analyser);
            
            // Reset state
            audioChunks = [];
            recordingStartTime = Date.now();
            
            // Update UI
            startBtn.disabled = true;
            stopBtn.disabled = false;
            playBtn.disabled = true;
            analyzeBtn.disabled = true;
            
            statusIndicator.className = 'status-indicator recording';
            statusText.textContent = 'Recording...';
            recordingTimer.style.display = 'flex';
            audioVisualization.style.display = 'block';
            recordingPlayback.style.display = 'none';
            
            // Start recording
            mediaRecorder.start();
            
            // Start timer
            startTimer();
            
            // Start visualization
            startVisualization();
            
            // Handle data available
            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };
            
            // Handle recording stop
            mediaRecorder.onstop = function() {
                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioURL = URL.createObjectURL(audioBlob);
                recordedAudio.src = audioURL;
                
                // Update UI
                playBtn.disabled = false;
                analyzeBtn.disabled = false;
                recordingPlayback.style.display = 'block';
                audioVisualization.style.display = 'none';
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            showError('Unable to access microphone. Please check permissions.');
        }
    });

    // Stop recording
    stopBtn.addEventListener('click', function() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            
            // Update UI
            startBtn.disabled = false;
            stopBtn.disabled = true;
            
            statusIndicator.className = 'status-indicator ready';
            statusText.textContent = 'Recording complete';
            recordingTimer.style.display = 'none';
            
            // Stop timer
            stopTimer();
            
            // Stop visualization
            stopVisualization();
        }
    });

    // Play recording
    playBtn.addEventListener('click', function() {
        if (recordedAudio.src) {
            recordedAudio.play();
        }
    });

    // Analyze recording
    analyzeBtn.addEventListener('click', function() {
        if (audioBlob) {
            analyzeRecording(audioBlob);
        }
    });

    // Timer functions
    function startTimer() {
        timerInterval = setInterval(updateTimer, 100);
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    }

    function updateTimer() {
        const elapsed = Date.now() - recordingStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        const milliseconds = Math.floor((elapsed % 1000) / 10);
        
        timerDisplay.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(2, '0')}`;
    }

    // Audio visualization
    function startVisualization() {
        const canvas = audioCanvas;
        const canvasCtx = canvas.getContext('2d');
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function draw() {
            animationId = requestAnimationFrame(draw);
            
            analyser.getByteFrequencyData(dataArray);
            
            canvasCtx.fillStyle = '#f8fafc';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
            
            const barWidth = (canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = (dataArray[i] / 255) * canvas.height;
                
                const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
                gradient.addColorStop(0, '#667eea');
                gradient.addColorStop(1, '#764ba2');
                
                canvasCtx.fillStyle = gradient;
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        }
        
        draw();
    }

    function stopVisualization() {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
    }

    // Analyze recording
    async function analyzeRecording(audioBlob) {
        try {
            // Show loading state
            analyzeBtn.disabled = true;
            analyzeBtn.querySelector('span').textContent = 'Analyzing...';
            loadingSpinner.style.display = 'block';

            // Create form data
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');

            // Send to server
            const response = await fetch('/record_predict', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const html = await response.text();
                // Replace main content with new HTML (analysis result)
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newMain = doc.querySelector('.main-content');
                if (newMain) {
                    document.querySelector('.main-content').replaceWith(newMain);
                } else {
                    // fallback: reload page if parsing fails
                    window.location.reload();
                }
            } else {
                throw new Error('Analysis failed');
            }

        } catch (error) {
            console.error('Error analyzing recording:', error);
            showError('Failed to analyze recording. Please try again.');

            // Reset button state
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector('span').textContent = 'Analyze Emotion';
            loadingSpinner.style.display = 'none';
        }
    }

    // Error handling
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
        `;
        
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

    // Check for microphone permission on page load
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
            console.log('Microphone access granted');
        })
        .catch((error) => {
            console.log('Microphone access denied:', error);
            showError('Microphone access is required for recording. Please enable it and refresh the page.');
        });
});
