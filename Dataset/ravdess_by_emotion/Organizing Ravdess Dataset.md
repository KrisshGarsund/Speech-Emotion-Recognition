import os
import shutil

# Path to your RAVDESS dataset
base_dir = r"C:\Users\PC1\OneDrive\Documents\EDAI (Sem-III)\Speech-Emotion-Recognition\datasets\ravdess\audio_speech_actors_01-24"

# Output directory (where files will be organized by emotion)
output_dir = os.path.join(os.path.dirname(base_dir), "ravdess_by_emotion")
os.makedirs(output_dir, exist_ok=True)

# Mapping from emotion number (3rd number in filename) to labels
emotion_map = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised"
}

# Loop through Actor folders
for actor in os.listdir(base_dir):
    actor_path = os.path.join(base_dir, actor)
    if not os.path.isdir(actor_path):
        continue
    
    # Loop through each file in Actor folder
    for file in os.listdir(actor_path):
        if not file.endswith(".wav"):
            continue
        
        # Extract emotion code from filename
        parts = file.split("-")
        emotion_code = parts[2]  # e.g., "05" → angry
        emotion = emotion_map.get(emotion_code, "unknown")
        
        # Create emotion folder if not exists
        emotion_dir = os.path.join(output_dir, emotion)
        os.makedirs(emotion_dir, exist_ok=True)
        
        # Copy file to emotion folder
        src_path = os.path.join(actor_path, file)
        dest_path = os.path.join(emotion_dir, file)
        
        if not os.path.exists(dest_path):  # avoid SameFileError
            shutil.copy(src_path, dest_path)

print("RAVDESS organized successfully into:", output_dir)     # You will see this message in terminal once the process is done.
