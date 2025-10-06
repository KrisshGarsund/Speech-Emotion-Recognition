import pickle
import numpy as np
import pandas as pd
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv1D, MaxPooling1D, BatchNormalization, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("FINAL MODEL TRAINING AND SAVING")
print("="*70)

def load_best_parameters():
    """Load the best parameters from random search results"""
    
    try:
        # Find the most recent random search results file
        result_files = [f for f in os.listdir('.') if f.startswith('random_search_results_')]
        
        if not result_files:
            print("ERROR: No random search results found!")
            return None
            
        latest_file = max(result_files, key=lambda x: os.path.getctime(x))
        print(f"Loading parameters from: {latest_file}")
        
        with open(latest_file, 'r') as f:
            results = json.load(f)
            
        return results['best_params']
        
    except Exception as e:
        print(f"Error loading parameters: {e}")
        return None

def load_and_prepare_data():
    """Load and prepare MFCC data"""
    
    print("Loading MFCC features...")
    
    with open("MFCC/features_ravdess.pkl", "rb") as f:
        data = pickle.load(f)

    X = np.array([np.array(f) for f in data['features']])
    y = np.array(data['label'])

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    num_classes = len(le.classes_)
    y_cat = to_categorical(y_encoded, num_classes=num_classes)

    print(f"Data shape: {X.shape}")
    print(f"Classes: {le.classes_}")

    # Same train-test split as used in random search
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_cat, test_size=0.2, random_state=42, stratify=y_encoded
    )

    # Reshape for Conv1D
    X_train = np.transpose(X_train, (0, 2, 1))
    X_test = np.transpose(X_test, (0, 2, 1))

    print(f"Training samples: {X_train.shape[0]}")
    print(f"Test samples: {X_test.shape[0]}")
    
    return X_train, X_test, y_train, y_test, le, num_classes

def create_final_model(params, num_classes):
    """Create the final model with best parameters"""
    
    model = Sequential()
    
    # Conv layers
    model.add(Conv1D(params['conv1_filters'], 
                     kernel_size=params['conv1_kernel'], 
                     activation='relu', 
                     padding='same', 
                     input_shape=(174, 40)))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(pool_size=params['pool_size']))
    model.add(Dropout(params['dropout_conv']))
    
    model.add(Conv1D(params['conv2_filters'], 
                     kernel_size=params['conv2_kernel'], 
                     activation='relu', 
                     padding='same'))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(params['dropout_conv']))
    
    # LSTM layers
    model.add(Bidirectional(LSTM(params['lstm1_units'], return_sequences=True)))
    model.add(Dropout(params['dropout_lstm']))
    
    model.add(Bidirectional(LSTM(params['lstm2_units'], return_sequences=False)))
    model.add(Dropout(params['dropout_lstm']))
    
    # Dense layers
    model.add(Dense(params['dense_units'], activation='relu'))
    model.add(Dropout(params['dropout_dense']))
    
    model.add(Dense(num_classes, activation='softmax'))
    
    # Compile
    optimizer = Adam(learning_rate=params['learning_rate'])
    model.compile(optimizer=optimizer, 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    
    return model

def train_and_save_final_model():
    """Train the final model and save in multiple formats"""
    
    # Load best parameters
    best_params = load_best_parameters()
    if best_params is None:
        print("Cannot proceed without best parameters")
        return
    
    print("Best parameters loaded:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    
    # Load data
    X_train, X_test, y_train, y_test, le, num_classes = load_and_prepare_data()
    
    # Create final model
    print("\nCreating final model...")
    final_model = create_final_model(best_params, num_classes)
    
    print("Model architecture:")
    final_model.summary()
    
    # Train final model
    print("\nTraining final model...")
    
    early_stop = EarlyStopping(
        patience=20, 
        restore_best_weights=True, 
        monitor='val_accuracy',
        verbose=1
    )
    
    history = final_model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=best_params['batch_size'],
        callbacks=[early_stop],
        verbose=1
    )
    
    # Evaluate final model
    train_loss, train_acc = final_model.evaluate(X_train, y_train, verbose=0)
    test_loss, test_acc = final_model.evaluate(X_test, y_test, verbose=0)
    
    print(f"\nFinal Model Performance:")
    print(f"Training Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
    print(f"Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    
    # Create timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save model in multiple formats
    print(f"\nSaving model in multiple formats...")
    
    # 1. Keras format (.keras) - New recommended format
    model_keras_path = f"speech_emotion_model_{timestamp}.keras"
    final_model.save(model_keras_path)
    print(f"[SUCCESS] Saved Keras model: {model_keras_path}")
    
    # 2. Legacy HDF5 format (.h5) - For compatibility
    model_h5_path = f"speech_emotion_model_{timestamp}.h5"
    final_model.save(model_h5_path)
    print(f"[SUCCESS] Saved H5 model: {model_h5_path}")
    
    # 3. TensorFlow SavedModel format (recommended for production)
    savedmodel_path = f"speech_emotion_savedmodel_{timestamp}"
    final_model.save(savedmodel_path, save_format='tf')
    print(f"[SUCCESS] Saved TensorFlow SavedModel: {savedmodel_path}/")
    
    # 4. Model weights only (smaller file size)
    weights_path = f"speech_emotion_weights_{timestamp}.h5"
    final_model.save_weights(weights_path)
    print(f"[SUCCESS] Saved model weights: {weights_path}")
    
    # 5. Save model metadata and preprocessing info
    model_info = {
        'model_type': 'CNN+LSTM for Speech Emotion Recognition',
        'feature_type': 'MFCC',
        'input_shape': (174, 40),
        'num_classes': num_classes,
        'class_names': le.classes_.tolist(),
        'best_parameters': best_params,
        'training_performance': {
            'train_accuracy': float(train_acc),
            'test_accuracy': float(test_acc),
            'train_loss': float(train_loss),
            'test_loss': float(test_loss)
        },
        'training_info': {
            'epochs_trained': len(history.history['accuracy']),
            'early_stopping_patience': 20,
            'timestamp': timestamp
        },
        'preprocessing_info': {
            'mfcc_coefficients': 40,
            'max_time_frames': 174,
            'sampling_rate': 'default_librosa',
            'normalization': 'feature_wise'
        }
    }
    
    info_path = f"model_info_{timestamp}.json"
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    print(f"[SUCCESS] Saved model info: {info_path}")
    
    # 6. Save label encoder for future use
    le_path = f"label_encoder_{timestamp}.pkl"
    with open(le_path, 'wb') as f:
        pickle.dump(le, f)
    print(f"[SUCCESS] Saved label encoder: {le_path}")
    
    # 7. Save training history
    history_path = f"training_history_{timestamp}.pkl"
    with open(history_path, 'wb') as f:
        pickle.dump(history.history, f)
    print(f"[SUCCESS] Saved training history: {history_path}")
    
    print(f"\n" + "="*60)
    print("MODEL SAVING SUMMARY")
    print("="*60)
    print(f"Final test accuracy: {test_acc:.1%}")
    print(f"Model files created:")
    print(f"  1. {model_keras_path} - New Keras format (recommended)")
    print(f"  2. {model_h5_path} - Legacy H5 format (compatibility)")
    print(f"  3. {savedmodel_path}/ - TensorFlow SavedModel (deployment)")
    print(f"  4. {weights_path} - Model weights only")
    print(f"  5. {info_path} - Model metadata and parameters")
    print(f"  6. {le_path} - Label encoder for predictions")
    print(f"  7. {history_path} - Training history")
    
    # Test model loading
    print(f"\nTesting model loading...")
    try:
        loaded_model = load_model(model_keras_path)
        test_pred = loaded_model.predict(X_test[:5], verbose=0)
        print("[SUCCESS] Model loading test successful")
    except Exception as e:
        print(f"[ERROR] Model loading test failed: {e}")
    
    return model_keras_path, test_acc

def create_model_usage_example():
    """Create a usage example file"""
    
    usage_code = '''
# Example: How to load and use the saved speech emotion recognition model

import numpy as np
import pickle
from tensorflow.keras.models import load_model
import librosa

# Load the trained model
model = load_model('speech_emotion_model_[timestamp].h5')

# Load the label encoder
with open('label_encoder_[timestamp].pkl', 'rb') as f:
    label_encoder = pickle.load(f)

def extract_mfcc_features(audio_file_path, max_pad_len=174):
    """Extract MFCC features from audio file"""
    
    # Load audio
    audio, sample_rate = librosa.load(audio_file_path, res_type='kaiser_fast')
    
    # Extract MFCCs (40 coefficients)
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    
    # Pad or truncate to fixed length
    if mfccs.shape[1] < max_pad_len:
        pad_width = max_pad_len - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfccs = mfccs[:, :max_pad_len]
    
    return mfccs

def predict_emotion(audio_file_path):
    """Predict emotion from audio file"""
    
    # Extract features
    features = extract_mfcc_features(audio_file_path)
    
    # Reshape for model input: (1, time_steps, features)
    features = np.transpose(features, (1, 0))  # (174, 40)
    features = np.expand_dims(features, axis=0)  # (1, 174, 40)
    
    # Make prediction
    predictions = model.predict(features, verbose=0)
    predicted_class = np.argmax(predictions, axis=1)[0]
    confidence = np.max(predictions)
    
    # Convert to emotion label
    emotion = label_encoder.inverse_transform([predicted_class])[0]
    
    return emotion, confidence

# Usage example:
# emotion, confidence = predict_emotion('path/to/audio/file.wav')
# print(f"Predicted emotion: {emotion} (confidence: {confidence:.2f})")
'''
    
    with open('model_usage_example.py', 'w') as f:
        f.write(usage_code)
    
    print("✓ Created model_usage_example.py")

if __name__ == "__main__":
    # Train and save the final model
    model_path, accuracy = train_and_save_final_model()
    
    # Create usage example
    create_model_usage_example()
    
    print(f"\n" + "="*70)
    print("FINAL MODEL SAVED SUCCESSFULLY!")
    print(f"Test Accuracy: {accuracy:.1%}")
    print("All model files and documentation created.")
    print("="*70)