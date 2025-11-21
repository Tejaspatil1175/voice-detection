# Quick Reference Guide

## 🎯 File Locations

### Frontend Files (e:\cloude\frontend\)
```
frontend/
├── index.html          ← Main analytics dashboard (with AI chatbot)
├── landing.html        ← Landing page (entry point)
├── script.js           ← All JavaScript logic + Gemini AI integration
├── style.css           ← Analytics dashboard styles
├── landing.css         ← Landing page styles
├── landing.js          ← Landing page animations
└── test-gemini.html    ← Gemini API test page (NEW!)
```

### Backend Files (e:\cloude\backend\)
```
backend/
├── app.py              ← Flask server
├── voice_analyzer.py   ← Voice analysis engine
├── requirements.txt    ← Python dependencies
└── uploads/            ← Temporary audio storage
```

## 🔧 Configuration Locations

### Gemini API Configuration
**File**: `frontend/script.js`
**Lines**: 1-11

```javascript
// Import Google Generative AI SDK
import { GoogleGenerativeAI } from '@google/generative-ai';

// API Configuration
const API_URL = 'http://localhost:5000';

// ==================== GEMINI API CONFIGURATION ====================
const GEMINI_API_KEY = 'AIzaSyDwYqJtNS0hbZ3C0Us2c7JbuL4gGw6YFTM';
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const geminiModel = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
// ==================================================================
```

### To Change API Key:
1. Edit line 8 in `frontend/script.js`
2. Replace the entire key string
3. Save file and refresh browser

### To Change Model:
1. Edit line 10 in `frontend/script.js`
2. Change model name in `{ model: 'gemini-2.0-flash-exp' }`
3. Available: `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`

## 🎨 UI Element Locations

### Floating Chatbot Widget
**File**: `frontend/index.html`
**Lines**: ~270-290

```html
<!-- Floating Chatbot Widget -->
<div class="chatbot-widget">
    <button class="chatbot-toggle" id="chatbotToggle">
        <!-- Toggle button in bottom-right corner -->
    </button>
    <div class="chatbot-panel" id="chatbotPanel">
        <!-- Chat interface -->
    </div>
</div>
```

**Styling**: `frontend/style.css` lines ~800-950

### Export PDF Button
**File**: `frontend/index.html`
**Line**: ~175

```html
<button id="exportPdfBtn">
    <svg>...</svg> Export Report as PDF
</button>
```

**Function**: `frontend/script.js` - `generatePDF()` function

## 📊 Chart Locations

All charts are in `frontend/script.js`:

| Chart Type | Function | Line Range |
|------------|----------|------------|
| Emotion Distribution | `createEmotionChart()` | ~700-750 |
| Stress Components | `createStressChart()` | ~750-800 |
| Voice Pitch | `createPitchChart()` | ~900-960 |
| Personality Radar | `createPersonalityChart()` | ~800-850 |
| Emotion Timeline | `createTimelineChart()` | ~750-800 |
| Confidence Heatmap | `createHeatmap()` | ~850-900 |

## 🤖 Chatbot Logic

### Main Functions (frontend/script.js)

```
initializeChatbot()     ← Lines ~1200-1240 (Setup event listeners)
sendChatMessage()       ← Lines ~1260-1290 (Send user message)
generateAIResponse()    ← Lines ~1305-1320 (Route to Gemini or fallback)
callGeminiAPI()         ← Lines ~1390-1420 (Gemini API integration)
addBotMessage()         ← Lines ~1470-1490 (Display bot response)
```

### Quick Questions (Test in chatbot after analysis):
- "What's my emotional state?"
- "How's my vocal health?"
- "Why is my stress level high/low?"
- "Explain my personality traits"
- "What issues were detected?"
- "What are the suggestions?"

## 🚀 Start Commands

### Start Backend Server
```powershell
cd e:\cloude\backend
python app.py
```
Server runs on: http://localhost:5000

### Access Pages
- **Landing Page**: http://localhost:5000/
- **Analytics Dashboard**: http://localhost:5000/analytics
- **Gemini API Test**: http://localhost:5000/test-gemini.html

## 🐛 Debug Mode

### Enable Console Logging
Open browser DevTools (F12) → Console tab

You'll see:
- `Voice Analysis Script Loaded - Version 3.2`
- API responses
- Gemini API calls
- Chart rendering logs
- Error messages (if any)

### Common Console Messages
```javascript
✅ "Gemini API initialized successfully"
✅ "Analysis complete: {...data}"
✅ "Charts rendered successfully"
❌ "Gemini API failed: ..." (falls back to rule-based)
❌ "jsPDF library not loaded" (CDN issue)
```

## 📝 Customization Quick Guide

### Change Colors
**File**: `frontend/style.css`
**Primary Gradient**: Lines ~50-60
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
```

### Change Chat Icon
**File**: `frontend/index.html`
**Line**: ~273
```html
<svg>...</svg> <!-- Replace SVG here -->
```

### Modify Loading Messages
**File**: `frontend/script.js`
**Function**: `showLoadingSteps()` around line ~400
```javascript
const steps = [
    { text: 'Your custom message', icon: '🎤' },
    ...
];
```

### Add New Chart
1. Create canvas in `index.html`: `<canvas id="myChart"></canvas>`
2. Add function in `script.js`: `function createMyChart(data) { ... }`
3. Call in `displayResults()`: `createMyChart(data);`

## 🎯 Key Features Checklist

Before deploying, verify:
- [ ] Backend server starts without errors
- [ ] Landing page loads (http://localhost:5000)
- [ ] Can record audio (microphone permission)
- [ ] Can upload audio files
- [ ] Analysis completes successfully
- [ ] All 5 charts render correctly
- [ ] Chatbot opens/closes smoothly
- [ ] Gemini AI responds (check console if issues)
- [ ] PDF export downloads successfully
- [ ] Mobile responsive (test at different widths)

## 💡 Pro Tips

1. **Faster Development**: Use `Ctrl + Shift + R` to hard refresh (bypass cache)
2. **Test Chatbot Quickly**: Use `test-gemini.html` before full analysis
3. **Debug Charts**: Open console, all Chart.js errors show there
4. **PDF Issues**: Check if CDN scripts load (Network tab in DevTools)
5. **API Limits**: Free tier = 60 req/min, monitor console for rate limit errors

---

**Last Updated**: November 22, 2025
**Version**: 3.2 (Gemini AI SDK Integration)
