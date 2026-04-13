"""
Configuration Module
Handles application configuration and settings
"""

import os
from pathlib import Path

class Config:
    # Database configuration
    DATABASE = 'videos.db'
    
    # Redis configuration (for caching, optional)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # API configuration
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    API_DEBUG = True
    API_THREADS = True
    
    # Processing configuration
    FRAME_INTERVAL = 2  # seconds between frames
    FRAME_QUALITY = 85  # JPEG quality (0-100)
    MODEL_SIZE = 'base'  # faster-whisper model size
    LANGUAGE = 'en'  # language for transcription
    
    # Ollama configuration
    OLLAMA_HOST = 'http://localhost:11434'
    OLLAMA_MODEL = 'llava'  # vision model for frame analysis
    
    # Model configuration
    MODEL_UPDATE_THRESHOLD = 0.1  # minimum confidence for model updates
    MIN_FEATURE_COUNT = 5  # minimum videos for model retraining
    
    # File paths
    WEIGHTS_FILE = 'weights.json'
    DATABASE_FILE = 'videos.db'
    VIDEOS_DIR = 'videos'
    
    # Default weights for self-adjusting learning
    DEFAULT_WEIGHTS = {
        'heard_keyword_victory': 10.0,
        'heard_keyword_glitch': 5.0,
        'heard_speaker_change': 2.0,
        'heard_high_energy': 3.0,
        'saw_win_screen': 15.0,
        'saw_glitch_effect': 10.0,
        'saw_object_detected': 2.0
    }
    
    @classmethod
    def get_video_directory(cls):
        """Get the directory for storing videos."""
        videos_dir = Path(cls.VIDEOS_DIR)
        videos_dir.mkdir(exist_ok=True)
        return videos_dir
    
    @classmethod
    def get_weights_file(cls):
        """Get the path to weights file."""
        return Path(cls.WEIGHTS_FILE)
    
    @classmethod
    def get_database_path(cls):
        """Get the path to database file."""
        return Path(cls.DATABASE_FILE)
    
    @classmethod
    def get_videos_directory(cls):
        """Get the directory for storing video files."""
        videos_dir = Path(cls.VIDEOS_DIR)
        videos_dir.mkdir(exist_ok=True)
        return videos_dir
    
    @classmethod
    def get_video_path(cls, filename):
        """Get the full path for a video file."""
        return cls.get_videos_directory() / filename
    
    @classmethod
    def get_temp_directory(cls):
        """Get temporary directory for in-memory processing."""
        temp_dir = Path('temp_processing')
        # Note: We don't create this directory as we process in-memory
        # But we define it for reference
        return temp_dir
    
    @classmethod
    def get_allowed_extensions(cls):
        """Get allowed video file extensions."""
        return {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv'}
    
    @classmethod
    def get_max_video_size(cls):
        """Get maximum video file size in bytes (100MB)."""
        return 100 * 1024 * 1024
    
    @classmethod
    def get_session_timeout(cls):
        """Get session timeout in seconds."""
        return 3600  # 1 hour
    
    @classmethod
    def get_logging_config(cls):
        """Get logging configuration."""
        return {
            'level': cls.LOG_LEVEL,
            'format': cls.LOG_FORMAT,
            'handlers': [
                {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'standard'
                }
            ],
            'formatters': {
                'standard': {
                    'format': cls.LOG_FORMAT
                }
            }
        }