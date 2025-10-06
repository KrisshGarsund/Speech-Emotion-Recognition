import numpy as np
import librosa
import pickle
from tensorflow.keras.models import load_model
import os
import pandas as pd
from datetime import datetime

class SpeechEmotionPredictor:
    def __init__(self, model_path, label_encoder_path):
        """
        Initialize the emotion predictor
        
        Args:
            model_path: Path to your saved .keras or .h5 model file
            label_encoder_path: Path to your saved label encoder .pkl file
        """
        # Load the trained model
        print(f"Loading model from: {model_path}")
        self.model = load_model(model_path)
        
        # Load label encoder
        print(f"Loading label encoder from: {label_encoder_path}")
        with open(label_encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
        
        # Get emotion classes
        self.emotions = self.label_encoder.classes_
        print(f"Model loaded successfully. Emotion classes: {list(self.emotions)}")
    
    def extract_mfcc_features(self, audio_path, max_pad_len=174):
        """
        Extract MFCC features from audio file (same as training)
        
        Args:
            audio_path: Path to the audio file
            max_pad_len: Maximum length for padding/truncation (default: 174)
        
        Returns:
            mfcc_features: Processed MFCC features ready for model input
        """
        try:
            # Load audio file
            audio, sample_rate = librosa.load(audio_path, res_type='kaiser_fast')
            print(f"Loaded audio: {os.path.basename(audio_path)} (duration: {len(audio)/sample_rate:.2f}s)")
            
            # Extract 40 MFCC coefficients (same as training)
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
            
            # Pad or truncate to fixed length (same preprocessing as training)
            pad_width = max_pad_len - mfccs.shape[1]
            if pad_width > 0:
                # Pad with zeros if too short
                mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
            else:
                # Truncate if too long
                mfccs = mfccs[:, :max_pad_len]
            
            print(f"MFCC shape after preprocessing: {mfccs.shape}")
            return mfccs
            
        except Exception as e:
            print(f"Error processing audio file {audio_path}: {e}")
            return None
    
    def predict_emotion(self, audio_path, return_probabilities=False):
        """
        Predict emotion from audio file
        
        Args:
            audio_path: Path to the audio file
            return_probabilities: Whether to return all class probabilities
        
        Returns:
            If return_probabilities=False: (emotion, confidence)
            If return_probabilities=True: (emotion, confidence, all_probabilities)
        """
        # Extract features
        mfcc_features = self.extract_mfcc_features(audio_path)
        
        if mfcc_features is None:
            return None
        
        # Reshape for model input: (1, time_steps, features)
        # Model expects (batch_size, 174, 40)
        features = np.transpose(mfcc_features, (1, 0))  # (174, 40)
        features = np.expand_dims(features, axis=0)      # (1, 174, 40)
        
        # Make prediction
        predictions = self.model.predict(features, verbose=0)
        
        # Get predicted class and confidence
        predicted_class_idx = np.argmax(predictions, axis=1)[0]
        confidence = np.max(predictions)
        
        # Convert to emotion label
        predicted_emotion = self.label_encoder.inverse_transform([predicted_class_idx])[0]
        
        print(f"Prediction: {predicted_emotion} (confidence: {confidence:.3f})")
        
        if return_probabilities:
            # Create probability dict for all emotions
            prob_dict = {}
            for i, emotion in enumerate(self.emotions):
                prob_dict[emotion] = predictions[0][i]
            
            return predicted_emotion, confidence, prob_dict
        else:
            return predicted_emotion, confidence
    
    def predict_batch(self, audio_files, output_csv=None):
        """
        Predict emotions for multiple audio files
        
        Args:
            audio_files: List of audio file paths
            output_csv: Optional path to save results as CSV
        
        Returns:
            DataFrame with predictions for all files
        """
        results = []
        
        print(f"\nProcessing {len(audio_files)} audio files...")
        
        for i, audio_path in enumerate(audio_files):
            print(f"\nProcessing file {i+1}/{len(audio_files)}: {os.path.basename(audio_path)}")
            
            # Get prediction with probabilities
            result = self.predict_emotion(audio_path, return_probabilities=True)
            
            if result is not None:
                emotion, confidence, probabilities = result
                
                # Create result record
                record = {
                    'audio_file': os.path.basename(audio_path),
                    'file_path': audio_path,
                    'predicted_emotion': emotion,
                    'confidence': confidence,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add individual class probabilities
                for emo, prob in probabilities.items():
                    record[f'prob_{emo}'] = prob
                
                results.append(record)
            else:
                # Handle failed predictions
                record = {
                    'audio_file': os.path.basename(audio_path),
                    'file_path': audio_path,
                    'predicted_emotion': 'ERROR',
                    'confidence': 0.0,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                results.append(record)
        
        # Create DataFrame
        results_df = pd.DataFrame(results)
        
        # Save to CSV if specified
        if output_csv:
            results_df.to_csv(output_csv, index=False)
            print(f"\nResults saved to: {output_csv}")
        
        # Print summary
        successful_predictions = len(results_df[results_df['predicted_emotion'] != 'ERROR'])
        print(f"\nBatch Prediction Summary:")
        print(f"Total files processed: {len(audio_files)}")
        print(f"Successful predictions: {successful_predictions}")
        print(f"Failed predictions: {len(audio_files) - successful_predictions}")
        
        return results_df

def main():
    """Example usage of the emotion predictor"""
    
    # Update these paths to match your saved model files
    MODEL_PATH = "Predict/SER_model.h5"  # Your saved model
    LABEL_ENCODER_PATH = "Predict/label_encoder.pkl"   # Your saved label encoder
    
    try:
        # Initialize predictor
        predictor = SpeechEmotionPredictor(MODEL_PATH, LABEL_ENCODER_PATH)
        
        # Single file prediction
        print("\n" + "="*60)
        print("SINGLE FILE PREDICTION EXAMPLE")
        print("="*60)
        
        # Replace with path to your test audio file
        test_audio = "path/to/your/test_audio.wav"
        
        if os.path.exists(test_audio):
            emotion, confidence = predictor.predict_emotion(test_audio)
            print(f"\nResult: The speaker sounds {emotion} with {confidence:.1%} confidence")
        else:
            print(f"Test audio file not found: {test_audio}")
            print("Please update the 'test_audio' variable with a valid audio file path")
        
        # Batch prediction
        print("\n" + "="*60)
        print("BATCH PREDICTION EXAMPLE")
        print("="*60)
        
        # Example audio files (update with your actual files)
        audio_files = [
            "audio1.wav",
            "audio2.wav",
            "audio3.wav"
        ]
        
        # Filter to only existing files
        existing_files = [f for f in audio_files if os.path.exists(f)]
        
        if existing_files:
            results_df = predictor.predict_batch(existing_files, output_csv="emotion_predictions.csv")
            
            # Display results
            print("\nPrediction Results:")
            print(results_df[['audio_file', 'predicted_emotion', 'confidence']].to_string(index=False))
        else:
            print("No valid audio files found for batch processing")
            print("Please add some .wav files to your directory or update the file paths")
        
    except FileNotFoundError as e:
        print(f"Error: Required model files not found - {e}")
        print("\nPlease ensure you have:")
        print("1. Trained model file (.keras or .h5)")
        print("2. Label encoder file (.pkl)")
        print("3. Update the file paths in the script")
    
    except Exception as e:
        print(f"Error: {e}")

def quick_predict(audio_path, model_path, label_encoder_path):
    """Quick prediction function for single file"""
    predictor = SpeechEmotionPredictor(model_path, label_encoder_path)
    return predictor.predict_emotion(audio_path)

def predict_from_microphone():
    """
    Example function to predict from microphone recording
    Note: Requires additional setup for microphone recording
    """
    print("Microphone recording feature would require:")
    print("1. pip install sounddevice")
    print("2. pip install soundfile")
    print("3. Implementation of real-time audio recording")
    print("This is a placeholder for future development")

if __name__ == "__main__":
    main()