import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

# ------------------------------
# Load Features
# ------------------------------
with open("MFCC/features_ravdess.pkl", "rb") as f:
    df = pickle.load(f)

print("Columns in DataFrame:", df.columns)
print("Number of samples:", len(df))

# ------------------------------
# Convert features and labels
# ------------------------------
X = np.array(df['features'].tolist())  # shape: (num_samples, 40, 174)
y = np.array(df['label'].tolist())

print("Original X shape:", X.shape)

# ------------------------------
# Reshape for MLP (2D required)
# ------------------------------
X = X.reshape(X.shape[0], -1)  # flatten to (num_samples, 6960)
print("Reshaped X shape for MLP:", X.shape)

# ------------------------------
# Encode Labels
# ------------------------------
le = LabelEncoder()
y = le.fit_transform(y)

# ------------------------------
# Train-Test Split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ------------------------------
# Standardize Features
# ------------------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ------------------------------
# Improved MLP Classifier
# ------------------------------
mlp = MLPClassifier(
    hidden_layer_sizes=(512, 256, 128),  # Deeper network
    activation="relu",
    solver="adam",
    batch_size=32,
    max_iter=500,                        # More iterations
    early_stopping=True,                 # Prevent overfitting
    validation_fraction=0.1,             # Use 10% for validation
    n_iter_no_change=20,                # Patience for early stopping
    learning_rate_init=0.001,           # Learning rate
    alpha=0.0001,                       # L2 regularization
    random_state=42,                    # Reproducible results
    verbose=True
)

mlp.fit(X_train, y_train)

# ------------------------------
# Evaluate
# ------------------------------
y_pred = mlp.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nImproved Baseline MLP Test Accuracy: {acc * 100:.2f}%")