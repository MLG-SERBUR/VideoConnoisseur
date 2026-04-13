import os
import sys
import json
import shutil
import torch
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image
from faster_whisper import WhisperModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- CONFIGURATION ---
INPUT_DIR = "./my_clips"
KEEP_DIR = "./KEEP"
JUNK_DIR = "./JUNK"
FRAME_INTERVAL = 3  # Seconds between frames for vision analysis
VRAM_LIMIT_GB = 6

# Keywords for "Keep" logic
KEEP_KEYWORDS = ['clip', 'insane', 'glitch', 'no way', 'lmao', 'holy', 'how', 'did you see', 'wow', 'clutch', 'pog']

class VideoConnoisseur:
    def __init__(self, input_path):
        self.input_path = input_path
        self.videos = [f for f in os.listdir(input_path) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]
        self.results = {v: {"audio_score": 0, "visual_score": 0, "reasons": []} for v in self.videos}
        
        os.makedirs(KEEP_DIR, exist_ok=True)
        os.makedirs(JUNK_DIR, exist_ok=True)

    def analyze_audio_phase(self):
        """Phase 1: Load Whisper, process all audio, then UNLOAD."""
        print(f"\n--- Phase 1: Audio Analysis ({len(self.videos)} files) ---")
        # Load Faster-Whisper (Distil-Large-v3 fits well in 6GB)
        model = WhisperModel("distil-large-v3", device="cuda", compute_type="float16")

        for video in tqdm(self.videos):
            video_path = os.path.join(self.input_path, video)
            
            try:
                # Transcribe
                segments, info = model.transcribe(video_path, beam_size=5)
                full_text = ""
                speaker_switches = 0
                last_start = 0

                for segment in segments:
                    full_text += segment.text.lower() + " "
                    # Simple banter check: if segments are short and frequent
                    if (segment.start - last_start) < 3.0:
                        speaker_switches += 1
                    last_start = segment.end

                # Scoring
                if any(kw in full_text for kw in KEEP_KEYWORDS):
                    self.results[video]["audio_score"] += 40
                    self.results[video]["reasons"].append("Exciting keywords heard")

                if speaker_switches > 5:
                    self.results[video]["audio_score"] += 20
                    self.results[video]["reasons"].append("High-energy banter detected")

                if not full_text.strip():
                    self.results[video]["audio_score"] -= 30
                    self.results[video]["reasons"].append("No speech detected")

            except Exception as e:
                print(f"Audio Error on {video}: {e}")

        # CRITICAL: Unload Whisper to free VRAM for Vision
        del model
        torch.cuda.empty_cache()
        import gc
        gc.collect()

    def analyze_visual_phase(self):
        """Phase 2: Load Moondream, process frames, then UNLOAD."""
        print(f"\n--- Phase 2: Visual Analysis ---")
        model_id = "vikhyatk/moondream2"
        revision = "2024-05-20" # Use a stable revision
        
        # Load Moondream2
        model = AutoModelForCausalLM.from_pretrained(
            model_id, trust_remote_code=True, revision=revision,
            torch_dtype=torch.float16, device_map={"": "cuda"}
        )
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

        for video in tqdm(self.videos):
            # Skip if audio already made it a definite keep (optional optimization)
            if self.results[video]["audio_score"] > 50:
                continue

            video_path = os.path.join(self.input_path, video)
            frames = self.extract_frames(video_path)
            
            for frame_img in frames:
                # Question 1: Gaming
                q1 = "Is there a 'Victory', 'Play of the Game', or 'MVP' text on screen?"
                ans1 = model.answer_question(model.encode_image(frame_img), q1, tokenizer).lower()
                
                if "yes" in ans1:
                    self.results[video]["visual_score"] += 50
                    self.results[video]["reasons"].append("Win screen/POTG detected")
                    break # Found a reason to keep, move to next video

                # Question 2: Social/Mutes
                q2 = "Is there a VRChat chatbox with text or a person drawing on a board?"
                ans2 = model.answer_question(model.encode_image(frame_img), q2, tokenizer).lower()
                if "yes" in ans2:
                    self.results[video]["visual_score"] += 40
                    self.results[video]["reasons"].append("Mute interaction detected")
                    break

                # Question 3: Glitches
                q3 = "Is any character model glitched, T-posing, or clipping through the floor?"
                ans3 = model.answer_question(model.encode_image(frame_img), q3, tokenizer).lower()
                if "yes" in ans3:
                    self.results[video]["visual_score"] += 30
                    self.results[video]["reasons"].append("Visual anomaly/glitch detected")
                    break

        del model
        torch.cuda.empty_cache()

    def extract_frames(self, video_path):
        """Extracts frames using OpenCV."""
        frames = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps <= 0: return []

        # Extract a frame every 3 seconds
        for i in range(0, total_frames, int(fps * FRAME_INTERVAL)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB for PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
            if len(frames) > 10: break # Don't over-analyze long clips
            
        cap.release()
        return frames

    def finalize(self):
        """Move files and write report."""
        manifest = []
        for video, data in self.results.items():
            total_score = data["audio_score"] + data["visual_score"]
            status = "KEEP" if total_score >= 0 else "JUNK"
            
            src = os.path.join(self.input_path, video)
            dst = os.path.join(KEEP_DIR if status == "KEEP" else JUNK_DIR, video)
            
            try:
                shutil.move(src, dst)
            except Exception as e:
                print(f"Error moving {video}: {e}")

            manifest.append({
                "file": video,
                "score": total_score,
                "status": status,
                "reasons": data["reasons"]
            })

        with open("analysis_report.json", "w") as f:
            json.dump(manifest, f, indent=4)
        
        print(f"\nDone! Check the {KEEP_DIR} and {JUNK_DIR} folders.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_connoisseur_pro.py ./path_to_videos")
    else:
        connoisseur = VideoConnoisseur(sys.argv[1])
        connoisseur.analyze_audio_phase()
        connoisseur.analyze_visual_phase()
        connoisseur.finalize()
