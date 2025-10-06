import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, BatchNormalization, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

# Load features
with open("MFCC/features_ravdess.pkl", "rb") as f:
    data = pickle.load(f)

X = np.array([np.array(f) for f in data['features']])  # (samples, 40, 174)
y = np.array(data['label'])

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)
num_classes = len(le.classes_)
y_cat = to_categorical(y_encoded, num_classes=num_classes)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_cat, test_size=0.2, random_state=42, stratify=y_encoded
)

# Reshape for Conv1D: (samples, time_steps, features)
X_train = np.transpose(X_train, (0, 2, 1))  # (samples, 174, 40)
X_test = np.transpose(X_test, (0, 2, 1))

# CNN + LSTM model (ACTUALLY with LSTM this time!)
model = Sequential()

# Conv layers for feature extraction
model.add(Conv1D(32, kernel_size=5, activation='relu', padding='same', input_shape=(174, 40)))
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.2))

model.add(Conv1D(64, kernel_size=5, activation='relu', padding='same'))
model.add(BatchNormalization())
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.2))

# LSTM layers (THIS is what was missing!)
model.add(Bidirectional(LSTM(64, return_sequences=True)))
model.add(Dropout(0.3))

model.add(Bidirectional(LSTM(32, return_sequences=False)))
model.add(Dropout(0.3))

# Dense layers
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.4))

# Final output
model.add(Dense(num_classes, activation='softmax'))

# Compile
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Early stopping to prevent overfitting
early_stop = EarlyStopping(patience=15, restore_best_weights=True, monitor='val_accuracy')

# Train
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=16,
    callbacks=[early_stop],
    verbose=1
)

# Evaluate
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Accuracy: {test_acc:.4f}")