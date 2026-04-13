from flask import Flask, request, jsonify, send_from_directory, render_template
import sqlite3
import json
import os
import logging
from datetime import datetime
from preprocessing import VideoProcessor
from models import ScorePredictor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect('videos.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    conn = get_db_connection()
    
    # Videos table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            duration REAL,
            score REAL DEFAULT 0,
            is_liked BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audio features table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS audio_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            transcript TEXT,
            keywords TEXT,
            speaker_changes INTEGER DEFAULT 0,
            energy_peaks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    
    # Visual features table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS visual_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            features TEXT,
            objects_detected TEXT,
            scene_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    
    # Processing jobs table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS processing_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            job_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            progress REAL DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    
    # Weights table for self-adjusting learning
    conn.execute('''
        CREATE TABLE IF NOT EXISTS weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_name TEXT UNIQUE NOT NULL,
            weight REAL DEFAULT 1.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize default weights
    default_weights = {
        'heard_keyword_victory': 10.0,
        'heard_keyword_glitch': 5.0,
        'heard_speaker_change': 2.0,
        'heard_high_energy': 3.0,
        'saw_win_screen': 15.0,
        'saw_glitch_effect': 10.0,
        'saw_object_detected': 2.0
    }
    
    for feature, weight in default_weights.items():
        conn.execute('''
            INSERT OR IGNORE INTO weights (feature_name, weight) 
            VALUES (?, ?)
        ''', (feature, weight))
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def get_or_create_weights():
    """Get current weights or create default ones."""
    conn = get_db_connection()
    weights = {}
    
    for row in conn.execute('SELECT feature_name, weight FROM weights'):
        weights[row['feature_name']] = row['weight']
    
    conn.close()
    
    # Add any missing default weights
    default_weights = {
        'heard_keyword_victory': 10.0,
        'heard_keyword_glitch': 5.0,
        'heard_speaker_change': 2.0,
        'heard_high_energy': 3.0,
        'saw_win_screen': 15.0,
        'saw_glitch_effect': 10.0,
        'saw_object_detected': 2.0
    }
    
    for feature, default_weight in default_weights.items():
        if feature not in weights:
            weights[feature] = default_weight
            conn = get_db_connection()
            conn.execute('INSERT INTO weights (feature_name, weight) VALUES (?, ?)', 
                        (feature, default_weight))
            conn.commit()
            conn.close()
    
    return weights

def save_weight_update(feature, delta):
    """Update a single weight value."""
    conn = get_db_connection()
    conn.execute('''
        UPDATE weights 
        SET weight = weight + ?, last_updated = CURRENT_TIMESTAMP 
        WHERE feature_name = ?
    ''', (delta, feature))
    conn.commit()
    conn.close()

def calculate_video_score(video_features, weights):
    """Calculate a score for a video based on its features and current weights."""
    score = 0
    score_details = []
    
    for feature_name, feature_value in video_features.items():
        weight = weights.get(feature_name, 1.0)
        contribution = feature_value * weight
        score += contribution
        if contribution != 0:
            score_details.append(f"{feature_name}: {feature_value} * {weight} = {contribution}")
    
    return score, score_details

app = Flask(__name__, 
            static_folder='.',
            template_folder='templates')

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/video/<path:filename>')
def serve_video(filename):
    """Serve video files."""
    videos_dir = os.path.join(os.getcwd(), 'videos')
    return send_from_directory(videos_dir, filename)

@app.route('/api/weights', methods=['GET'])
def get_weights():
    """Get current weights."""
    weights = get_or_create_weights()
    return jsonify(weights)

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get all videos with their scores, sorted by score."""
    conn = get_db_connection()
    weights = get_or_create_weights()
    
    videos = []
    for row in conn.execute('SELECT * FROM videos ORDER BY score DESC'):
        video_data = dict(row)
        # Calculate current score with weights
        video_features = {
            'heard_keyword_victory': video_data.get('heard_keyword_victory', 0),
            'heard_keyword_glitch': video_data.get('heard_keyword_glitch', 0),
            'heard_speaker_change': video_data.get('heard_speaker_change', 0),
            'heard_high_energy': video_data.get('heard_high_energy', 0),
            'saw_win_screen': video_data.get('saw_win_screen', 0),
            'saw_glitch_effect': video_data.get('saw_glitch_effect', 0),
            'saw_object_detected': video_data.get('saw_object_detected', 0)
        }
        
        current_score, _ = calculate_video_score(video_features, weights)
        video_data['current_score'] = current_score
        videos.append(video_data)
    
    conn.close()
    return jsonify(videos)

@app.route('/api/video/<int:video_id>/vote', methods=['POST'])
def vote_video(video_id):
    """Handle video voting and update weights."""
    vote_type = request.json.get('vote')  # 'like' or 'dislike'
    
    conn = get_db_connection()
    
    # Get video features
    video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # Get features from related tables
    audio_features = conn.execute('SELECT * FROM audio_features WHERE video_id = ?', (video_id,)).fetchone()
    visual_features = conn.execute('SELECT * FROM visual_features WHERE video_id = ?', (video_id,)).fetchone()
    
    # Prepare feature list for weight updates
    features_to_update = []
    
    if audio_features:
        if audio_features['keywords']:
            keywords = json.loads(audio_features['keywords'])
            for keyword in keywords:
                if 'victory' in keyword.lower():
                    features_to_update.append('heard_keyword_victory')
                elif 'glitch' in keyword.lower():
                    features_to_update.append('heard_keyword_glitch')
                else:
                    features_to_update.append('heard_keyword_other')
        
        if audio_features['speaker_changes'] and audio_features['speaker_changes'] > 0:
            features_to_update.append('heard_speaker_change')
        
        if audio_features['energy_peaks'] and audio_features['energy_peaks'] > 0:
            features_to_update.append('heard_high_energy')
    
    if visual_features:
        features = json.loads(visual_features['features'])
        if features.get('win_screen', False):
            features_to_update.append('saw_win_screen')
        if features.get('glitch', False):
            features_to_update.append('saw_glitch_effect')
        if features.get('objects'):
            features_to_update.append('saw_object_detected')
    
    # Apply weight updates
    delta = 1 if vote_type == 'like' else -1
    for feature in set(features_to_update):  # Use set to avoid duplicate updates
        save_weight_update(feature, delta)
    
    # Update video vote status
    is_liked = 1 if vote_type == 'like' else 0
    conn.execute('UPDATE videos SET is_liked = ? WHERE id = ?', (is_liked, video_id))
    
    # Record in liked/disliked files
    file_path = video['file_path']
    filename = 'liked_videos.txt' if vote_type == 'like' else 'disliked_videos.txt'
    with open(filename, 'a') as f:
        f.write(file_path + '\n')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'weights_updated': features_to_update})

@app.route('/api/video/<int:video_id>')
def get_video_details(video_id):
    """Get detailed information about a specific video."""
    conn = get_db_connection()
    video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
    
    if not video:
        conn.close()
        return jsonify({'error': 'Video not found'}), 404
    
    video_data = dict(video)
    
    # Get audio features
    audio_features = conn.execute('SELECT * FROM audio_features WHERE video_id = ?', (video_id,)).fetchone()
    video_data['audio_features'] = dict(audio_features) if audio_features else {}
    
    # Get visual features
    visual_features = conn.execute('SELECT * FROM visual_features WHERE video_id = ?', (video_id,)).fetchone()
    video_data['visual_features'] = dict(visual_features) if visual_features else {}
    
    # Get current score with weights
    weights = get_or_create_weights()
    video_features_dict = {
        'heard_keyword_victory': video_data.get('heard_keyword_victory', 0),
        'heard_keyword_glitch': video_data.get('heard_keyword_glitch', 0),
        'heard_speaker_change': video_data.get('heard_speaker_change', 0),
        'heard_high_energy': video_data.get('heard_high_energy', 0),
        'saw_win_screen': video_data.get('saw_win_screen', 0),
        'saw_glitch_effect': video_data.get('saw_glitch_effect', 0),
        'saw_object_detected': video_data.get('saw_object_detected', 0)
    }
    
    current_score, score_details = calculate_video_score(video_features_dict, weights)
    video_data['current_score'] = current_score
    video_data['score_details'] = score_details
    
    conn.close()
    return jsonify(video_data)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start the server
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)