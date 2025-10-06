// Recording JavaScript for Speech Emotion Recognition
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingDuration = 0;
        this.recordingTimer = null;
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.dataArray = null;
        this.volumeLevel = 0;
        
        this.initializeElements();
        this.setupEventListeners();
        this.initializeAudioContext();
    }

    initializeElements() {
        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.microphoneIcon = document.getElementById('microphoneIcon');
        this.recordingWaves = document.getElementById('recordingWaves');
        this.recordingStatus = document.getElementById('recordingStatus');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.audioPlayback = document.getElementById('audioPlayback');
        this.resultSection = document.getElementById('resultSection');
        this.durationElement = document.getElementById('duration');
        this.volumeElement = document.getElementById('volume');
        this.emotionIcon = document.getElementById('emotionIcon');
        this.emotionName = document.getElementById('emotionName');
        this.confidenceValue = document.getElementById('confidenceValue');
        this.confidenceFill = document.getElementById('confidenceFill');
    }

    setupEventListeners() {
        this.recordBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        this.analyzeBtn.addEventListener('click', () => this.analyzeRecording());
    }

    async initializeAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        } catch (error) {
            console.error('Error initializing audio context:', error);
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            this.recordingDuration = 0;
            
            // Update UI
            this.updateRecordingUI(true);
            this.startTimer();
            this.startVolumeMonitoring(stream);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Unable to access microphone. Please check permissions.');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Stop all tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // Update UI
            this.updateRecordingUI(false);
            this.stopTimer();
            this.stopVolumeMonitoring();
        }
    }

    processRecording() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Show audio playback
        this.audioPlayer.src = audioUrl;
        this.audioPlayback.style.display = 'block';
        
        // Enable analyze button
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
        
        // Store the blob for analysis
        this.recordedAudioBlob = audioBlob;
    }

    async analyzeRecording() {
        if (!this.recordedAudioBlob) {
            this.showError('No recording to analyze');
            return;
        }

        // Show loading state
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';
        this.analyzeBtn.style.background = 'linear-gradient(45deg, #cbd5e0, #a0aec0)';

        try {
            // Convert webm to wav for processing
            const wavBlob = await this.convertToWav(this.recordedAudioBlob);
            
            // Send to server for analysis
            const formData = new FormData();
            formData.append('audio', wavBlob, 'recording.wav');
            
            const response = await fetch('/process_recorded_audio', {
                method: 'POST',
                body: wavBlob
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayResults(result.emotion, result.confidence);
            } else {
                this.showError(result.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Error analyzing recording:', error);
            this.showError('Error analyzing recording. Please try again.');
        } finally {
            // Reset analyze button
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.innerHTML = '<i class="fas fa-brain"></i><span>Analyze Emotion</span>';
            this.analyzeBtn.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
        }
    }

    async convertToWav(webmBlob) {
        // For simplicity, we'll send the webm blob directly
        // In a production environment, you might want to convert to WAV
        return webmBlob;
    }

    displayResults(emotion, confidence) {
        // Update emotion icon and name
        const emotionIcons = {
            'happy': 'fas fa-smile',
            'sad': 'fas fa-frown',
            'angry': 'fas fa-angry',
            'fearful': 'fas fa-surprise',
            'surprised': 'fas fa-grin-beam',
            'disgust': 'fas fa-grimace',
            'calm': 'fas fa-smile-beam',
            'neutral': 'fas fa-meh'
        };
        
        const iconClass = emotionIcons[emotion.toLowerCase()] || 'fas fa-question';
        this.emotionIcon.innerHTML = `<i class="${iconClass}"></i>`;
        this.emotionName.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
        
        // Update confidence
        this.confidenceValue.textContent = Math.round(confidence * 100);
        this.confidenceFill.style.width = `${confidence * 100}%`;
        
        // Show results
        this.resultSection.style.display = 'block';
        this.resultSection.scrollIntoView({ behavior: 'smooth' });
        
        // Animate confidence bar
        setTimeout(() => {
            this.confidenceFill.style.transition = 'width 1s ease-out';
        }, 100);
    }

    updateRecordingUI(isRecording) {
        if (isRecording) {
            this.recordBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.recordingWaves.style.display = 'flex';
            this.recordingStatus.textContent = 'Recording...';
            this.microphoneIcon.style.color = '#e53e3e';
            this.microphoneIcon.style.animation = 'pulse 1s infinite';
        } else {
            this.recordBtn.disabled = false;
            this.stopBtn.disabled = true;
            this.recordingWaves.style.display = 'none';
            this.recordingStatus.textContent = 'Recording stopped';
            this.microphoneIcon.style.color = '#667eea';
            this.microphoneIcon.style.animation = 'none';
        }
    }

    startTimer() {
        this.recordingTimer = setInterval(() => {
            this.recordingDuration++;
            this.updateDuration();
        }, 1000);
    }

    stopTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }

    updateDuration() {
        const minutes = Math.floor(this.recordingDuration / 60);
        const seconds = this.recordingDuration % 60;
        this.durationElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    startVolumeMonitoring(stream) {
        if (this.audioContext && this.analyser) {
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);
            
            const updateVolume = () => {
                if (this.isRecording) {
                    this.analyser.getByteFrequencyData(this.dataArray);
                    const average = this.dataArray.reduce((a, b) => a + b) / this.dataArray.length;
                    this.volumeLevel = Math.round((average / 255) * 100);
                    this.volumeElement.textContent = `${this.volumeLevel}%`;
                    requestAnimationFrame(updateVolume);
                }
            };
            updateVolume();
        }
    }

    stopVolumeMonitoring() {
        if (this.microphone) {
            this.microphone.disconnect();
            this.microphone = null;
        }
        this.volumeLevel = 0;
        this.volumeElement.textContent = '0%';
    }

    showError(message) {
        // Create error notification
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const recorder = new AudioRecorder();
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
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
        
        .recording-waves {
            display: none;
            justify-content: center;
            align-items: center;
            gap: 4px;
            margin-top: 20px;
        }
        
        .wave {
            width: 4px;
            height: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 2px;
            animation: wave 1.5s ease-in-out infinite;
        }
        
        .wave-1 { animation-delay: 0s; }
        .wave-2 { animation-delay: 0.1s; }
        .wave-3 { animation-delay: 0.2s; }
        .wave-4 { animation-delay: 0.3s; }
        .wave-5 { animation-delay: 0.4s; }
        
        @keyframes wave {
            0%, 100% { height: 20px; }
            50% { height: 40px; }
        }
    `;
    document.head.appendChild(style);
});
