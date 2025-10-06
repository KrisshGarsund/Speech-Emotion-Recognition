import streamlit as st
import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os

# Flask backend URL
FLASK_API_URL = "http://127.0.0.1:5000/predict"


st.set_page_config(page_title="Audio Emotion Recognition", page_icon="🎤", layout="centered")
st.title("Speech Emotion Recognition Dashboard")

# Option to choose input type
option = st.radio("Select Input Type:", ["Upload Audio File", "Record with Microphone"])

def send_to_backend(file_path):
    """Send file to Flask API and return prediction"""
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(FLASK_API_URL, files=files, headers={"Accept": "application/json"})
    try:
        result = response.json()
        # Convert confidence to percentage if present
        if "confidence" in result:
            result["confidence"] = f'{float(result["confidence"]):.2f}%'
        return result
    except Exception:
        return {"error": "Backend did not return valid JSON. Status code: {}. Response: {}".format(response.status_code, response.text)}

if option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload an audio file (.wav)", type=["wav"])
    if uploaded_file is not None:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        st.audio(temp_path, format="audio/wav")

        if st.button("Predict"):
            result = send_to_backend(temp_path)
            if "prediction" in result:
                st.success(f"Prediction: {result['prediction']} (Confidence: {result.get('confidence', 'N/A')})")

                # Show detailed analysis if available
                analysis = result.get("detailed_analysis", {})
                if analysis:
                    st.markdown(f"**Analysis Summary:** {analysis.get('analysis_text', '')}")
                    st.markdown("**All Emotion Probabilities:**")
                    for emo in analysis.get("all_emotions", []):
                        st.write(f"{emo['emotion'].title()}: {emo['percentage']}%")
                    if analysis.get("recommendations"):
                        st.markdown("**Recommendations:**")
                        for rec in analysis["recommendations"]:
                            st.write(f"- {rec}")
            else:
                st.error("Prediction failed")

elif option == "Record with Microphone":
    duration = st.slider("Recording Duration (seconds)", 2, 10, 5)

    if st.button("Start Recording "):
        st.info("Recording...")
        fs = 44100  # Sampling frequency
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        st.success("Recording completed ")

        # Convert to int16 for wav compatibility
        recording_int16 = (recording * 32767).astype(np.int16)

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wav.write(tmp_file.name, fs, recording_int16)
            temp_path = tmp_file.name

        st.audio(temp_path, format="audio/wav")

        if st.button("Predict"):
            result = send_to_backend(temp_path)
            if "prediction" in result:
                st.success(f"Prediction: {result['prediction']} (Confidence: {result.get('confidence', 'N/A')})")
                # Show detailed analysis if available
                analysis = result.get("detailed_analysis", {})
                if analysis:
                    st.markdown(f"**Analysis Summary:** {analysis.get('analysis_text', '')}")
                    st.markdown("**All Emotion Probabilities:**")
                    for emo in analysis.get("all_emotions", []):
                        st.write(f"{emo['emotion'].title()}: {emo['percentage']}%")
                    if analysis.get("recommendations"):
                        st.markdown("**Recommendations:**")
                        for rec in analysis["recommendations"]:
                            st.write(f"- {rec}")
            else:
                st.error("Prediction failed")
