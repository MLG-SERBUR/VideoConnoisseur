import os
import subprocess
import numpy as np
from faster_whisper import Whisper, ModelName
from pydub import AudioSegment
from scipy.signal import find_peaks

# Keywords that indicate interesting content
KEEP_KEYWORDS = [
    'clip', 'insane', 'glitch', 'no way', 'lmao', 
    'laughter', 'holy', 'how', 'did you see', 'wow', 'amazing'
]

def extract_audio(video_path, audio_path):
    """Extract audio from video using ffmpeg"""
    command = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1', audio_path, '-y'
    ]
    subprocess.run(command, capture_output=True, check=True)

def analyze_audio(video_path):
    """Analyze audio for interesting content"""
    audio_path = video_path + '.wav'
    
    try:
        # Extract audio
        extract_audio(video_path, audio_path)
        
        # Load audio file
        audio = AudioSegment.from_wav(audio_path)
        duration = len(audio) / 1000.0  # Convert to seconds
        
        # Analyze silence (below -30dB)
        silence_threshold = -30  # dB
        silence_frames = audio.dBFS < silence_threshold
        silence_percentage = np.mean(silence_frames) * 100
        
        # Use faster-whisper for transcription
        model = Whisper.create(ModelName.distil_large_v3)
        result = model.transcribe(audio_path)
        
        # Analyze transcription
        transcript = result['text'].lower()
        keywords_found = [kw for kw in KEEP_KEYWORDS if kw in transcript]
        
        # Analyze speaker changes (simple energy-based detection)
        energy = np.array(audio.rms)
        peaks, _ = find_peaks(energy, height=np.percentile(energy, 90))
        speaker_changes = len(peaks)
        
        # Calculate scores
        score = 0
        reasons = []
        
        # Keyword detection
        if keywords_found:
            score += 40
            reasons.append(f"Detected keywords: {', '.join(keywords_found)}")
        
        # Speaker changes (banter detection)
        if speaker_changes > 3 and duration < 10:
            score += 20
            reasons.append(f"High-energy banter detected ({speaker_changes} speaker changes)")
        
        # Silence check
        if silence_percentage > 90:
            score -= 50
            reasons.append(f"Total silence ({silence_percentage:.1f}% of clip)")
        
        # Default reason if nothing detected
        if not reasons:
            reasons.append("No interesting audio content detected")
        
        # Clean up
        os.remove(audio_path)
        
        return score, "; ".join(reasons)
    
    except Exception as e:
        return -30, f"Audio analysis failed: {str(e)}"

if __name__ == "__main__":
    # Test the audio analysis
    test_video = "test_video.mp4"
    score, reason = analyze_audio(test_video)
    print(f"Audio Score: {score}")
    print(f"Reason: {reason}")