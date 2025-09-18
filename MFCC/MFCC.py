import os
import librosa
import numpy as np
import pandas as pd

# Path to your RAVDESS dataset
DATASET_PATH = r"H:\speech emotion\Speech-Emotion-Recognition\Dataset\ravdess_by_emotion"

# Emotion code mapping (RAVDESS specific)
emotion_map = {
    "01": "Neutral",
    "02": "Calm",
    "03": "Happy",
    "04": "Sad",
    "05": "Angry",
    "06": "Fearful",
    "07": "Disgust",
    "08": "Surprised"
}

# Function to extract MFCCs (2D, not flattened)
def extract_features(file_path: str, max_pad_len: int = 174):
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast') 
        
        # Extract 40 MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        
        # Pad or truncate to fixed length
        pad_width = max_pad_len - mfccs.shape[1]
        if pad_width > 0:
            mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            mfccs = mfccs[:, :max_pad_len]
        
        return mfccs  # <-- keep 2D (40, time_steps)
    except Exception as e:
        print(f"Error extracting {file_path}: {e}")
        return None

# Collect features
features = []
for root, _, files in os.walk(DATASET_PATH):
    for file in files:
        if file.endswith(".wav"):
            file_path = os.path.join(root, file)
            
            # Extract emotion code
            parts = file.split("-")
            emotion_code = parts[2]
            emotion_label = emotion_map.get(emotion_code, "Unknown")
            
            # Extract MFCCs
            mfccs = extract_features(file_path)
            if mfccs is not None:
                features.append([mfccs, emotion_label])

# Convert to DataFrame
df = pd.DataFrame(features, columns=["features", "label"])

# Save as pickle
df.to_pickle("features_ravdess.pkl")
print(f"Feature extraction complete! Saved {len(df)} samples with shape {df['features'].iloc[0].shape}.")
