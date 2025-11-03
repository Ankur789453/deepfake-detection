#!/usr/bin/env python3
"""
Startup script for the Streamlit frontend
"""

import os
import sys
import subprocess
import time
import requests

def check_backend_running():
    """Check if the backend server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
    except:
        pass
    
    print("⚠️ Backend server is not running")
    print("Please start the backend first by running: python start_backend.py")
    print("Or start it manually: python backend.py")
    return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import requests
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    print("Frontend will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the frontend\n")
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def main():
    print("=" * 50)
    print("🔍 Deepfake Detection Frontend")
    print("=" * 50)
    
    # Check prerequisites
    if not check_dependencies():
        return
    
    # Check if backend is running (optional warning)
    check_backend_running()
    
    # Start the frontend
    start_frontend()

if __name__ == "__main__":
    main()
