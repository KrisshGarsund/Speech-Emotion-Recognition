# 🎤 SpeechSense Frontend - Complete Setup Guide

A modern, professional web interface for Speech Emotion Recognition with real-time audio analysis.

## 📋 Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Testing the Application](#testing-the-application)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## ✨ Features

### User Interface
- ✅ **Dark Mode by Default** with light mode toggle
- ✅ **Glass-morphism Design** with neon lime green accents
- ✅ **Animated Background** that follows your mouse cursor
- ✅ **3D Hover Effects** on emotion cards
- ✅ **Smooth Scroll Animations** throughout the page
- ✅ **Fully Responsive** - works on desktop, tablet, and mobile

### Functionality
- 🎵 **Upload Audio Files** - Drag & drop or click to browse
- 🎙️ **Live Audio Recording** - Record directly from your microphone
- 📊 **Real-time Visualization** - See audio frequencies as you record
- 🧠 **AI-Powered Analysis** - Instant emotion recognition
- 📈 **Detailed Results** - Confidence scores and probability breakdown

### Supported Emotions
The model recognizes **8 emotions**:
1. 😊 **Happy** - Joy, pleasure, contentment
2. 😢 **Sad** - Sorrow, grief, melancholy
3. 😠 **Angry** - Rage, frustration, irritation
4. 😳 **Fearful** - Anxiety, worry, apprehension
5. 🍃 **Calm** - Peace, tranquility, relaxation
6. 😲 **Surprised** - Shock, amazement, astonishment
7. 😵 **Disgust** - Revulsion, aversion, distaste
8. 😐 **Neutral** - Balanced, indifferent, composed

---

## 🔧 Prerequisites

### Required Software
1. **Python 3.8 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download: https://www.python.org/downloads/

2. **Trained Model Files** (These should already exist in your project)
   - `Predict/SER_model.h5` - The trained emotion recognition model
   - `Predict/label_encoder.pkl` - Label encoder for emotion classes

### Required Python Packages
All packages are listed in `requirements.txt`:
- Flask 3.0.3 - Web framework
- flask-cors 4.0.0 - CORS support
- tensorflow 2.17.0 - Deep learning framework
- librosa 0.10.2.post1 - Audio processing
- numpy, pandas, scikit-learn - Data processing

---

## 📦 Installation

### Step 1: Clone or Navigate to Project Directory
```bash
cd "H:\speech emotion\Speech-Emotion-Recognition"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** Installation may take 5-10 minutes due to TensorFlow and other large packages.

### Step 4: Verify Model Files
Check that these files exist:
```
✓ Predict/SER_model.h5
✓ Predict/label_encoder.pkl
```

If missing, you'll need to train the model first using the training scripts.

---

## 🚀 Running the Application

### Option 1: Double-click (Easiest - Windows)
Simply double-click `run_server.bat` in the project root folder.

### Option 2: Command Line (Windows)
```bash
python app.py
```

### Option 3: Command Line (Linux/Mac)
```bash
python3 app.py
```

### Option 4: Using Shell Script (Linux/Mac)
```bash
chmod +x run_server.sh
./run_server.sh
```

### Expected Output
```
============================================================
SpeechSense - Speech Emotion Recognition Server
============================================================
Loading emotion recognition model...
✓ Model loaded from: Predict/SER_model.h5
✓ Label encoder loaded. Emotions: ['Angry' 'Calm' 'Disgust' 'Fearful' 'Happy' 'Neutral' 'Sad' 'Surprised']
✓ Model initialization complete!

Starting Flask server...
Frontend URL: http://localhost:5000
API Endpoint: http://localhost:5000/predict
Health Check: http://localhost:5000/health

Press Ctrl+C to stop the server
============================================================
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.xxx:5000
```

### Access the Application
Open your web browser and go to:
```
http://localhost:5000
```

---

## 🧪 Testing the Application

### 1. Test with Sample Audio File

#### Upload Method:
1. Navigate to the **Predict** section
2. Click on **Upload Audio** card
3. Click the dropzone or drag a `.wav` file
4. Click **Analyze Emotion** button
5. Wait for results (usually 1-3 seconds)

#### Test Files:
You can use files from your dataset:
```
Dataset/ravdess_by_emotion/happy/03-01-03-01-01-01-01.wav
Dataset/ravdess_by_emotion/angry/03-01-05-01-01-01-01.wav
Dataset/ravdess_by_emotion/sad/03-01-04-01-01-01-01.wav
```

### 2. Test with Live Recording

#### Recording Method:
1. Navigate to the **Predict** section
2. Click on **Record Live Audio** card
3. Click **Start Recording** (allow microphone access)
4. Speak with emotion for 3-5 seconds
5. Click **Stop Recording**
6. Listen to playback (optional)
7. Click **Analyze Recording**
8. View results

#### What to Say:
Try expressing different emotions:
- Happy: "I'm so excited! This is amazing!"
- Sad: "I feel so disappointed and down..."
- Angry: "This is completely unacceptable!"
- Fearful: "I'm really worried about this..."
- Calm: "Everything is peaceful and relaxed."
- Surprised: "Wow! I can't believe this!"

### 3. Understanding Results

#### Result Display:
- **Emotion Name** - The predicted emotion
- **Emotion Icon** - Visual representation
- **Confidence Level** - Percentage (0-100%)
  - 🟢 **High (75-100%)** - Very confident
  - 🟡 **Medium (50-75%)** - Moderately confident
  - 🔴 **Low (0-50%)** - Less confident

#### Probability Breakdown:
Click "View All Emotion Probabilities" to see:
- All 8 emotions ranked by probability
- Individual confidence bars
- Percentage values

---

## 🐛 Troubleshooting

### Issue: "Model not loaded" error

**Solution:**
1. Check if model files exist:
   ```bash
   dir Predict\SER_model.h5
   dir Predict\label_encoder.pkl
   ```
2. If missing, train the model first:
   ```bash
   python "random search tuning/Random_Search_Tuning.py"
   python savemodel.py
   ```

### Issue: Port 5000 already in use

**Solution:**
1. Find and kill the process using port 5000:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -i :5000
   kill -9 <PID>
   ```
2. Or change the port in `app.py`:
   ```python
   app.run(host='0.0.0.0', port=8000)  # Use different port
   ```

### Issue: Microphone not working

**Causes & Solutions:**
1. **Browser permissions** - Allow microphone access when prompted
2. **HTTPS required** - Microphone works on localhost or HTTPS only
3. **Browser compatibility** - Use Chrome, Firefox, or Edge
4. **Hardware** - Check if microphone is connected and working

### Issue: Cannot connect to server

**Solution:**
1. Ensure server is running (check terminal)
2. Try accessing: http://127.0.0.1:5000
3. Check firewall settings
4. Verify `API_BASE_URL` in `frontend/script.js`

### Issue: "Could not connect to the server" in browser

**Solution:**
1. Check if Flask server is running in terminal
2. Look for this message: `* Running on http://127.0.0.1:5000`
3. If not running, check for Python errors in terminal
4. Common issues:
   - Missing dependencies: `pip install -r requirements.txt`
   - Wrong Python version: Use Python 3.8+
   - Model files missing: Train model first

### Issue: Slow predictions

**Causes:**
- Large audio files (use shorter clips)
- CPU-only inference (TensorFlow on CPU is slower)
- First prediction is always slower (model initialization)

**Solution:**
- Use audio clips under 5 seconds
- Consider GPU acceleration if available
- Second+ predictions will be faster

### Issue: Theme toggle not working

**Solution:**
- Clear browser cache
- Check browser console for JavaScript errors
- Ensure `script.js` is loaded properly

---

## 🏗️ Architecture

### Frontend Structure
```
frontend/
├── index.html          # Main HTML structure
│   ├── Hero Section    # Landing with emotion cards
│   ├── About Section   # How it works
│   ├── Predict Section # Upload & Record
│   └── Contact Section # Get in touch
│
├── styles.css          # All styling
│   ├── CSS Variables   # Theme colors
│   ├── Components      # Buttons, cards, etc.
│   ├── Animations      # Scroll & hover effects
│   └── Responsive      # Mobile breakpoints
│
└── script.js           # JavaScript functionality
    ├── Navigation      # Menu & scroll
    ├── Theme Toggle    # Dark/Light mode
    ├── File Upload     # Drag & drop
    ├── Audio Recording # MediaRecorder API
    ├── Visualization   # Canvas frequency bars
    └── API Calls       # Fetch predictions
```

### Backend Structure
```
app.py                  # Flask server
├── /                   # Serve frontend
├── /predict            # Main prediction endpoint
├── /health             # Health check
└── /emotions           # List emotions
```

### Data Flow
```
User Action (Upload/Record)
    ↓
JavaScript (script.js)
    ↓
Fetch API Request
    ↓
Flask Backend (app.py)
    ↓
MFCC Feature Extraction (librosa)
    ↓
Model Prediction (TensorFlow)
    ↓
JSON Response
    ↓
Display Results (DOM manipulation)
```

---

## 🎨 Customization

### Change Accent Color
Edit `frontend/styles.css`:
```css
:root {
    --primary: #c4f82a;  /* Change this to your preferred color */
}
```

### Change Backend URL
Edit `frontend/script.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000';  // Update this
```

### Add Custom Emotions
1. Retrain model with new emotions
2. Update `EMOTION_ICONS` in `script.js`
3. Add emotion cards in `index.html`

---

## 📊 Performance Metrics

### Model Performance
- **Test Accuracy:** 78.12%
- **Macro F1-Score:** 0.771
- **Best Performing:** Calm (86.1%), Surprised (85.7%)
- **Most Challenging:** Happy (64.0%), Neutral (66.7%)

### Response Times
- Audio upload: ~1-3 seconds
- Live recording: ~1-3 seconds (after recording stops)
- File size limit: 16MB

---

## 🌐 Browser Compatibility

| Browser | Upload | Recording | Visualization |
|---------|--------|-----------|---------------|
| Chrome  | ✅     | ✅        | ✅            |
| Firefox | ✅     | ✅        | ✅            |
| Edge    | ✅     | ✅        | ✅            |
| Safari  | ✅     | ✅        | ⚠️            |
| Opera   | ✅     | ✅        | ✅            |

⚠️ = May require additional permissions or have limited support

---

## 📝 API Documentation

### POST /predict
**Description:** Analyze audio file and predict emotion

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -F "audio=@sample.wav"
```

**Response:**
```json
{
  "emotion": "Happy",
  "confidence": 0.8523,
  "probabilities": {
    "Happy": 0.8523,
    "Surprised": 0.0821,
    "Calm": 0.0412,
    "Neutral": 0.0123,
    "Sad": 0.0089,
    "Angry": 0.0021,
    "Fearful": 0.0009,
    "Disgust": 0.0002
  }
}
```

### GET /health
**Description:** Check server and model status

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "emotions": ["Angry", "Calm", "Disgust", "Fearful", "Happy", "Neutral", "Sad", "Surprised"]
}
```

---

## 🔐 Security Notes

1. **File Upload Validation**
   - Only `.wav` files accepted
   - 16MB file size limit
   - Secure filename sanitization

2. **CORS Enabled**
   - Allow frontend-backend communication
   - Configured for development (localhost)

3. **Temporary File Handling**
   - Uploaded files deleted after processing
   - No persistent storage of user data

---

## 📱 Mobile Experience

### Responsive Design
- Hamburger menu on mobile
- Stacked layouts for small screens
- Touch-friendly buttons
- Optimized font sizes

### Mobile Recording
- Works on iOS Safari and Android Chrome
- Requires HTTPS in production
- May need user gesture to start

---

## 🚀 Deployment to Production

### Step 1: Update Flask Configuration
```python
app.run(
    host='0.0.0.0',
    port=5000,
    debug=False  # Important!
)
```

### Step 2: Use Production Server
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Step 3: Setup HTTPS (Required for microphone)
- Use Nginx or Apache as reverse proxy
- Obtain SSL certificate (Let's Encrypt)
- Configure proxy pass to Flask

### Step 4: Update Frontend URL
Edit `frontend/script.js`:
```javascript
const API_BASE_URL = 'https://yourdomain.com';
```

---

## 🎓 Learning Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **Web Audio API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **MediaRecorder API:** https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
- **CSS Grid:** https://css-tricks.com/snippets/css/complete-guide-grid/
- **Fetch API:** https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

## 📧 Support & Contact

For issues, questions, or contributions:
1. Check this documentation first
2. Review the main project README
3. Check the troubleshooting section
4. Contact the development team

---

## 🎉 Success Checklist

Before considering setup complete, verify:

- [ ] Server starts without errors
- [ ] Frontend loads at http://localhost:5000
- [ ] Health check returns "healthy" status
- [ ] Can upload and analyze a test audio file
- [ ] Can record and analyze live audio
- [ ] Results display correctly with all information
- [ ] Theme toggle works (dark/light mode)
- [ ] Mobile responsive layout works
- [ ] All 8 emotions are recognized

---

**🎤 Enjoy using SpeechSense! Express yourself, and let AI understand your emotions! 🎵**

