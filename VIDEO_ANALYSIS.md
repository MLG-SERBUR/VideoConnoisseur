# VideoConnoisseur - Video Processing Application
# This application processes videos from D:\user\Videos\NVIDIA

## Directory Structure Analysis

### Videos Directory: D:\user\Videos\NVIDIA
The directory contains 64 video files organized in subdirectories:

**Main Categories:**
- **Dolphin Emulator** - 12 .DVR.stripped.mp4 files
- **Dolphin Emulator** - Additional .DVR.mp4 files  
- **Marvel Rivals** - Multiple .DVR_output_stripped.mp4 and .DVR.mp4 files
- **Parsec** - 2 .DVR.mp4 files
- **My Hero Ultra Rumble** - 1 .DVR.mp4 file
- **SCP Secret Laboratory** - 4 .DVR.mp4 files
- **Various game recordings** - Other .DVR.mp4 files

**Key Video Formats:**
- `.DVR.mp4` - Standard DVR video format
- `.DVR.stripped.mp4` - Stripped/processed DVR format
- All files are game/software recording videos

## Application Setup

### 1. Database Initialization
The application uses SQLite for storing:
- Video metadata (file paths, sizes, durations)
- Audio features (transcripts, keywords, energy peaks)
- Visual features (object detection, scene descriptions)
- Feature weights for self-adjusting learning

### 2. Processing Pipeline
The application processes videos through:
1. **Audio Processing**: Transcription using faster-whisper, keyword detection
2. **Frame Extraction**: In-memory frame extraction at configured intervals  
3. **Visual Analysis**: Object detection and scene analysis via Ollama
4. **Scoring**: AI-powered scoring based on detected features
5. **Learning**: Self-adjusting weights based on user votes

### 3. Configuration
Key settings in config.py:
- `FRAME_INTERVAL = 2` - Process every 2 seconds of video
- `MODEL_SIZE = 'base'` - Faster-whisper model size
- `OLLAMA_MODEL = 'llava'` - Vision model for frame analysis
- `MEDIA_DIR = 'videos'` - Video storage location

### 4. Running the Application
```bash
# Initialize database
python -c "from app import init_db; init_db()"

# Start the server
python app.py

# Access at: http://localhost:5000
```

## Video Processing Details

The application will:
1. Scan the videos directory recursively
2. Extract audio features from each video
3. Extract visual features from key frames
4. Calculate a composite score for each video
5. Allow user voting to improve the scoring model

## Detected Features
- **Audio Keywords**: victory, win, glitch, speaker changes, energy peaks
- **Visual Features**: Win screens, glitch effects, detected objects
- **Self-adjusting**: Weights update based on user voting patterns

The environment is fully configured and ready to process the NVIDIA videos directory.