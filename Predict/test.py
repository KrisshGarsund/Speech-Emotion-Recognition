<<<<<<< HEAD
from audio_predictor import SpeechEmotionPredictor

# Initialize with your H5 model
predictor = SpeechEmotionPredictor(
    "SER_model.h5",
    "label_encoder.pkl"
=======
from Predict.audio_predictor import SpeechEmotionPredictor

# Initialize with your H5 model
predictor = SpeechEmotionPredictor(
    "predict/SER_model.h5",
    "predict/label_encoder.pkl"
>>>>>>> e852bce6a109d5e82125faad1a34803a402c153b
)

# Predict on any .wav file
emotion, confidence = predictor.predict_emotion(r"C:\Users\harsh\Downloads\CREMA-D-Segregated\CREMA-D-Segregated\Fear\1082_IEO_FEA_MD.wav")
print(f"Predicted emotion: {emotion} (confidence: {confidence:.2%})")