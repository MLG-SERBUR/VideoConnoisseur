# VideoConnoisseur Installation and Setup Guide

## Overview

VideoConnoisseur is a web-based, TikTok/Reels-style local video processing application with AI-powered scoring and self-adjusting learning capabilities.

## Quick Start

### 1. Install Dependencies with uv

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install all dependencies
uv sync
```

### 2. Set Up Ollama

```bash
# Start Ollama service
ollama serve

# In a separate terminal, pull the vision model
ollama run llava
```

### 3. Create Required Directories

```bash
mkdir -p videos models temp_processing .kilo/agent
```

### 4. Run the Application

```bash
python app.py
```

The application will start on http://0.0.0.0:5000

## Detailed Installation

### Step 1: Create Virtual Environment

```bash
# Using uv (recommended)
uv venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Step 2: Install Dependencies

```bash
# Install using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Step 3: Configure Ollama

1. **Install Ollama** (if not already installed):
   - Visit https://ollama.com/download
   - Follow installation instructions for your OS

2. **Start Ollama Service**:
   ```bash
   ollama serve
   ```

3. **Pull Vision Model**:
   ```bash
   ollama run llava
   ```

   Alternative vision models:
   ```bash
   ollama run llama3.2-vision
   ollama run moondream
   ```

4. **Pull Audio Model** (optional, for faster-whisper):
   ```bash
   ollama pull faster-whisper:base
   ```

### Step 4: Create Directory Structure

```bash
# Create required directories
mkdir -p videos models temp_processing .kilo/agent

# Create placeholder files
touch videos/.gitkeep
touch models/.gitkeep
touch temp_processing/.gitkeep
```

### Step 5: Configure Application

Edit `config.py` to customize:

```python
# API settings
API_HOST = '0.0.0.0'
API_PORT = 5000

# Processing settings
FRAME_INTERVAL = 2  # seconds between frames
MODEL_SIZE = 'base'  # 'base', 'small', 'medium', 'large'

# Ollama settings
OLLAMA_HOST = 'http://localhost:11434'
OLLAMA_MODEL = 'llava'
```

### Step 6: Run the Application

```bash
python app.py
```

The application will start and you should see:
```
Starting Flask server on 0.0.0.0:5000
```

Access the web interface at: http://localhost:5000

## Using the Application

### Uploading Videos

1. **Method 1: Drag and Drop**
   - Drag video files into the browser window
   - Supported formats: mp4, mov, avi, mkv, webm, flv, wmv

2. **Method 2: File Dialog**
   - Click the file input in the upload section
   - Select video files from your computer

3. **Method 3: Manual Placement**
   - Place video files in the `videos/` directory
   - The application will automatically detect and process them

### Interacting with Videos

1. **Play/Pause**: Click play button or press Space
2. **Next Video**: Click thumbs up (👍) or press right arrow
3. **Previous Video**: Click thumbs down (👎) or press left arrow
4. **Skip Video**: Click skip button (⏭)
5. **Keyboard Shortcuts**:
   - `1`: Vote "Keep"
   - `2`: Vote "Junk"
   - `→`: Next video
   - `←`: Previous video
   - `Space`: Play/Pause

### Understanding the Interface

**Video Player**: Full-screen video player with overlay controls

**Info Panel**:
- **Video Info**: Filename, current score, score bar
- **Features Detected**: Audio and visual features identified by AI
- **Current Weights**: Feature weights used for scoring
- **History**: Recent voting actions

**Scoring System**:
- Each feature has an initial weight
- Voting adjusts weights:
  - **Thumbs Up**: Increases feature weights
  - **Thumbs Down**: Decreases feature weights
- Videos are sorted by weighted score

## Memory Management

The application is designed to respect your 6GB VRAM limit:

- Models are unloaded immediately after use
- Torch cache is cleared between processing stages
- Frames are processed in-memory without disk writes
- Garbage collection is triggered after audio processing

### Memory Optimization Tips

1. **Reduce Model Size**:
   ```python
   MODEL_SIZE = 'base'  # Instead of 'large'
   ```

2. **Increase Frame Interval**:
   ```python
   FRAME_INTERVAL = 3  # Process fewer frames
   ```

3. **Limit Video Duration**:
   - Process shorter clips
   - Use video editing software to trim clips before processing

## Troubleshooting

### Issue: Ollama Connection Error

**Solution**:
```bash
# Ensure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Issue: Model Not Found

**Solution**:
```bash
# Pull the model
ollama run llava

# Or try alternative models
ollama run llama3.2-vision
ollama run moondream
```

### Issue: Out of Memory (OOM)

**Solutions**:
1. Reduce model size in `config.py`:
   ```python
   MODEL_SIZE = 'small'  # or 'base'
   ```

2. Increase frame interval:
   ```python
   FRAME_INTERVAL = 3  # or 4
   ```

3. Restart application to clear GPU memory

4. Reduce video resolution before processing

### Issue: No Videos Processed

**Check**:
1. Video format compatibility:
   ```bash
   # Supported formats: mp4, mov, avi, mkv, webm, flv, wmv
   ```

2. Videos directory:
   ```bash
   ls -la videos/
   ```

3. Application logs for errors

### Issue: Slow Processing

**Solutions**:
1. Use GPU acceleration (CUDA)
2. Reduce video resolution
3. Decrease frame rate
4. Process shorter video clips

## Database File Structure

The application creates the following files:

- `videos.db`: SQLite database with video metadata and features
- `weights.json`: Feature weights for scoring (auto-generated)
- `liked_videos.txt`: Paths of videos you've liked
- `disliked_videos.txt`: Paths of videos you've disliked

## API Endpoints

- `GET /`: Main web interface
- `GET /api/weights`: Current feature weights
- `GET /api/videos`: All videos sorted by score
- `POST /api/video/<id>/vote`: Vote on a video
- `GET /api/video/<id>`: Video details with scoring

## Advanced Features

### Custom Feature Weights

Edit `weights.json` to adjust initial weights:

```json
{
  "heard_keyword_victory": 10.0,
  "heard_keyword_glitch": 5.0,
  "saw_win_screen": 15.0
}
```

### Batch Processing

Place multiple videos in the `videos/` directory and they will be processed automatically.

### Integration with External Tools

The application can be extended to integrate with:
- Video editing software
- Cloud storage services
- Machine learning pipelines
- Analytics platforms

## Maintenance

### Regular Tasks

1. **Monitor Database Size**:
   ```bash
   ls -lh videos.db
   ```

2. **Check Log Files**:
   - Application logs are printed to console
   - Consider adding file logging for production use

3. **Update Weights**:
   - Weights are automatically updated based on your votes
   - Monitor `weights.json` for changes

### Backup Strategy

```bash
# Backup important files
cp videos.db videos.db.backup
cp weights.json weights.json.backup
cp liked_videos.txt liked_videos.txt.backup
cp disliked_videos.txt disliked_videos.txt.backup
```

## Performance Tips

1. **Use GPU**: Ensure CUDA is properly configured
2. **Batch Processing**: Process multiple videos at once
3. **Frame Sampling**: Adjust `FRAME_INTERVAL` based on video length
4. **Model Selection**: Choose appropriate model size for your hardware

## Security Considerations

- Keep your Ollama models updated
- Use file validation for uploaded videos
- Monitor system resources
- Backup important data regularly

## Support and Contributing

For issues and feature requests, please refer to the project's GitHub repository.

## License

MIT License - Free to use and modify for personal and commercial use.