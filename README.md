# 🎵 AI Music Processor

Professional AI-powered music processing tool for YouTube downloads, karaoke creation, and pitch shifting with advanced brightness preservation.

## ✨ Features

### 🎤 Professional Karaoke Creation
- **Enhanced 4-Step Pipeline**: Complete vocal removal using AI ensemble
- **Dual AI Models**: Demucs htdemucs_6s (6-stem) + MDX-Net BS-Roformer
- **Ensemble Blending**: 50/50 mix for maximum vocal isolation quality
- **Brightness Preservation**: Enhanced post-processing to maintain fullness and clarity
- **Checkpoint System**: Resume processing without restarting (saves 30-60 min on retries)

### 🎵 High-Quality Pitch Shifting
- **Rubberband Algorithm**: Professional-grade pitch shifting (used in DAWs)
- **Brightness Compensation**: Automatic high-frequency boost based on pitch shift amount
- **Range**: ±12 semitones with maintained audio quality
- **Smart Processing**: Pre-emphasis for down-pitch, presence enhancement for all shifts

### 📥 YouTube Download
- **Highest Quality**: Automatic selection of best available audio stream
- **Format Conversion**: Converts to 320kbps MP3 @ 48kHz
- **Quality Reporting**: Detailed bitrate, codec, and resolution information
- **Trim Support**: Skip intro/ads with `--trim-start` option

### 🔄 Local File Processing
- **Iterative Workflow**: Process existing MP3/audio files without re-downloading
- **Format Support**: MP3, WAV, FLAC, M4A, AAC, OGG
- **Quick Pitch Testing**: Test different pitch shifts on existing files

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** with `uv` package manager
- **FFmpeg 8.0+** with Rubberband support
- **macOS** (tested on M2 Max, should work on other systems)
- **32GB RAM** recommended for processing

### Installation

```bash
# Clone the repository
git clone https://github.com/vibhupb/ai-music-processor.git
cd ai-music-processor

# Install dependencies with uv
uv sync
```

### Dependencies

The following packages will be installed automatically:
- `pytubefix 10.0.0` - YouTube video/audio downloads
- `demucs 4.0.1` - AI-powered source separation
- `audio-separator 0.39.1` - MDX-Net model wrapper
- `ffmpeg-python` - FFmpeg integration

**AI Models** (downloaded on first use):
- Demucs: `htdemucs_6s` (6-stem separation)
- MDX-Net: `model_bs_roformer_ep_317_sdr_12.9755.ckpt` (SDR 16.5)

## 📖 Usage

### Basic Commands

```bash
# Download highest quality video
uv run main.py "https://youtube.com/watch?v=..."

# Create professional karaoke
uv run main.py "https://youtube.com/watch?v=..." --karaoke

# Create karaoke with pitch adjustment
uv run main.py "https://youtube.com/watch?v=..." --karaoke --pitch=-4

# Pitch-shift existing file
uv run main.py "song.mp3" --pitch=-3

# Process local file to karaoke
uv run main.py "song.mp3" --karaoke --pitch=2
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--karaoke` | Create professional karaoke (complete vocal removal) | `--karaoke` |
| `--pitch=N` | Adjust pitch by N semitones (±12) | `--pitch=-4` |
| `--trim-start=N` | Skip first N seconds (remove ads/intros) | `--trim-start=30` |
| `--help` | Show detailed help message | `--help` |

## 🎯 Use Cases

### 1️⃣ Create Karaoke for Your Vocal Range
```bash
# Download song and shift pitch down 4 semitones
uv run main.py "https://youtube.com/watch?v=..." --karaoke --pitch=-4
```

**Result**: Pure instrumental track at comfortable singing pitch

### 2️⃣ Manual Chorus Layering
```bash
# Step 1: Create karaoke with pitch shift
uv run main.py "URL" --karaoke --pitch=-4

# Step 2: Pitch-shift original (for chorus extraction)
uv run main.py "original.mp3" --pitch=-4
```

**Workflow**: Import both into DAW, extract chorus from original, layer over karaoke

### 3️⃣ Quick Pitch Testing
```bash
# Test different pitches without re-downloading
uv run main.py "song.mp3" --pitch=-2
uv run main.py "song.mp3" --pitch=-3
uv run main.py "song.mp3" --pitch=-4
```

**Benefit**: Find perfect pitch quickly without 45-min reprocessing

## ⏱️ Processing Times

**On M2 Max 32GB RAM:**

| Song Length | Karaoke Only | Karaoke + Pitch |
|-------------|--------------|-----------------|
| 3-4 minutes | ~45-55 min   | ~47-57 min      |
| 5 minutes   | ~65-85 min   | ~67-87 min      |
| 10 minutes  | ~130-170 min | ~135-175 min    |

**Pitch adjustment alone**: ~5 seconds (57x realtime speed)

**Note**: First run downloads AI models (~500MB total). Subsequent runs use cached models.

## 🎨 Audio Quality

### Karaoke Pipeline (4 Steps)

1. **Demucs htdemucs_6s**: 6-stem separation (vocals/drums/bass/guitar/piano/other)
2. **MDX-Net BS-Roformer**: Professional vocal isolation (SDR 12.9755)
3. **Ensemble Blend**: 50/50 mix for optimal quality
4. **Enhanced Polish**: 
   - Gentle high-pass @ 20Hz (DC offset removal)
   - Presence boost @ 3kHz +1dB (clarity)
   - High-shelf @ 8kHz +1.5dB (air & sparkle)
   - Light dynamic normalization
   - Gentle compression
   - Soft limiting

### Pitch Shifting Enhancements

**Brightness Compensation Formula**: `0.2dB per semitone` (capped at 2.5dB)

**Filter Chain**:
1. Pre-emphasis (down-pitch only): High-shelf @ 6kHz
2. Rubberband pitch shift (high-quality algorithm)
3. Post-brightness restoration: High-shelf @ 7kHz
4. Presence enhancement: +0.8dB @ 3.5kHz

**Result**: No muffled sound, maintains clarity across pitch range

## 📁 Output Files

### Naming Convention

```
Original Download:
└── Song_Title.mp3

Karaoke Output:
├── Song_Title_demucs_no_vocals.mp3      (STEP 1: Demucs output)
├── Song_Title_mdx_no_vocals.mp3          (STEP 2: MDX-Net output)
├── Song_Title_ensemble_karaoke.mp3       (STEP 3: Ensemble blend)
└── Song_Title_final_polished_karaoke.mp3 (STEP 4: Final output)

Pitch-Adjusted:
└── Song_Title_pitch-4.mp3                (Pitch shifted by -4)

Karaoke + Pitch:
└── Song_Title_final_polished_karaoke_pitch-4.mp3
```

### Checkpoint/Resume

All intermediate files are cached. If processing is interrupted:
- Re-run the same command
- Pipeline resumes from last completed step
- Saves 30-60 minutes on retries

## 🛠️ Technical Details

### System Requirements

- **CPU**: Multi-core recommended (Demucs uses all cores)
- **RAM**: 32GB recommended, 16GB minimum
- **Storage**: ~2GB per song (intermediate files, can be deleted)
- **GPU**: Optional (not currently utilized, CPU-only processing)

### FFmpeg Configuration

Required FFmpeg build with:
- Rubberband support (`--enable-librubberband`)
- MP3 encoder (`--enable-libmp3lame`)
- Standard audio filters

**Verify**: `ffmpeg -filters | grep rubberband`

### AI Models Location

Models are cached by respective libraries:
- Demucs: `~/.cache/torch/hub/checkpoints/`
- Audio-separator: `~/.cache/audio-separator-models/`

## 🔧 Troubleshooting

### Common Issues

**1. "FFmpeg does not support rubberband"**
```bash
# Reinstall FFmpeg with Rubberband
brew reinstall ffmpeg
```

**2. "CUDA out of memory" or RAM issues**
```bash
# Close other applications
# Reduce concurrent processing
# For 16GB RAM: Process shorter songs first
```

**3. "YouTube video unavailable"**
```bash
# Try different video URL
# Some videos are region-locked or age-restricted
# Use official audio uploads when possible
```

**4. Checkpoint files out of sync**
```bash
# Delete intermediate files and restart
rm *_demucs_no_vocals.mp3 *_mdx_no_vocals.mp3 *_ensemble_karaoke.mp3
```

### Performance Tips

1. **First Run**: Expect longer processing (model downloads)
2. **Checkpoint System**: Don't delete intermediate files until final output is ready
3. **Local File Mode**: Use for iterative pitch testing
4. **Batch Processing**: Process one song at a time (memory intensive)

## 📝 Version Control

**Excluded from Git** (via `.gitignore`):
- All audio/video files (`.mp3`, `.mp4`, `.wav`, etc.)
- AI model files (`.ckpt`, `.pth`, `.onnx`)
- Separated audio folders (`separated/`, `mdx_separated/`)
- Virtual environments (`.venv/`)
- System files (`.DS_Store`, `__pycache__/`)

## 🤝 Contributing

This is a private repository. For feature requests or bug reports, please contact the repository owner.

## 📄 License

Private project. All rights reserved.

## 🙏 Acknowledgments

Built with:
- **Demucs** by Facebook Research (Meta AI)
- **MDX-Net** by KUIELab (BS-Roformer model)
- **Rubberband** by Breakfast Quay
- **PyTubeFix** for YouTube downloads
- **Audio-Separator** for model integration

## 📬 Contact

Repository Owner: [@vibhupb](https://github.com/vibhupb)

---

**Last Updated**: October 21, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅