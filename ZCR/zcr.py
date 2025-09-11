import os
import librosa
import numpy as np

# Paths
base_dir = r"H:\speech emotion\Speech-Emotion-Recognition\Dataset\ravdess_by_emotion"   # original dataset
save_dir = r"H:\speech emotion\Speech-Emotion-Recognition\ZCR"         # where to save ZCR features

# Create save directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)

# Process each emotion folder
for emotion in os.listdir(base_dir):
    emotion_path = os.path.join(base_dir, emotion)
    save_emotion_path = os.path.join(save_dir, emotion)
    os.makedirs(save_emotion_path, exist_ok=True)

    print(f"\nProcessing ZCR for {emotion}...")
    files = [f for f in os.listdir(emotion_path) if f.endswith('.wav')]

    for file in files:
        file_path = os.path.join(emotion_path, file)
        y, sr = librosa.load(file_path, sr=None)

        # Extract ZCR
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=2048, hop_length=512)
        
        # Save as .npy file
        save_path = os.path.join(save_emotion_path, file.replace('.wav', '.npy'))
        np.save(save_path, zcr)

print("\nAll ZCR files processed and saved!")
