import pickle
import numpy as np
import pandas as pd
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (classification_report, confusion_matrix, 
                           accuracy_score, precision_recall_fscore_support)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, BatchNormalization, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("TEST PREDICTIONS GENERATOR - MFCC FINE-TUNED MODEL")
print("="*70)

# Step 1: Load best parameters from MFCC random search results
def load_best_parameters():
    """Load best parameters from the most recent MFCC random search results"""
    try:
        # Look for MFCC random search result files
        result_files = [f for f in os.listdir('.') if f.startswith('random_search_results_')]
        
        if not result_files:
            print("[ERROR] No random search results found!")
            print("Please run the MFCC random search script first.")
            return None
            
        # Get the most recent file
        latest_file = max(result_files, key=lambda x: os.path.getctime(x))
        print(f"Loading parameters from: {latest_file}")
        
        with open(latest_file, 'r') as f:
            results = json.load(f)
            
        best_params = results['best_params']
        best_accuracy = results['best_accuracy']
        
        print(f"Best validation accuracy from search: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
        print("Best parameters:")
        for param, value in best_params.items():
            print(f"  {param}: {value}")
            
        return best_params
        
    except Exception as e:
        print(f"[ERROR] Could not load random search results: {e}")
        return None

# Step 2: Load and prepare MFCC data (same as training)
def load_and_prepare_data():
    """Load MFCC features and prepare for training"""
    print("\nLoading MFCC features...")
    
    try:
        with open("features_ravdess.pkl", "rb") as f:
            data = pickle.load(f)
        print("[SUCCESS] MFCC features loaded")
    except FileNotFoundError:
        print("[ERROR] MFCC features file not found!")
        print("Please check the path: MFCC/features_ravdess.pkl")
        return None, None, None, None, None, None, None
    
    X = np.array([np.array(f) for f in data['features']])  # (samples, 40, 174)
    y = np.array(data['label'])
    
    # Encode labels (same as training)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    num_classes = len(le.classes_)
    y_cat = to_categorical(y_encoded, num_classes=num_classes)
    
    print(f"Data shape: {X.shape}")
    print(f"Number of classes: {num_classes}")
    print(f"Classes: {le.classes_}")
    
    # Same train-test split as used in random search (CRITICAL!)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_cat, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Get original labels for test set
    _, y_test_labels, _, _ = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Reshape for Conv1D: (samples, time_steps, features)
    X_train = np.transpose(X_train, (0, 2, 1))  # (samples, 174, 40)
    X_test = np.transpose(X_test, (0, 2, 1))
    
    print(f"Training samples: {X_train.shape[0]}")
    print(f"Test samples: {X_test.shape[0]}")
    
    return X_train, X_test, y_train, y_test, y_test_labels, le, num_classes

# Step 3: Create model with best parameters (same as random search)
def create_tuned_model(params, num_classes):
    """Create CNN+LSTM model with tuned parameters for MFCC features"""
    
    model = Sequential()
    
    # Conv layers
    model.add(Conv1D(params['conv1_filters'], 
                     kernel_size=params['conv1_kernel'], 
                     activation='relu', 
                     padding='same', 
                     input_shape=(174, 40)))  # MFCC input shape
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

# Step 4: Train final model and generate predictions
def train_and_predict(model, X_train, X_test, y_train, y_test, params, le, y_test_labels):
    """Train final model and generate test predictions"""
    
    print("\nTraining final MFCC tuned model...")
    print("-" * 50)
    
    # Callbacks
    early_stop = EarlyStopping(
        patience=20, 
        restore_best_weights=True, 
        monitor='val_accuracy',
        verbose=1
    )
    
    # Train model (same as random search final training)
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,  # Same as your random search
        batch_size=params['batch_size'],
        callbacks=[early_stop],
        verbose=1
    )
    
    print("\n[SUCCESS] Model training completed!")
    
    # Generate predictions
    print("\nGenerating test predictions...")
    y_pred_prob = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred_prob, axis=1)
    y_test_classes = np.argmax(y_test, axis=1)
    
    # Convert back to emotion labels
    y_pred_labels = le.inverse_transform(y_pred_classes)
    y_true_labels = le.inverse_transform(y_test_classes)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test_classes, y_pred_classes)
    
    return y_pred_prob, y_pred_labels, y_true_labels, accuracy, history

# Step 5: Comprehensive analysis and saving
def analyze_and_save_results(y_pred_prob, y_pred_labels, y_true_labels, accuracy, le, params, history):
    """Perform detailed analysis and save all results"""
    
    print("\n" + "="*70)
    print("DETAILED RESULTS ANALYSIS - MFCC MODEL")
    print("="*70)
    
    # Create comprehensive results DataFrame
    results_df = pd.DataFrame({
        'Sample_Index': range(len(y_true_labels)),
        'True_Emotion': y_true_labels,
        'Predicted_Emotion': y_pred_labels,
        'Correct': y_true_labels == y_pred_labels,
        'Confidence': np.max(y_pred_prob, axis=1),
        'True_Class_Probability': y_pred_prob[range(len(y_pred_prob)), 
                                              [list(le.classes_).index(label) for label in y_true_labels]]
    })
    
    # Add individual class probabilities
    for i, emotion in enumerate(le.classes_):
        results_df[f'Prob_{emotion}'] = y_pred_prob[:, i]
    
    # Calculate per-class metrics
    y_test_classes = np.array([list(le.classes_).index(label) for label in y_true_labels])
    y_pred_classes = np.array([list(le.classes_).index(label) for label in y_pred_labels])
    
    # Classification report
    class_report = classification_report(y_test_classes, y_pred_classes, 
                                       target_names=le.classes_, 
                                       output_dict=True, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_test_classes, y_pred_classes)
    
    # Print summary
    print(f"Final Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Total test samples: {len(y_true_labels)}")
    print(f"Correct predictions: {np.sum(results_df['Correct'])}")
    print(f"Wrong predictions: {np.sum(~results_df['Correct'])}")
    
    # Performance assessment
    if accuracy > 0.85:
        print("EXCELLENT: Outstanding performance for emotion recognition!")
    elif accuracy > 0.75:
        print("GOOD: Strong performance, competitive with published results")
    elif accuracy > 0.65:
        print("FAIR: Reasonable performance, room for improvement")
    else:
        print("NEEDS IMPROVEMENT: Below expected performance")
    
    # Per-class performance
    print(f"\nPer-Class Performance:")
    print("-" * 60)
    print(f"{'Emotion':<12} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8}")
    print("-" * 60)
    
    for emotion in le.classes_:
        if emotion in class_report:
            prec = class_report[emotion]['precision']
            rec = class_report[emotion]['recall']
            f1 = class_report[emotion]['f1-score']
            sup = int(class_report[emotion]['support'])
            print(f"{emotion:<12} {prec:<10.3f} {rec:<10.3f} {f1:<10.3f} {sup:<8}")
    
    # Error analysis
    print(f"\nError Analysis:")
    print("-" * 40)
    
    # Most confused pairs
    confusion_pairs = []
    for i in range(len(le.classes_)):
        for j in range(len(le.classes_)):
            if i != j and cm[i, j] > 0:
                confusion_pairs.append({
                    'True': le.classes_[i],
                    'Predicted': le.classes_[j],
                    'Count': cm[i, j],
                    'Percentage': (cm[i, j] / np.sum(cm[i, :])) * 100
                })
    
    confusion_pairs.sort(key=lambda x: x['Count'], reverse=True)
    
    print("Top confusion pairs:")
    for pair in confusion_pairs[:5]:
        print(f"  {pair['True']} -> {pair['Predicted']}: {pair['Count']} ({pair['Percentage']:.1f}%)")
    
    # Low confidence predictions
    low_conf = results_df.nsmallest(5, 'Confidence')
    print(f"\nLowest confidence predictions:")
    for _, row in low_conf.iterrows():
        status = "CORRECT" if row['Correct'] else "WRONG"
        print(f"  {row['True_Emotion']} -> {row['Predicted_Emotion']} (conf: {row['Confidence']:.3f}) [{status}]")
    
    # Save all results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Save detailed predictions
    predictions_file = f'mfcc_test_predictions_{timestamp}.csv'
    results_df.to_csv(predictions_file, index=False)
    
    # 2. Save summary analysis
    summary = {
        'model_info': {
            'feature_type': 'MFCC Only',
            'model_parameters': params,
            'training_epochs': len(history.history['accuracy']),
            'timestamp': timestamp
        },
        'performance_metrics': {
            'test_accuracy': float(accuracy),
            'total_samples': len(y_true_labels),
            'correct_predictions': int(np.sum(results_df['Correct'])),
            'wrong_predictions': int(np.sum(~results_df['Correct']))
        },
        'per_class_metrics': {
            emotion: {
                'precision': float(class_report[emotion]['precision']),
                'recall': float(class_report[emotion]['recall']),
                'f1_score': float(class_report[emotion]['f1-score']),
                'support': int(class_report[emotion]['support'])
            } for emotion in le.classes_ if emotion in class_report
        },
        'confusion_matrix': cm.tolist(),
        'top_confusions': confusion_pairs[:5]
    }
    
    summary_file = f'mfcc_analysis_{timestamp}.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # 3. Generate visualizations
    plt.style.use('default')
    
    # Confusion Matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title(f'Confusion Matrix - MFCC Model (Accuracy: {accuracy*100:.1f}%)')
    plt.xlabel('Predicted Emotion')
    plt.ylabel('True Emotion')
    plt.tight_layout()
    confusion_file = f'mfcc_confusion_matrix_{timestamp}.png'
    plt.savefig(confusion_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    # Training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss', color='red')
    plt.plot(history.history['val_loss'], label='Validation Loss', color='blue')
    plt.title('MFCC Model Loss During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Training Accuracy', color='red')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy', color='blue')
    plt.title('MFCC Model Accuracy During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    training_file = f'mfcc_training_history_{timestamp}.png'
    plt.savefig(training_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print file locations
    print(f"\n" + "="*70)
    print("RESULTS SAVED SUCCESSFULLY")
    print("="*70)
    print(f"[SAVED] Detailed predictions: {predictions_file}")
    print(f"[SAVED] Analysis summary: {summary_file}")
    print(f"[SAVED] Confusion matrix: {confusion_file}")
    print(f"[SAVED] Training history: {training_file}")
    
    return predictions_file, summary_file

# Main execution
def main():
    """Main execution function"""
    
    # Step 1: Load best parameters
    best_params = load_best_parameters()
    if best_params is None:
        return
    
    # Step 2: Load and prepare data
    X_train, X_test, y_train, y_test, y_test_labels, le, num_classes = load_and_prepare_data()
    if X_train is None:
        return
    
    # Step 3: Create tuned model
    print(f"\nCreating tuned MFCC model with best parameters...")
    model = create_tuned_model(best_params, num_classes=num_classes)
    
    print(f"Model architecture:")
    model.summary()
    
    # Step 4: Train and predict
    y_pred_prob, y_pred_labels, y_true_labels, accuracy, history = train_and_predict(
        model, X_train, X_test, y_train, y_test, best_params, le, y_test_labels
    )
    
    # Step 5: Analyze and save results
    analyze_and_save_results(y_pred_prob, y_pred_labels, y_true_labels, 
                           accuracy, le, best_params, history)
    
    print(f"\n" + "="*70)
    print(f"FINAL MFCC MODEL RESULT: {accuracy*100:.2f}% TEST ACCURACY")
    print(f"MFCC TEST PREDICTIONS GENERATION COMPLETE!")
    print("="*70)

# Run the script
if __name__ == "__main__":
    main()