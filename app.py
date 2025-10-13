"""
SpeechSense - Speech Emotion Recognition Backend
Flask API for serving the frontend and handling emotion predictions
"""

import os
import numpy as np
import librosa
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pickle
from tensorflow.keras.models import load_model
import tempfile
import traceback

# ========================================
# Flask App Configuration
# ========================================
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
# WAV is primary format (converted on client-side for recordings)
# Other formats supported if ffmpeg is available
ALLOWED_EXTENSIONS = {'wav', 'webm', 'ogg', 'mp3', 'mp4', 'm4a', 'flac'}

# ========================================
# Model Configuration
# ========================================
MODEL_PATH = 'Predict/SER_model.h5'
LABEL_ENCODER_PATH = 'Predict/label_encoder.pkl'

# Global variables for model
model = None
label_encoder = None
emotions = None

# ========================================
# Model Loading
# ========================================
def load_emotion_model():
    """Load the trained emotion recognition model and label encoder"""
    global model, label_encoder, emotions
    
    try:
        print("Loading emotion recognition model...")
        model = load_model(MODEL_PATH)
        print(f"✓ Model loaded from: {MODEL_PATH}")
        
        print("Loading label encoder...")
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            label_encoder = pickle.load(f)
        
        emotions = label_encoder.classes_
        print(f"✓ Label encoder loaded. Emotions: {list(emotions)}")
        print("✓ Model initialization complete!")
        return True
        
    except FileNotFoundError as e:
        print(f"✗ Error: Model files not found - {e}")
        print(f"  Please ensure these files exist:")
        print(f"  - {MODEL_PATH}")
        print(f"  - {LABEL_ENCODER_PATH}")
        return False
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        traceback.print_exc()
        return False

# ========================================
# Audio Processing
# ========================================
def extract_mfcc_features(audio_path, max_pad_len=174):
    """
    Extract MFCC features from audio file (same as training)
    
    Args:
        audio_path: Path to the audio file
        max_pad_len: Maximum length for padding/truncation (default: 174)
    
    Returns:
        mfcc_features: Processed MFCC features ready for model input
    """
    try:
        print(f"Loading audio file: {audio_path}")
        
        # Load audio file - librosa can handle various formats
        # sr=None uses the native sampling rate, then we resample if needed
        audio, sample_rate = librosa.load(audio_path, res_type='kaiser_fast', sr=None)
        
        print(f"Audio loaded: duration={len(audio)/sample_rate:.2f}s, sr={sample_rate}Hz")
        
        # Resample to a standard rate if necessary (22050 Hz is librosa's default)
        if sample_rate != 22050:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=22050)
            sample_rate = 22050
            print(f"Resampled to {sample_rate}Hz")
        
        # Extract 40 MFCC coefficients (same as training)
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        
        print(f"MFCC shape before padding: {mfccs.shape}")
        
        # Pad or truncate to fixed length (same preprocessing as training)
        pad_width = max_pad_len - mfccs.shape[1]
        if pad_width > 0:
            # Pad with zeros if too short
            mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            # Truncate if too long
            mfccs = mfccs[:, :max_pad_len]
        
        print(f"MFCC shape after padding: {mfccs.shape}")
        
        return mfccs
        
    except Exception as e:
        print(f"Error processing audio file: {e}")
        traceback.print_exc()
        raise

def predict_emotion_from_audio(audio_path):
    """
    Predict emotion from audio file
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        dict: Prediction results with emotion, confidence, and probabilities
    """
    if model is None or label_encoder is None:
        raise Exception("Model not loaded")
    
    # Extract features
    mfcc_features = extract_mfcc_features(audio_path)
    
    # Reshape for model input: (1, time_steps, features)
    # Model expects (batch_size, 174, 40)
    features = np.transpose(mfcc_features, (1, 0))  # (174, 40)
    features = np.expand_dims(features, axis=0)      # (1, 174, 40)
    
    # Make prediction
    predictions = model.predict(features, verbose=0)
    
    # Get predicted class and confidence
    predicted_class_idx = np.argmax(predictions, axis=1)[0]
    confidence = float(np.max(predictions))
    
    # Convert to emotion label
    predicted_emotion = label_encoder.inverse_transform([predicted_class_idx])[0]
    
    # Create probability dict for all emotions
    probabilities = {}
    for i, emotion in enumerate(emotions):
        probabilities[emotion] = float(predictions[0][i])
    
    return {
        'emotion': predicted_emotion,
        'confidence': confidence,
        'probabilities': probabilities
    }

# ========================================
# Utility Functions
# ========================================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========================================
# Routes
# ========================================

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'emotions': list(emotions) if emotions is not None else []
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Expects:
        - audio file in request.files['audio']
    
    Returns:
        JSON with prediction results
    """
    try:
        # Check if model is loaded
        if model is None or label_encoder is None:
            return jsonify({
                'error': 'Model not loaded',
                'message': 'The emotion recognition model is not available'
            }), 503
        
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({
                'error': 'No audio file',
                'message': 'Please provide an audio file'
            }), 400
        
        file = request.files['audio']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Supported formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Predict emotion
            print(f"Processing file: {filename} (size: {os.path.getsize(temp_path)} bytes)")
            result = predict_emotion_from_audio(temp_path)
            
            print(f"✓ Prediction successful: {result['emotion']} (confidence: {result['confidence']:.3f})")
            
            return jsonify(result)
            
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Prediction failed: {error_msg}")
            
            # Provide helpful error messages
            if 'NoBackendError' in error_msg or 'audioread' in error_msg:
                return jsonify({
                    'error': 'Audio format not supported',
                    'message': 'Please install ffmpeg to support this audio format. For webm/ogg files, run: pip install pydub && install ffmpeg',
                    'details': error_msg
                }), 500
            else:
                return jsonify({
                    'error': 'Processing failed',
                    'message': f'Could not process audio file: {error_msg}',
                    'details': 'Check server logs for more information'
                }), 500
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Cleaned up temporary file: {filename}")
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500

@app.route('/emotions')
def get_emotions():
    """Get list of supported emotions"""
    if emotions is None:
        return jsonify({
            'error': 'Model not loaded'
        }), 503
    
    return jsonify({
        'emotions': list(emotions),
        'count': len(emotions)
    })

# ========================================
# Error Handlers
# ========================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'message': 'File size exceeds 16MB limit'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# ========================================
# Main Execution
# ========================================

if __name__ == '__main__':
    print("="*60)
    print("SpeechSense - Speech Emotion Recognition Server")
    print("="*60)
    
    # Load model on startup
    model_loaded = load_emotion_model()
    
    if not model_loaded:
        print("\n⚠️  WARNING: Model could not be loaded!")
        print("The server will start but predictions will not work.")
        print("Please check the model files and restart the server.\n")
    
    print("\nStarting Flask server...")
    print("Frontend URL: http://localhost:5000")
    print("API Endpoint: http://localhost:5000/predict")
    print("Health Check: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

