"""
Setup and Installation Script
Creates necessary directories and virtual environment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("VideoConnoisseur Setup Script")
    print("=" * 60)
    
    # Create necessary directories
    dirs_to_create = [
        'videos',
        'models',
        'temp_processing',
        '.kilo/agent'
    ]
    
    print("\nCreating directories...")
    for dir_name in dirs_to_create:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"  ✓ Created: {dir_path}")
    
    # Create videos directory with sample structure
    videos_dir = Path('videos')
    videos_dir.mkdir(exist_ok=True)
    
    # Create empty placeholder files
    (videos_dir / '.gitkeep').touch()
    (Path('models') / '.gitkeep').touch()
    (Path('temp_processing') / '.gitkeep').touch()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Install dependencies: uv sync")
    print("2. Start Ollama and run: ollama run llava")
    print("3. Start the application: python app.py")
    print("4. Access the web UI at: http://localhost:5000")

if __name__ == '__main__':
    main()