# Voice Analysis System - Setup Instructions

## 📌 AI Chatbot Configuration

### ✅ Gemini API is Already Configured!

The chatbot is **ready to use** with Google Gemini 2.0 Flash (latest model).

**Current Configuration**:
- **API Key**: AIzaSyDwYqJtNS0hbZ3C0Us2c7JbuL4gGw6YFTM
- **Model**: gemini-2.0-flash-exp (most advanced, fastest responses)
- **SDK**: Official Google Generative AI SDK

### How to Change API Key (if needed):
1. Open `frontend/script.js`
2. Find line 8:
   ```javascript
   const GEMINI_API_KEY = 'AIzaSyDwYqJtNS0hbZ3C0Us2c7JbuL4gGw6YFTM';
   ```
3. Replace with your own key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### How to Change Model (if needed):
1. Open `frontend/script.js`
2. Find line 10:
   ```javascript
   const geminiModel = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
   ```
3. Available models:
   - `gemini-2.0-flash-exp` - Latest, fastest (recommended)
   - `gemini-1.5-pro` - Most capable, slower
   - `gemini-1.5-flash` - Fast, balanced

---

## 🔧 Troubleshooting

### PDF Export Not Working

**Problem**: When clicking "Export Report as PDF", nothing happens or shows an error.

**Solutions**:
1. **Check browser console** (F12 → Console tab) for errors
2. **Clear browser cache** and refresh the page (Ctrl + Shift + R)
3. **Verify CDN is accessible**:
   - The script uses: `https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js`
   - Open this URL in your browser to ensure it loads
4. **Check if analysis data exists**:
   - PDF export requires completed voice analysis
   - Record/upload audio and wait for results before exporting
5. **Browser compatibility**:
   - Use modern browsers: Chrome 90+, Firefox 88+, Edge 90+
   - Safari may have issues - try Chrome instead

### Gemini AI Chatbot Not Responding

**Problem**: Chatbot gives generic responses instead of AI-powered answers.

**Solutions**:
1. **Verify API key is added** (see Step 2 above)
2. **Check API key is valid**:
   - Make sure you copied the entire key
   - No extra spaces before/after the key
   - Key should start with `AIza`
3. **Check browser console** for API errors
4. **Verify internet connection** - Gemini API requires online access
5. **Fallback behavior**: If Gemini fails, the chatbot uses rule-based responses

### Backend Not Starting

**Problem**: Flask server won't start or crashes.

**Solutions**:
```powershell
# Install missing dependencies
cd e:\cloude\backend
pip install -r requirements.txt

# Ensure FFmpeg is available
# The app will auto-download FFmpeg if missing

# Run the server
python app.py
```

---

## 🎯 Features Overview

### 1. **Voice Analysis**
- Record audio using microphone
- Upload existing audio files (WAV, MP3, OGG, M4A)
- Real-time volume monitoring during recording

### 2. **Analytics Dashboard**
- Emotion detection with confidence levels
- Vocal health scoring
- Stress level analysis
- Personality trait breakdown (Big Five)
- Interactive charts (Chart.js)
- Pitch visualization
- Emotional timeline heatmap

### 3. **AI Chatbot Assistant**
- Floating button in bottom-right corner
- Click to open/close chat panel
- Powered by Google Gemini AI (when API key is configured)
- Ask natural language questions about your analysis
- Get personalized insights and suggestions

### 4. **PDF Export**
- Download comprehensive analysis report
- Includes all metrics, charts, and insights
- Professional formatting
- Automatic timestamp and page numbering

---

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop (recommended for best experience)
- Tablets (iPad, Android tablets)
- Mobile phones (for viewing results)

**Note**: Voice recording requires HTTPS on mobile devices (except localhost).

---

## 🔒 Privacy & Security

- **All processing is local** - your voice data is not stored permanently
- **Gemini API**: Only analysis metadata is sent (not raw audio)
- **No tracking** - no analytics or third-party trackers
- **Temporary storage**: Uploaded files are stored in `backend/uploads/` temporarily

---

## 📊 Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | 90+     | ✅ Fully Supported |
| Firefox | 88+     | ✅ Fully Supported |
| Edge    | 90+     | ✅ Fully Supported |
| Safari  | 14+     | ⚠️ Partial (PDF may have issues) |
| Opera   | 76+     | ✅ Fully Supported |

---

## 💡 Tips for Best Results

1. **Recording Quality**:
   - Use a quiet environment
   - Speak naturally for 10-30 seconds
   - Avoid background noise
   - Use a good quality microphone

2. **Chatbot Usage**:
   - Be specific in your questions
   - Examples: "Why is my stress level high?", "What do my personality traits mean?"
   - The AI has context of your entire analysis

3. **PDF Export**:
   - Wait for all charts to fully load before exporting
   - Ensure you're connected to the internet (for CDN libraries)
   - Use Chrome for best PDF quality

---

## 🆘 Getting Help

If you encounter issues:
1. Check browser console (F12) for error messages
2. Verify all dependencies are installed
3. Ensure backend server is running on port 5000
4. Try a different browser
5. Clear cache and cookies
6. Restart the backend server

---

## 🚀 Quick Start Commands

```powershell
# Terminal 1: Start Backend
cd e:\cloude\backend
python app.py

# Terminal 2: Open in Browser
# Navigate to: http://localhost:5000
```

### 🧪 Testing

**Full System Test**:
1. Open http://localhost:5000
2. Click "Get Started"
3. Record or upload audio
4. After analysis, test the chatbot and PDF export

**Gemini API Test Only**:
- Open http://localhost:5000/test-gemini.html
- Click "Test Gemini API" button
- Should see success message with AI response

---

## 🆕 What's New in Version 3.2

### ✨ Gemini AI Integration (Properly Implemented!)
- **Official Google Generative AI SDK** (not REST API)
- **Latest Model**: `gemini-2.0-flash-exp` (fastest, most advanced)
- **Pre-configured API Key**: `AIzaSyDwYqJtNS0hbZ3C0Us2c7JbuL4gGw6YFTM`
- **ES6 Modules**: Proper import/export syntax
- **Intelligent Context**: AI receives all voice analysis metrics
- **Natural Language**: Ask questions in plain English
- **Smart Fallback**: Rule-based responses if API unavailable

### 📋 All Features
- 🎤 Voice Recording (real-time volume meter)
- 📁 File Upload (WAV, MP3, OGG, M4A)
- 😊 Emotion Detection (with confidence %)
- 🎵 Vocal Health Score (pitch, jitter, shimmer)
- 😰 Stress Analysis (acoustic, linguistic, temporal)
- 🧠 Personality Traits (Big Five model)
- 📊 5 Interactive Charts (Chart.js)
- 💬 AI Chatbot (floating widget)
- 📄 PDF Export (comprehensive reports)
- 🎨 Modern UI (dark theme, glassmorphism)

---

## 🔑 API Key Details

**Current Configuration**:
```javascript
API Key: AIzaSyDwYqJtNS0hbZ3C0Us2c7JbuL4gGw6YFTM
Model: gemini-2.0-flash-exp
SDK: @google/generative-ai (official)
Rate Limit: 60 requests/minute (free tier)
```

**Usage**: Free for development/personal projects

**Get Your Own** (optional):
1. Visit https://makersuite.google.com/app/apikey
2. Create API key (free)
3. Replace in `frontend/script.js` line 8

That's it! Enjoy your AI-powered voice analysis system! 🎤✨
