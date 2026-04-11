# VideoConnoisseur Pro

A Python-based video analysis and filtering tool that categorizes clips into `KEEP` and `JUNK` folders based on gameplay, social interaction, and visual anomalies.

## Requirements

- NVIDIA RTX 2060 (6GB VRAM)
- Python 3.8+
- FFmpeg installed on system

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   cd VideoConnoisseur
   python setup.py
   ```

## Usage

```bash
python video_connoisseur_pro.py /path/to/video/directory
```

## How It Works

### Phase 1: Audio Analysis
- Extracts audio and uses Faster-Whisper to detect keywords
- Analyzes speaker changes for social banter
- Checks for silence levels

### Phase 2: Visual Analysis
- Extracts 1 frame every 3 seconds
- Uses Moondream2 to analyze frames for:
  - Gaming UI (Victory/Defeat/POTG text)
  - Social interactions (drawing/gestures)
  - Visual glitches (T-pose, clipping, artifacts)

### Phase 3: Classification
- Combines audio and visual scores
- Applies scoring modifiers:
  - UI Text: +50
  - Laughter/Excitement: +40
  - Social Interaction: +40
  - Glitch: +30
  - High-energy banter: +20
  - Total silence: -50
  - Static image: -40
  - No speech/UI: -30

### Phase 4: File Organization
- Creates `KEEP` and `JUNK` directories
- Moves original files based on classification
- Generates `manifest.json` with reasons

## Output

- `KEEP/` - Interesting clips
- `JUNK/` - Uninteresting clips
- `manifest.json` - Classification details