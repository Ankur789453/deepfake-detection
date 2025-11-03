# 🔍 Deepfake Detection System

A comprehensive deepfake detection system built with PyTorch and ResNet50, featuring data preprocessing, model training, and a complete web application for real-time deepfake detection in images and videos.

## 🌟 Features

### 🧠 Machine Learning Pipeline
- **ResNet50-based Architecture**: Deep learning model for accurate deepfake detection
- **Face Detection & Extraction**: Automated face cropping using OpenCV and FaceNet-PyTorch
- **Data Preprocessing**: Complete pipeline from raw videos to training-ready datasets
- **Model Training**: Configurable training with checkpointing and validation

### 🌐 Web Application
- **Real-time Detection**: Upload images/videos for instant deepfake analysis
- **REST API**: FastAPI backend with comprehensive endpoints
- **Modern UI**: Beautiful Streamlit interface with confidence scoring
- **Batch Processing**: Support for multiple file formats and video frame analysis

### 📊 Data Processing
- **Video Frame Extraction**: Extract frames from videos at configurable FPS
- **Face Cropping**: Automated face detection and cropping for training
- **CSV Labeling**: Automated dataset labeling and organization
- **Data Validation**: Testing utilities for data integrity

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DEEPFAKE DETECTION SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📁 DATA PIPELINE          🧠 ML PIPELINE          🌐 WEB APP │
│  ┌─────────────────┐      ┌─────────────────┐      ┌────────┐ │
│  │ Raw Videos      │ ──►  │ Model Training  │ ──►  │FastAPI │ │
│  │ Frame Extract   │      │ Face Detection  │      │Backend │ │
│  │ Face Cropping   │      │ ResNet50        │      │        │ │
│  │ CSV Labeling    │      │ Validation      │      │        │ │
│  └─────────────────┘      └─────────────────┘      └────────┘ │
│           │                         │                    │    │
│           ▼                         ▼                    ▼    │
│  ┌─────────────────┐      ┌─────────────────┐      ┌────────┐ │
│  │ Processed Data  │      │ Trained Model   │      │Streamlit│ │
│  │ face_labels.csv │      │ .pth checkpoint │      │Frontend│ │
│  └─────────────────┘      └─────────────────┘      └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
deepfake_prediction/
├── 📊 DATA & PREPROCESSING
│   ├── data/
│   │   ├── raw/                     # Raw video files (real/fake)
│   │   ├── frames/                  # Extracted frames
│   │   ├── crops/                   # Cropped face images
│   │   ├── temp_faces/             # Temporary face processing
│   │   └── face_labels.csv         # Dataset labels
│   ├── test_data/
│   │   └── Real/                   # Test images
│   ├── extract_frame.py            # Video frame extraction
│   ├── crop_faces.py               # Face detection & cropping
│   ├── improved_extract_faces.py   # Enhanced face extraction
│   ├── csv_label.py                # Dataset labeling
│   └── pytorch.py                  # PyTorch dataset utilities
│
├── 🧠 MACHINE LEARNING
│   ├── best_deepfake_model.pth     # Trained ResNet50 model (94MB)
│   ├── small_epochs.py             # Model training script
│   ├── model_inference.py          # Inference utilities
│   ├── model_test.py               # Model testing
│   └── test.py                     # Face detection testing
│
├── 🌐 WEB APPLICATION
│   ├── backend.py                  # FastAPI REST API server
│   ├── streamlit_app.py            # Streamlit web interface
│   ├── start_backend.py            # Backend startup script
│   ├── start_frontend.py           # Frontend startup script
│   ├── start_app.bat               # Windows batch launcher
│   └── test_app.py                 # Application testing
│
├── 📋 CONFIGURATION
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # This documentation
│   ├── README_APP.md               # Web app documentation
│   └── myenv/                      # Virtual environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (optional, for faster training/inference)
- FFmpeg (for video processing)

### Installation

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd deepfake_prediction
pip install -r requirements.txt
```

2. **Quick Launch (Windows)**
```bash
# Launch both backend and frontend
start_app.bat
```

3. **Manual Launch**
```bash
# Terminal 1: Start backend
python start_backend.py

# Terminal 2: Start frontend  
python start_frontend.py
```

4. **Access Application**
- Web Interface: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📊 Data Pipeline

### 1. Data Preparation
```bash
# Extract frames from videos
python extract_frame.py

# Crop faces from frames
python crop_faces.py

# Generate CSV labels
python csv_label.py
```

### 2. Data Structure
- **Raw Videos**: Place in `data/raw/real/` and `data/raw/fake/`
- **Extracted Frames**: Automatically saved to `data/frames/`
- **Cropped Faces**: Processed faces saved to `data/crops/`
- **Labels**: CSV file with paths and labels generated

## 🧠 Model Training

### Training Process
```bash
# Train the model
python small_epochs.py
```

### Model Architecture
- **Base**: ResNet50 (pretrained on ImageNet)
- **Input Size**: 224x224 RGB images
- **Output**: Binary classification (Real/Fake)
- **Threshold**: 51% for deepfake classification

### Model Testing
```bash
# Test trained model
python model_test.py path/to/test/image.jpg

# Test face detection
python test.py
```

## 🌐 Web Application

### Features
- **Multi-format Support**: Images (JPG, PNG, BMP, TIFF, WebP) and Videos (MP4, AVI, MOV, MKV, WMV, FLV, WebM)
- **Real-time Processing**: Instant results with confidence scores
- **Video Analysis**: Frame-by-frame analysis with aggregated results
- **API Access**: RESTful endpoints for programmatic access

### API Endpoints

#### Health Check
```http
GET /health
Response: {"status": "healthy", "model_loaded": true}
```

#### Image Prediction
```http
POST /predict/image
Content-Type: multipart/form-data
Body: file=<image_file>

Response:
{
  "filename": "test.jpg",
  "file_type": "image", 
  "prediction": "Real",
  "confidence": 0.8542,
  "is_deepfake": false,
  "details": {
    "fake_probability": 0.1458,
    "real_probability": 0.8542,
    "threshold": 0.51,
    "model_confidence": 0.8542
  }
}
```

#### Video Prediction
```http
POST /predict/video
Content-Type: multipart/form-data
Body: file=<video_file>, max_frames=30

Response:
{
  "filename": "test.mp4",
  "file_type": "video",
  "prediction": "Deepfake/AI Generated",
  "confidence": 0.7234,
  "is_deepfake": true,
  "video_details": {
    "total_frames_analyzed": 30,
    "frames_detected_fake": 18,
    "frames_detected_real": 12,
    "average_confidence": 0.7234
  }
}
```

#### Auto Detection
```http
POST /predict/auto
Content-Type: multipart/form-data
Body: file=<image_or_video_file>
```

## ⚙️ Configuration

### Model Settings
```python
# In model_inference.py
THRESHOLD = 0.51          # Classification threshold
IMAGE_SIZE = 224          # Input image size
DEVICE = "auto"           # cuda/cpu auto-detection
```

### Video Processing
```python
# In streamlit_app.py
MAX_FRAMES = 30           # Maximum frames to analyze
FRAME_DISTRIBUTION = "even"  # Frame sampling method
```

### Face Detection
```python
# In crop_faces.py
SCALE_FACTOR = 1.1        # Face detection scale
MIN_NEIGHBORS = 5         # Minimum face neighbors
MIN_SIZE = (30, 30)       # Minimum face size
```

## 🔧 Development

### Adding New Features

1. **Backend API**: Extend `backend.py` with new endpoints
2. **Frontend UI**: Modify `streamlit_app.py` for new interfaces  
3. **Model Logic**: Update `model_inference.py` for new functionality
4. **Data Processing**: Add scripts in the root directory

### Testing

```bash
# Test model inference
python model_inference.py

# Test web application
python test_app.py

# Test face detection
python test.py

# Manual API testing
curl -X POST "http://localhost:8000/predict/image" \
     -F "file=@test_image.jpg"
```

### Performance Optimization

1. **GPU Acceleration**: Ensure CUDA is available
2. **Batch Processing**: Process multiple files via API
3. **Video Optimization**: Adjust `max_frames` parameter
4. **Model Caching**: Model loads once and stays in memory

## 📈 Model Performance

### Training Metrics
- **Architecture**: ResNet50 with custom classification head
- **Dataset**: Custom real/fake face dataset
- **Training**: Progressive epochs with validation
- **Accuracy**: Achieved through iterative training

### Inference Speed
- **GPU**: ~50ms per image
- **CPU**: ~200ms per image  
- **Video**: Depends on frame count and hardware

## 🔒 Security & Privacy

- **Temporary Processing**: Files processed in temp directories
- **No Permanent Storage**: Files deleted after processing
- **CORS Enabled**: For development (restrict in production)
- **API Rate Limiting**: Consider implementing for production

## 🐛 Troubleshooting

### Common Issues

#### Model Loading Errors
```bash
# Verify model file
python -c "import torch; torch.load('best_deepfake_model.pth')"

# Check file size (should be ~94MB)
ls -lh best_deepfake_model.pth
```

#### Face Detection Issues
```bash
# Test face detection
python test.py

# Verify OpenCV installation
python -c "import cv2; print(cv2.__version__)"
```

#### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check port availability
netstat -an | findstr :8000
```

#### Dependencies Issues
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

## 📚 Dataset Requirements

### Training Data Structure
```
data/raw/
├── real/           # Real videos
│   ├── video1.mp4
│   ├── video2.avi
│   └── ...
└── fake/           # Deepfake videos
    ├── video1.mp4
    ├── video2.avi
    └── ...
```

### Supported Formats
- **Videos**: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- **Images**: JPG, JPEG, PNG, BMP, TIFF, WebP
- **Minimum Resolution**: 224x224 pixels recommended

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation for API changes

## 📄 License

This project is for educational and research purposes. Please ensure compliance with applicable laws and regulations when using deepfake detection technology.

## 🙏 Acknowledgments

- **PyTorch Team**: For the excellent deep learning framework
- **OpenCV Community**: For computer vision utilities
- **Streamlit**: For the amazing web app framework
- **FastAPI**: For the high-performance API framework

## 📞 Support

For issues and questions:

1. **Check Documentation**: Review this README and README_APP.md
2. **Run Tests**: Execute test scripts to verify setup
3. **Check Logs**: Review console output for error details
4. **Verify Dependencies**: Ensure all requirements are installed

### Common Solutions
- **CUDA Issues**: Install appropriate CUDA toolkit version
- **Memory Errors**: Reduce batch size or video frame count
- **Port Conflicts**: Change ports in startup scripts
- **Model Errors**: Re-download or retrain the model

---

**🚀 Happy Deepfake Detection!** 

*Built with ❤️ for AI safety and media authenticity*
