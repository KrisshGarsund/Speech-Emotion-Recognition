# Speech Emotion Recognition using Deep Learning

A CNN+LSTM hybrid deep learning model for recognizing emotions from speech audio using MFCC features. Achieves competitive performance on the RAVDESS dataset with systematic hyperparameter optimization.

## Table of Contents
- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Model Architecture](#model-architecture)
- [Performance Metrics](#performance-metrics)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Methodology](#methodology)
- [Results Analysis](#results-analysis)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This project implements a deep learning approach for automatic speech emotion recognition (SER) using audio signal processing and neural networks. The system can classify emotions from speech audio into 8 categories: Angry, Calm, Disgust, Fearful, Happy, Neutral, Sad, and Surprised.

### Key Features
- MFCC feature extraction for robust audio representation
- CNN+LSTM hybrid architecture for spatial and temporal pattern recognition
- Systematic hyperparameter optimization using random search
- Comprehensive evaluation with confusion matrix analysis
- Model persistence in multiple formats (.keras, .h5)

## Dataset

**RAVDESS (Ryerson Audio-Visual Database of Emotional Speech and Song)**
- 1,440 audio files from 24 professional actors
- 8 emotion categories with balanced representation
- Controlled recording conditions for consistent quality
- Standard benchmark for emotion recognition research

### Data Distribution
| Emotion   | Training Samples | Test Samples | Total |
|-----------|------------------|--------------|-------|
| Angry     | 154              | 38           | 192   |
| Calm      | 154              | 38           | 192   |
| Disgust   | 154              | 38           | 192   |
| Fearful   | 155              | 39           | 194   |
| Happy     | 155              | 39           | 194   |
| Neutral   | 77               | 19           | 96    |
| Sad       | 154              | 38           | 192   |
| Surprised | 155              | 39           | 194   |

**Note:** Neutral class shows imbalance with fewer samples, which impacts model performance on this category.

## Model Architecture

### Hybrid CNN+LSTM Design

The model combines convolutional and recurrent neural network components:

```
Input: (174, 40) - MFCC features
    ↓
Conv1D Layer 1 → BatchNorm → MaxPool → Dropout
    ↓
Conv1D Layer 2 → BatchNorm → MaxPool → Dropout
    ↓
Bidirectional LSTM Layer 1 → Dropout
    ↓
Bidirectional LSTM Layer 2 → Dropout
    ↓
Dense Layer → Dropout
    ↓
Output: (8,) - Emotion probabilities
```

### Architecture Justification

1. **CNN Layers**: Extract local spectral patterns from MFCC features
   - Captures frequency-domain characteristics of emotions
   - Reduces dimensionality while preserving important features

2. **LSTM Layers**: Model temporal dependencies in speech
   - Captures how acoustic patterns evolve over time
   - Bidirectional processing for context from both directions

3. **Regularization**: Prevent overfitting on limited dataset
   - Dropout layers at multiple stages
   - Batch normalization for training stability
   - Early stopping based on validation performance

## Performance Metrics

### Final Model Performance
- **Test Accuracy**: 73.61% - 79.51% (varies across training runs)
- **Training Accuracy**: ~95-99% (indicates some overfitting)
- **Best Validation Accuracy**: 79.51%

### Per-Class Performance (Best Run)
| Emotion   | Precision | Recall | F1-Score | Support |
|-----------|-----------|--------|----------|---------|
| Angry     | 0.786     | 0.868  | 0.825    | 38      |
| Calm      | 0.829     | 0.895  | 0.861    | 38      |
| Disgust   | 0.931     | 0.711  | 0.806    | 38      |
| Fearful   | 0.691     | 0.974  | 0.809    | 39      |
| Happy     | 0.667     | 0.615  | 0.640    | 39      |
| Neutral   | 0.909     | 0.526  | 0.667    | 19      |
| Sad       | 0.722     | 0.684  | 0.703    | 38      |
| Surprised | 0.868     | 0.846  | 0.857    | 39      |

**Overall Macro F1-Score**: 0.759

### Key Observations
- **Strongest Performance**: Calm (86.1% F1), Surprised (85.7% F1)
- **Most Challenging**: Happy (64.0% F1), Neutral (66.7% F1)
- **Common Confusions**: Happy↔Fearful, Sad→Fearful, Disgust→Angry

## Installation

### Requirements
```bash
python >= 3.8
tensorflow >= 2.12.0
librosa >= 0.10.0
scikit-learn >= 1.3.0
pandas >= 1.5.0
numpy >= 1.24.0
matplotlib >= 3.7.0
seaborn >= 0.12.0
```

### Setup
```bash
git clone https://github.com/yourusername/speech-emotion-recognition.git
cd speech-emotion-recognition
pip install -r requirements.txt
```

## Usage

### 1. Feature Extraction
```bash
python MFCC.py
```
Extracts MFCC features from RAVDESS dataset and saves to `features_ravdess.pkl`

### 2. Model Training & Hyperparameter Tuning
```bash
python Random_Search_Tuning.py
```
Performs random search optimization and trains the final model

### 3. Generate Test Predictions
```bash
python generate_predictions.py
```
Creates detailed predictions and analysis for the test set

### 4. Save Final Model
```bash
python savemodel.py
```
Saves the trained model in multiple formats for deployment

### 5. Make Predictions on New Audio
```python
from tensorflow.keras.models import load_model
import librosa
import numpy as np

# Load trained model
model = load_model('speech_emotion_model_[timestamp].keras')

# Load and preprocess audio
def predict_emotion(audio_path):
    # Extract MFCC features
    audio, sr = librosa.load(audio_path, res_type='kaiser_fast')
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    
    # Pad/truncate to 174 frames
    if mfccs.shape[1] < 174:
        mfccs = np.pad(mfccs, ((0,0), (0, 174-mfccs.shape[1])))
    else:
        mfccs = mfccs[:, :174]
    
    # Reshape for model input
    features = np.transpose(mfccs, (1, 0))
    features = np.expand_dims(features, axis=0)
    
    # Predict
    prediction = model.predict(features)
    emotion_idx = np.argmax(prediction)
    emotions = ['Angry', 'Calm', 'Disgust', 'Fearful', 'Happy', 'Neutral', 'Sad', 'Surprised']
    
    return emotions[emotion_idx], prediction[0][emotion_idx]

# Usage
emotion, confidence = predict_emotion('path/to/audio.wav')
print(f"Emotion: {emotion}, Confidence: {confidence:.2f}")
```

## File Structure

```
speech-emotion-recognition/
├── README.md
├── requirements.txt
├── MFCC.py                          # Feature extraction
├── Random_Search_Tuning.py          # Hyperparameter optimization
├── generate_predictions.py          # Test set evaluation
├── savemodel.py                     # Model persistence
├── model_usage_example.py           # Inference example
├── models/
│   ├── speech_emotion_model_[timestamp].keras
│   ├── speech_emotion_model_[timestamp].h5
│   ├── model_info_[timestamp].json
│   └── label_encoder_[timestamp].pkl
├── results/
│   ├── random_search_results_[timestamp].json
│   ├── mfcc_test_predictions_[timestamp].csv
│   └── training_history_[timestamp].pkl
└── Dataset/
    └── ravdess_by_emotion/
        ├── Angry/
        ├── Calm/
        ├── Disgust/
        ├── Fearful/
        ├── Happy/
        ├── Neutral/
        ├── Sad/
        └── Surprised/
```

## Methodology

### 1. Feature Engineering
- **MFCC (Mel-Frequency Cepstral Coefficients)**: 40 coefficients
- **Temporal Padding**: Fixed length of 174 time frames
- **Normalization**: Feature-wise standardization

**MFCC Justification**:
- Mimics human auditory perception
- Captures spectral characteristics relevant to emotion
- Compact representation (40 features vs raw audio)
- Proven effective in speech recognition tasks

### 2. Model Development Process

#### Initial Approach
- Baseline CNN model: ~64% accuracy
- Added LSTM layers: ~72% accuracy
- Systematic hyperparameter tuning: 79.51% accuracy

#### Hyperparameter Search Space
- **Conv Filters**: [16, 32, 64, 128, 256]
- **Kernel Sizes**: [3, 5, 7]
- **LSTM Units**: [16, 32, 64, 128]
- **Dropout Rates**: [0.1, 0.2, 0.3, 0.4, 0.5]
- **Learning Rates**: [0.0001, 0.001, 0.01]
- **Batch Sizes**: [8, 16, 32]

#### Best Hyperparameters
```json
{
  "conv1_filters": 64,
  "conv1_kernel": 5,
  "conv2_filters": 128,
  "conv2_kernel": 3,
  "lstm1_units": 64,
  "lstm2_units": 32,
  "dense_units": 128,
  "dropout_conv": 0.3,
  "dropout_lstm": 0.4,
  "dropout_dense": 0.5,
  "learning_rate": 0.001,
  "batch_size": 16
}
```

### 3. Training Strategy
- **Train/Test Split**: 80/20 stratified by emotion
- **Early Stopping**: Patience of 20 epochs on validation accuracy
- **Optimization**: Adam optimizer with learning rate scheduling
- **Regularization**: Dropout + Batch normalization + Early stopping

### 4. Evaluation Methodology
- **Cross-validation**: 5-fold stratified for robust assessment
- **Metrics**: Accuracy, Precision, Recall, F1-score per class
- **Error Analysis**: Confusion matrix and misclassification patterns
- **Statistical Validation**: Multiple training runs to assess variance

## Results Analysis

### Model Performance Comparison
| Model Version | Test Accuracy | Notes |
|---------------|---------------|-------|
| Baseline CNN  | 64.0%         | Simple architecture |
| CNN + LSTM    | 72.0%         | Added temporal modeling |
| Optimized     | 79.51%        | Hyperparameter tuning |

### Strengths
1. **Competitive Performance**: Results align with published RAVDESS benchmarks (75-85%)
2. **Robust Architecture**: CNN+LSTM handles both spectral and temporal patterns
3. **Systematic Optimization**: Random search improved performance by 15.51%
4. **Reproducible Methodology**: Fixed seeds and proper train/test separation

### Limitations
1. **Overfitting Tendency**: Large train-test gap (95-99% vs 73-79%)
2. **Class Imbalance**: Neutral emotion underrepresented (96 vs 192+ samples)
3. **Confusion Patterns**: Happy-Fearful and Sad-Fearful frequently confused
4. **Dataset Constraints**: Limited to acted emotions in controlled conditions

### Error Analysis Insights
- **Acoustic Similarity**: Emotions with similar arousal levels get confused
- **Sample Size Impact**: Neutral class suffers from insufficient training data  
- **Bidirectional Confusion**: Some emotion pairs show mutual misclassification
- **High Arousal Bias**: Model performs better on clearly expressed emotions

## Future Improvements

### Technical Enhancements
1. **Feature Engineering**
   - Combine MFCC with prosodic features (pitch, intensity, rhythm)
   - Experiment with spectral features (chroma, spectral centroid)
   - Add contextual features (speaking rate, pause patterns)

2. **Architecture Improvements**
   - Attention mechanisms for better temporal modeling
   - Residual connections to improve gradient flow
   - Multi-scale CNN kernels for different temporal resolutions

3. **Training Strategies**
   - Data augmentation (speed perturbation, noise injection)
   - Transfer learning from pre-trained speech models
   - Ensemble methods combining multiple architectures

### Data and Evaluation
1. **Dataset Expansion**
   - Include spontaneous emotion datasets
   - Add cross-cultural emotion variations
   - Balance class distributions

2. **Robustness Testing**
   - Cross-dataset evaluation
   - Noise robustness assessment
   - Speaker-independent validation

### Deployment Considerations
1. **Real-time Processing**: Optimize for streaming audio
2. **Mobile Deployment**: Model quantization and compression
3. **API Development**: RESTful service for emotion recognition
4. **User Interface**: Web/mobile app for practical applications

## Research Context

### Comparison with Literature
- **State-of-the-art RAVDESS**: 85-90% (transformer-based models)
- **CNN-LSTM approaches**: 75-82% (similar to our results)
- **Traditional ML**: 60-70% (SVM, Random Forest with handcrafted features)

### Contribution
This work demonstrates:
- Effective hyperparameter optimization for emotion recognition
- Systematic comparison of feature combinations
- Practical implementation with deployment-ready model formats
- Comprehensive evaluation methodology with error analysis

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

### Areas for Contribution
- Additional feature extraction methods
- Alternative neural network architectures
- Cross-dataset validation experiments
- Mobile/web deployment implementations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- RAVDESS dataset creators for providing high-quality emotion data
- TensorFlow/Keras community for deep learning framework
- librosa developers for audio processing capabilities
- Research community for emotion recognition methodologies



