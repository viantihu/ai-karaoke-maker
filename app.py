import streamlit as st
import os
import shutil
from main import create_demucs_karaoke, adjust_pitch

st.set_page_config(
    page_title="AI Karaoke Maker - Basic Demo",
    page_icon="🎤",
    layout="wide"
)

# Header
st.title("🎤 AI Karaoke Maker")
st.subheader("Basic Demo - Optimized for Streamlit Cloud")

# Info banner
st.info("""
**✨ You're using the Basic version** - Fast AI-powered vocal removal using Demucs, optimized for cloud deployment.
""")

# Main interface
st.markdown("### 🎵 Process Your Music")

mode = st.radio(
    "Choose input source:",
    ["YouTube URL", "Upload Audio File"],
    horizontal=True
)

col1, col2 = st.columns(2)
with col1:
    karaoke = st.checkbox("🎤 Create Karaoke (Remove vocals)", value=True)
with col2:
    pitch = st.slider("🎵 Pitch Shift (semitones)", -12, 12, 0,
                     help="Adjust pitch to match your vocal range. 0 = no change")

trim = st.number_input("✂️ Trim Start (seconds)", min_value=0, value=0,
                      help="Skip the first N seconds (useful for removing intros/ads)")

input_file = None
youtube_url = None

def cleanup_temp():
    for d in ["separated", "mdx_separated"]:
        if os.path.exists(d):
            shutil.rmtree(d)

def process_audio(audio_path):
    output = audio_path
    if karaoke:
        # Use 'basic' mode for Streamlit Cloud (lighter, faster)
        output = create_demucs_karaoke(audio_path, mode="basic")
    if pitch != 0:
        output = adjust_pitch(output, pitch)
    return output

st.markdown("---")

if mode == "YouTube URL":
    youtube_url = st.text_input(
        "🔗 Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste the full YouTube URL here"
    )
    if youtube_url:
        st.success("✅ URL provided - ready to process!")
else:
    uploaded = st.file_uploader(
        "📁 Upload your audio file:",
        type=["mp3", "wav", "flac", "m4a", "aac", "ogg"],
        help="Supported formats: MP3, WAV, FLAC, M4A, AAC, OGG"
    )
    if uploaded:
        temp_path = f"temp_uploaded_{uploaded.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded.read())
        input_file = temp_path
        st.success(f"✅ File uploaded: {uploaded.name} - ready to process!")

st.markdown("---")

# Process button with better styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button("🚀 Start Processing", type="primary", use_container_width=True)

if process_button:
    # Show processing summary
    st.markdown("### 📋 Processing Summary")
    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.metric("Mode", "Basic (Demucs)")
    with summary_cols[1]:
        st.metric("Karaoke", "Yes" if karaoke else "No")
    with summary_cols[2]:
        st.metric("Pitch Shift", f"{pitch:+d} semitones" if pitch != 0 else "None")

    with st.spinner("🎵 Processing your audio... This may take 3-5 minutes."):
        try:
            if mode == "YouTube URL":
                if not youtube_url:
                    st.error("Please enter a YouTube URL.")
                else:
                    # Download audio using pytubefix
                    from pytubefix import YouTube
                    yt = YouTube(youtube_url)
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    if not audio_stream:
                        st.error("No audio stream found!")
                    else:
                        audio_file = audio_stream.download(filename="temp_youtube_audio.mp4")
                        # Trim if needed
                        if trim > 0:
                            trimmed = "temp_youtube_audio_trimmed.mp4"
                            os.system(f"ffmpeg -y -i '{audio_file}' -ss {trim} -c copy '{trimmed}'")
                            os.remove(audio_file)
                            audio_file = trimmed
                        # Convert to mp3
                        mp3_file = yt.title.replace('/', '-').replace('\\', '-') + ".mp3"
                        os.system(f"ffmpeg -y -i '{audio_file}' -vn -ab 320k -ar 48000 '{mp3_file}'")
                        os.remove(audio_file)
                        output = process_audio(mp3_file)

                        # Success message with download
                        st.success("✅ Processing complete!")
                        st.balloons()

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**🎵 Song:** {yt.title}")
                            if karaoke:
                                st.markdown("**🎤 Type:** Karaoke (vocals removed)")
                            if pitch != 0:
                                st.markdown(f"**🎶 Pitch:** {pitch:+d} semitones")

                        with col2:
                            with open(output, "rb") as f:
                                st.download_button(
                                    "⬇️ Download Your Track",
                                    f,
                                    file_name=os.path.basename(output),
                                    mime="audio/mpeg",
                                    type="primary",
                                    use_container_width=True
                                )

                        cleanup_temp()
            else:
                if not input_file:
                    st.error("Please upload an audio file.")
                else:
                    # Trim if needed
                    trimmed_file = input_file
                    if trim > 0:
                        trimmed_file = f"trimmed_{input_file}"
                        os.system(f"ffmpeg -y -i '{input_file}' -ss {trim} -c copy '{trimmed_file}'")
                    output = process_audio(trimmed_file)

                    # Success message with download
                    st.success("✅ Processing complete!")
                    st.balloons()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📁 File:** {uploaded.name}")
                        if karaoke:
                            st.markdown("**🎤 Type:** Karaoke (vocals removed)")
                        if pitch != 0:
                            st.markdown(f"**🎶 Pitch:** {pitch:+d} semitones")

                    with col2:
                        with open(output, "rb") as f:
                            st.download_button(
                                "⬇️ Download Your Track",
                                f,
                                file_name=os.path.basename(output),
                                mime="audio/mpeg",
                                type="primary",
                                use_container_width=True
                            )

                    cleanup_temp()
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.info("💡 Tip: If you're experiencing issues, try with a shorter audio file or simpler settings.")

# Footer
st.markdown("---")
st.markdown("### 💡 Tips & Best Practices")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    **🎤 For Best Karaoke Results:**
    - Use high-quality source audio
    - Songs with clear vocals work best
    - Pop, rock, and mainstream genres are ideal
    - Basic mode works great for most songs!
    """)

with tips_col2:
    st.markdown("""
    **🎵 Pitch Shifting Tips:**
    - -2 to -4 semitones: Lower for male vocals
    - +2 to +4 semitones: Raise for female vocals
    - 0 semitones: Keep original key
    - Test different values to find your range
    """)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    Made with ❤️ using Streamlit |
    <a href='https://github.com/viantihu/ai-karaoke-maker' target='_blank'>GitHub</a> |
    Powered by Demucs AI
    </div>
    """,
    unsafe_allow_html=True
)
