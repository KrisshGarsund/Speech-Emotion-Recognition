from flask import Flask, request, jsonify, render_template
import os
import numpy as np
import tensorflow as tf
import librosa
import pickle
import tempfile

app = Flask(__name__)

# Load the trained model and label encoder
MODEL_PATH = "SER_model.h5"
LABEL_ENCODER_PATH = "label_encoder.pkl"

model = tf.keras.models.load_model(MODEL_PATH)

with open(LABEL_ENCODER_PATH, "rb") as f:
    label_encoder = pickle.load(f)

def extract_features(file_path):
    y, sr = librosa.load(file_path, res_type='kaiser_fast', mono=True)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    max_pad_len = 174
    if mfcc.shape[1] < max_pad_len:
        pad_width = max_pad_len - mfcc.shape[1]
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :max_pad_len]
    mfcc = mfcc.T
    mfcc = mfcc[..., np.newaxis]
    return mfcc

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict_multiple_files", methods=["POST"])
def predict_multiple_files():
    results = []

    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")

    for file in files:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            features = extract_features(tmp_path)
            features = np.expand_dims(features, axis=0)
            prediction = model.predict(features)
            pred_index = np.argmax(prediction)
            emotion = label_encoder.inverse_transform([pred_index])[0]
            confidence = float(np.max(prediction))

            results.append({
                "file": file.filename,
                "emotion": emotion,
                "confidence": confidence
            })

            os.remove(tmp_path)

        except Exception as e:
            results.append({
                "file": file.filename,
                "error": str(e)
            })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
