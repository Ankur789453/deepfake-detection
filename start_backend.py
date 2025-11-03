#!/usr/bin/env python3
"""
Startup script for the FastAPI backend server
"""

import os
import sys
import subprocess
import time
import requests

def check_model_exists():
    """Check if the trained model exists"""
    model_path = "best_deepfake_model.pth"
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        print("Please train the model first by running: python small_epochs.py")
        return False
    
    print(f"✅ Model file found: {model_path}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import torch
        import fastapi
        import uvicorn
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    print("=" * 50)
    print("🔍 Deepfake Detection Backend Server")
    print("=" * 50)
    
    # Check prerequisites
    if not check_model_exists():
        return
    
    if not check_dependencies():
        return
    
    # Start the server
    start_backend()

if __name__ == "__main__":
    main()
