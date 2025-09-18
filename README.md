# 🎤 Speech Emotion Recognition (SER)

![Python](https://img.shields.io/badge/Python-3.9-blue)  
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)  
![Librosa](https://img.shields.io/badge/Librosa-Audio--Processing-green)  
![Status](https://img.shields.io/badge/Status-In_Progress-yellow)

---

##  Overview
This project implements a **Speech Emotion Recognition (SER)** system using the **RAVDESS dataset**.  
The goal is to classify human emotions from speech signals by extracting features such as **MFCC, ZCR, and Mel-Spectrogram**, and training deep learning models including **CNN** and **LSTM**.  

---

##  Dataset
- **RAVDESS (Ryerson Audio-Visual Database of Emotional Speech and Song)**  
- Consists of recordings categorized into the following **emotions**:  
  -  Neutral  
  -  Calm  
  -  Happy  
  -  Sad  
  -  Angry  
  -  Fearful  
  -  Disgust  
  -  Surprised  

Dataset was **organized into subfolders emotion-wise** for preprocessing.

---

##  Libraries & Tools
- `numpy`  
- `pandas`  
- `matplotlib` / `seaborn`  
- `librosa`  
- `scikit-learn`  
- `tensorflow` / `keras`

---

##  Feature Extraction
We extracted acoustic features from audio signals:
-  **MFCC (Mel-Frequency Cepstral Coefficients)**  
-  **ZCR (Zero Crossing Rate)**  
-  **Mel-Spectrogram**

These features capture **spectral** and **temporal** information of speech.

---

## Models Implemented
1. **Baseline Model**
   - Simple classifier (MLP / SVM) trained on extracted features

2. **Advanced Models**
   -  **CNN** → learns spatial patterns from spectrograms  
   -  **LSTM** → captures sequential/temporal dependencies  


