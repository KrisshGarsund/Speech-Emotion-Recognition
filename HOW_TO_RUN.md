# 🚀 How to Run SpeechSense

## Option 1: Main Web Frontend (Recommended)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Flask Backend
```bash
cd "H:\speech emotion\Speech-Emotion-Recognition"
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

The modern SpeechSense frontend will load automatically!

---

## Option 2: Streamlit Dashboard

### 1. Ensure Backend is Running
Make sure Flask is running on port 5000 (see Option 1, step 2)

### 2. Start Streamlit
```bash
streamlit run Streamlit/aura_dashboard.py
```

### 3. Open in Browser
```
http://localhost:8501
```

### 4. Configure API (in Streamlit sidebar)
- Set Backend API to: `http://127.0.0.1:5000/predict`

---

## Features

### Main Frontend (localhost:5000)
- ✅ Upload audio files (.wav, .mp3, .webm, .ogg, .m4a)
- ✅ Record live audio with microphone
- ✅ Real-time audio visualization
- ✅ Instant emotion predictions
- ✅ Confidence scores & probability breakdown
- ✅ Download results (PDF, CSV, Image)
- ✅ Dark/Light theme toggle
- ✅ Mobile responsive

### Streamlit Dashboard (localhost:8501)
- ✅ Beautiful gauge charts for confidence
- ✅ Interactive probability bars
- ✅ Waveform visualization
- ✅ Session history tracking
- ✅ CSV export
- ✅ Branded SpeechSense design

---

## Troubleshooting

### Frontend Not Loading
1. Make sure you're running: `python app.py` (in project root)
2. NOT `python Backend_connection/app.py`
3. Navigate to: `http://localhost:5000`
4. Force refresh: Ctrl+F5

### Port Already in Use
```bash
# Windows - Find process on port 5000
netstat -ano | findstr :5000
# Kill process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

### Model Not Loading
Ensure these files exist:
- `Predict/SER_model.h5`
- `Predict/label_encoder.pkl`

---

## Quick Test

1. **Start Backend**: `python app.py`
2. **Open**: http://localhost:5000
3. **Upload**: Any .wav file from `Dataset/ravdess_by_emotion/happy/`
4. **Click**: "Analyze Emotion"
5. **View**: Prediction results with confidence!

---

## API Endpoints

- `GET /` - Main frontend
- `POST /predict` - Emotion prediction (multipart/form-data with 'audio' file)
- `GET /health` - Health check
- `GET /emotions` - List of supported emotions

Enjoy your SpeechSense Speech Emotion Recognition system! 🎤

