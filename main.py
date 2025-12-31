from pytubefix import YouTube
from pytubefix.cli import on_progress
import subprocess
import os
import sys
import shutil
import time
import json
from audio_separator.separator import Separator

def get_audio_duration(audio_file):
    """
    Get the duration of an audio file in seconds using FFmpeg.

    Args:
        audio_file: Path to audio file

    Returns:
        Duration in seconds (float)
    """
    result = subprocess.run(
        [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            audio_file
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to get audio duration: {result.stderr}")

    data = json.loads(result.stdout)
    duration = float(data['format']['duration'])
    return duration

def create_karaoke(audio_file, output_file):
    """
    Create karaoke version by removing center vocals using FFmpeg's audio filters.
    This uses the "stereotool" and "pan" filters to isolate instrumental.
    Returns True if successful, False otherwise.
    """
    print(f"\n🎤 Creating karaoke version (removing center vocals)...")
    print(f"Note: This uses audio filtering to reduce vocals. Results vary by song.")
    
    # Use FFmpeg's audio filters to remove center-panned vocals
    # This works by exploiting that vocals are usually center-panned
    karaoke_command = [
        'ffmpeg',
        '-i', audio_file,
        '-af', 'stereotools=mlev=0.015625',  # Reduce center channel
        '-y',
        output_file
    ]
    
    result = subprocess.run(karaoke_command, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        print(f"❌ Vocal removal failed: {result.stderr}")
        return False

def create_demucs_karaoke(audio_path: str, mode: str = 'basic') -> str:
    """
    Create karaoke track using AI separation.

    Modes:
    - 'basic': Demucs only (faster, lighter, works on Streamlit Cloud free tier)
    - 'professional': Full 4-step pipeline with Demucs + MDX-Net (requires more resources)

    Args:
        audio_path: Path to input audio file
        mode: Processing mode ('basic' or 'professional')

    Returns:
        Path to final processed karaoke track
    """
    base_name = os.path.splitext(audio_path)[0]

    # BASIC MODE: Demucs only (optimized for Streamlit Cloud)
    if mode == 'basic':
        print(f"\n🎤 Creating AI-powered karaoke (Demucs)...")
        print(f"   🎯 Mode: Basic - Fast vocal removal")
        print(f"   ✨ Optimized for Streamlit Cloud deployment")

        # Use Demucs with --two-stems for faster processing
        demucs_output = os.path.join(os.path.dirname(audio_path), 'separated', 'htdemucs', os.path.splitext(os.path.basename(audio_path))[0])
        demucs_no_vocals = os.path.join(demucs_output, 'no_vocals.mp3')

        if os.path.exists(demucs_no_vocals):
            print(f"\n✅ Demucs output already exists, using cached version...")
            print(f"   Using: {demucs_no_vocals}")
        else:
            print(f"\n📊 Running Demucs (2-stem separation)...")

            result = subprocess.run(
                [
                    'demucs',
                    '--two-stems=vocals',  # Only separate vocals/no_vocals (faster)
                    '-n', 'htdemucs',      # Standard model (lighter than htdemucs_6s)
                    '--mp3',               # Output as MP3
                    '--mp3-bitrate=320',   # High quality
                    audio_path
                ],
                timeout=7200,  # 2 hours max
                text=True,
                env={**os.environ, 'TORCH_HOME': os.path.expanduser('~/.cache/torch')}
            )

            if result.returncode != 0:
                raise RuntimeError(f"Demucs failed with return code {result.returncode}")

            if not os.path.exists(demucs_no_vocals):
                raise FileNotFoundError(f"Demucs output not found at: {demucs_no_vocals}")

            print(f"✅ Karaoke track created successfully!")

        return demucs_no_vocals

    # PROFESSIONAL MODE: Full 4-step pipeline
    print(f"\n🎤 Creating AI-powered karaoke (4-step enhanced pipeline)...")
    print(f"   🎯 Mode: Professional - Complete vocal removal")
    print(f"   ✨ Enhanced: Brightness restoration + fullness preservation")
    print(f"   ⚠️  Warning: Requires significant resources (not recommended for Streamlit Cloud free tier)")

    # Determine step labels
    total_steps = 4

    # STEP 1: Demucs 6-stem separation (~30-40 minutes)
    demucs_output = os.path.join(os.path.dirname(audio_path), 'separated', 'htdemucs_6s', os.path.splitext(os.path.basename(audio_path))[0])
    demucs_no_vocals = os.path.join(demucs_output, 'no_vocals.mp3')
    
    if os.path.exists(demucs_no_vocals):
        print(f"\n✅ STEP 1/{total_steps}: Demucs output already exists, skipping...")
        print(f"   Using cached: {demucs_no_vocals}")
    else:
        print(f"\n📊 STEP 1/{total_steps}: Running Demucs htdemucs_6s (6-stem separation)...")
        
        # Clean up any partial model files before running
        cache_dir = os.path.expanduser('~/.cache/torch/hub/checkpoints')
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                if file.endswith('.partial') or file.endswith('.th.part'):
                    partial_path = os.path.join(cache_dir, file)
                    print(f"🧹 Cleaning up partial download: {file}")
                    try:
                        os.remove(partial_path)
                    except:
                        pass
        
        result = subprocess.run(
            [
                'demucs',
                '--two-stems=vocals',
                '-n', 'htdemucs_6s',
                '--float32',
                '--shifts=10',
                '--overlap=0.25',
                '--mp3',  # Force MP3 output to avoid Python 3.13 torchcodec issues
                '--mp3-bitrate=320',  # High quality
                audio_path
            ],
            timeout=10800,  # 3 hours max
            text=True,
            env={**os.environ, 'TORCH_HOME': os.path.expanduser('~/.cache/torch')}
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Demucs failed with return code {result.returncode}")
        
        if not os.path.exists(demucs_no_vocals):
            raise FileNotFoundError(f"Demucs output not found at: {demucs_no_vocals}")
        
        print(f"✅ STEP 1 complete: Demucs separation finished")
    
    # STEP 2: MDX-Net separation (~30-40 minutes)
    mdx_output_dir = os.path.join(os.path.dirname(audio_path), 'mdx_separated')
    os.makedirs(mdx_output_dir, exist_ok=True)
    
    # Find existing MDX-Net output
    mdx_instrumental = None
    if os.path.exists(mdx_output_dir):
        for file in os.listdir(mdx_output_dir):
            if 'Instrumental' in file and file.endswith('.mp3'):
                mdx_instrumental = os.path.join(mdx_output_dir, file)
                break
    
    if mdx_instrumental and os.path.exists(mdx_instrumental):
        print(f"\n✅ STEP 2/{total_steps}: MDX-Net output already exists, skipping...")
        print(f"   Using cached: {mdx_instrumental}")
    else:
        print(f"\n📊 STEP 2/{total_steps}: Running MDX-Net BS-Roformer (professional vocal isolation)...")
        
        result = subprocess.run(
            [
                'audio-separator',
                audio_path,
                '-m', 'model_bs_roformer_ep_317_sdr_12.9755.ckpt',
                '--output_format', 'MP3',
                '--output_dir', mdx_output_dir,
                '--normalization', '0.9',
                '--single_stem', 'Instrumental'
            ],
            timeout=10800,  # 3 hours max
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"MDX-Net failed with return code {result.returncode}")
        
        # Find the MDX-Net instrumental output
        mdx_instrumental = None
        for file in os.listdir(mdx_output_dir):
            if 'Instrumental' in file and file.endswith('.mp3'):
                mdx_instrumental = os.path.join(mdx_output_dir, file)
                break
        
        if not mdx_instrumental or not os.path.exists(mdx_instrumental):
            raise FileNotFoundError(f"MDX-Net output not found in: {mdx_output_dir}")
        
        print(f"✅ STEP 2 complete: MDX-Net separation finished")
    
    # STEP 3: Ensemble blend (~30 seconds)
    ensemble_output = f"{base_name}_ensemble_karaoke.mp3"
    
    if os.path.exists(ensemble_output):
        print(f"\n✅ STEP 3/{total_steps}: Ensemble blend already exists, skipping...")
        print(f"   Using cached: {ensemble_output}")
    else:
        print(f"\n📊 STEP 3/{total_steps}: Blending ensemble (50% Demucs + 50% MDX-Net)...")
        
        result = subprocess.run(
            [
                'ffmpeg', '-y',
                '-i', demucs_no_vocals,
                '-i', mdx_instrumental,
                '-filter_complex',
                '[0:a][1:a]amix=inputs=2:weights=0.5 0.5:duration=longest:normalize=0[mixed]',
                '-map', '[mixed]',
                '-b:a', '320k',
                ensemble_output
            ],
            timeout=300,  # 5 minutes max
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Ensemble blending failed with return code {result.returncode}")
        
        print(f"✅ STEP 3 complete: Ensemble blend finished")
    
    # STEP 4: Enhanced post-processing with brightness restoration
    final_output = f"{base_name}_final_polished_karaoke.mp3"
    
    if os.path.exists(final_output):
        print(f"\n✅ STEP 4/{total_steps}: Post-processing already complete!")
        print(f"   Using cached: {final_output}")
    else:
        print(f"\n🎚️  STEP 4/{total_steps}: Applying enhanced post-processing...")
        print(f"   • Gentle brightness restoration (preserve fullness)")
        print(f"   • Light high-pass filter (remove only rumble)")
        print(f"   • Subtle compression (maintain dynamics)")
        print(f"   • Soft limiting (prevent clipping)")
        
        result = subprocess.run(
            [
                'ffmpeg', '-y',
                '-i', ensemble_output,
                '-af',
                # Enhanced post-processing with brightness preservation:
                # 1. Very gentle high-pass at 20Hz (remove DC offset only, not 30Hz)
                # 2. Presence boost at 3kHz +1dB (add clarity without harshness)
                # 3. High-shelf at 8kHz +1.5dB (restore air and sparkle)
                # 4. Light dynamic normalization (preserve dynamics better)
                # 5. Gentle compression (avoid squashing)
                # 6. Soft limiter (prevent clipping)
                'highpass=f=20,'
                'equalizer=f=3000:width_type=o:width=1:g=1,'
                'highshelf=f=8000:g=1.5,'
                'dynaudnorm=f=300:g=10:p=0.8:m=10:r=0.4:b=0,'
                'compand=attacks=0.15:decays=0.4:points=-80/-80|-45/-25|-27/-15|0/-8,'
                'alimiter=limit=0.96',
                '-b:a', '320k',
                final_output
            ],
            timeout=300,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Post-processing failed with return code {result.returncode}")
        
        print(f"✅ STEP 4 complete: Enhanced post-processing finished")
    
    print(f"\n🎉 4-step enhanced karaoke pipeline complete!")
    print(f"   🎯 ALL vocals: REMOVED (complete vocal removal)")
    print(f"   🎸 Output: Pure instrumental track")
    print(f"   ✨ Sound quality: BRIGHT & FULL")
    print(f"📁 Final polished karaoke: {final_output}")
    
    return final_output


def adjust_pitch(audio_path: str, semitones: int) -> str:
    """
    Adjust pitch of audio file by specified semitones using high-quality Rubberband algorithm
    with brightness preservation to avoid muffled sound.
    
    Args:
        audio_path: Path to input audio file
        semitones: Number of semitones to shift (+/- 12)
        
    Returns:
        Path to pitch-adjusted audio file
    """
    print(f"\n🎵 STEP 5/5: Adjusting pitch by {semitones:+d} semitones (with brightness preservation)...")
    
    base_name = os.path.splitext(audio_path)[0]
    output_path = f"{base_name}_pitch{semitones:+d}.mp3"
    
    # Calculate pitch ratio for rubberband
    # Rubberband uses pitch ratio (multiplier), not semitones
    # Formula: ratio = 2^(semitones/12)
    pitch_ratio = 2 ** (semitones / 12)
    
    # Enhanced pitch shifting with brightness preservation:
    # Pitch shifting, especially downward, tends to dull high frequencies
    # We compensate by boosting brightness based on shift direction
    
    # Calculate brightness compensation (more boost for larger pitch changes)
    brightness_gain = abs(semitones) * 0.2  # 0.2dB per semitone
    brightness_gain = min(brightness_gain, 2.5)  # Cap at 2.5dB to avoid harshness
    
    # Build filter chain for enhanced pitch shifting
    filter_chain = []
    
    # 1. Pre-emphasis: Slight high-frequency boost before shifting (only for down-pitch)
    if semitones < 0:
        filter_chain.append(f'highshelf=f=6000:g={brightness_gain * 0.5}')
    
    # 2. High-quality pitch shifting with Rubberband
    filter_chain.append(f'rubberband=pitch={pitch_ratio}')
    
    # 3. Post-brightness restoration (compensate for dulling)
    # Boost highs more aggressively than pre-emphasis
    filter_chain.append(f'highshelf=f=7000:g={brightness_gain}')
    
    # 4. Presence enhancement (add clarity that pitch-shifting loses)
    filter_chain.append('equalizer=f=3500:width_type=o:width=0.8:g=0.8')
    
    # Combine all filters
    audio_filter = ','.join(filter_chain)
    
    print(f"   • Rubberband pitch shift: {pitch_ratio:.4f}x")
    print(f"   • Brightness compensation: +{brightness_gain:.1f}dB @ 7kHz")
    print(f"   • Presence enhancement: +0.8dB @ 3.5kHz")
    
    result = subprocess.run(
        [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-af', audio_filter,
            '-b:a', '320k',
            output_path
        ],
        timeout=300,  # 5 minutes max
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Pitch adjustment failed with return code {result.returncode}")
    
    print(f"✅ STEP 5 complete: Pitch adjusted by {semitones:+d} semitones (brightness preserved)")
    print(f"📁 Pitch-adjusted track: {output_path}")
    
    return output_path


def main():
    # Check if URL/file is provided as command-line argument
    if len(sys.argv) < 2:
        print("=" * 70)
        print("YouTube Downloader with Professional Karaoke Creation")
        print("=" * 70)
        print("\nUsage:")
        print("  uv run main.py <youtube_url_or_file> [options]")
        print("\n🎯 THREE CORE SCENARIOS:")
        print("")
        print("  1️⃣  Download Original Video")
        print("      uv run main.py \"https://youtube.com/watch?v=...\"")
        print("")
        print("  2️⃣  Download with Pitch Shift")
        print("      uv run main.py \"URL\" --pitch=-2")
        print("      (Adjust to match your vocal range)")
        print("")
        print("  3️⃣  Create Karaoke Track (AI-powered, no vocals)")
        print("      uv run main.py \"URL\" --karaoke")
        print("      uv run main.py \"URL\" --karaoke --pitch=-3")
        print("")
        print("\n💡 BONUS: Process Local Files")
        print("  4️⃣  Adjust Pitch of Existing File")
        print("      uv run main.py \"song.mp3\" --pitch=-2")
        print("      (Re-pitch existing karaoke or original)")
        print("")
        print("  5️⃣  Create Karaoke from Local File")
        print("      uv run main.py \"song.mp3\" --karaoke")
        print("      uv run main.py \"song.mp3\" --karaoke --pitch=-4")
        print("")
        print("\n📋 OPTIONS:")
        print("  --karaoke         Create professional karaoke (AI vocal removal)")
        print("                    → Enhanced 4-step pipeline (bright & full sound)")
        print("                    → Removes ALL vocals (lead + chorus + harmony)")
        print("                    → Processing: ~45-55 min (with caching)")
        print("                    → Output: MP3 audio only (320kbps)")
        print("")
        print("  --pitch=N         Adjust pitch by N semitones (±12)")
        print("                    → Uses Rubberband with brightness preservation")
        print("                    → Works with original OR karaoke")
        print("                    → Examples: --pitch=2 (up), --pitch=-3 (down)")
        print("")
        print("  --trim-start=N    Skip first N seconds (remove ads/intros)")
        print("  --trim-end=N      Trim last N seconds (remove outros/ads)")
        print("")
        print("\n📁 OUTPUT:")
        print("  Default:          Highest quality video (up to 8K)")
        print("  With --karaoke:   Professional karaoke MP3 (pure instrumental)")
        print("  With --pitch:     Pitch-adjusted version (original or karaoke)")
        print("")
        print("=" * 70)
        sys.exit(1)
    
    # Check for help flags
    if '--help' in sys.argv or '-h' in sys.argv or 'help' in sys.argv:
        print("=" * 70)
        print("YouTube Downloader with Professional Karaoke Creation")
        print("=" * 70)
        print("\nUsage:")
        print("  uv run main.py <youtube_url_or_file> [options]")
        print("\n🎯 THREE CORE SCENARIOS:")
        print("")
        print("  1️⃣  Download Original Video")
        print("      uv run main.py \"https://youtube.com/watch?v=...\"")
        print("")
        print("  2️⃣  Download with Pitch Shift")
        print("      uv run main.py \"URL\" --pitch=-2")
        print("      (Adjust to match your vocal range)")
        print("")
        print("  3️⃣  Create Karaoke Track (AI-powered, no vocals)")
        print("      uv run main.py \"URL\" --karaoke")
        print("      uv run main.py \"URL\" --karaoke --pitch=-3")
        print("")
        print("\n💡 BONUS: Process Local Files")
        print("  4️⃣  Adjust Pitch of Existing File")
        print("      uv run main.py \"song.mp3\" --pitch=-2")
        print("      (Re-pitch existing karaoke or original)")
        print("")
        print("  5️⃣  Create Karaoke from Local File")
        print("      uv run main.py \"song.mp3\" --karaoke")
        print("      uv run main.py \"song.mp3\" --karaoke --pitch=-4")
        print("")
        print("\n📋 OPTIONS:")
        print("  --karaoke         Create professional karaoke (AI vocal removal)")
        print("                    → Enhanced 4-step pipeline (bright & full sound)")
        print("                    → Removes ALL vocals (lead + chorus + harmony)")
        print("                    → Processing: ~45-55 min (with caching)")
        print("                    → Output: MP3 audio only (320kbps)")
        print("")
        print("  --pitch=N         Adjust pitch by N semitones (±12)")
        print("                    → Uses Rubberband with brightness preservation")
        print("                    → Works with original OR karaoke")
        print("                    → Examples: --pitch=2 (up), --pitch=-3 (down)")
        print("")
        print("  --trim-start=N    Skip first N seconds (remove ads/intros)")
        print("  --trim-end=N      Trim last N seconds (remove outros/ads)")
        print("")
        print("\n📁 OUTPUT:")
        print("  Default:          Highest quality video (up to 8K)")
        print("  With --karaoke:   Professional karaoke MP3 (pure instrumental)")
        print("  With --pitch:     Pitch-adjusted version (original or karaoke)")
        print("")
        print("=" * 70)
        sys.exit(1)
    
    # Get URL/file path and remove any backslash escapes
    input_source = sys.argv[1].replace('\\', '')
    
    # Check if input is a local file or YouTube URL
    is_local_file = os.path.isfile(input_source)
    
    if is_local_file:
        print(f"📂 Local file mode: {input_source}")
    else:
        print(f"🌐 YouTube mode: {input_source}")
    
    # Check mode
    karaoke_mode = '--karaoke' in sys.argv or '--demucs' in sys.argv  # Support both for backward compat
    
    # Check for trim start time
    trim_start = 0
    for arg in sys.argv:
        if arg.startswith('--trim-start='):
            try:
                trim_start = int(arg.split('=')[1])
                print(f"⏩ Will skip first {trim_start} seconds")
            except:
                print(f"⚠️  Invalid trim-start value, ignoring")

    # Check for trim end time
    trim_end = 0
    for arg in sys.argv:
        if arg.startswith('--trim-end='):
            try:
                trim_end = int(arg.split('=')[1])
                print(f"⏩ Will trim last {trim_end} seconds")
            except:
                print(f"⚠️  Invalid trim-end value, ignoring")

    # Check for pitch adjustment
    pitch_shift = 0
    for arg in sys.argv:
        if arg.startswith('--pitch='):
            try:
                pitch_shift = int(arg.split('=')[1])
                if abs(pitch_shift) > 12:
                    print(f"⚠️  Pitch shift limited to ±12 semitones, capping at {12 if pitch_shift > 0 else -12}")
                    pitch_shift = max(-12, min(12, pitch_shift))
                if pitch_shift != 0:
                    print(f"🎵 Will adjust pitch by {pitch_shift:+d} semitones (high-quality Rubberband)")
            except:
                print(f"⚠️  Invalid pitch value, ignoring")
    
    try:
        # LOCAL FILE MODE
        if is_local_file:
            print(f"\n🎵 Processing local file: {input_source}")
            
            # Verify it's an audio file
            if not input_source.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')):
                print(f"⚠️  Warning: File doesn't have a common audio extension")
            
            if karaoke_mode:
                # Create karaoke from local file
                print(f"\n🎤 Creating karaoke from local file...")
                karaoke_output = create_demucs_karaoke(input_source, mode='professional')
                
                # Apply pitch adjustment if requested
                if pitch_shift != 0:
                    karaoke_output = adjust_pitch(karaoke_output, pitch_shift)
                
                print(f"\n✅ Karaoke creation complete!")
                print(f"📁 Output: {karaoke_output}")
                
                # Cleanup
                for cleanup_dir in ['separated', 'mdx_separated']:
                    if os.path.exists(cleanup_dir):
                        shutil.rmtree(cleanup_dir)
                
            elif pitch_shift != 0:
                # Just apply pitch adjustment to existing file
                print(f"\n🎵 Adjusting pitch of existing file...")
                pitched_output = adjust_pitch(input_source, pitch_shift)
                
                print(f"\n✅ Pitch adjustment complete!")
                print(f"📁 Original: {input_source}")
                print(f"📁 Pitched:  {pitched_output}")
            else:
                print(f"\n⚠️  No operation specified!")
                print(f"   Use --karaoke to create karaoke track")
                print(f"   Use --pitch=N to adjust pitch")
            
            return
        
        # YOUTUBE MODE (original logic)
        url = input_source
        print(f"Downloading video from: {url}")

        yt = YouTube(url, on_progress_callback=on_progress)
        
        print(f"Title: {yt.title}")
        print(f"Author: {yt.author}")
        print(f"Length: {yt.length} seconds")
        print(f"Views: {yt.views}")
        
        if karaoke_mode:
            # SCENARIO 3: Karaoke mode - download audio and create karaoke
            print(f"\n🎤 Karaoke mode enabled (AI vocal removal)")
            
            # Get the highest quality audio stream
            print(f"\n🔍 Scanning available audio streams...")
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            if not audio_stream:
                print(f"❌ No audio stream found!")
                return
            
            print(f"✅ Selected HIGHEST QUALITY audio:")
            print(f"   • Bitrate: {audio_stream.abr}")
            print(f"   • Codec: {audio_stream.audio_codec}")
            print(f"   • File type: {audio_stream.mime_type}")
            print(f"   • Will convert to: 320kbps MP3 @ 48kHz (maximum quality)")
            print(f"\nDownloading audio stream...")
            
            audio_file = audio_stream.download(filename='temp_audio.mp4')

            # Trim if requested
            if trim_start > 0 or trim_end > 0:
                trim_msg = []
                if trim_start > 0:
                    trim_msg.append(f"first {trim_start} seconds")
                if trim_end > 0:
                    trim_msg.append(f"last {trim_end} seconds")
                print(f"\n✂️  Trimming {' and '.join(trim_msg)}...")

                trimmed_file = 'temp_audio_trimmed.mp4'
                ffmpeg_cmd = ['ffmpeg', '-y']

                # Add trim-start if specified
                if trim_start > 0:
                    ffmpeg_cmd.extend(['-ss', str(trim_start)])

                ffmpeg_cmd.extend(['-i', audio_file])

                # Add trim-end if specified (need to calculate duration)
                if trim_end > 0:
                    duration = get_audio_duration(audio_file)
                    target_duration = duration - trim_start - trim_end
                    if target_duration <= 0:
                        print(f"⚠️  Error: Trim settings would result in zero or negative duration!")
                        print(f"   Audio duration: {duration:.1f}s, trim-start: {trim_start}s, trim-end: {trim_end}s")
                        sys.exit(1)
                    ffmpeg_cmd.extend(['-t', str(target_duration)])

                ffmpeg_cmd.extend(['-c', 'copy', trimmed_file])

                subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                os.remove(audio_file)
                audio_file = trimmed_file
            
            # Convert to high-quality MP3
            mp3_filename = f"{yt.title}.mp3".replace('/', '-').replace('\\', '-')
            print(f"\nConverting to MP3...")
            
            convert_command = [
                'ffmpeg',
                '-i', audio_file,
                '-vn',  # No video
                '-ab', '320k',  # High quality bitrate
                '-ar', '48000',  # Sample rate
                '-y',
                mp3_filename
            ]
            
            result = subprocess.run(convert_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n✅ Audio extraction successful!")
                print(f"MP3 saved as: {mp3_filename}")
                
                # Clean up temporary file
                os.remove(audio_file)
                
                # Create karaoke track
                karaoke_mp3_filename = f"{yt.title}_KARAOKE.mp3".replace('/', '-').replace('\\', '-')
                
                # Use Demucs + MDX-Net ensemble for ULTIMATE quality
                instrumental_file = create_demucs_karaoke(mp3_filename, mode='professional')
                
                # Apply pitch adjustment if requested
                if pitch_shift != 0:
                    instrumental_file = adjust_pitch(instrumental_file, pitch_shift)
                
                if instrumental_file:
                    # Rename final output to our desired filename
                    shutil.move(instrumental_file, karaoke_mp3_filename)
                    
                    print(f"\n✅ ULTIMATE karaoke audio created!")
                    print(f"Original MP3: {mp3_filename}")
                    print(f"Karaoke MP3: {karaoke_mp3_filename}")
                    
                    # Cleanup separated dirs
                    for cleanup_dir in ['separated', 'mdx_separated']:
                        if os.path.exists(cleanup_dir):
                            shutil.rmtree(cleanup_dir)
            else:
                print(f"\n❌ MP3 conversion failed!")
                print(f"Error: {result.stderr}")
        else:
            # SCENARIO 1 & 2: Video mode (download original, optionally with pitch shift)
            if pitch_shift != 0:
                print(f"\n🎵 Video mode with pitch adjustment")
            else:
                print(f"\n📹 Video mode (original quality)")
            
            # Get the highest quality video stream (adaptive - video only)
            print(f"\n🔍 Scanning available video streams...")
            video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        
            # Get the highest quality audio stream
            print(f"🔍 Scanning available audio streams...")
            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
            
            if not video_stream or not audio_stream:
                print(f"❌ Could not find suitable video or audio stream!")
                return
            
            print(f"\n✅ Selected HIGHEST QUALITY streams:")
            print(f"   VIDEO:")
            print(f"   • Resolution: {video_stream.resolution}")
            print(f"   • FPS: {video_stream.fps}")
            print(f"   • Codec: {video_stream.video_codec}")
            print(f"   • File type: {video_stream.mime_type}")
            print(f"   AUDIO:")
            print(f"   • Bitrate: {audio_stream.abr}")
            print(f"   • Codec: {audio_stream.audio_codec}")
            print(f"   • File type: {audio_stream.mime_type}")
            
            print(f"\nDownloading video stream...")
            video_file = video_stream.download(filename='video.mp4')
            
            print(f"\nDownloading audio stream...")
            audio_file = audio_stream.download(filename='audio.mp4')

            # Trim if requested
            if trim_start > 0 or trim_end > 0:
                trim_msg = []
                if trim_start > 0:
                    trim_msg.append(f"first {trim_start} seconds")
                if trim_end > 0:
                    trim_msg.append(f"last {trim_end} seconds")
                print(f"\n✂️  Trimming {' and '.join(trim_msg)} from audio...")

                trimmed_file = 'audio_trimmed.mp4'
                ffmpeg_cmd = ['ffmpeg', '-y']

                # Add trim-start if specified
                if trim_start > 0:
                    ffmpeg_cmd.extend(['-ss', str(trim_start)])

                ffmpeg_cmd.extend(['-i', audio_file])

                # Add trim-end if specified (need to calculate duration)
                if trim_end > 0:
                    duration = get_audio_duration(audio_file)
                    target_duration = duration - trim_start - trim_end
                    if target_duration <= 0:
                        print(f"⚠️  Error: Trim settings would result in zero or negative duration!")
                        print(f"   Audio duration: {duration:.1f}s, trim-start: {trim_start}s, trim-end: {trim_end}s")
                        sys.exit(1)
                    ffmpeg_cmd.extend(['-t', str(target_duration)])

                ffmpeg_cmd.extend(['-c', 'copy', trimmed_file])

                subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                os.remove(audio_file)
                audio_file = trimmed_file
            
            print(f"\nDownload completed successfully!")
            print(f"Video file: {video_file}")
            print(f"Audio file: {audio_file}")
            
            # Apply pitch adjustment to audio if requested (SCENARIO 2)
            if pitch_shift != 0:
                print(f"\n🎵 Applying pitch adjustment to audio...")
                # Extract audio to MP3 first
                temp_audio_mp3 = "temp_audio_for_pitch.mp3"
                subprocess.run([
                    'ffmpeg', '-y', '-i', audio_file, '-vn', '-ab', '320k', temp_audio_mp3
                ], capture_output=True, text=True)
                
                # Apply pitch shift
                pitched_audio = adjust_pitch(temp_audio_mp3, pitch_shift)
                
                # Convert back to format suitable for merging
                os.remove(audio_file)
                subprocess.run([
                    'ffmpeg', '-y', '-i', pitched_audio, '-c:a', 'aac', '-b:a', '320k', audio_file
                ], capture_output=True, text=True)
                
                # Cleanup temp files
                os.remove(temp_audio_mp3)
                os.remove(pitched_audio)
            
            # Merge video and audio using ffmpeg
            output_filename = f"{yt.title}.mp4".replace('/', '-').replace('\\', '-')
            if pitch_shift != 0:
                output_filename = f"{yt.title}_pitch{pitch_shift:+d}.mp4".replace('/', '-').replace('\\', '-')
            
            print(f"\nMerging video and audio with ffmpeg...")
            
            # Build FFmpeg command properly
            merge_command = [
                'ffmpeg',
                '-y',  # Overwrite output file if it exists (must come early)
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'copy',
            ]
            
            # Add audio codec settings
            if pitch_shift != 0:
                merge_command.extend(['-c:a', 'aac', '-b:a', '320k'])
            else:
                merge_command.extend(['-c:a', 'copy'])
            
            # Add output filename
            merge_command.append(output_filename)
            
            result = subprocess.run(merge_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n✅ Merge successful!")
                print(f"Final video saved as: {output_filename}")
                
                # Clean up temporary files
                print(f"\nCleaning up temporary files...")
                os.remove(video_file)
                os.remove(audio_file)
                print(f"Temporary files removed.")
                
                print(f"\n✨ Download complete!")
                print(f"Final video: {output_filename}")
                    
            else:
                print(f"\n❌ Merge failed!")
                print(f"Error: {result.stderr}")
                print(f"Video and audio files are still available separately.")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
