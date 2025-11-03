#!/usr/bin/env python3
"""
Test script for the deepfake detection application
"""

import os
import sys
import time
import requests
from PIL import Image
import numpy as np

def test_model_loading():
    """Test if the model can be loaded"""
    print("🧠 Testing model loading...")
    try:
        from model_inference import DeepfakeDetector
        detector = DeepfakeDetector()
        print("✅ Model loaded successfully")
        print(f"   Device: {detector.device}")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_image_prediction():
    """Test image prediction functionality"""
    print("\n🖼️ Testing image prediction...")
    try:
        from model_inference import DeepfakeDetector
        detector = DeepfakeDetector()
        
        # Create a test image
        test_image = Image.new('RGB', (224, 224), color='red')
        prediction, confidence, details = detector.predict_image(test_image)
        
        print(f"✅ Image prediction successful")
        print(f"   Prediction: {prediction}")
        print(f"   Confidence: {confidence:.3f}")
        return True
    except Exception as e:
        print(f"❌ Image prediction failed: {e}")
        return False

def test_backend_startup():
    """Test if backend can start (just import test)"""
    print("\n🌐 Testing backend imports...")
    try:
        import backend
        print("✅ Backend imports successful")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def test_frontend_imports():
    """Test if frontend dependencies are available"""
    print("\n🎨 Testing frontend imports...")
    try:
        import streamlit
        print("✅ Streamlit import successful")
        return True
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

def test_backend_api():
    """Test backend API if it's running"""
    print("\n🔌 Testing backend API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API is running")
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            return True
        else:
            print(f"⚠️ Backend API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ Backend API is not running (this is OK for initial testing)")
        print("   Start it with: python start_backend.py")
        return False
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False

def test_dependencies():
    """Test all required dependencies"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'torch', 'torchvision', 'opencv-python', 'PIL', 
        'numpy', 'fastapi', 'uvicorn', 'streamlit', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies are installed")
        return True

def test_model_file():
    """Test if model file exists and is valid"""
    print("\n📁 Testing model file...")
    
    model_path = "best_deepfake_model.pth"
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        print("Train the model first with: python small_epochs.py")
        return False
    
    try:
        import torch
        checkpoint = torch.load(model_path, map_location='cpu')
        print(f"✅ Model file is valid")
        
        if 'val_acc' in checkpoint:
            print(f"   Validation accuracy: {checkpoint['val_acc']:.2f}%")
        if 'epoch' in checkpoint:
            print(f"   Trained epochs: {checkpoint['epoch']}")
        
        return True
    except Exception as e:
        print(f"❌ Model file is corrupted: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔍 Deepfake Detection Application - System Test")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Model File", test_model_file),
        ("Model Loading", test_model_loading),
        ("Image Prediction", test_image_prediction),
        ("Backend Imports", test_backend_startup),
        ("Frontend Imports", test_frontend_imports),
        ("Backend API", test_backend_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your application is ready to run.")
        print("\nNext steps:")
        print("1. Start backend: python start_backend.py")
        print("2. Start frontend: python start_frontend.py")
        print("3. Or use: start_app.bat (Windows)")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Please fix the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
