# Debugging for CNN+LSTM_using_MFCC.py
# Check the structure of the pickle file for correct key names and shapes
import pickle

data = None
with open("MFCC/features_ravdess.pkl", "rb") as f:
    data = pickle.load(f)

print("Type of loaded data:", type(data))
if isinstance(data, dict):
    print("Keys:", data.keys())
    for k, v in data.items():
        print(f"Key: {k}, Type: {type(v)}")
        if hasattr(v, 'shape'):
            print(f"  Shape: {v.shape}")
        elif isinstance(v, list):
            print(f"  List length: {len(v)}")
            if len(v) > 0:
                print(f"  First element type: {type(v[0])}")
else:
    print("Loaded data:", data)
