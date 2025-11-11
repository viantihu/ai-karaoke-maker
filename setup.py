from setuptools import setup

setup(
    name="ai-karaoke-maker",
    version="0.1.0",
    py_modules=[],
    install_requires=[
        "audio-separator>=0.39.1",
        "onnxruntime>=1.23.1",
        "streamlit>=1.24.1",
        "pytubefix>=10.0.0",
        "ffmpeg-python>=0.2.1",
    ],
)
