import pickle
import numpy as np

with open("MFCC/features_ravdess.pkl", "rb") as f:
    data = pickle.load(f)

X = np.array(data['features'].tolist())
print("X shape:", X.shape)
if X.ndim == 3:
    print("Sample shape (should be [timesteps, n_mfcc]):", X[0].shape)
elif X.ndim == 2:
    print("Sample shape (likely 1D, needs reshape):", X[0].shape)
else:
    print("Unexpected feature shape!")
