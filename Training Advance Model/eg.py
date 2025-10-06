import pickle

with open("MFCC/features_ravdess.pkl", "rb") as f:
    df = pickle.load(f)

print("Columns in DataFrame:", df.columns)
print("\nFirst row sample:\n", df.iloc[0])
