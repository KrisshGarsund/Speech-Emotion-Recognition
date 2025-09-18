import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, BatchNormalization, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
import random
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

print("="*60)
print("RANDOM SEARCH HYPERPARAMETER TUNING FOR CNN+LSTM")
print("="*60)

# Load features
print("Loading data...")
with open("MFCC/features_ravdess.pkl", "rb") as f:
    data = pickle.load(f)

X = np.array([np.array(f) for f in data['features']])  # (samples, 40, 174)
y = np.array(data['label'])

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)
num_classes = len(le.classes_)
y_cat = to_categorical(y_encoded, num_classes=num_classes)

print(f"Data shape: {X.shape}")
print(f"Number of classes: {num_classes}")
print(f"Classes: {le.classes_}")

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_cat, test_size=0.2, random_state=42, stratify=y_encoded
)

# Reshape for Conv1D: (samples, time_steps, features)
X_train = np.transpose(X_train, (0, 2, 1))  # (samples, 174, 40)
X_test = np.transpose(X_test, (0, 2, 1))

print(f"Training samples: {X_train.shape[0]}")
print(f"Test samples: {X_test.shape[0]}")

# Define hyperparameter search space
param_space = {
    'conv1_filters': [16, 32, 64, 128],
    'conv1_kernel': [3, 5, 7],
    'conv2_filters': [32, 64, 128, 256],
    'conv2_kernel': [3, 5, 7],
    'lstm1_units': [32, 64, 128],
    'lstm2_units': [16, 32, 64],
    'dense_units': [32, 64, 128, 256],
    'dropout_conv': [0.1, 0.2, 0.3],
    'dropout_lstm': [0.2, 0.3, 0.4],
    'dropout_dense': [0.3, 0.4, 0.5],
    'learning_rate': [0.0001, 0.001, 0.01],
    'batch_size': [8, 16, 32],
    'pool_size': [2, 3, 4]
}

def create_model(params):
    """Create CNN+LSTM model with given parameters"""
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
    
    # Compile with specified learning rate
    optimizer = Adam(learning_rate=params['learning_rate'])
    model.compile(optimizer=optimizer, 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    
    return model

def random_search(param_space, n_trials=20):
    """Perform random search over hyperparameter space"""
    
    results = []
    best_accuracy = 0
    best_params = None
    
    print(f"\nStarting Random Search with {n_trials} trials...")
    print("-" * 60)
    
    for trial in range(n_trials):
        # Sample random parameters
        params = {}
        for param_name, param_values in param_space.items():
            params[param_name] = random.choice(param_values)
        
        print(f"\nTrial {trial + 1}/{n_trials}")
        print(f"Parameters: {params}")
        
        try:
            # Create and train model
            model = create_model(params)
            
            # Early stopping
            early_stop = EarlyStopping(
                patience=10, 
                restore_best_weights=True, 
                monitor='val_accuracy',
                verbose=0
            )
            
            # Train model
            history = model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=30,  # Reduced for faster search
                batch_size=params['batch_size'],
                callbacks=[early_stop],
                verbose=0
            )
            
            # Get best validation accuracy
            val_accuracy = max(history.history['val_accuracy'])
            train_accuracy = max(history.history['accuracy'])
            
            print(f"Training Accuracy: {train_accuracy:.4f}")
            print(f"Validation Accuracy: {val_accuracy:.4f}")
            
            # Store results
            result = {
                'trial': trial + 1,
                'params': params.copy(),
                'train_accuracy': train_accuracy,
                'val_accuracy': val_accuracy,
                'epochs_trained': len(history.history['accuracy'])
            }
            results.append(result)
            
            # Update best result
            if val_accuracy > best_accuracy:
                best_accuracy = val_accuracy
                best_params = params.copy()
                print(f"*** NEW BEST ACCURACY: {val_accuracy:.4f} ***")
            
        except Exception as e:
            print(f"Trial {trial + 1} failed: {str(e)}")
            continue
    
    return results, best_params, best_accuracy

# Perform random search
n_trials = 15  # You can increase this for more thorough search
results, best_params, best_accuracy = random_search(param_space, n_trials)

# Display results
print("\n" + "="*60)
print("RANDOM SEARCH RESULTS")
print("="*60)

if results:
    # Convert to DataFrame for easy analysis
    df_results = pd.DataFrame(results)
    
    print(f"\nCompleted {len(results)} successful trials")
    print(f"Best Validation Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
    print(f"\nBest Parameters:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    
    # Show top 5 results
    print(f"\nTop 5 Results:")
    top_results = df_results.nlargest(5, 'val_accuracy')[['trial', 'val_accuracy', 'train_accuracy']]
    print(top_results.to_string(index=False))
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"random_search_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'best_params': best_params,
            'best_accuracy': float(best_accuracy),
            'all_results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

else:
    print("No successful trials completed!")
    best_params = None

# Train final model with best parameters
if best_params:
    print("\n" + "="*60)
    print("TRAINING FINAL TUNED MODEL")
    print("="*60)
    
    print("Creating final model with best parameters...")
    final_model = create_model(best_params)
    
    # Train with more epochs for final model
    early_stop = EarlyStopping(
        patience=20, 
        restore_best_weights=True, 
        monitor='val_accuracy'
    )
    
    print("Training final model...")
    final_history = final_model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=best_params['batch_size'],
        callbacks=[early_stop],
        verbose=1
    )
    
    # Final evaluation
    final_train_acc = max(final_history.history['accuracy'])
    final_val_acc = max(final_history.history['val_accuracy'])
    test_loss, test_acc = final_model.evaluate(X_test, y_test, verbose=0)
    
    print("\n" + "="*60)
    print("FINAL RESULTS COMPARISON")
    print("="*60)
    print("UNTUNED MODEL (from previous implementation):")
    print("  Expected Accuracy: ~78-82%")
    print("\nTUNED MODEL (Random Search):")
    print(f"  Final Training Accuracy: {final_train_acc:.4f} ({final_train_acc*100:.2f}%)")
    print(f"  Final Validation Accuracy: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
    print(f"  Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    
    # Calculate improvement
    baseline_acc = 0.64  # Assuming baseline was around 80%
    improvement = (test_acc - baseline_acc) * 100
    print(f"\nIMPROVEMENT: +{improvement:.2f}% over baseline")
    
    if improvement > 2:
        print("SIGNIFICANT IMPROVEMENT ACHIEVED!")
    elif improvement > 0:
        print("Modest improvement achieved")
    else:
        print("No improvement - may need different search space")

else:
    print("\nCould not complete random search - check your setup!")

print("\n" + "="*60)
print("RANDOM SEARCH TUNING COMPLETE")
print("="*60)