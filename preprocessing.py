"""
Video Processing Module
Handles video preprocessing, frame extraction, and analysis
"""

import cv2
import json
import base64
import numpy as np
import ollama
import torch
import gc
from faster_whisper import WhisperModel
import os
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        
    def extract_frames_in_memory(self, video_path, interval=2):
        """
        Extract frames from video in memory without saving to disk.
        Returns list of base64 encoded frames.
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception(f"Cannot open video file: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps * interval))
            
            frame_count = 0
            success = True
            while success:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    # Convert frame to base64 without saving to disk
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    frames.append(frame_b64)
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from {video_path}")
            
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            raise
        
        return frames
    
    def analyze_with_ollama(self, frame_b64, model_name="llava", prompt=None):
        """
        Analyze frame using Ollama model.
        Uses in-memory processing - no files written to disk.
        """
        if prompt is None:
            prompt = "Is there a victory screen or glitch in this frame? Describe what you see."
        
        try:
            # Prepare the request
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {'type': 'image', 'source': {'type': 'base64', 'data': frame_b64}}
                    ]
                }
            ]
            
            # Call Ollama API
            response = ollama.client.Client(host=self.ollama_url).generate(
                model=model_name,
                prompt=json.dumps(messages),
                stream=False
            )
            
            return response.get('response', '')
            
        except Exception as e:
            logger.error(f"Error analyzing frame with Ollama: {e}")
            return ""
    
    def transcribe_audio(self, video_path, model_size="base", language="en"):
        """
        Transcribe audio using faster-whisper and detect key features.
        """
        try:
            # Load model
            model = WhisperModel(model_size, device="cuda" if torch.cuda.is_available() else "cpu")
            
            # Transcribe
            segments, info = model.transcribe(
                video_path,
                language=language,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Process results
            transcript = ""
            keywords = []
            speaker_changes = 0
            energy_peaks = 0
            
            for segment in segments:
                transcript += segment.text + " "
                
                # Detect keywords
                text_lower = segment.text.lower()
                victory_keywords = ['victory', 'win', 'won', 'champion', 'winning']
                glitch_keywords = ['glitch', 'bug', 'error', 'broken', 'freeze', 'lag']
                
                for keyword in victory_keywords:
                    if keyword in text_lower:
                        keywords.append(f"victory_{keyword}")
                
                for keyword in glitch_keywords:
                    if keyword in text_lower:
                        keywords.append(f"glitch_{keyword}")
                
                # Simple energy detection (based on segment length and punctuation)
                if len(segment.text) > 50 or any(c in segment.text for c in ['!', '?']):
                    energy_peaks += 1
            
            # Detect speaker changes (simplified - based on segment count)
            if info.speech_probability > 0.5:
                speaker_changes = max(0, info.language_probability.get('en', 0) - 1)
            
            # Clean up model from memory
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            return {
                'transcript': transcript,
                'keywords': keywords,
                'speaker_changes': speaker_changes,
                'energy_peaks': energy_peaks
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                'transcript': '',
                'keywords': [],
                'speaker_changes': 0,
                'energy_peaks': 0
            }
    
    def detect_objects_in_frame(self, frame_b64):
        """
        Detect objects in a frame using Ollama.
        """
        try:
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': 'What objects and elements do you see in this frame?'},
                        {'type': 'image', 'source': {'type': 'base64', 'data': frame_b64}}
                    ]
                }
            ]
            
            response = ollama.client.Client(host="http://localhost:11434").generate(
                model="llava",
                prompt=json.dumps(messages),
                stream=False
            )
            
            return response.get('response', '')
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
            return ""
    
    def process_video(self, video_path):
        """
        Complete video processing pipeline.
        Returns audio and visual features.
        """
        result = {
            'audio_features': None,
            'visual_features': None,
            'error': None
        }
        
        try:
            # Step 1: Audio processing
            logger.info("Processing audio...")
            audio_features = self.transcribe_audio(video_path)
            result['audio_features'] = audio_features
            
            # Step 2: Frame extraction in memory
            logger.info("Extracting frames in memory...")
            frames = self.extract_frames_in_memory(video_path)
            
            # Step 3: Analyze frames with Ollama
            logger.info("Analyzing frames with Ollama...")
            visual_features = []
            
            for i, frame_b64 in enumerate(frames):
                # Detect objects in each frame
                objects = self.detect_objects_in_frame(frame_b64)
                analysis = self.analyze_with_ollama(frame_b64)
                
                visual_features.append({
                    'frame_number': i,
                    'analysis': analysis,
                    'objects': objects
                })
                
                # Free memory
                del frame_b64
            
            result['visual_features'] = visual_features
            
            logger.info("Video processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in video processing: {e}")
            result['error'] = str(e)
            return result