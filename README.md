# VideoConnoisseur - TikTok/Reels Style Local Video Application

A web-based, self-adjusting video processing application with AI-powered scoring and personalized feeds.

## Features

- **AI Pre-Processing Pipeline**: Automatic video analysis using audio transcription and vision models
- **Self-Adjusting Learning**: Dynamic weight system that learns from your voting behavior
- **Local Network Access**: Web UI accessible from any device on your local network
- **In-Memory Processing**: Frame extraction without creating temporary files
- **Real-Time Feedback**: Immediate weight updates based on your votes

## Requirements

- Python 3.8+
- Ollama installed and running
- CUDA-compatible GPU (recommended for faster-whisper)
- ~6GB VRAM for model processing

## Installation

### 1. Create Virtual Environment
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Start Ollama and Pull Model
```bash
# Start Ollama service
ollama serve

# Pull the vision model
ollama run llava
```

### 4. Setup Application
```bash
# Create necessary directories
python setup.py

# Or manually create directories:
mkdir videos models temp_processing .kilo/agent
```

### 5. Run the Application
```bash
python app.py
```

## Usage

1. **Start the Application**: Run `python app.py`
2. **Access Web UI**: Open http://localhost:5000 in your browser
3. **Upload Videos**: Place video files in the `videos/` directory or use the upload interface
4. **Vote on Videos**: Click thumbs up/down to score videos
5. **Personalized Feed**: Videos are automatically sorted by their AI-predicted scores

## How It Works

### AI Pre-Processing Pipeline

1. **Audio Analysis**: Uses faster-whisper to transcribe audio and detect:
   - Keyword mentions (victory, glitch, etc.)
   - Speaker changes
   - High energy segments
   
2. **Vision Analysis**: Extracts frames in-memory and analyzes with Ollama:
   - Detects victory screens
   - Identifies glitches
   - Recognizes objects
   
3. **Database Storage**: Saves all features to SQLite for persistent learning

### Self-Adjusting Learning

The system maintains a `weights.json` file with feature weights:
- **Thumbs Up**: Increases weights of detected features
- **Thumbs Down**: Decreases weights of detected features
- **Dynamic Scoring**: Videos are sorted by weighted feature scores

### File Structure

```
VideoConnoisseur/
├── app.py              # Main Flask application
├── preprocessing.py    # Video processing logic
├── models.py          # ML model management
├── config.py          # Configuration settings
├── setup.py          # Setup script
├── videos.db          # SQLite database
├── weights.json       # Feature weights (auto-generated)
├── liked_videos.txt   # Paths of liked videos
├── disliked_videos.txt # Paths of disliked videos
└── videos/            # Video storage directory
```

## API Endpoints

- `GET /` - Main web interface
- `GET /api/weights` - Get current feature weights
- `GET /api/videos` - Get all videos sorted by score
- `POST /api/video/<id>/vote` - Vote on a video
- `GET /api/video/<id>` - Get detailed video information

## Configuration

Key settings in `config.py`:
- `FRAME_INTERVAL`: Seconds between extracted frames (default: 2)
- `MODEL_SIZE`: faster-whisper model size (base, small, medium, large)
- `OLLAMA_MODEL`: Vision model to use (llava, llama3.2-vision, etc.)
- `DEFAULT_WEIGHTS`: Initial feature weights for scoring

## Memory Management

The application is designed to respect your 6GB VRAM limit:
- Models are unloaded immediately after use
- Torch cache is cleared between processing stages
- Frames are processed in-memory without disk writes
- Garbage collection is triggered after audio processing

## Troubleshooting

### Ollama Connection Error
Ensure Ollama is running: `ollama serve`

### Model Not Found
Pull the model: `ollama run llava`

### Out of Memory
- Reduce `MODEL_SIZE` in config.py
- Increase `FRAME_INTERVAL` to process fewer frames
- Restart application to clear memory

### No Videos Processed
- Check video format compatibility (mp4, mov, avi, mkv, webm)
- Verify videos directory contains files
- Check application logs for processing errors

## License

MIT License - Free to use and modify

## Contributing

Suggestions and improvements welcome! Focus areas:
- Additional vision models
- More audio features
- Advanced learning algorithms
- Performance optimizations