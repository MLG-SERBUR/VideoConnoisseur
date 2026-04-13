# Database Schema for Video Processing Application

## Tables

### users
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- username (VARCHAR(80), UNIQUE, NOT NULL)
- email (VARCHAR(120), UNIQUE, NOT NULL)
- password_hash (VARCHAR(128), NOT NULL)
- created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- updated_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- is_admin (BOOLEAN, DEFAULT 0)

### videos
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- user_id (INTEGER, FOREIGN KEY REFERENCES users(id))
- filename (VARCHAR(255), NOT NULL)
- original_filename (VARCHAR(255))
- file_path (VARCHAR(500), NOT NULL)
- file_size (BIGINT)
- file_format (VARCHAR(10))
- status (VARCHAR(20), DEFAULT 'pending')
- error_message (TEXT)
- created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- updated_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- processed_at (DATETIME)

### video_frames
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- video_id (INTEGER, FOREIGN KEY REFERENCES videos(id))
- frame_number (INTEGER, NOT NULL)
- frame_path (VARCHAR(500))
    thumbnail_path (VARCHAR(500))
    timestamp (FLOAT)
    created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### analysis_results
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- video_id (INTEGER, FOREIGN KEY REFERENCES videos(id))
    frame_id (INTEGER, FOREIGN KEY REFERENCES video_frames(id))
    prediction_data (JSON)
    confidence_score (FLOAT)
    detected_class (VARCHAR(100))
    bounding_box (JSON)
    processing_time (FLOAT)
    created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### processing_jobs
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    video_id (INTEGER, FOREIGN KEY REFERENCES videos(id))
    job_type (VARCHAR(50))
    status (VARCHAR(20))
    parameters (JSON)
    result_data (JSON)
    error_message (TEXT)
    started_at (DATETIME)
    completed_at (DATETIME)
    created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### model_versions
- id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    model_name (VARCHAR(100))
    version (VARCHAR(20))
    model_file (VARCHAR(500))
    training_data (VARCHAR(500))
    accuracy_score (FLOAT)
    created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    is_active (BOOLEAN, DEFAULT 1)

## Indexes
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_video_frames_video_id ON video_frames(video_id);
CREATE INDEX idx_analysis_results_video_id ON analysis_results(video_id);
CREATE INDEX idx_processing_jobs_video_id ON processing_jobs(video_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);

## Initial Data
INSERT INTO users (username, email, password_hash) VALUES 
('admin', 'admin@videoprocessing.com', 'pbkdf2:sha256:150000$abc123$def456');

INSERT INTO model_versions (model_name, version, model_file, accuracy_score) VALUES 
('video_classifier', '1.0.0', 'models/classifier_v1.pkl', 0.95);