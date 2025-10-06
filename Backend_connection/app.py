# app.py
import soundfile as sf
from flask import Flask, request, render_template, jsonify, session, redirect, url_for, flash
import numpy as np
import pickle
import tensorflow as tf
import librosa
import os
import tempfile
import hashlib
import sqlite3
from datetime import datetime
from functools import wraps

# ---------------------------
# Load your model & label encoder
# ---------------------------
MODEL_PATH = "Predict/SER_model.h5"               
LABEL_ENCODER_PATH = "Predict/label_encoder.pkl"  

model = tf.keras.models.load_model(MODEL_PATH)

# Load label encoder 
try:
    with open(LABEL_ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
except Exception:
    label_encoder = None
    print("Warning: LabelEncoder not found. Please save it as 'label_encoder.pkl' during training.")


# Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = 'your-secret-key-change-this-in-production'

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication functions
def create_user(username, email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                      (username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute('SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?',
                  (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def get_detailed_analysis(predictions, label_encoder):
    """Generate detailed analysis of emotion predictions"""
    if label_encoder is None:
        return {"error": "Label encoder not available"}
    
    # Get all emotion labels
    emotion_labels = label_encoder.classes_
    
    # Create detailed analysis
    analysis = {
        "primary_emotion": emotion_labels[np.argmax(predictions)],
        "confidence": float(np.max(predictions)),
        "all_emotions": [],
        "analysis_text": "",
        "recommendations": []
    }
    
    # Get all emotion probabilities
    for i, emotion in enumerate(emotion_labels):
        prob = float(predictions[i])
        analysis["all_emotions"].append({
            "emotion": emotion,
            "probability": prob,
            "percentage": round(prob * 100, 1)
        })
    
    # Sort by probability
    analysis["all_emotions"].sort(key=lambda x: x["probability"], reverse=True)
    
    # Generate analysis text
    primary = analysis["primary_emotion"]
    confidence = analysis["confidence"]
    
    if confidence > 0.8:
        confidence_level = "very high"
    elif confidence > 0.6:
        confidence_level = "high"
    elif confidence > 0.4:
        confidence_level = "moderate"
    else:
        confidence_level = "low"
    
    analysis["analysis_text"] = f"The analysis shows a {confidence_level} confidence ({confidence:.1%}) that the primary emotion is {primary.title()}. "
    
    # secondary emotions if significant
    secondary_emotions = [e for e in analysis["all_emotions"][1:3] if e["percentage"] > 15]
    if secondary_emotions:
        analysis["analysis_text"] += f"Secondary emotions detected include {', '.join([e['emotion'].title() for e in secondary_emotions])}. "
    
    # specific analysis based on emotion
    emotion_analysis = {
        "happy": "The speech pattern indicates positive emotional state with likely elevated pitch and faster speech rate.",
        "sad": "The analysis suggests a melancholic emotional state, possibly with slower speech and lower pitch variations.",
        "angry": "The speech shows signs of frustration or anger, typically with increased intensity and sharp pitch changes.",
        "fearful": "The pattern indicates anxiety or fear, often characterized by rapid speech and higher pitch.",
        "surprised": "The speech shows sudden emotional response, likely with quick pitch changes and varied intensity.",
        "disgust": "The analysis suggests negative emotional response, possibly with distinct speech patterns indicating aversion.",
        "calm": "The speech pattern indicates a relaxed and composed emotional state with steady rhythm.",
        "neutral": "The speech shows minimal emotional variation, indicating a balanced or unemotional state."
    }
    
    if primary.lower() in emotion_analysis:
        analysis["analysis_text"] += emotion_analysis[primary.lower()]
    
    # recommendations
    if confidence < 0.5:
        analysis["recommendations"].append("Consider recording a longer audio sample for more accurate analysis.")
    if confidence < 0.7:
        analysis["recommendations"].append("Try speaking more clearly or in a quieter environment.")
    
    analysis["recommendations"].append("For best results, speak naturally and avoid background noise.")
    
    return analysis


# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template("login.html")
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields', 'error')
            return render_template("signup.html")
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template("signup.html")
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template("signup.html")
        
        if create_user(username, email, password):
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists', 'error')
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get('username'))

@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html", username=session.get('username'))

@app.route("/upload_predict", methods=["POST"])
@login_required
def upload_predict():
    try:
        if "file" not in request.files:
            return render_template("upload.html", error="No file uploaded", username=session.get('username'))

        file = request.files["file"]
        features = extract_features(file)
        features = np.expand_dims(features, axis=0)

        preds = model.predict(features)
        pred_class = np.argmax(preds, axis=1)[0]
        confidence = float(np.max(preds))

        if label_encoder:
            emotion = label_encoder.inverse_transform([pred_class])[0]
        else:
            emotion = str(pred_class)

        # detailed analysis
        detailed_analysis = get_detailed_analysis(preds[0], label_encoder)
        
        return render_template("upload.html", 
                             prediction=emotion, 
                             confidence=f"{confidence:.2f}", 
                             detailed_analysis=detailed_analysis,
                             username=session.get('username'))

    except Exception as e:
        return render_template("upload.html", error=f"Error: {str(e)}", username=session.get('username'))

@app.route("/record")
@login_required
def record_page():
    return render_template("record.html", username=session.get('username'))

@app.route("/record_predict", methods=["POST"])
@login_required
def record_predict():
    try:
        if "file" not in request.files:
            return render_template("record.html", error="No audio data received", username=session.get('username'))

        file = request.files["file"]
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Use librosa to load the audio file with proper format for WebM
            y, sr = librosa.load(temp_path, sr=None, mono=True, duration=3)  # Load as is
            
            # Convert to WAV format in memory
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_tmp:
                sf.write(wav_tmp.name, y, sr)
                wav_path = wav_tmp.name
            
            # Extract features from the WAV file
            features = extract_features_from_file(wav_path)
            
        except Exception as e:
            return render_template("record.html", 
                                 error=f"Error processing audio: {str(e)}", 
                                 username=session.get('username'))
        finally:
            # Clean up temporary files
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.unlink(wav_path)

        features = np.expand_dims(features, axis=0)
        preds = model.predict(features)
        pred_class = np.argmax(preds, axis=1)[0]
        confidence = float(np.max(preds))

        if label_encoder:
            emotion = label_encoder.inverse_transform([pred_class])[0]
        else:
            emotion = str(pred_class)

        # Get detailed analysis
        detailed_analysis = get_detailed_analysis(preds[0], label_encoder)
        
        return render_template("record.html", 
                             prediction=emotion, 
                             confidence=f"{confidence:.2f}", 
                             detailed_analysis=detailed_analysis,
                             username=session.get('username'))

    except Exception as e:
        return render_template("record.html", 
                             error=f"Error analyzing recording: {str(e)}", 
                             username=session.get('username'))

@app.route("/history")
@login_required
def history_page():
    return render_template("history.html", username=session.get('username'))

@app.route("/about")
@login_required
def about_page():
    return render_template("about.html", username=session.get('username'))

@app.route("/process_recorded_audio", methods=["POST"])
@login_required
def process_recorded_audio():
    import subprocess
    import tempfile
    try:
        if "file" not in request.files:
            return render_template("record.html", error="No audio data received", username=session.get('username'))

        file = request.files["file"]
        # If recorded file is webm, convert to wav
        if file.filename.endswith('.webm'):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_webm:
                file.save(tmp_webm.name)
                wav_path = tmp_webm.name.replace(".webm", ".wav")
                # Convert using ffmpeg
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", tmp_webm.name, wav_path
                    ], check=True)
                except Exception as ffmpeg_error:
                    return render_template("record.html", error=f"Error converting audio: {ffmpeg_error}", username=session.get('username'))
            features = extract_features_from_file(wav_path)
            # Clean up temp files
            try:
                os.remove(tmp_webm.name)
                os.remove(wav_path)
            except Exception:
                pass
        else:
            features = extract_features(file)
        features = np.expand_dims(features, axis=0)

        preds = model.predict(features)
        pred_class = np.argmax(preds, axis=1)[0]
        confidence = float(np.max(preds))

        if label_encoder:
            emotion = label_encoder.inverse_transform([pred_class])[0]
        else:
            emotion = str(pred_class)

        # Get detailed analysis
        detailed_analysis = get_detailed_analysis(preds[0], label_encoder)
        
        return render_template("record.html", 
                             prediction=emotion, 
                             confidence=f"{confidence:.2f}", 
                             detailed_analysis=detailed_analysis,
                             username=session.get('username'))

    except Exception as e:
        return render_template("record.html", error=f"Error: {str(e)}", username=session.get('username'))
    except Exception as e:
        return jsonify({"error": f"Error processing audio: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/home")
def home():
    """Landing page for non-authenticated users"""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            # If API call, return JSON error
            if request.headers.get('Accept') == 'application/json' or request.args.get('api') == '1':
                return jsonify({"error": "No file uploaded"}), 400
            return render_template("index.html", error="No file uploaded")

        file = request.files["file"]
        features = extract_features(file)
        features = np.expand_dims(features, axis=0)

        preds = model.predict(features)
        pred_class = np.argmax(preds, axis=1)[0]
        confidence = float(np.max(preds)) * 100

        if label_encoder:
            emotion = label_encoder.inverse_transform([pred_class])[0]
        else:
            emotion = str(pred_class)

        # Get detailed analysis
        detailed_analysis = get_detailed_analysis(preds[0], label_encoder)

        # If API call, return JSON
        if request.headers.get('Accept') == 'application/json' or request.args.get('api') == '1':
            return jsonify({
                "prediction": emotion,
                "confidence": round(confidence, 2),
                "detailed_analysis": detailed_analysis
            })

        return render_template("dashboard.html", 
                             prediction=emotion, 
                             confidence=f"{confidence:.2f}", 
                             detailed_analysis=detailed_analysis,
                             username=session.get('username'))

    except Exception as e:
        # If API call, return JSON error
        if request.headers.get('Accept') == 'application/json' or request.args.get('api') == '1':
            return jsonify({"error": f"Error: {str(e)}"}), 500
        return render_template("dashboard.html", error=f"Error: {str(e)}", username=session.get('username'))


def extract_features_from_file(file_path):
    """Extract features from a file path instead of file object"""
    y, sr = librosa.load(file_path, res_type='kaiser_fast', mono=True)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    
    max_pad_len = 174
    pad_width = max_pad_len - mfcc.shape[1]
    if pad_width > 0:
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :max_pad_len]
    
    mfcc = mfcc.T
    mfcc = mfcc[..., np.newaxis]
    return mfcc

# MFCC feature extractor consistent with training
def extract_features(audio_file):
    """
    Extract MFCC features matching training:
    - librosa.load with res_type='kaiser_fast'
    - n_mfcc=40
    - pad/trim to 174 frames (time steps)
    - return shape (174, 40, 1)

    audio_file: Werkzeug FileStorage object from Flask
    """
    tmp_path = None
    try:
        # Save uploaded file to a temporary path so librosa can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        # Load audio (mono), default sr, fast resampling
        y, sr = librosa.load(tmp_path, res_type='kaiser_fast', mono=True)

        # Compute MFCCs (40 coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)  # (40, T)

        # Ensure fixed time dimension of 174 frames
        max_pad_len = 174
        pad_width = max_pad_len - mfcc.shape[1]
        if pad_width > 0:
            mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            mfcc = mfcc[:, :max_pad_len]

        # Re-orient to (T, features) and add channel dim -> (174, 40, 1)
        mfcc = mfcc.T  # (174, 40)
        mfcc = mfcc[..., np.newaxis]
        return mfcc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass



# Run app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
