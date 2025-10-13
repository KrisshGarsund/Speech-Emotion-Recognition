# SpeechSense Frontend

Modern, professional Speech Emotion Recognition web application built with pure HTML, CSS, and JavaScript.

## 🎨 Design Features

- **Dark Mode by Default** with light mode toggle
- **Glass-morphism** surfaces with subtle neon effects
- **Animated Background** with cursor-following glow
- **3D Hover Effects** on emotion cards
- **Real-time Audio Visualization** with canvas API
- **Smooth Animations** and scroll-triggered effects
- **Fully Responsive** design for all devices

## 🚀 Quick Start

### Prerequisites

1. Python 3.8 or higher
2. Required packages (install from main `requirements.txt`)

### Running the Application

#### Option 1: Using Python directly

```bash
# From the project root directory
python app.py
```

#### Option 2: Using the batch file (Windows)

```bash
# From the project root directory
run_server.bat
```

#### Option 3: Using the shell script (Linux/Mac)

```bash
# From the project root directory
chmod +x run_server.sh
./run_server.sh
```

### Access the Application

Once the server is running, open your browser and go to:

```
http://localhost:5000
```

## 📁 File Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # All styling and animations
├── script.js           # JavaScript functionality
└── README.md           # This file

Root Files:
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies
└── run_server.bat      # Quick start script (Windows)
```

## 🎯 Features

### 1. Upload Audio
- Drag & drop interface
- Click to browse files
- Supports .wav audio files
- File validation and preview

### 2. Record Live Audio
- Real-time frequency visualization
- Start/Stop recording controls
- Audio playback before analysis
- WebRTC-based recording

### 3. Prediction Results
- Large emotion icon display
- Confidence meter with color coding
- Expandable probability breakdown
- All 8 emotions with percentages

### 4. Supported Emotions

The model recognizes 8 emotions:
- 😊 Happy
- 😢 Sad
- 😠 Angry
- 😳 Fearful
- 🍃 Calm
- 😲 Surprised
- 😵 Disgust
- 😐 Neutral

## 🎨 Color Scheme

### Dark Mode (Default)
- Background: `#0B0C10`
- Surface: `rgba(22, 28, 41, 0.5)`
- Text: `#E6F1FF`
- Accent: `#c4f82a` (Lime Green)

### Light Mode
- Background: `#F5F7FA`
- Surface: `#FFFFFF`
- Text: `#0B0C10`
- Accent: `#c4f82a` (Lime Green)

## 🔧 Configuration

### Backend URL

By default, the frontend connects to `http://localhost:5000`. To change this:

1. Open `script.js`
2. Find the line: `const API_BASE_URL = 'http://localhost:5000';`
3. Update it to your backend URL

### Model Files

The backend expects these files:
- `Predict/SER_model.h5` - Trained emotion recognition model
- `Predict/label_encoder.pkl` - Label encoder for emotions

## 🌐 Browser Support

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

**Note:** Audio recording requires HTTPS in production or localhost for development.

## 📱 Responsive Breakpoints

- Desktop: 1200px+
- Tablet: 768px - 992px
- Mobile: < 768px
- Small Mobile: < 480px

## 🎭 Animations

### Scroll Animations
- Fade in + slide up on scroll
- Applied to section titles and cards
- Uses Intersection Observer API

### Hover Effects
- 3D transformations on emotion cards
- Button lift effects
- Smooth color transitions

### Theme Transitions
- All color properties animate smoothly
- 300ms ease timing function

## 🔍 API Endpoints

### POST /predict
Upload audio file for emotion prediction

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: audio file (key: 'audio')

**Response:**
```json
{
  "emotion": "Happy",
  "confidence": 0.85,
  "probabilities": {
    "Happy": 0.85,
    "Surprised": 0.08,
    "Calm": 0.04,
    "Neutral": 0.02,
    "Sad": 0.01,
    "Angry": 0.00,
    "Fearful": 0.00,
    "Disgust": 0.00
  }
}
```

### GET /health
Check server health and model status

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "emotions": ["Angry", "Calm", "Disgust", "Fearful", "Happy", "Neutral", "Sad", "Surprised"]
}
```

### GET /emotions
Get list of supported emotions

**Response:**
```json
{
  "emotions": ["Angry", "Calm", "Disgust", "Fearful", "Happy", "Neutral", "Sad", "Surprised"],
  "count": 8
}
```

## 🐛 Troubleshooting

### Model not loading
- Check if `Predict/SER_model.h5` exists
- Check if `Predict/label_encoder.pkl` exists
- Verify file paths in `app.py`

### Cannot connect to server
- Ensure Flask server is running
- Check if port 5000 is available
- Verify `API_BASE_URL` in `script.js`

### Microphone not working
- Grant microphone permissions in browser
- Use HTTPS or localhost
- Check browser console for errors

### CORS errors
- Flask-CORS is enabled by default
- Check browser console for specific errors
- Ensure backend allows your frontend origin

## 🚀 Deployment

### Development
```bash
python app.py
```
Server runs with debug mode on port 5000.

### Production

1. **Update Flask settings in app.py:**
```python
app.run(
    host='0.0.0.0',
    port=5000,
    debug=False  # Set to False in production
)
```

2. **Use a production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **For HTTPS (required for microphone in production):**
- Use a reverse proxy (Nginx, Apache)
- Obtain SSL certificate (Let's Encrypt)
- Configure proxy to forward to Flask

## 📝 Customization

### Change Colors
Edit CSS custom properties in `styles.css`:
```css
:root {
    --primary: #c4f82a;  /* Your accent color */
    /* ... other variables ... */
}
```

### Add New Emotions
1. Update model to support new emotions
2. Add icon mapping in `script.js`:
```javascript
const EMOTION_ICONS = {
    'YourEmotion': 'fa-your-icon',
    // ...
};
```

### Modify Layout
Edit grid layouts in `styles.css`:
```css
.hero-emotions {
    grid-template-columns: repeat(3, 1fr);  /* Change column count */
}
```

## 📄 License

Part of the Speech-Emotion-Recognition project. See main project README for license information.

## 🙏 Acknowledgments

- **Font:** Poppins by Google Fonts
- **Icons:** Font Awesome 6.4.2
- **Design Inspiration:** Modern glass-morphism and neon aesthetics

## 📧 Support

For issues or questions, refer to the main project documentation or contact the development team.

---

**Built with ❤️ for SpeechSense Speech Emotion Recognition**

