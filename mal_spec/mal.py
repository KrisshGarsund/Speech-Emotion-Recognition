import os
import librosa
import numpy as np
from tqdm import tqdm
import time

# Paths
base_dir = r"H:\speech emotion\Speech-Emotion-Recognition\Dataset\ravdess_by_emotion"   # original dataset
save_dir = r"H:\speech emotion\Speech-Emotion-Recognition\mal_spec"     # where to save features

# Create save directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)

# Process each emotion folder
for emotion in os.listdir(base_dir):
    emotion_path = os.path.join(base_dir, emotion)
    save_emotion_path = os.path.join(save_dir, emotion)
    os.makedirs(save_emotion_path, exist_ok=True)

    print(f"\nProcessing {emotion}...")

    files = [f for f in os.listdir(emotion_path) if f.endswith('.wav')]
    start_time = time.time()

    # Use tqdm to show progress bar
    for file in tqdm(files, desc=f"Files in {emotion}", unit="file"):
        file_path = os.path.join(emotion_path, file)
        y, sr = librosa.load(file_path, sr=None)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # Save as .npy
        save_path = os.path.join(save_emotion_path, file.replace('.wav', '.npy'))
        np.save(save_path, mel_spec_db)

    end_time = time.time()
    print(f"Completed {emotion} in {end_time - start_time:.2f} seconds.")

print("\nAll files processed and saved!")
