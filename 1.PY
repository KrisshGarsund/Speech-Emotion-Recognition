import numpy as np

# Load ZCR
zcr = np.load(r"H:\speech emotion\Speech-Emotion-Recognition\ZCR\happy\03-01-03-01-01-01-06.npy")

# Load Mel-Spectrogram
mel_spec = np.load(r"H:\speech emotion\Speech-Emotion-Recognition\mal_spec\happy\03-01-03-01-01-01-07.npy")

# Example: concatenate along a new axis
features = np.concatenate((mel_spec, zcr), axis=0)  # or another method depending on model input shape
