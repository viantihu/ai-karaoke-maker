import streamlit as st
import os
import shutil
from main import create_demucs_karaoke, adjust_pitch

st.set_page_config(page_title="AI Music Processor", page_icon="🎵")
st.title("🎵 AI Music Processor")
st.markdown("Professional AI-powered music processing: YouTube download, karaoke, pitch shift.")

mode = st.radio("Input Source", ["YouTube URL", "Upload Audio File"])

karaoke = st.checkbox("Create Karaoke (AI vocal removal)", value=True)
pitch = st.slider("Pitch Shift (semitones)", -12, 12, 0)
trim = st.number_input("Trim Start (seconds)", min_value=0, value=0)

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
        # For local use with more resources, change to mode="professional"
        output = create_demucs_karaoke(audio_path, mode="basic")
    if pitch != 0:
        output = adjust_pitch(output, pitch)
    return output

if mode == "YouTube URL":
    youtube_url = st.text_input("YouTube URL")
else:
    uploaded = st.file_uploader("Upload audio file", type=["mp3", "wav", "flac", "m4a", "aac", "ogg"])
    if uploaded:
        temp_path = f"temp_uploaded_{uploaded.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded.read())
        input_file = temp_path

if st.button("Process"):
    with st.spinner("Processing..."):
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
                        st.success("Done!")
                        with open(output, "rb") as f:
                            st.download_button("Download Output", f, file_name=os.path.basename(output))
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
                    st.success("Done!")
                    with open(output, "rb") as f:
                        st.download_button("Download Output", f, file_name=os.path.basename(output))
                    cleanup_temp()
        except Exception as e:
            st.error(f"Error: {e}")
