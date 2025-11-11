# Deployment Guide for AI Karaoke Maker

## Option 1: Deploy to Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account with your repository
- Streamlit account (sign up at https://streamlit.io)

### Steps

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Click "New app"
   - Select your GitHub repository
   - Choose the branch: `main`
   - Set the main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets (if needed)**
   - In your Streamlit Cloud dashboard, go to App settings → Secrets
   - Add any API keys or sensitive data as needed

### Important Notes
- **FFmpeg requirement**: Streamlit Cloud has FFmpeg pre-installed
- **Processing time**: Large audio files may take a while. Consider setting longer timeout values
- **Memory limits**: Be aware of upload size limits (default 500MB in config)

---

## Option 2: Deploy to Heroku

### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository with your code

### Steps

1. **Create a Buildpack configuration file** (`Procfile`)
   ```bash
   echo "web: streamlit run app.py" > Procfile
   ```

2. **Add system dependencies** (`apt-packages` for buildpack-apt)
   ```bash
   echo "ffmpeg" > apt-packages
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

---

## Option 3: Deploy to AWS/Google Cloud

### For AWS EC2
1. Launch an Ubuntu instance
2. Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg python3-pip python3-venv -y
   ```
3. Clone your repo and install requirements
4. Run: `streamlit run app.py`

### For Google Cloud Run
1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.13-slim
   RUN apt-get update && apt-get install -y ffmpeg
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["streamlit", "run", "app.py"]
   ```
2. Deploy using `gcloud run deploy`

---

## Option 4: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`

---

## Troubleshooting

### FFmpeg not found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Audio processing is slow
- This is normal for AI model inference
- Consider optimizing model loading by caching
- Use smaller models for faster processing

### Upload size limits
- Adjust `maxUploadSize` in `.streamlit/config.toml`
- Default is 500MB

### Dependencies issues
- Use `pip install --upgrade -r requirements.txt`
- Consider using a virtual environment: `python -m venv venv`

---

## Performance Optimization Tips

1. **Cache model loading**: Add `@st.cache_resource` to heavy computations
2. **Optimize audio processing**: Consider smaller batch sizes
3. **Use async operations**: For file uploads and downloads
4. **Monitor memory usage**: Especially with large audio files

---

## Next Steps

1. Choose your deployment platform (Streamlit Cloud is easiest)
2. Set up GitHub repository if not done
3. Configure any environment variables or secrets
4. Test the deployment
5. Monitor logs for any issues
