import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import numpy as np
import os
from typing import Union, Tuple, List
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepfakeDetector:
    """
    Deepfake detection model wrapper for inference
    """
    
    def __init__(self, model_path: str = "best_deepfake_model.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = None
        self.transform = None
        self.face_cascade = None
        
        # Initialize components
        self._load_model()
        self._setup_transforms()
        self._setup_face_detector()
        
        logger.info(f"DeepfakeDetector initialized on device: {self.device}")
    
    def _load_model(self):
    """Load the trained model."""

    try:
        # Optimize CPU execution for low-memory hosting
        torch.set_num_threads(1)

        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass

        # Use CPU on Render
        self.device = torch.device("cpu")

        # Check whether model file exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}"
            )

        logger.info("Creating ResNet50 architecture...")

        # Create model architecture
        self.model = models.resnet50(weights=None)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, 2)

        logger.info("Loading trained weights...")

        # Load checkpoint
        checkpoint = torch.load(
            self.model_path,
            map_location="cpu",
            weights_only=True,
            mmap=True
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        if "val_acc" in checkpoint:
            logger.info(
                f"Model validation accuracy: {checkpoint['val_acc']:.2f}%"
            )

        del checkpoint

        import gc
        gc.collect()

        # Prepare model for inference
        self.model.to(self.device)
        self.model.eval()

        logger.info("Model loaded successfully on CPU")

    except Exception:
        logger.exception("Error loading model")
        raise
    
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
    
    def _setup_face_detector(self):
        """Setup OpenCV face detector"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            logger.info("Face detector loaded successfully")
        except Exception as e:
            logger.error(f"Error loading face detector: {e}")
            self.face_cascade = None
    
    def extract_face(self, image: Union[str, np.ndarray, Image.Image]) -> Image.Image:
        """
        Extract face from image using OpenCV
        
        Args:
            image: Input image (file path, numpy array, or PIL Image)
            
        Returns:
            PIL Image of extracted face or original image if no face found
        """
        try:
            # Convert input to PIL Image
            if isinstance(image, str):
                pil_image = Image.open(image).convert('RGB')
            elif isinstance(image, np.ndarray):
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            elif isinstance(image, Image.Image):
                pil_image = image.convert('RGB')
            else:
                raise ValueError("Unsupported image type")
            
            # Convert to OpenCV format for face detection
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    # Get the largest face
                    largest_face = max(faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = largest_face
                    
                    # Add padding
                    padding = 20
                    x1 = max(0, x - padding)
                    y1 = max(0, y - padding)
                    x2 = min(cv_image.shape[1], x + w + padding)
                    y2 = min(cv_image.shape[0], y + h + padding)
                    
                    # Crop face
                    face_crop = cv_image[y1:y2, x1:x2]
                    
                    # Convert back to PIL
                    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                    face_pil = Image.fromarray(face_rgb)
                    
                    logger.info("Face extracted successfully")
                    return face_pil
            
            # If no face detected, return original image
            logger.warning("No face detected, using original image")
            return pil_image
            
        except Exception as e:
            logger.error(f"Error extracting face: {e}")
            # Return original image as fallback
            if isinstance(image, str):
                return Image.open(image).convert('RGB')
            elif isinstance(image, Image.Image):
                return image.convert('RGB')
            else:
                return Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8))
    
    def predict_image(self, image: Union[str, np.ndarray, Image.Image]) -> Tuple[str, float, dict]:
        """
        Predict if an image is deepfake or real
        
        Args:
            image: Input image (file path, numpy array, or PIL Image)
            
        Returns:
            Tuple of (prediction, confidence, details)
        """
        try:
            # Extract face
            face_image = self.extract_face(image)
            
            # Preprocess
            input_tensor = self.transform(face_image).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.inference_mode():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                fake_prob = probabilities[0][1].item()  # Probability of being fake
                real_prob = probabilities[0][0].item()  # Probability of being real
            
            # Determine prediction based on threshold (>51% fake)
            if fake_prob > 0.55:
                prediction = "Deepfake/AI Generated"
                confidence = fake_prob
            else:
                prediction = "Real"
                confidence = real_prob
            
            details = {
                "fake_probability": fake_prob,
                "real_probability": real_prob,
                "threshold": 0.51,
                "model_confidence": max(fake_prob, real_prob)
            }
            
            logger.info(f"Prediction: {prediction}, Confidence: {confidence:.3f}")
            return prediction, confidence, details
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return "Error", 0.0, {"error": str(e)}
    
    def extract_video_frames(self, video_path: str, max_frames: int = 30) -> List[np.ndarray]:
        """
        Extract frames from video for analysis
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of video frames as numpy arrays
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame interval to get evenly distributed frames
            if total_frames <= max_frames:
                frame_interval = 1
            else:
                frame_interval = total_frames // max_frames
            
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frames.append(frame)
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from video")
            
        except Exception as e:
            logger.error(f"Error extracting video frames: {e}")
        
        return frames
    
    def predict_video(self, video_path: str, max_frames: int = 30) -> Tuple[str, float, dict]:
        """
        Predict if a video is deepfake or real by analyzing multiple frames
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to analyze
            
        Returns:
            Tuple of (prediction, confidence, details)
        """
        try:
            # Extract frames
            frames = self.extract_video_frames(video_path, max_frames)
            
            if not frames:
                return "Error", 0.0, {"error": "No frames could be extracted from video"}
            
            # Analyze each frame
            fake_scores = []
            real_scores = []
            frame_predictions = []
            
            for i, frame in enumerate(frames):
                try:
                    prediction, confidence, details = self.predict_image(frame)
                    
                    fake_scores.append(details['fake_probability'])
                    real_scores.append(details['real_probability'])
                    frame_predictions.append({
                        'frame': i,
                        'prediction': prediction,
                        'fake_prob': details['fake_probability'],
                        'real_prob': details['real_probability']
                    })
                    
                except Exception as e:
                    logger.warning(f"Error analyzing frame {i}: {e}")
                    continue
            
            if not fake_scores:
                return "Error", 0.0, {"error": "No frames could be analyzed"}
            
            # Calculate overall prediction
            avg_fake_prob = np.mean(fake_scores)
            avg_real_prob = np.mean(real_scores)
            
            # Count frame predictions
            fake_frame_count = sum(1 for pred in frame_predictions if pred['prediction'] == "Deepfake/AI Generated")
            total_frames_analyzed = len(frame_predictions)
            
            # Overall prediction based on average probability
            if avg_fake_prob > 0.51:
                prediction = "Deepfake/AI Generated"
                confidence = avg_fake_prob
            else:
                prediction = "Real"
                confidence = avg_real_prob
            
            details = {
                "average_fake_probability": avg_fake_prob,
                "average_real_probability": avg_real_prob,
                "frames_analyzed": total_frames_analyzed,
                "fake_frames": fake_frame_count,
                "real_frames": total_frames_analyzed - fake_frame_count,
                "fake_frame_percentage": (fake_frame_count / total_frames_analyzed) * 100,
                "threshold": 0.51,
                "frame_predictions": frame_predictions[:10]  # Show first 10 frame details
            }
            
            logger.info(f"Video prediction: {prediction}, Avg confidence: {confidence:.3f}")
            return prediction, confidence, details
            
        except Exception as e:
            logger.error(f"Error in video prediction: {e}")
            return "Error", 0.0, {"error": str(e)}

# Convenience function for quick testing
def quick_predict(file_path: str, model_path: str = "best_deepfake_model.pth") -> dict:
    """
    Quick prediction function for testing
    
    Args:
        file_path: Path to image or video file
        model_path: Path to model file
        
    Returns:
        Dictionary with prediction results
    """
    detector = DeepfakeDetector(model_path)
    
    # Check if it's a video or image
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in video_extensions:
        prediction, confidence, details = detector.predict_video(file_path)
    else:
        prediction, confidence, details = detector.predict_image(file_path)
    
    return {
        "file_path": file_path,
        "prediction": prediction,
        "confidence": confidence,
        "details": details
    }

if __name__ == "__main__":
    # Test the detector
    detector = DeepfakeDetector()
    print("DeepfakeDetector initialized successfully!")
    print(f"Model loaded on device: {detector.device}")
