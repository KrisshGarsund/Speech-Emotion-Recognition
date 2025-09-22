import pickle
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Load your MFCC features (contains labels)
with open(r"H:\speech emotion\Speech-Emotion-Recognition\MFCC\features_ravdess.pkl", "rb") as f:
    data = pickle.load(f)

# Recreate the same label encoder used in training
y = np.array(data['label'])
le = LabelEncoder()
le.fit(y)

print("Emotion classes:", le.classes_)

# Save the label encoder
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("Label encoder saved as 'label_encoder.pkl'")