# Debugging for Baseline_Train_using_MLP.py
# 1. The error indicates that X is a string, not a numpy array. This means the pickle file does not contain (X, y) as expected, or the structure is different.
# 2. Let's inspect the type and content of what is loaded from the pickle file before proceeding.

import pickle

with open("MFCC/features_ravdess.pkl", "rb") as f:
    data = pickle.load(f)
    print("Type of loaded data:", type(data))
    if isinstance(data, tuple):
        print("Tuple length:", len(data))
        for i, item in enumerate(data):
            print(f"Type of item {i}:", type(item))
            if hasattr(item, 'shape'):
                print(f"Shape of item {i}:", item.shape)
    else:
        print("Loaded data:", data)
