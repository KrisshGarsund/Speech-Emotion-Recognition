from audio_predictor import SpeechEmotionPredictor

# Initialize with your H5 model
predictor = SpeechEmotionPredictor(
    "SER_model.h5",
    "label_encoder.pkl"
)

# Predict on any .wav file
emotion, confidence = predictor.predict_emotion(r"C:\Users\harsh\Downloads\CREMA-D-Segregated\CREMA-D-Segregated\Fear\1082_IEO_FEA_MD.wav")
print(f"Predicted emotion: {emotion} (confidence: {confidence:.2%})")