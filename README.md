# Voice Analysis System

AI-powered voice analysis system that detects emotion, vocal health, stress levels, personality traits, and more from audio recordings.

## Features

- **Emotion Detection**: Identifies 7 emotions (Happy, Sad, Angry, Fearful, Disgusted, Surprised, Neutral)
- **Vocal Health Analysis**: Measures jitter, shimmer, and HNR to assess vocal cord health
- **Stress Level Detection**: Calculates stress from vocal patterns and emotional state
- **Personality Analysis**: Estimates extraversion, emotional stability, and openness
- **Voice Age Estimation**: Predicts speaker's age from voice characteristics
- **Trigger Word Detection**: Identifies specific keywords in speech
- **Timeline Analysis**: Shows how emotions change over time
- **Health Suggestions**: Provides recommendations based on analysis

## Tech Stack

### Backend
- Python 3.8+
- Flask (REST API)
- Transformers (Hugging Face AI models)
- Parselmouth (Vocal analysis)
- Librosa (Audio processing)

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Web Audio API (for recording)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)

### Step 1: Clone/Download Project
```bash
# If using git
git clone <repository-url>
cd voice-analyzer

# Or simply download and extract the ZIP file
```

### Step 2: Install FFmpeg (Required)

**FFmpeg is required for audio processing!**

**Quick Setup (Automated):**
```bash
cd backend
python setup_ffmpeg.py
```

**Manual Installation Options:**

*Option A: Using Chocolatey (Run as Administrator)*
```powershell
choco install ffmpeg -y
```

*Option B: Download Manually*
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

*Option C: Using Scoop*
```powershell
scoop install ffmpeg
```

**Verify Installation:**
```bash
ffmpeg -version
```

See `FFMPEG_SETUP.md` for detailed instructions.

### Step 3: Install Backend Dependencies
```bash
# Navigate to backend folder
cd backend

# Install required packages (this may take 5-10 minutes)
pip install -r requirements.txt

# If you get errors, try:
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Start Backend Server
```bash
# Simply run app.py - FFmpeg is now auto-detected!
cd backend
python app.py
```

You should see:
```
✓ FFmpeg found and added to PATH: E:\cloude\backend\ffmpeg\...
Initializing Voice Analyzer...
Loading AI models...
Models loaded successfully!
Server ready!
 * Running on http://127.0.0.1:5000
```

**Note**: 
- First run will download AI models (~500MB). This is one-time only and takes 30-60 seconds.
- FFmpeg is automatically detected and configured - no manual PATH setup needed!
- If you see FFmpeg errors, run: `python setup_ffmpeg.py`

### Step 5: Open Frontend
```bash
# Open a new terminal
# Navigate to frontend folder
cd frontend

# Open index.html in browser
# Option 1: Double-click index.html file
# Option 2: Use a local server (recommended)
python -m http.server 8000

# Then open: http://localhost:8000
```

## Usage

### Upload Audio File
1. Click "Choose File" button
2. Select an audio file (WAV, MP3, OGG, FLAC, M4A)
3. Click "Analyze Voice"
4. Wait for results (10-30 seconds)

### Record Audio
1. Click "Start Recording"
2. Allow microphone access when prompted
3. Speak for 5-30 seconds
4. Click "Stop Recording"
5. Click "Analyze Voice"

### View Results
The system displays:
- Quick stats cards (Emotion, Health, Stress, Age)
- Personality trait bars
- Detected issues and health signals
- Trigger words found in speech
- Personalized suggestions
- Emotion timeline chart
- Raw JSON data (expandable)

## API Documentation

### Endpoints

#### GET /health
Health check endpoint
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Voice Analysis API",
  "version": "1.0"
}
```

#### POST /analyze
Analyze audio file
```bash
curl -X POST -F "audio=@recording.wav" http://localhost:5000/analyze
```

Response:
```json
{
  "success": true,
  "data": {
    "emotion": "happy",
    "vocal_health_score": 85.5,
    "stress_level": 25.3,
    "voice_age": 30,
    "personality_analysis": {
      "extraversion": 65.2,
      "emotional_stability": 72.8,
      "openness": 58.4
    },
    "issues_detected": [],
    "early_illness_signals": [],
    "trigger_word_alert": ["yes", "go"],
    "suggestions": ["Voice health is good - keep it up!"],
    "timeline_emotion": "happy",
    "heatmap": {},
    "live_analysis": {},
    "raw": {}
  }
}
```

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'flask'`
```bash
# Solution:
pip install -r requirements.txt
```

**Problem**: Models download failing
```bash
# Solution: Try manual download
pip install transformers torch --upgrade
python -c "from transformers import pipeline; pipeline('audio-classification', model='Hatman/audio-emotion-detection')"
```

**Problem**: Port 5000 already in use
```bash
# Solution: Change port in app.py (last line)
app.run(debug=True, host='0.0.0.0', port=5001)

# Update API_URL in frontend/script.js
const API_URL = 'http://localhost:5001';
```

### Frontend Issues

**Problem**: CORS errors in browser console
```bash
# Solution: Make sure Flask-CORS is installed
pip install flask-cors
```

**Problem**: Cannot connect to backend
```bash
# Solution: 
# 1. Check backend is running (terminal should show server messages)
# 2. Check firewall isn't blocking port 5000
# 3. Try accessing http://localhost:5000/health directly in browser
```

**Problem**: Microphone not working
```bash
# Solution:
# 1. Use HTTPS or localhost (HTTP also works on localhost)
# 2. Grant microphone permissions in browser
# 3. Check browser console for specific errors
```

### Performance Issues

**Problem**: Analysis is very slow
```bash
# Solution:
# 1. Use smaller audio files (< 30 seconds recommended)
# 2. Use WAV format for best compatibility
# 3. Ensure you have at least 4GB RAM available
# 4. Close other applications during analysis
```

## File Limits
- Maximum file size: 10MB
- Supported formats: WAV, MP3, OGG, FLAC, M4A
- Recommended duration: 5-30 seconds
- Sample rate: Any (automatically converted)

## Project Structure
```
voice-analyzer/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── voice_analyzer.py         # Core analysis logic
│   ├── requirements.txt          # Python dependencies
│   └── uploads/                  # Temporary upload folder (auto-created)
├── frontend/
│   ├── index.html               # Main UI
│   ├── style.css                # Styling
│   └── script.js                # Frontend logic
└── README.md                     # This file
```

## Notes
- First run downloads ~500MB of AI models (one-time)
- Analysis takes 10-30 seconds depending on audio length
- Internet required for initial model download only
- Results are estimates based on acoustic features
- Not for medical diagnosis - consult professionals for health concerns

## Support
For issues or questions, check:
1. Error messages in terminal (backend)
2. Browser console (F12) for frontend errors
3. This README troubleshooting section

## Version
1.0.0 - Initial Release
