#!/usr/bin/env python
"""
Quick verification script to test if recording feature will work
"""

import sys
import subprocess

def check_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def main():
    print("="*60)
    print("RECORDING FEATURE VERIFICATION")
    print("="*60)
    print()
    
    all_good = True
    
    # Check required packages
    packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'librosa': 'librosa',
        'tensorflow': 'TensorFlow',
        'numpy': 'NumPy',
        'pickle': 'pickle'
    }
    
    print("Checking Python packages...")
    for pkg, name in packages.items():
        if check_package(pkg):
            print(f"  [OK] {name} installed")
        else:
            print(f"  [FAIL] {name} NOT installed")
            all_good = False
    
    print()
    
    # Check ffmpeg (optional but recommended for webm/ogg)
    print("Checking ffmpeg (optional, for webm/ogg support)...")
    if check_ffmpeg():
        print("  [OK] ffmpeg installed")
    else:
        print("  [WARN] ffmpeg NOT installed (optional)")
        print("    Recording in webm/ogg may not work without ffmpeg")
        print("    Install: 'choco install ffmpeg' (Windows) or 'brew install ffmpeg' (Mac)")
    
    print()
    
    # Check model files
    print("Checking model files...")
    import os
    
    model_files = {
        'Predict/SER_model.h5': 'Trained Model',
        'Predict/label_encoder.pkl': 'Label Encoder'
    }
    
    for file_path, name in model_files.items():
        if os.path.exists(file_path):
            print(f"  [OK] {name} found")
        else:
            print(f"  [FAIL] {name} NOT found at {file_path}")
            all_good = False
    
    print()
    
    # Check frontend files
    print("Checking frontend files...")
    frontend_files = {
        'frontend/index.html': 'HTML',
        'frontend/styles.css': 'CSS',
        'frontend/script.js': 'JavaScript',
        'app.py': 'Flask Backend'
    }
    
    for file_path, name in frontend_files.items():
        if os.path.exists(file_path):
            print(f"  [OK] {name} found")
        else:
            print(f"  [FAIL] {name} NOT found at {file_path}")
            all_good = False
    
    print()
    print("="*60)
    
    if all_good:
        print("[SUCCESS] ALL CHECKS PASSED!")
        print()
        print("Your recording feature should work!")
        print()
        print("To start the server:")
        print("  python app.py")
        print()
        print("Then open: http://localhost:5000")
        print("="*60)
        return 0
    else:
        print("[ERROR] SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before running the server.")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())

