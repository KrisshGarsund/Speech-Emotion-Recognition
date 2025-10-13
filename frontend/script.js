// ========================================
// DOM Elements
// ========================================
const header = document.getElementById('header');
const navMenu = document.getElementById('navMenu');
const navToggle = document.getElementById('navToggle');
const navClose = document.getElementById('navClose');
const navLinks = document.querySelectorAll('.nav-link');
const themeToggle = document.getElementById('themeToggle');
const mouseGlow = document.getElementById('mouseGlow');

// Page containers
const homePage = document.getElementById('homePage');
const predictPage = document.getElementById('predictPage');

// Scroll emoji elements
const scrollEmoji = document.getElementById('scrollEmoji');
const emojiIcon = document.getElementById('emojiIcon');

// Download modal elements
const downloadModal = document.getElementById('downloadModal');
const downloadResultBtn = document.getElementById('downloadResultBtn');
const modalClose = document.getElementById('modalClose');
const modalOverlay = document.getElementById('modalOverlay');
const downloadPDF = document.getElementById('downloadPDF');
const downloadCSV = document.getElementById('downloadCSV');
const downloadImage = document.getElementById('downloadImage');

// Upload elements
const dropzone = document.getElementById('dropzone');
const audioFileInput = document.getElementById('audioFile');
const fileInfo = document.getElementById('fileInfo');
const uploadBtn = document.getElementById('uploadBtn');

// Recording elements
const audioVisualizer = document.getElementById('audioVisualizer');
const startRecordBtn = document.getElementById('startRecordBtn');
const stopRecordBtn = document.getElementById('stopRecordBtn');
const recordedAudio = document.getElementById('recordedAudio');
const analyzeRecordBtn = document.getElementById('analyzeRecordBtn');

// Result elements
const loading = document.getElementById('loading');
const predictionResult = document.getElementById('predictionResult');
const resultIcon = document.getElementById('resultIcon');
const resultEmotion = document.getElementById('resultEmotion');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceFill = document.getElementById('confidenceFill');
const confidenceText = document.getElementById('confidenceText');
const probabilitiesToggle = document.getElementById('probabilitiesToggle');
const probabilitiesContent = document.getElementById('probabilitiesContent');

// ========================================
// Configuration
// ========================================
const API_BASE_URL = 'http://localhost:5000';  // Update this to your Flask backend URL
const EMOTION_ICONS = {
    'Happy': 'fa-smile-beam',
    'Sad': 'fa-sad-tear',
    'Angry': 'fa-angry',
    'Fearful': 'fa-flushed',
    'Fear': 'fa-flushed',
    'Calm': 'fa-leaf',
    'Surprised': 'fa-surprise',
    'Surprise': 'fa-surprise',
    'Disgust': 'fa-dizzy',
    'Neutral': 'fa-meh'
};

// ========================================
// State Management
// ========================================
let selectedFile = null;
let recordedBlob = null;
let mediaRecorder = null;
let audioContext = null;
let analyser = null;
let animationId = null;

// Emoji scroll state
const emotionEmojis = ['😊', '😢', '😠', '😳', '🍃', '😲', '🤢', '😐'];
const emotionNames = ['Happy', 'Sad', 'Angry', 'Fearful', 'Calm', 'Surprised', 'Disgust', 'Neutral'];
let currentEmojiIndex = 0;
let lastScrollPosition = 0;

// Prediction result data (for download)
let currentPredictionData = null;

// ========================================
// Page Navigation
// ========================================
function showPage(pageName) {
    // Hide all pages
    homePage.style.display = 'none';
    predictPage.style.display = 'none';
    
    // Show requested page
    if (pageName === 'home') {
        homePage.style.display = 'block';
        window.scrollTo(0, 0);
    } else if (pageName === 'predict') {
        predictPage.style.display = 'block';
        window.scrollTo(0, 0);
    }
}

// ========================================
// Navigation & Header
// ========================================

// Show/Hide mobile menu
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.add('show');
    });
}

if (navClose) {
    navClose.addEventListener('click', () => {
        navMenu.classList.remove('show');
    });
}

// Handle navigation clicks
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        
        // Handle page navigation
        if (href === '#home' || href === '#about' || href === '#contact') {
            e.preventDefault();
            showPage('home');
            
            // Scroll to section if not home
            if (href !== '#home') {
                setTimeout(() => {
                    const section = document.querySelector(href);
                    if (section) {
                        section.scrollIntoView({ behavior: 'smooth' });
                    }
                }, 100);
            }
        } else if (href === '#predict') {
            e.preventDefault();
            showPage('predict');
        }
        
        // Close mobile menu
        navMenu.classList.remove('show');
        
        // Update active link
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
    });
});

// Header background on scroll
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// ========================================
// Theme Toggle
// ========================================
const currentTheme = localStorage.getItem('theme') || 'dark';
document.body.classList.toggle('light-mode', currentTheme === 'light');

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    const theme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
    localStorage.setItem('theme', theme);
});

// ========================================
// Scroll-based Emoji Changer
// ========================================
function changeEmoji(index) {
    if (!emojiIcon) return;
    
    // Add changing animation
    emojiIcon.classList.add('changing');
    
    // Change emoji after brief delay
    setTimeout(() => {
        emojiIcon.textContent = emotionEmojis[index];
        emojiIcon.classList.remove('changing');
    }, 200);
}

// Scroll event listener for emoji changes
window.addEventListener('scroll', () => {
    if (!scrollEmoji || !emojiIcon) return;
    
    const scrollPosition = window.scrollY;
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    
    // Avoid division by zero
    if (scrollHeight <= 0) return;
    
    const scrollPercentage = (scrollPosition / scrollHeight) * 100;
    
    // Determine which emoji to show based on scroll percentage
    const emojiIndex = Math.floor((scrollPercentage / 100) * emotionEmojis.length);
    const clampedIndex = Math.min(emojiIndex, emotionEmojis.length - 1);
    
    // Only change if different from current
    if (clampedIndex !== currentEmojiIndex) {
        currentEmojiIndex = clampedIndex;
        changeEmoji(currentEmojiIndex);
    }
    
    lastScrollPosition = scrollPosition;
});

// ========================================
// Mouse Glow Effect
// ========================================
document.addEventListener('mousemove', (e) => {
    if (document.body.classList.contains('dark-mode')) {
        mouseGlow.style.left = e.clientX + 'px';
        mouseGlow.style.top = e.clientY + 'px';
    }
});

// ========================================
// Scroll Animations
// ========================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
        }
    });
}, observerOptions);

// Observe all animatable elements
document.querySelectorAll('.section-title, .section-subtitle, .about-card, .predict-card').forEach(el => {
    observer.observe(el);
});

// ========================================
// File Upload - Drag & Drop
// ========================================
dropzone.addEventListener('click', () => {
    audioFileInput.click();
});

audioFileInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

function handleFileSelect(file) {
    if (!file) return;
    
    // Validate file type - accept common audio formats
    const validExtensions = ['.wav', '.mp3', '.webm', '.ogg', '.m4a', '.flac', '.mp4'];
    const isValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    const isValidType = file.type.startsWith('audio/') || file.type.includes('webm') || file.type.includes('ogg');
    
    if (!isValidExtension && !isValidType) {
        showError('Please select a valid audio file (.wav, .mp3, .webm, .ogg, .m4a, .flac)');
        return;
    }
    
    selectedFile = file;
    fileInfo.innerHTML = `
        <i class="fas fa-file-audio" style="color: var(--primary);"></i>
        <span>${file.name}</span>
        <span style="margin-left: auto; color: var(--text-secondary);">
            ${(file.size / 1024 / 1024).toFixed(2)} MB
        </span>
    `;
    fileInfo.classList.add('show');
    uploadBtn.disabled = false;
}

// Handle upload and predict
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    await predictEmotion(selectedFile, 'upload');
});

// ========================================
// Audio Recording
// ========================================
let audioChunks = [];

startRecordBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Setup MediaRecorder with options
        // Try to use audio/wav if supported, otherwise use default format
        let options = { mimeType: 'audio/webm' };
        
        // Check for supported mime types
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options = { mimeType: 'audio/webm;codecs=opus' };
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
            options = { mimeType: 'audio/webm' };
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
            options = { mimeType: 'audio/ogg;codecs=opus' };
        }
        
        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];
        
        console.log('Recording with MIME type:', options.mimeType);
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            // Create blob with the actual recorded format
            recordedBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            const audioUrl = URL.createObjectURL(recordedBlob);
            recordedAudio.src = audioUrl;
            recordedAudio.style.display = 'block';
            analyzeRecordBtn.style.display = 'block';
            
            console.log('Recording stopped. Blob size:', recordedBlob.size, 'bytes');
            console.log('Blob type:', recordedBlob.type);
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
            
            // Stop visualization
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
        };
        
        mediaRecorder.start();
        
        // Update button states
        startRecordBtn.disabled = true;
        stopRecordBtn.disabled = false;
        
        // Start visualization
        setupAudioVisualization(stream);
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showError('Could not access microphone. Please check permissions.');
    }
});

stopRecordBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        startRecordBtn.disabled = false;
        stopRecordBtn.disabled = true;
    }
});

analyzeRecordBtn.addEventListener('click', async () => {
    if (!recordedBlob) return;
    
    console.log('Converting recording to WAV format...');
    
    try {
        // Convert the recorded audio to WAV format on client side
        const wavBlob = await convertToWav(recordedBlob);
        
        // Create a file from the WAV blob
        const file = new File([wavBlob], 'recording.wav', { type: 'audio/wav' });
        console.log('Converted to WAV:', file.name, 'Size:', file.size);
        
        await predictEmotion(file, 'recording');
    } catch (error) {
        console.error('Error converting audio:', error);
        showError('Failed to convert audio. Please try recording again.');
    }
});

// ========================================
// Audio Conversion to WAV
// ========================================
async function convertToWav(blob) {
    /**
     * Convert any audio blob (webm, ogg, etc.) to WAV format
     * This eliminates the need for ffmpeg on the server!
     */
    
    // Create an audio context
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Read the blob as an array buffer
    const arrayBuffer = await blob.arrayBuffer();
    
    // Decode the audio data
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
    // Convert to WAV format
    const wavBlob = audioBufferToWav(audioBuffer);
    
    return wavBlob;
}

function audioBufferToWav(audioBuffer) {
    /**
     * Convert AudioBuffer to WAV blob
     * Creates a proper WAV file with headers
     */
    
    const numOfChan = audioBuffer.numberOfChannels;
    const length = audioBuffer.length * numOfChan * 2 + 44;
    const buffer = new ArrayBuffer(length);
    const view = new DataView(buffer);
    const channels = [];
    let offset = 0;
    let pos = 0;
    
    // Write WAV header
    setUint32(0x46464952); // "RIFF"
    setUint32(length - 8); // file length - 8
    setUint32(0x45564157); // "WAVE"
    
    setUint32(0x20746d66); // "fmt " chunk
    setUint32(16); // length = 16
    setUint16(1); // PCM (uncompressed)
    setUint16(numOfChan);
    setUint32(audioBuffer.sampleRate);
    setUint32(audioBuffer.sampleRate * 2 * numOfChan); // avg. bytes/sec
    setUint16(numOfChan * 2); // block-align
    setUint16(16); // 16-bit
    
    setUint32(0x61746164); // "data" - chunk
    setUint32(length - pos - 4); // chunk length
    
    // Write interleaved data
    for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
        channels.push(audioBuffer.getChannelData(i));
    }
    
    while (pos < length) {
        for (let i = 0; i < numOfChan; i++) {
            let sample = Math.max(-1, Math.min(1, channels[i][offset]));
            sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767) | 0;
            view.setInt16(pos, sample, true);
            pos += 2;
        }
        offset++;
    }
    
    return new Blob([buffer], { type: 'audio/wav' });
    
    function setUint16(data) {
        view.setUint16(pos, data, true);
        pos += 2;
    }
    
    function setUint32(data) {
        view.setUint32(pos, data, true);
        pos += 4;
    }
}

// ========================================
// Audio Visualization
// ========================================
function setupAudioVisualization(stream) {
    const canvasCtx = audioVisualizer.getContext('2d');
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    source.connect(analyser);
    analyser.fftSize = 256;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    function draw() {
        animationId = requestAnimationFrame(draw);
        
        analyser.getByteFrequencyData(dataArray);
        
        canvasCtx.fillStyle = getComputedStyle(document.body).getPropertyValue('--bg-color');
        canvasCtx.fillRect(0, 0, audioVisualizer.width, audioVisualizer.height);
        
        const barWidth = (audioVisualizer.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            barHeight = (dataArray[i] / 255) * audioVisualizer.height;
            
            canvasCtx.fillStyle = '#c4f82a';
            canvasCtx.fillRect(x, audioVisualizer.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }
    
    draw();
}

// ========================================
// API Communication
// ========================================
async function predictEmotion(file, source) {
    // Hide previous results
    predictionResult.style.display = 'none';
    loading.style.display = 'block';
    
    // Scroll to results area
    loading.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    try {
        const formData = new FormData();
        formData.append('audio', file);
        
        // Make API request with retry logic
        const response = await fetchWithRetry(`${API_BASE_URL}/predict`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Display results
        displayPrediction(result);
        
    } catch (error) {
        console.error('Prediction error:', error);
        loading.style.display = 'none';
        
        if (error.message.includes('Failed to fetch')) {
            showError('Could not connect to the server. Please make sure the backend is running on ' + API_BASE_URL);
        } else {
            showError('Error analyzing audio: ' + error.message);
        }
    }
}

async function fetchWithRetry(url, options, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            return response;
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}

// ========================================
// Display Prediction Results
// ========================================
function displayPrediction(data) {
    loading.style.display = 'none';
    predictionResult.style.display = 'block';
    
    // Extract emotion and confidence
    const emotion = data.emotion || data.predicted_emotion;
    const confidence = data.confidence;
    const probabilities = data.probabilities || data.all_probabilities || {};
    
    // Store prediction data for download
    currentPredictionData = {
        emotion: emotion,
        confidence: confidence,
        probabilities: probabilities,
        filename: selectedFile ? selectedFile.name : 'recording.wav',
        timestamp: new Date().toLocaleString()
    };
    
    // Update emotion and icon
    resultEmotion.textContent = emotion;
    const iconClass = EMOTION_ICONS[emotion] || 'fa-meh';
    resultIcon.className = `result-icon fas ${iconClass}`;
    
    // Update confidence
    const confidencePercent = confidence * 100;
    confidenceValue.textContent = `${confidencePercent.toFixed(1)}%`;
    confidenceFill.style.width = `${confidencePercent}%`;
    
    // Update confidence text and color
    if (confidencePercent >= 75) {
        confidenceText.textContent = 'High Confidence';
        confidenceText.className = 'confidence-text high';
    } else if (confidencePercent >= 50) {
        confidenceText.textContent = 'Medium Confidence';
        confidenceText.className = 'confidence-text medium';
    } else {
        confidenceText.textContent = 'Low Confidence';
        confidenceText.className = 'confidence-text low';
    }
    
    // Display all probabilities
    displayProbabilities(probabilities);
    
    // Scroll to result
    predictionResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function displayProbabilities(probabilities) {
    // Convert to array and sort by confidence
    const probArray = Object.entries(probabilities).map(([emotion, prob]) => ({
        emotion,
        probability: prob * 100
    })).sort((a, b) => b.probability - a.probability);
    
    // Generate HTML
    const html = probArray.map(item => `
        <div class="probability-item">
            <span class="probability-emotion">${item.emotion}</span>
            <div class="probability-bar">
                <div class="probability-fill" style="width: ${item.probability}%"></div>
            </div>
            <span class="probability-value">${item.probability.toFixed(1)}%</span>
        </div>
    `).join('');
    
    probabilitiesContent.innerHTML = html;
}

// Toggle probabilities
probabilitiesToggle.addEventListener('click', () => {
    const isVisible = probabilitiesContent.style.display !== 'none';
    probabilitiesContent.style.display = isVisible ? 'none' : 'block';
    probabilitiesToggle.classList.toggle('active');
});

// ========================================
// Error Handling
// ========================================
function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: calc(var(--header-height) + 1rem);
        right: 1rem;
        background-color: var(--error);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    errorDiv.innerHTML = `
        <div style="display: flex; align-items: start; gap: 0.75rem;">
            <i class="fas fa-exclamation-circle" style="font-size: 1.25rem; margin-top: 0.125rem;"></i>
            <div>
                <strong style="display: block; margin-bottom: 0.25rem;">Error</strong>
                <span>${message}</span>
            </div>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        errorDiv.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

// Add animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
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
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ========================================
// Download Functions
// ========================================

// Download as CSV
function downloadAsCSV() {
    if (!currentPredictionData) return;
    
    const {emotion, confidence, probabilities, filename, timestamp} = currentPredictionData;
    
    // Create CSV content
    let csvContent = 'Emotion,Probability\n';
    
    // Sort by probability descending
    const sortedEmotions = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1]);
    
    sortedEmotions.forEach(([emo, prob]) => {
        csvContent += `${emo},${(prob * 100).toFixed(2)}%\n`;
    });
    
    // Add metadata
    csvContent += `\nPredicted Emotion,${emotion}\n`;
    csvContent += `Confidence,${(confidence * 100).toFixed(2)}%\n`;
    csvContent += `Filename,${filename}\n`;
    csvContent += `Timestamp,${timestamp}\n`;
    
    // Create download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `emotion_prediction_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    hideDownloadModal();
}

// Download as PDF
function downloadAsPDF() {
    if (!currentPredictionData) return;
    
    const {emotion, confidence, probabilities, filename, timestamp} = currentPredictionData;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Set colors
    const primaryColor = [196, 248, 42]; // Lime green
    const darkColor = [11, 12, 16];
    const lightColor = [230, 241, 255];
    
    // Header with branding
    doc.setFillColor(...primaryColor);
    doc.rect(0, 0, 210, 40, 'F');
    doc.setTextColor(11, 12, 16);
    doc.setFontSize(28);
    doc.setFont('helvetica', 'bold');
    doc.text('SpeechSense', 105, 20, { align: 'center' });
    doc.setFontSize(12);
    doc.text('Speech Emotion Recognition Report', 105, 30, { align: 'center' });
    
    // Main result
    doc.setTextColor(...darkColor);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('Prediction Result', 20, 55);
    
    // Emotion box
    doc.setFillColor(245, 245, 245);
    doc.roundedRect(20, 65, 170, 30, 3, 3, 'F');
    doc.setFontSize(24);
    doc.setTextColor(...primaryColor);
    doc.text(`Emotion: ${emotion}`, 105, 82, { align: 'center' });
    
    // Confidence
    doc.setFontSize(16);
    doc.setTextColor(...darkColor);
    doc.text(`Confidence: ${(confidence * 100).toFixed(1)}%`, 105, 92, { align: 'center' });
    
    // Top 3 Probabilities
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Top 3 Emotions:', 20, 115);
    
    const sortedEmotions = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3);
    
    let yPos = 125;
    sortedEmotions.forEach(([emo, prob], index) => {
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(12);
        doc.text(`${index + 1}. ${emo}`, 25, yPos);
        
        // Progress bar
        const barWidth = prob * 140;
        doc.setFillColor(220, 220, 220);
        doc.rect(70, yPos - 5, 140, 8, 'F');
        doc.setFillColor(...primaryColor);
        doc.rect(70, yPos - 5, barWidth, 8, 'F');
        
        // Percentage
        doc.text(`${(prob * 100).toFixed(1)}%`, 215, yPos, {align: 'right'});
        
        yPos += 15;
    });
    
    // All Probabilities
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.text('All Emotion Probabilities:', 20, 180);
    
    yPos = 195;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    
    Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1])
        .forEach(([emo, prob]) => {
            doc.text(`${emo}:`, 25, yPos);
            doc.text(`${(prob * 100).toFixed(2)}%`, 100, yPos);
            yPos += 7;
        });
    
    // File Info
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(12);
    doc.text('File Information:', 20, yPos + 10);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text(`Filename: ${filename}`, 25, yPos + 20);
    doc.text(`Analysis Date: ${timestamp}`, 25, yPos + 27);
    
    // Footer
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text('Generated by SpeechSense - Speech Emotion Recognition System', 105, 285, { align: 'center' });
    
    // Save PDF
    doc.save(`emotion_report_${Date.now()}.pdf`);
    hideDownloadModal();
}

// Download as Visual Card (Image)
function downloadAsImage() {
    if (!currentPredictionData) return;
    
    const {emotion, confidence, probabilities, filename, timestamp} = currentPredictionData;
    
    // Create visual card element
    const card = document.createElement('div');
    card.style.cssText = `
        width: 800px;
        padding: 40px;
        background: linear-gradient(135deg, #0B0C10 0%, #1a1d29 100%);
        border: 3px solid #c4f82a;
        border-radius: 20px;
        color: #E6F1FF;
        font-family: 'Poppins', sans-serif;
        position: absolute;
        left: -9999px;
        top: 0;
    `;
    
    // Get top 3 emotions
    const top3 = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3);
    
    card.innerHTML = `
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #c4f82a; font-size: 36px; margin: 0 0 10px 0;">SpeechSense</h1>
            <p style="color: #8892b0; margin: 0;">Speech Emotion Recognition</p>
        </div>
        
        <div style="background: rgba(22, 28, 41, 0.6); padding: 30px; border-radius: 15px; margin-bottom: 25px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 72px; margin-bottom: 10px;">${emotionEmojis[emotionNames.indexOf(emotion)] || '😊'}</div>
                <h2 style="color: #c4f82a; font-size: 42px; margin: 0;">${emotion}</h2>
                <p style="color: #8892b0; margin: 10px 0 0 0;">Predicted Emotion</p>
            </div>
            
            <div style="margin-top: 25px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: 600;">Confidence Level</span>
                    <span style="color: #c4f82a; font-size: 24px; font-weight: 700;">${(confidence * 100).toFixed(1)}%</span>
                </div>
                <div style="background: #0B0C10; height: 20px; border-radius: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(to right, #dc3545, #ffc107, #28a745); height: 100%; width: ${confidence * 100}%;"></div>
                </div>
            </div>
        </div>
        
        <div style="background: rgba(22, 28, 41, 0.6); padding: 25px; border-radius: 15px; margin-bottom: 25px;">
            <h3 style="color: #E6F1FF; margin: 0 0 20px 0; font-size: 20px;">Top 3 Emotions</h3>
            ${top3.map((item, index) => `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>${index + 1}. ${item[0]}</span>
                        <span style="color: #c4f82a;">${(item[1] * 100).toFixed(1)}%</span>
                    </div>
                    <div style="background: #0B0C10; height: 10px; border-radius: 5px; overflow: hidden;">
                        <div style="background: #c4f82a; height: 100%; width: ${item[1] * 100}%;"></div>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div style="background: rgba(22, 28, 41, 0.4); padding: 20px; border-radius: 10px; font-size: 14px; color: #8892b0;">
            <p style="margin: 0 0 5px 0;"><strong style="color: #E6F1FF;">File:</strong> ${filename}</p>
            <p style="margin: 0;"><strong style="color: #E6F1FF;">Generated:</strong> ${timestamp}</p>
        </div>
    `;
    
    document.body.appendChild(card);
    
    // Use html2canvas to capture
    html2canvas(card, {
        backgroundColor: null,
        scale: 2,
        logging: false
    }).then(canvas => {
        // Convert to image and download
        canvas.toBlob(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `emotion_card_${Date.now()}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            // Clean up
            document.body.removeChild(card);
            hideDownloadModal();
        });
    });
}

// Add download handlers
if (downloadCSV) {
    downloadCSV.addEventListener('click', downloadAsCSV);
}

if (downloadPDF) {
    downloadPDF.addEventListener('click', downloadAsPDF);
}

if (downloadImage) {
    downloadImage.addEventListener('click', downloadAsImage);
}

// ========================================
// Download Modal Controls
// ========================================
function showDownloadModal() {
    downloadModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function hideDownloadModal() {
    downloadModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Download button click
if (downloadResultBtn) {
    downloadResultBtn.addEventListener('click', () => {
        if (currentPredictionData) {
            showDownloadModal();
        }
    });
}

// Close modal handlers
if (modalClose) {
    modalClose.addEventListener('click', hideDownloadModal);
}

if (modalOverlay) {
    modalOverlay.addEventListener('click', hideDownloadModal);
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && downloadModal.style.display === 'flex') {
        hideDownloadModal();
    }
});

// ========================================
// Predict Tab Switching
// ========================================
const predictTabBtns = document.querySelectorAll('.predict-tab-btn');
const predictTabContents = document.querySelectorAll('.predict-tab-content');

function switchPredictTab(tabName) {
    // Remove active class from all buttons and contents
    predictTabBtns.forEach(btn => btn.classList.remove('active'));
    predictTabContents.forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    const selectedBtn = document.querySelector(`.predict-tab-btn[data-tab="${tabName}"]`);
    const selectedContent = document.getElementById(`${tabName}Tab`);
    
    if (selectedBtn && selectedContent) {
        selectedBtn.classList.add('active');
        selectedContent.classList.add('active');
    }
}

// Add click handlers to tab buttons
predictTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.getAttribute('data-tab');
        switchPredictTab(tabName);
    });
});

// ========================================
// Initialize on page load
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('SpeechSense initialized');
    console.log('Backend URL:', API_BASE_URL);
    console.log('To change backend URL, update API_BASE_URL in script.js');
    
    // Show home page by default
    showPage('home');
    
    // Initialize first tab as active
    switchPredictTab('upload');
});

// ========================================
// Smooth Scroll & Navigation Handler
// ========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Skip if already handled by nav links or if empty
        if (href === '#' || href === '' || this.classList.contains('nav-link')) {
            return;
        }
        
        // Handle predict page navigation
        if (href === '#predict') {
            e.preventDefault();
            showPage('predict');
            return;
        }
        
        // Handle sections on home page
        if (href === '#home' || href === '#about' || href === '#contact') {
            e.preventDefault();
            showPage('home');
            setTimeout(() => {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }, 100);
        }
    });
});

