// History Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const searchInput = document.getElementById('searchInput');
    const emotionFilter = document.getElementById('emotionFilter');
    const sortBy = document.getElementById('sortBy');
    const historyList = document.getElementById('historyList');
    const emptyState = document.getElementById('emptyState');
    const totalAnalyses = document.getElementById('totalAnalyses');
    const mostCommonEmotion = document.getElementById('mostCommonEmotion');
    const averageConfidence = document.getElementById('averageConfidence');
    const lastAnalysis = document.getElementById('lastAnalysis');

    // Sample data (in real app, this would come from the server)
    let historyData = [
        {
            id: 1,
            emotion: 'happy',
            confidence: 87,
            timestamp: new Date(Date.now() - 2 * 60 * 1000), // 2 minutes ago
            source: 'Recorded Audio',
            duration: '3.2s'
        },
        {
            id: 2,
            emotion: 'sad',
            confidence: 92,
            timestamp: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
            source: 'Uploaded File',
            duration: '4.1s'
        },
        {
            id: 3,
            emotion: 'neutral',
            confidence: 78,
            timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000), // 3 hours ago
            source: 'Recorded Audio',
            duration: '2.8s'
        },
        {
            id: 4,
            emotion: 'angry',
            confidence: 85,
            timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
            source: 'Uploaded File',
            duration: '5.2s'
        }
    ];

    // Initialize page
    init();

    function init() {
        updateStatistics();
        renderHistoryList();
        setupEventListeners();
    }

    function setupEventListeners() {
        searchInput.addEventListener('input', filterHistory);
        emotionFilter.addEventListener('change', filterHistory);
        sortBy.addEventListener('change', sortHistory);
    }

    function updateStatistics() {
        const total = historyData.length;
        totalAnalyses.textContent = total;

        if (total === 0) {
            mostCommonEmotion.textContent = '-';
            averageConfidence.textContent = '0%';
            lastAnalysis.textContent = '-';
            return;
        }

        // Calculate most common emotion
        const emotionCounts = {};
        historyData.forEach(item => {
            emotionCounts[item.emotion] = (emotionCounts[item.emotion] || 0) + 1;
        });
        
        const mostCommon = Object.keys(emotionCounts).reduce((a, b) => 
            emotionCounts[a] > emotionCounts[b] ? a : b
        );
        mostCommonEmotion.textContent = mostCommon.charAt(0).toUpperCase() + mostCommon.slice(1);

        // Calculate average confidence
        const avgConf = Math.round(
            historyData.reduce((sum, item) => sum + item.confidence, 0) / total
        );
        averageConfidence.textContent = `${avgConf}%`;

        // Get last analysis time
        const last = historyData.sort((a, b) => b.timestamp - a.timestamp)[0];
        lastAnalysis.textContent = formatTimeAgo(last.timestamp);
    }

    function formatTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return `${diffInSeconds}s ago`;
        } else if (diffInSeconds < 3600) {
            return `${Math.floor(diffInSeconds / 60)}m ago`;
        } else if (diffInSeconds < 86400) {
            return `${Math.floor(diffInSeconds / 3600)}h ago`;
        } else {
            return `${Math.floor(diffInSeconds / 86400)}d ago`;
        }
    }

    function getEmotionIcon(emotion) {
        const icons = {
            'happy': 'fas fa-smile',
            'sad': 'fas fa-frown',
            'angry': 'fas fa-angry',
            'fearful': 'fas fa-surprise',
            'surprised': 'fas fa-grin-beam',
            'disgust': 'fas fa-grimace',
            'calm': 'fas fa-smile-beam',
            'neutral': 'fas fa-meh'
        };
        return icons[emotion] || 'fas fa-question';
    }

    function renderHistoryList(filteredData = historyData) {
        if (filteredData.length === 0) {
            historyList.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        historyList.style.display = 'block';
        emptyState.style.display = 'none';

        historyList.innerHTML = filteredData.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-icon">
                    <i class="${getEmotionIcon(item.emotion)}"></i>
                </div>
                <div class="history-content">
                    <div class="history-header">
                        <h4>${item.emotion.charAt(0).toUpperCase() + item.emotion.slice(1)}</h4>
                        <span class="history-time">${formatTimeAgo(item.timestamp)}</span>
                    </div>
                    <div class="history-details">
                        <div class="confidence-bar">
                            <span class="confidence-label">Confidence: ${item.confidence}%</span>
                            <div class="confidence-track">
                                <div class="confidence-fill" style="width: ${item.confidence}%"></div>
                            </div>
                        </div>
                        <div class="history-meta">
                            <span class="source">${item.source}</span>
                            <span class="duration">${item.duration}</span>
                        </div>
                    </div>
                </div>
                <div class="history-actions">
                    <button class="action-btn" title="Play Audio" onclick="playAudio(${item.id})">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="action-btn" title="Delete" onclick="deleteAnalysis(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    function filterHistory() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedEmotion = emotionFilter.value;
        
        let filtered = historyData.filter(item => {
            const matchesSearch = item.emotion.toLowerCase().includes(searchTerm) ||
                                item.source.toLowerCase().includes(searchTerm);
            const matchesEmotion = !selectedEmotion || item.emotion === selectedEmotion;
            
            return matchesSearch && matchesEmotion;
        });
        
        renderHistoryList(filtered);
    }

    function sortHistory() {
        const sortValue = sortBy.value;
        let sorted = [...historyData];
        
        switch (sortValue) {
            case 'date-desc':
                sorted.sort((a, b) => b.timestamp - a.timestamp);
                break;
            case 'date-asc':
                sorted.sort((a, b) => a.timestamp - b.timestamp);
                break;
            case 'confidence-desc':
                sorted.sort((a, b) => b.confidence - a.confidence);
                break;
            case 'confidence-asc':
                sorted.sort((a, b) => a.confidence - b.confidence);
                break;
        }
        
        renderHistoryList(sorted);
    }

    // Global functions for action buttons
    window.playAudio = function(id) {
        const item = historyData.find(item => item.id === id);
        if (item) {
            // In a real app, this would play the actual audio
            showNotification(`Playing audio for ${item.emotion} analysis`, 'info');
        }
    };

    window.deleteAnalysis = function(id) {
        if (confirm('Are you sure you want to delete this analysis?')) {
            historyData = historyData.filter(item => item.id !== id);
            updateStatistics();
            renderHistoryList();
            showNotification('Analysis deleted successfully', 'success');
        }
    };

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#f0fdf4' : '#eff6ff'};
            color: ${type === 'success' ? '#166534' : '#1d4ed8'};
            padding: 15px 20px;
            border-radius: 8px;
            border: 1px solid ${type === 'success' ? '#bbf7d0' : '#bfdbfe'};
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Add CSS animations
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
        
        .notification {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);
});