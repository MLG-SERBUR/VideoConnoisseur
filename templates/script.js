class VideoFeedManager {
    constructor() {
        this.currentVideoIndex = 0;
        this.videos = [];
        this.weights = {};
        this.history = [];
        this.isProcessing = false;
        this.currentVideoElement = null;
        
        // DOM Elements
        this.videoPlayer = document.getElementById('video-player');
        this.videoContainer = document.getElementById('video-player-container');
        this.videoOverlay = document.getElementById('video-overlay');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.progressBar = document.getElementById('progress-bar');
        this.progressFill = document.getElementById('progress-fill');
        this.btnThumbsUp = document.getElementById('btn-thumbs-up');
        this.btnThumbsDown = document.getElementById('btn-thumbs-down');
        this.btnSkip = document.getElementById('btn-skip');
        this.videoCounter = document.getElementById('video-counter');
        this.videoFilename = document.getElementById('video-filename');
        this.featuresList = document.getElementById('features-list');
        this.videoScore = document.getElementById('video-score');
        this.scoreBarFill = document.getElementById('score-bar-fill');
        this.weightsDisplay = document.getElementById('weights-display');
        this.historyList = document.getElementById('history-list');
        
        this.initializeEventListeners();
        this.loadWeights();
        this.loadVideos();
    }
    
    initializeEventListeners() {
        // Control buttons
        this.btnThumbsUp.addEventListener('click', () => this.vote('like'));
        this.btnThumbsDown.addEventListener('click', () => this.vote('dislike'));
        this.btnSkip.addEventListener('click', () => this.skipVideo());
        
        // Video events
        this.videoPlayer.addEventListener('loadedmetadata', () => {
            this.updateProgress();
        });
        
        this.videoPlayer.addEventListener('timeupdate', () => {
            this.updateProgress();
        });
        
        this.videoPlayer.addEventListener('ended', () => {
            this.nextVideo();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.togglePlayPause();
            } else if (e.key === 'ArrowRight') {
                this.nextVideo();
            } else if (e.key === 'ArrowLeft') {
                this.previousVideo();
            } else if (e.key === '1') {
                this.vote('like');
            } else if (e.key === '2') {
                this.vote('dislike');
            }
        });
        
        // File drop support
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('dragleave', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => {
            e.preventDefault();
            this.handleDrop(e);
        });
        
        // File input
        document.getElementById('file-input').addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });
    }
    
    async loadWeights() {
        try {
            const response = await fetch('/api/weights');
            this.weights = await response.json();
            this.updateWeightsDisplay();
        } catch (error) {
            console.error('Failed to load weights:', error);
        }
    }
    
    async loadVideos() {
        try {
            const response = await fetch('/api/videos');
            this.videos = await response.json();
            this.currentVideoIndex = 0;
            this.renderVideoCounter();
            if (this.videos.length > 0) {
                this.playCurrentVideo();
            }
        } catch (error) {
            console.error('Failed to load videos:', error);
        }
    }
    
    renderVideoCounter() {
        this.videoCounter.textContent = `Video ${this.currentVideoIndex + 1} of ${this.videos.length}`;
    }
    
    renderVideoInfo() {
        const video = this.videos[this.currentVideoIndex];
        if (!video) return;
        
        // Update filename
        this.videoFilename.textContent = video.file_name;
        
        // Update score
        this.videoScore.textContent = video.current_score || 0;
        
        // Update score bar
        const score = video.current_score || 0;
        this.scoreBarFill.style.width = score + '%';
        
        // Update features
        this.featuresList.innerHTML = '';
        if (video.audio_features) {
            Object.entries(video.audio_features).forEach(([key, value]) => {
                if (value > 0) {
                    const item = this.createFeatureItem(key, value);
                    this.featuresList.appendChild(item);
                }
            });
        }
        
        if (video.visual_features) {
            Object.entries(video.visual_features).forEach(([key, value]) => {
                if (value > 0) {
                    const item = this.createFeatureItem(key, value);
                    this.featuresList.appendChild(item);
                }
            });
        }
        
        // Update weights display
        this.updateWeightsDisplay();
        
        // Update history
        this.updateHistory();
    }
    
    createFeatureItem(name, value) {
        const div = document.createElement('div');
        div.className = 'feature-item';
        div.innerHTML = `
            <span class="feature-name">${name}</span>
            <span class="feature-value">${value}</span>
        `;
        return div;
    }
    
    updateWeightsDisplay() {
        this.weightsDisplay.innerHTML = '';
        Object.entries(this.weights).forEach(([key, value]) => {
            const div = document.createElement('div');
            div.className = 'weight-row';
            const isPositive = value > 0;
            div.innerHTML = `
                <span class="weight-name">${key}</span>
                <span class="weight-value ${isPositive ? 'positive' : 'negative'}">${value.toFixed(2)}</span>
            `;
            this.weightsDisplay.appendChild(div);
        });
    }
    
    updateHistory() {
        // Keep last 10 items
        const recentHistory = this.history.slice(-10);
        this.historyList.innerHTML = '';
        recentHistory.forEach(item => {
            const div = document.createElement('div');
            div.className = `history-item ${item.action}`;
            div.innerHTML = `
                <span>${item.file_name}</span>
                <span>${item.action.toUpperCase()}</span>
            `;
            this.historyList.appendChild(div);
        });
    }
    
    async playCurrentVideo() {
        if (this.currentVideoIndex < 0 || this.currentVideoIndex >= this.videos.length) {
            return;
        }
        
        const video = this.videos[this.currentVideoIndex];
        
        // Show loading
        this.showLoading(true);
        
        // Set video source
        this.videoPlayer.src = `/video/${video.file_path}`;
        
        // Wait for video to load
        await new Promise((resolve) => {
            this.videoPlayer.onloadeddata = resolve;
        });
        
        // Hide loading
        this.showLoading(false);
        
        // Play video
        this.videoPlayer.play().catch(e => console.log('Autoplay prevented:', e));
        
        // Render video info
        this.renderVideoInfo();
    }
    
    showLoading(show) {
        if (show) {
            this.loadingIndicator.classList.add('visible');
            this.progressBar.style.display = 'block';
        } else {
            this.loadingIndicator.classList.remove('visible');
            this.progressBar.style.display = 'none';
            this.progressFill.style.width = '0%';
        }
    }
    
    updateProgress() {
        if (this.videoPlayer.duration) {
            const progress = (this.videoPlayer.currentTime / this.videoPlayer.duration) * 100;
            this.progressFill.style.width = progress + '%';
        }
    }
    
    togglePlayPause() {
        if (this.videoPlayer.paused) {
            this.videoPlayer.play();
        } else {
            this.videoPlayer.pause();
        }
    }
    
    async vote(type) {
        if (this.isProcessing || this.currentVideoIndex < 0) return;
        
        this.isProcessing = true;
        const video = this.videos[this.currentVideoIndex];
        
        try {
            const response = await fetch(`/api/video/${video.id}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ vote: type })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update weights locally
                result.weights_updated.forEach(feature => {
                    const delta = type === 'like' ? 1 : -1;
                    this.weights[feature] = (this.weights[feature] || 0) + delta;
                });
                
                // Update display
                this.updateWeightsDisplay();
                
                // Add to history
                this.history.push({
                    file_name: video.file_name,
                    action: type,
                    timestamp: new Date().toISOString()
                });
                
                // Update video list with new scores
                await this.loadVideos();
                
                // Show next video
                this.nextVideo();
            }
        } catch (error) {
            console.error('Vote failed:', error);
        } finally {
            this.isProcessing = false;
        }
    }
    
    nextVideo() {
        if (this.videos.length === 0) return;
        
        this.currentVideoIndex = (this.currentVideoIndex + 1) % this.videos.length;
        this.playCurrentVideo();
    }
    
    previousVideo() {
        if (this.videos.length === 0) return;
        
        this.currentVideoIndex = (this.currentVideoIndex - 1 + this.videos.length) % this.videos.length;
        this.playCurrentVideo();
    }
    
    skipVideo() {
        if (this.videos.length === 0) return;
        
        // Mark current video as junk if playing
        if (this.currentVideoIndex >= 0 && this.videoPlayer.src) {
            const video = this.videos[this.currentVideoIndex];
            this.vote('dislike');
        } else {
            this.nextVideo();
        }
    }
    
    handleDrop(event) {
        const files = event.dataTransfer.files;
        this.processFiles(files);
    }
    
    handleFileSelect(event) {
        const files = event.target.files;
        this.processFiles(files);
    }
    
    processFiles(files) {
        // Filter video files
        const videoFiles = Array.from(files).filter(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            return ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv'].includes(ext);
        });
        
        if (videoFiles.length === 0) return;
        
        // For now, just reload with new videos
        // In a full implementation, you'd upload and process them
        alert(`Found ${videoFiles.length} video files. Please place them in the videos/ directory manually or use the upload functionality in a full implementation.`);
    }
}

// Export for use in other modules
window.VideoFeedManager = VideoFeedManager;

// VideoProcessor class (from original implementation)
class VideoProcessor {
    constructor() {
        this.apiBase = '/api';
        this.currentView = 'home';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Navigation
        document.getElementById('homeBtn').addEventListener('click', () => this.showSection('home'));
        document.getElementById('uploadBtn').addEventListener('click', () => this.showSection('upload'));
        document.getElementById('resultsBtn').addEventListener('click', () => this.showSection('results'));

        // Upload form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        }
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected section
        document.getElementById(sectionName).classList.add('active');
        document.getElementById(`${sectionName}Btn`).classList.add('active');
        
        this.currentView = sectionName;

        // Load results if requested
        if (sectionName === 'results') {
            this.loadResults();
        }
    }

    async handleUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const statusDiv = document.getElementById('uploadStatus');
        const loadingDiv = document.getElementById('loading');
        const resultsContent = document.getElementById('resultsContent');

        try {
            // Show loading
            statusDiv.style.display = 'none';
            loadingDiv.classList.remove('hidden');
            resultsContent.innerHTML = '';
            this.showSection('results');

            // Upload video
            const response = await fetch(`${this.apiBase}/process`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Upload failed');
            }

            const result = await response.json();
            this.displayResults(result);

            loadingDiv.classList.add('hidden');
            
        } catch (error) {
            loadingDiv.classList.add('hidden');
            statusDiv.textContent = `Error: ${error.message}`;
            statusDiv.className = 'status-message error';
            statusDiv.style.display = 'block';
            
            setTimeout(() => {
                statusDiv.style.display = 'none';
                this.showSection('upload');
            }, 5000);
        }
    }

    displayResults(results) {
        const resultsContent = document.getElementById('resultsContent');
        
        if (results.error) {
            resultsContent.innerHTML = `<p style="color: red;">Error: ${results.error}</p>`;
            return;
        }

        let html = `
            <h3>Analysis Summary</h3>
            <div class="summary-box">
                <p><strong>Total Frames Processed:</strong> ${results.frame_count}</p>
                <p><strong>Average Confidence:</strong> ${(results.results.average_confidence * 100).toFixed(2)}%</p>
                <p><strong>Detected Actions:</strong> ${results.results.detected_actions.join(', ')}</p>
            </div>
            
            <h3>Frame Details</h3>
            <div class="frames-grid">
        `;

        results.results.predictions.forEach(pred => {
            html += `
                <div class="frame-card">
                    <h4>Frame ${pred.frame_index}</h4>
                    <p>Class: ${pred.class}</p>
                    <p>Confidence: ${(pred.confidence * 100).toFixed(2)}%</p>
                    <p>Position: (${pred.bounding_box.x}, ${pred.bounding_box.y})</p>
                </div>
            `;
        });

        html += `
            </div>
        `;

        resultsContent.innerHTML = html;
    }

    async loadResults() {
        // Load any cached results or show empty state
        const resultsContent = document.getElementById('resultsContent');
        if (resultsContent.innerHTML.trim() === '') {
            resultsContent.innerHTML = '<p>No results available yet. Upload a video to see analysis results.</p>';
        }
    }
}

// Initialize applications when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.videoFeedManager = new VideoFeedManager();
    window.videoProcessor = new VideoProcessor();
});

// Handle form submission with fetch API
async function handleFileUpload(event) {
    event.preventDefault();
    const fileInput = document.getElementById('videoFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a video file');
        return;
    }

    const formData = new FormData();
    formData.append('video', file);
    formData.append('frameRate', document.getElementById('frameRate').value);
    formData.append('targetSize', document.getElementById('targetSize').value);

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            throw new Error(result.error || 'Processing failed');
        }
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Upload failed: ' + error.message);
    }
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <h2>Analysis Results</h2>
        <div class="results-summary">
            <p>Frames processed: ${results.frame_count}</p>
            <p>Confidence: ${(results.average_confidence * 100).toFixed(2)}%</p>
        </div>
    `;
}