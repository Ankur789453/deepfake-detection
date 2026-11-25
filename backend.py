from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
from typing import Dict, Any
import threading
from pathlib import Path
import logging
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Deepfake Detection API",
    description="API for detecting deepfake/AI-generated images and videos",
    version="1.0.0"
)

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the deepfake detector
# Lazy model initialization
detector = None

detector_lock = threading.Lock()
inference_lock = threading.Lock()

BASE_DIR = Path(__file__).resolve().parent


def get_detector():
    """
    Load the deepfake model only when the first prediction is requested.
    """
    global detector

    if detector is None:
        with detector_lock:
            if detector is None:
                from model_inference import DeepfakeDetector

                model_path = BASE_DIR / "best_deepfake_model.pth"

                detector = DeepfakeDetector(
                    model_path=str(model_path)
                )

                logger.info("Deepfake detector loaded successfully")

    return detector

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Deepfake Detection API is running",
        "status": "healthy",
        "model_loaded": detector is not None
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "device": str(detector.device) if detector else "cpu"
    }

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Predict if an uploaded image is deepfake or real
    
    Args:
        file: Uploaded image file
        
    Returns:
        Prediction results
    """
    #if detector is None:
    #    raise HTTPException(status_code=500, detail="Model not loaded")
    current_detector = get_detector()
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Make prediction
        with inference_lock:
            prediction, confidence, details = current_detector.predict_image(
                temp_file_path
            )
        
        # Prepare response
        response = {
            "filename": file.filename,
            "file_type": "image",
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "is_deepfake": prediction == "Deepfake/AI Generated",
            "details": {
                "fake_probability": round(details.get("fake_probability", 0), 4),
                "real_probability": round(details.get("real_probability", 0), 4),
                "threshold": details.get("threshold", 0.56),
                "model_confidence": round(details.get("model_confidence", 0), 4)
            }
        }
        
        # Add error info if present
        if "error" in details:
            response["error"] = details["error"]
        
        logger.info(f"Image prediction completed: {file.filename} -> {prediction}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing image {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

@app.post("/predict/video")
async def predict_video(file: UploadFile = File(...), max_frames: int = 30) -> Dict[str, Any]:
    """
    Predict if an uploaded video is deepfake or real
    
    Args:
        file: Uploaded video file
        max_frames: Maximum number of frames to analyze
        
    Returns:
        Prediction results
    """
    #if detector is None:
    #   raise HTTPException(status_code=500, detail="Model not loaded")
    current_detector = get_detector()
    # Validate file type
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate max_frames parameter
    if max_frames < 1 or max_frames > 100:
        raise HTTPException(
            status_code=400, 
            detail="max_frames must be between 1 and 100"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Make prediction
        with inference_lock:
            prediction, confidence, details = current_detector.predict_video(
                temp_file_path, max_frames
            )
        
        # Prepare response
        response = {
            "filename": file.filename,
            "file_type": "video",
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "is_deepfake": prediction == "Deepfake/AI Generated",
            "details": {
                "average_fake_probability": round(details.get("average_fake_probability", 0), 4),
                "average_real_probability": round(details.get("average_real_probability", 0), 4),
                "frames_analyzed": details.get("frames_analyzed", 0),
                "fake_frames": details.get("fake_frames", 0),
                "real_frames": details.get("real_frames", 0),
                "fake_frame_percentage": round(details.get("fake_frame_percentage", 0), 2),
                "threshold": details.get("threshold", 0.55),
                "max_frames_requested": max_frames
            }
        }
        
        # Add sample frame predictions if available
        if "frame_predictions" in details:
            response["details"]["sample_frame_predictions"] = details["frame_predictions"]
        
        # Add error info if present
        if "error" in details:
            response["error"] = details["error"]
        
        logger.info(f"Video prediction completed: {file.filename} -> {prediction}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing video {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

@app.post("/predict/auto")
async def predict_auto(file: UploadFile = File(...), max_frames: int = 30) -> Dict[str, Any]:
    """
    Automatically detect file type and make appropriate prediction
    
    Args:
        file: Uploaded file (image or video)
        max_frames: Maximum frames for video analysis
        
    Returns:
        Prediction results
    """
    #if detector is None:
    #    raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Determine file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    if file_ext in video_extensions:
        return await predict_video(file, max_frames)
    elif file_ext in image_extensions:
        return await predict_image(file)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(image_extensions | video_extensions)}"
        )

@app.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "image_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
        "video_formats": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
        "max_video_frames": 100
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
