# 🎤 AI Karaoke Maker

AI-powered karaoke creation tool with two versions: a **Basic web app** for Streamlit Cloud and a **Professional command-line tool** for local processing.

## 🚀 Quick Start

### **Option 1: Web App (Recommended for Most Users)**

Try the live demo on Streamlit Cloud or run locally:

```bash
streamlit run app.py
```

**Basic Mode Features:**
- 🎤 AI-powered vocal removal (Demucs)
- 🎵 Pitch shifting (±12 semitones)
- 📥 YouTube downloads
- 📁 Audio file uploads
- ⚡ Fast processing (3-5 minutes)
- ☁️ Works on Streamlit Cloud free tier

### **Option 2: Command-Line (Professional Mode)**

For advanced users who need the highest quality:

```bash
# Install dependencies
uv sync

# Create professional karaoke with full 4-step pipeline
uv run main.py "song.mp3" --karaoke

# Create karaoke with pitch adjustment
uv run main.py "https://youtube.com/watch?v=..." --karaoke --pitch=-4
```

## 📊 Basic vs Professional Modes

| Feature | Basic Mode (Web App) | Professional Mode (CLI) |
|---------|---------------------|------------------------|
| **AI Model** | Demucs (2-stem) | Demucs 6-stem + MDX-Net ensemble |
| **Processing Time** | 3-5 minutes | 45-85 minutes |
| **Vocal Removal Quality** | Excellent | Studio-grade |
| **Pitch Shifting** | ✅ Yes | ✅ Yes (with brightness compensation) |
| **Interface** | Web UI | Command-line |
| **Cloud Compatible** | ✅ Yes | ❌ No (requires local setup) |
| **Best For** | Quick karaoke creation | Maximum quality production work |

## ✨ Features

### 🎤 Karaoke Creation
- **Basic Mode**: Fast AI vocal removal using Demucs htdemucs (2-stem separation)
- **Professional Mode**: Enhanced 4-step pipeline with dual AI models (Demucs 6-stem + MDX-Net BS-Roformer)
- **Checkpoint System** (Professional): Resume processing without restarting

### 🎵 Pitch Shifting
- **Range**: ±12 semitones
- **Basic Mode**: Standard pitch adjustment
- **Professional Mode**: Rubberband algorithm with brightness compensation
- **Smart Processing**: Maintains audio quality across pitch range

### 📥 YouTube Download
- **Highest Quality**: Automatic selection of best available audio stream
- **Format Conversion**: Converts to 320kbps MP3
- **Trim Support**: Skip intro/ads with trim start option

### 🔄 File Processing
- **Format Support**: MP3, WAV, FLAC, M4A, AAC, OGG
- **Upload or Local**: Web UI supports file uploads, CLI processes local files
- **Iterative Workflow**: Test different pitch shifts without re-processing

## 📦 Installation

### Basic Mode (Web App)

**Requirements:**
- Python 3.8+
- FFmpeg
- Streamlit

```bash
# Clone the repository
git clone https://github.com/viantihu/ai-karaoke-maker.git
cd ai-karaoke-maker

# Install dependencies
pip install -r requirements.txt

# Run the web app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Professional Mode (CLI)

**Requirements:**
- Python 3.13+ with `uv` package manager
- FFmpeg with Rubberband support
- 16GB RAM minimum, 32GB recommended

```bash
# Install dependencies with uv
uv sync

# Verify FFmpeg has Rubberband support (for professional mode)
ffmpeg -filters | grep rubberband
```

### Dependencies

**All modes:**
- `pytubefix` - YouTube downloads
- `demucs` - AI-powered vocal separation
- `streamlit` - Web interface
- FFmpeg - Audio processing

**Professional mode only:**
- `audio-separator` - MDX-Net model wrapper

**AI Models** (downloaded automatically on first use):
- Basic Mode: Demucs `htdemucs` (~150MB)
- Professional Mode: Demucs `htdemucs_6s` + MDX-Net BS-Roformer (~800MB total)

## 📖 Usage

### Web App (Basic Mode)

1. Run `streamlit run app.py`
2. Choose input source:
   - **YouTube URL**: Paste any YouTube link
   - **Upload File**: Drag and drop an audio file
3. Select options:
   - Enable "Create Karaoke" to remove vocals
   - Adjust pitch slider (±12 semitones)
   - Set trim start time (skip intros/ads)
4. Click "Start Processing"
5. Download your processed track when complete

**Processing Time:** 3-5 minutes for typical songs

### Command-Line (Professional Mode)

```bash
# Create studio-grade karaoke
uv run main.py "song.mp3" --karaoke

# Create karaoke with pitch adjustment
uv run main.py "https://youtube.com/watch?v=..." --karaoke --pitch=-4

# Pitch-shift existing file
uv run main.py "song.mp3" --pitch=-3

# Download with trim
uv run main.py "URL" --karaoke --trim-start=30
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--karaoke` | Create professional karaoke (4-step pipeline) | `--karaoke` |
| `--pitch=N` | Adjust pitch by N semitones (±12) | `--pitch=-4` |
| `--trim-start=N` | Skip first N seconds | `--trim-start=30` |
| `--help` | Show help message | `--help` |

## 🎯 Use Cases

### 1️⃣ Create Karaoke for Your Vocal Range
**Web App**: Upload song → Enable karaoke → Adjust pitch slider → Download
**CLI**: `uv run main.py "song.mp3" --karaoke --pitch=-4`

**Result**: Pure instrumental track at comfortable singing pitch

### 2️⃣ Quick Pitch Testing
Upload your file once in the web app and try different pitch values to find your perfect key.

### 3️⃣ Professional Production (CLI Only)
Use Professional mode for maximum vocal removal quality when producing final tracks for performance or recording

## ⏱️ Processing Times

### Basic Mode (Web App)
- **3-5 minutes** for typical songs
- Fast AI processing optimized for cloud deployment
- First run downloads ~150MB Demucs model

### Professional Mode (CLI)
**On M1 Max 32GB RAM:**

| Song Length | Karaoke Only | Karaoke + Pitch |
|-------------|--------------|-----------------|
| 3-4 minutes | ~45-55 min   | ~47-57 min      |
| 5 minutes   | ~65-85 min   | ~67-87 min      |

**Pitch adjustment alone**: ~5 seconds

**Note**: First run downloads ~800MB of AI models. Subsequent runs use cached models.

## 🎨 Audio Quality

### Basic Mode
- **AI Model**: Demucs htdemucs (2-stem separation)
- **Quality**: Excellent vocal removal for most songs
- **Output**: 320kbps MP3
- **Best For**: Pop, rock, and mainstream genres

### Professional Mode (4-Step Pipeline)

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

### Pitch Shifting

**Basic Mode**: Standard high-quality pitch adjustment

**Professional Mode Enhancements**:
- Rubberband algorithm (professional-grade)
- Brightness compensation: 0.2dB per semitone (capped at 2.5dB)
- Pre-emphasis for down-pitch shifts
- Post-brightness restoration
- Presence enhancement for clarity

**Result**: Maintains audio clarity across full ±12 semitone range

## 📁 Output Files

### Basic Mode (Web App)
- Downloads directly through browser
- Single output file per processing operation
- Clean, simple naming based on original filename

### Professional Mode (CLI)

**Naming Convention:**
```
Original Download:
└── Song_Title.mp3

Karaoke Output:
├── Song_Title_demucs_no_vocals.mp3      (STEP 1: Demucs output)
├── Song_Title_mdx_no_vocals.mp3          (STEP 2: MDX-Net output)
├── Song_Title_ensemble_karaoke.mp3       (STEP 3: Ensemble blend)
└── Song_Title_final_polished_karaoke.mp3 (STEP 4: Final output)

Pitch-Adjusted:
└── Song_Title_pitch-4.mp3

Karaoke + Pitch:
└── Song_Title_final_polished_karaoke_pitch-4.mp3
```

**Checkpoint/Resume:**
All intermediate files are cached. If processing is interrupted:
- Re-run the same command
- Pipeline resumes from last completed step
- Saves 30-60 minutes on retries

## 🛠️ Technical Details

### System Requirements

**Basic Mode (Web App):**
- **CPU**: Any modern processor
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: ~500MB for models + temporary files
- **Platform**: Works on Streamlit Cloud free tier

**Professional Mode (CLI):**
- **CPU**: Multi-core recommended (Demucs uses all cores)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: ~2GB per song (intermediate files)
- **GPU**: Optional (not currently utilized)

### FFmpeg Configuration

**Basic Mode**: Standard FFmpeg installation
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from ffmpeg.org
```

**Professional Mode**: FFmpeg with Rubberband support
- Rubberband support (`--enable-librubberband`)
- MP3 encoder (`--enable-libmp3lame`)
- Verify: `ffmpeg -filters | grep rubberband`

### AI Models Location

Models are automatically downloaded and cached:
- **Demucs**: `~/.cache/torch/hub/checkpoints/`
- **Audio-separator** (Professional only): `~/.cache/audio-separator-models/`

## 🔧 Troubleshooting

### Common Issues

**1. Web App: "Processing failed" or timeout**
- Try with a shorter audio file (under 5 minutes)
- Check that FFmpeg is installed: `ffmpeg -version`
- Restart the Streamlit app
- Check available RAM and close other applications

**2. "YouTube video unavailable"**
- Try a different video URL
- Some videos are region-locked or age-restricted
- Use official audio uploads when possible

**3. Professional Mode: "FFmpeg does not support rubberband"**
```bash
# Reinstall FFmpeg with Rubberband
brew reinstall ffmpeg
```

**4. Professional Mode: RAM issues**
- Close other applications
- Process shorter songs first
- Requires 16GB RAM minimum

**5. Professional Mode: Checkpoint files out of sync**
```bash
# Delete intermediate files and restart
rm *_demucs_no_vocals.mp3 *_mdx_no_vocals.mp3 *_ensemble_karaoke.mp3
```

### Performance Tips

**Basic Mode:**
1. First run downloads ~150MB model (may take a few minutes)
2. Use shorter audio clips for faster processing
3. Clear browser cache if experiencing issues

**Professional Mode:**
1. First run downloads ~800MB of models
2. Don't delete intermediate files until final output is ready
3. Use checkpoint system to resume interrupted processing
4. Process one song at a time (memory intensive)

## 🌐 Deployment

### Streamlit Cloud (Basic Mode)

The Basic mode web app is optimized for Streamlit Cloud deployment:

1. Fork this repository
2. Connect to Streamlit Cloud
3. Deploy `app.py`
4. The app will automatically install dependencies and be ready to use

**Note**: Streamlit Cloud free tier works great for Basic mode processing times.

### Local Deployment

Both Basic and Professional modes work locally:
- **Basic Mode**: `streamlit run app.py`
- **Professional Mode**: `uv run main.py <options>`

## 📝 Project Structure

```
ai-karaoke-maker/
├── app.py                 # Streamlit web app (Basic mode)
├── main.py               # CLI tool (Professional mode)
├── requirements.txt      # Python dependencies
├── .streamlit/          # Streamlit configuration
│   └── config.toml
└── README.md
```

**Excluded from Git** (via `.gitignore`):
- Audio/video files (`.mp3`, `.mp4`, `.wav`, etc.)
- AI model files (`.ckpt`, `.pth`, `.onnx`)
- Separated audio folders (`separated/`, `mdx_separated/`)
- Virtual environments (`.venv/`)

## 🙏 Acknowledgments

Built with:
- **Demucs** by Facebook Research (Meta AI) - AI vocal separation
- **MDX-Net** by KUIELab (BS-Roformer model) - Professional mode
- **Rubberband** by Breakfast Quay - High-quality pitch shifting
- **PyTubeFix** - YouTube downloads
- **Audio-Separator** - Model integration
- **Streamlit** - Web interface

## 📬 Contact

Repository: [github.com/viantihu/ai-karaoke-maker](https://github.com/viantihu/ai-karaoke-maker)

---

**Version**: 2.0.0 (Basic + Professional modes)
**Status**: Production Ready ✅
