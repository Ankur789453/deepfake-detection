import os
import glob
import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch
from tqdm import tqdm
import random
import matplotlib.pyplot as plt

def setup_face_detector():
    """
    Initialize MTCNN face detector with more lenient settings
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # More lenient settings for better detection
    mtcnn = MTCNN(
        image_size=224,
        margin=20,
        min_face_size=40,  # Reduced from 80 to detect smaller faces
        thresholds=[0.5, 0.6, 0.6],  # Reduced thresholds for more detections
        factor=0.709,
        post_process=False,
        device=device,
        keep_all=True  # Keep all detected faces
    )
    
    return mtcnn

def test_single_image(image_path, mtcnn, show_debug=True):
    """
    Test face detection on a single image for debugging
    """
    try:
        print(f"\nTesting image: {image_path}")
        
        # Load image
        img = Image.open(image_path).convert('RGB')
        print(f"Image size: {img.size}")
        
        # Detect faces
        boxes, probs = mtcnn.detect(img)
        
        print(f"Boxes: {boxes}")
        print(f"Probabilities: {probs}")
        
        if boxes is not None:
            print(f"Found {len(boxes)} faces")
            for i, (box, prob) in enumerate(zip(boxes, probs)):
                print(f"Face {i}: confidence = {prob:.3f}, box = {box}")
        else:
            print("No faces detected")
        
        # Show image with bounding boxes if debug is enabled
        if show_debug and boxes is not None:
            img_array = np.array(img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            for box, prob in zip(boxes, probs):
                x1, y1, x2, y2 = box.astype(int)
                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img_bgr, f'{prob:.3f}', (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Save debug image
            debug_path = "debug_face_detection.jpg"
            cv2.imwrite(debug_path, img_bgr)
            print(f"Debug image saved to: {debug_path}")
        
        return boxes, probs
        
    except Exception as e:
        print(f"Error testing image {image_path}: {str(e)}")
        return None, None

def extract_face_from_image(image_path, mtcnn, min_confidence=0.5):  # Reduced confidence
    """
    Extract face from a single image with improved error handling
    """
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        
        # Check image size
        if img.size[0] < 50 or img.size[1] < 50:
            print(f"Image too small: {img.size}")
            return None
        
        # Detect faces
        boxes, probs = mtcnn.detect(img)
        
        if boxes is not None and probs is not None and len(boxes) > 0:
            # Find face with highest confidence
            best_idx = np.argmax(probs)
            
            if probs[best_idx] >= min_confidence:
                box = boxes[best_idx]
                
                # Convert to numpy array for cropping
                img_array = np.array(img)
                
                # Extract coordinates with padding
                x1, y1, x2, y2 = box.astype(int)
                padding = 20
                
                h, w = img_array.shape[:2]
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)
                
                # Check if crop would be valid
                if x2 <= x1 or y2 <= y1:
                    print(f"Invalid crop coordinates: ({x1},{y1}) to ({x2},{y2})")
                    return None
                
                # Crop face
                face_crop = img_array[y1:y2, x1:x2]
                
                # Check if crop is not empty
                if face_crop.size == 0:
                    print("Empty face crop")
                    return None
                
                # Convert back to PIL
                face_pil = Image.fromarray(face_crop)
                
                # Resize to standard size
                face_pil = face_pil.resize((224, 224), Image.Resampling.LANCZOS)
                
                return face_pil
        
        return None
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def process_frames_directory(frames_dir, output_dir, mtcnn, category, debug_mode=False):
    """
    Process all frame directories and extract faces with improved debugging
    """
    # Get all subdirectories (each represents a video)
    video_dirs = [d for d in os.listdir(frames_dir) 
                  if os.path.isdir(os.path.join(frames_dir, d))]
    
    if not video_dirs:
        print(f"No video directories found in {frames_dir}")
        return 0
    
    print(f"Processing {len(video_dirs)} video directories for {category} category")
    
    total_faces = 0
    face_count = 0
    processed_images = 0
    
    # Process each video directory
    for video_dir in tqdm(video_dirs, desc=f"Processing {category} videos"):
        video_path = os.path.join(frames_dir, video_dir)
        
        print(f"\nProcessing video directory: {video_dir}")
        
        # Get all image files in this video directory
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(video_path, ext)))
        
        print(f"Found {len(image_files)} images in {video_dir}")
        
        if debug_mode and len(image_files) > 0:
            # Test first image for debugging
            print(f"Testing first image for debugging...")
            test_single_image(image_files[0], mtcnn, show_debug=True)
        
        # Process each frame
        for image_path in image_files:
            processed_images += 1
            face = extract_face_from_image(image_path, mtcnn)
            
            if face is not None:
                # Save face with unique filename
                face_filename = f"{category}_{face_count:06d}.jpg"
                face_path = os.path.join(output_dir, face_filename)
                
                face.save(face_path, 'JPEG', quality=95)
                face_count += 1
                total_faces += 1
                
                if debug_mode and total_faces <= 5:
                    print(f"Saved face: {face_path}")
        
        print(f"Video {video_dir}: {len(image_files)} images processed")
    
    print(f"Total images processed: {processed_images}")
    print(f"Total faces extracted: {total_faces}")
    return total_faces

def debug_dataset_structure(frames_dir):
    """
    Debug function to check dataset structure
    """
    print(f"\n=== Debugging dataset structure: {frames_dir} ===")
    
    if not os.path.exists(frames_dir):
        print(f"ERROR: Directory does not exist: {frames_dir}")
        return False
    
    # List all items in frames directory
    items = os.listdir(frames_dir)
    print(f"Items in {frames_dir}: {items}")
    
    # Check each subdirectory
    for item in items:
        item_path = os.path.join(frames_dir, item)
        if os.path.isdir(item_path):
            print(f"\nSubdirectory: {item}")
            
            # Count images in subdirectory
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
            image_count = 0
            sample_images = []
            
            for ext in image_extensions:
                images = glob.glob(os.path.join(item_path, ext))
                image_count += len(images)
                if len(images) > 0 and len(sample_images) < 3:
                    sample_images.extend(images[:3-len(sample_images)])
            
            print(f"  Images found: {image_count}")
            print(f"  Sample images: {sample_images[:3]}")
            
            # Check if images can be opened
            for img_path in sample_images:
                try:
                    img = Image.open(img_path)
                    print(f"  {os.path.basename(img_path)}: {img.size}, {img.mode}")
                except Exception as e:
                    print(f"  ERROR loading {img_path}: {e}")
    
    return True

def split_data(real_dir, fake_dir, train_real_dir, train_fake_dir, 
               val_real_dir, val_fake_dir, train_ratio=0.8):
    """
    Split extracted faces into train and validation sets
    """
    print("\n=== Splitting data into train/val sets ===")
    
    # Get all face images
    real_faces = glob.glob(os.path.join(real_dir, "*.jpg"))
    fake_faces = glob.glob(os.path.join(fake_dir, "*.jpg"))
    
    print(f"Real faces: {len(real_faces)}")
    print(f"Fake faces: {len(fake_faces)}")
    
    if len(real_faces) == 0 or len(fake_faces) == 0:
        print("ERROR: No faces found to split!")
        return
    
    # Shuffle the data
    random.shuffle(real_faces)
    random.shuffle(fake_faces)
    
    # Calculate split indices
    real_train_count = int(len(real_faces) * train_ratio)
    fake_train_count = int(len(fake_faces) * train_ratio)
    
    # Split real faces
    train_real = real_faces[:real_train_count]
    val_real = real_faces[real_train_count:]
    
    # Split fake faces
    train_fake = fake_faces[:fake_train_count]
    val_fake = fake_faces[fake_train_count:]
    
    print(f"\nTrain set: {len(train_real)} real, {len(train_fake)} fake")
    print(f"Val set: {len(val_real)} real, {len(val_fake)} fake")
    
    # Create directories
    os.makedirs(train_real_dir, exist_ok=True)
    os.makedirs(train_fake_dir, exist_ok=True)
    os.makedirs(val_real_dir, exist_ok=True)
    os.makedirs(val_fake_dir, exist_ok=True)
    
    # Copy files to train directories
    for i, face_path in enumerate(tqdm(train_real, desc="Copying train real")):
        dst_path = os.path.join(train_real_dir, f"real_train_{i:06d}.jpg")
        img = Image.open(face_path)
        img.save(dst_path)
    
    for i, face_path in enumerate(tqdm(train_fake, desc="Copying train fake")):
        dst_path = os.path.join(train_fake_dir, f"fake_train_{i:06d}.jpg")
        img = Image.open(face_path)
        img.save(dst_path)
    
    # Copy files to validation directories
    for i, face_path in enumerate(tqdm(val_real, desc="Copying val real")):
        dst_path = os.path.join(val_real_dir, f"real_val_{i:06d}.jpg")
        img = Image.open(face_path)
        img.save(dst_path)
    
    for i, face_path in enumerate(tqdm(val_fake, desc="Copying val fake")):
        dst_path = os.path.join(val_fake_dir, f"fake_val_{i:06d}.jpg")
        img = Image.open(face_path)
        img.save(dst_path)

def main():
    """
    Main function to extract faces from frames with debugging
    """
    print("=== Improved Face Extraction from Frames ===")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Define paths
    real_frames_dir = "data/frames/real_frames"
    fake_frames_dir = "data/frames/fake_frames"
    
    # Debug dataset structure first
    print("1. Debugging dataset structure...")
    real_ok = debug_dataset_structure(real_frames_dir)
    fake_ok = debug_dataset_structure(fake_frames_dir)
    
    if not real_ok or not fake_ok:
        print("Please fix dataset structure issues before continuing.")
        return
    
    # Setup face detector
    print("\n2. Initializing face detector...")
    mtcnn = setup_face_detector()
    
    # Temporary directories for all extracted faces
    temp_real_dir = "data/temp_faces/real_faces"
    temp_fake_dir = "data/temp_faces/fake_faces"
    
    os.makedirs(temp_real_dir, exist_ok=True)
    os.makedirs(temp_fake_dir, exist_ok=True)
    
    # Extract faces with debug mode enabled for first run
    print("\n3. Extracting faces from REAL frames...")
    real_faces = process_frames_directory(
        real_frames_dir, temp_real_dir, mtcnn, "real", debug_mode=True
    )
    
    print("\n4. Extracting faces from FAKE frames...")
    fake_faces = process_frames_directory(
        fake_frames_dir, temp_fake_dir, mtcnn, "fake", debug_mode=True
    )
    
    print(f"\n=== Face Extraction Summary ===")
    print(f"Real faces extracted: {real_faces}")
    print(f"Fake faces extracted: {fake_faces}")
    print(f"Total faces: {real_faces + fake_faces}")
    
    if real_faces == 0 and fake_faces == 0:
        print("\nERROR: No faces detected in any category!")
        print("Possible issues:")
        print("1. Images might be corrupted or unreadable")
        print("2. Images might not contain visible faces")
        print("3. Face detection parameters might be too strict")
        print("4. MTCNN model might have issues")
        print("\nTry running with even lower confidence threshold or check sample images manually.")
        return
    
    if real_faces == 0 or fake_faces == 0:
        print("Warning: No faces detected in one category!")
        print("Consider checking your videos or adjusting detection parameters.")
        
        # Continue with available data
        if real_faces > 0 or fake_faces > 0:
            print("Continuing with available faces...")
    
    # Split into train/val sets only if we have faces
    if real_faces > 0 and fake_faces > 0:
        split_data(
            temp_real_dir, temp_fake_dir,
            "data/crops/train/real", "data/crops/train/fake",
            "data/crops/val/real", "data/crops/val/fake"
        )
        
        print("\n=== Final Dataset Structure ===")
        train_real_count = len(glob.glob("data/crops/train/real/*.jpg"))
        train_fake_count = len(glob.glob("data/crops/train/fake/*.jpg"))
        val_real_count = len(glob.glob("data/crops/val/real/*.jpg"))
        val_fake_count = len(glob.glob("data/crops/val/fake/*.jpg"))
        
        print(f"Training set: {train_real_count} real, {train_fake_count} fake")
        print(f"Validation set: {val_real_count} real, {val_fake_count} fake")
        
        # Clean up temp directories
        import shutil
        shutil.rmtree("data/temp_faces", ignore_errors=True)
        
        print("\nFace extraction complete! Ready for training.")
    else:
        print("\nSkipping train/val split due to insufficient data.")
        print("Please fix the issues and run again.")

if __name__ == "__main__":
    main()