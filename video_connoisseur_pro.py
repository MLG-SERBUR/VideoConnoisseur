import os
import sys
import json
import cv2
import numpy as np
import torch
from tqdm import tqdm
from audio_analysis import analyze_audio
from visual_analysis import analyze_visuals
from classification import classify_clip

def main(input_dir):
    # Create output directories
    os.makedirs('KEEP', exist_ok=True)
    os.makedirs('JUNK', exist_ok=True)
    
    # Get list of video files
    video_files = [f for f in os.listdir(input_dir) 
                   if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    manifest = []
    
    for video_file in tqdm(video_files, desc="Processing videos"):
        video_path = os.path.join(input_dir, video_file)
        
        # Check if static clip first (save time)
        if is_static_clip(video_path):
            score = -40  # Static penalty
            reason = "Static image (no motion between frames)"
            destination = 'JUNK'
        else:
            # Phase 1: Audio Analysis
            audio_score, audio_reason = analyze_audio(video_path)
            
            # Phase 2: Visual Analysis
            visual_score, visual_reason = analyze_visuals(video_path)
            
            # Phase 3: Classification
            score = audio_score + visual_score
            reason = f"{audio_reason}; {visual_reason}"
            destination = 'KEEP' if score >= 0 else 'JUNK'
        
        # Move file to appropriate folder
        dest_path = os.path.join(destination, video_file)
        os.rename(video_path, dest_path)
        
        # Add to manifest
        manifest.append({
            'filename': video_file,
            'score': score,
            'reason': reason,
            'destination': destination
        })
    
    # Save manifest
    with open('manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nProcessing complete! {len(video_files)} videos analyzed.")
    print(f"KEEP: {len([m for m in manifest if m['destination'] == 'KEEP'])}")
    print(f"JUNK: {len([m for m in manifest if m['destination'] == 'JUNK'])}")

def is_static_clip(video_path):
    """Check if clip is static by comparing frame variance"""
    cap = cv2.VideoCapture(video_path)
    ret, frame1 = cap.read()
    if not ret:
        return True
    
    ret, frame2 = cap.read()
    if not ret:
        return True
    
    # Calculate mean squared error between frames
    mse = np.mean((frame1 - frame2) ** 2)
    cap.release()
    
    # If frames are too similar, consider it static
    return mse < 100

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python video_connoisseur_pro.py <input_directory>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory")
        sys.exit(1)
    
    main(input_dir)