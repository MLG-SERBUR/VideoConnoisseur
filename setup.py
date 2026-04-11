import subprocess
import sys

def install_requirements():
    """Install Python requirements"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def test_installation():
    """Test if all required packages are installed"""
    try:
        import torch
        import transformers
        import faster_whisper
        import ffmpeg_python
        import cv2
        import tqdm
        print("All required packages installed successfully!")
    except ImportError as e:
        print(f"Error: {e}")
        print("Some packages are missing. Please install requirements manually.")
        sys.exit(1)

if __name__ == "__main__":
    print("Setting up VideoConnoisseur Pro...")
    install_requirements()
    test_installation()
    print("Setup complete! You can now run: python video_connoisseur_pro.py <input_directory>")