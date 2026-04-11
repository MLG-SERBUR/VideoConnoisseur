import os
import subprocess
import numpy as np
from transformers import AutoProcessor, AutoModel
from einops import rearrange
import torch

# Questions to ask Moondream2 for each frame
QUESTIONS = [
    "Is there a 'Victory', 'Defeat', 'MVP', or 'Play of the Game' text on screen? Is there a kill-feed in the corner?",
    "Is there a player drawing on the screen, using a chatbox, or performing a hand gesture close to the camera?",
    "Are there any characters in a T-pose, objects clipping through walls, or visual artifacts like stretched textures?"
]

def extract_frames(video_path, frame_dir):
    """Extract frames every 3 seconds using ffmpeg"""
    os.makedirs(frame_dir, exist_ok=True)
    command = [
        'ffmpeg', '-i', video_path, '-vf', 'fps=1/3',
        os.path.join(frame_dir, 'frame_%04d.jpg'), '-y'
    ]
    subprocess.run(command, capture_output=True, check=True)

def analyze_visuals(video_path):
    """Analyze video frames for visual content"""
    frame_dir = video_path + '_frames'
    
    try:
        # Extract frames
        extract_frames(video_path, frame_dir)
        frame_files = sorted(os.listdir(frame_dir))
        
        # Load Moondream2 model
        model_name = "MoonDreamer/MoonDreamer2"
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Analyze each frame
        scores = []
        reasons = []
        
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            
            # Load and preprocess frame
            image = processor(image=frame_path, return_tensors="pt")
            
            # Run inference
            with torch.no_grad():
                outputs = model(image.pixel_values)
            
            # Analyze responses to questions
            for i, question in enumerate(QUESTIONS):
                # Get model response
                response = outputs.logits[i].softmax(dim=-1)
                answer = response.argmax().item()
                
                # Score based on answers
                if i == 0 and answer == 1:  # UI text detected
                    scores.append(50)
                    reasons.append("UI Text (Victory/POTG) detected")
                elif i == 1 and answer == 1:  # Social interaction detected
                    scores.append(40)
                    reasons.append("VRChat Mute interaction (drawing/gestures) detected")
                elif i == 2 and answer == 1:  # Glitch detected
                    scores.append(30)
                    reasons.append("Glitch/Anomaly detected")
        
        # Clean up frames
        for frame_file in frame_files:
            os.remove(os.path.join(frame_dir, frame_file))
        os.rmdir(frame_dir)
        
        # Calculate final score
        if not scores:
            return -30, "No speech and no UI elements"
        
        return sum(scores), "; ".join(reasons)
    
    except Exception as e:
        return -30, f"Visual analysis failed: {str(e)}"

if __name__ == "__main__":
    # Test the visual analysis
    test_video = "test_video.mp4"
    score, reason = analyze_visuals(test_video)
    print(f"Visual Score: {score}")
    print(f"Reason: {reason}")