import os
import glob
import cv2
import numpy as np
from PIL import Image
import torch
from tqdm import tqdm
import random

def setup_opencv_detector():
    """
    Setup OpenCV face detector as backup
    """
    try:
        # Load Haar cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print("✓ OpenCV face detector loaded successfully")
        return face_cascade
    except Exception as e:
        print(f"✗ Error loading OpenCV detector: {e}")
        return None

def setup_mtcnn_detector():
    """
    Setup MTCNN detector with error handling
    """
    try:
        from facenet_pytorch import MTCNN
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")
        
        mtcnn = MTCNN(
            image_size=224,
            margin=20,
            min_face_size=20,
            thresholds=[0.3, 0.4, 0.4],  # Very lenient
            factor=0.709,
            post_process=False,
            device=device,
            keep_all=True
        )
        
        print("✓ MTCNN detector loaded successfully")
        return mtcnn
    except Exception as e:
        print(f"✗ Error loading MTCNN: {e}")
        print("Will use OpenCV as fallback")
        return None

def extract_face_opencv(image_path, face_cascade, scale_factor=1.1, min_neighbors=5):
    """
    Extract face using OpenCV Haar cascade
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(30, 30)
        )
        
        if len(faces) > 0:
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Add padding
            padding = 20
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img.shape[1], x + w + padding)
            y2 = min(img.shape[0], y + h + padding)
            
            # Crop face
            face_crop = img[y1:y2, x1:x2]
            
            # Convert to PIL and resize
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            face_pil = face_pil.resize((224, 224), Image.Resampling.LANCZOS)
            
            return face_pil
        
        return None
        
    except Exception as e:
        print(f"Error in OpenCV detection for {image_path}: {e}")
        return None

def extract_face_mtcnn(image_path, mtcnn, min_confidence=0.3):
    """
    Extract face using MTCNN
    """
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        
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
                
                # Crop face
                face_crop = img_array[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    face_pil = Image.fromarray(face_crop)
                    face_pil = face_pil.resize((224, 224), Image.Resampling.LANCZOS)
                    return face_pil
        
        return None
        
    except Exception as e:
        print(f"Error in MTCNN detection for {image_path}: {e}")
        return None

def extract_face_from_image(image_path, mtcnn=None, face_cascade=None):
    """
    Extract face using multiple methods (MTCNN first, OpenCV as backup)
    """
    face = None
    
    # Try MTCNN first if available
    if mtcnn is not None:
        face = extract_face_mtcnn(image_path, mtcnn)
        if face is not None:
            return face, "MTCNN"
    
    # Try OpenCV as backup
    if face_cascade is not None:
        face = extract_face_opencv(image_path, face_cascade)
        if face is not None:
            return face, "OpenCV"
    
    return None, "None"

def test_single_image(image_path, mtcnn=None, face_cascade=None):
    """
    Test face detection on a single image
    """
    print(f"\n=== Testing: {os.path.basename(image_path)} ===")
    
    try:
        # Load image
        img = Image.open(image_path)
        print(f"Image size: {img.size}")
        print(f"Image mode: {img.mode}")
        
        # Test MTCNN
        if mtcnn is not None:
            print("\nTesting MTCNN...")
            try:
                boxes, probs = mtcnn.detect(img)
                if boxes is not None:
                    print(f"MTCNN detected {len(boxes)} faces")
                    for i, (box, prob) in enumerate(zip(boxes, probs)):
                        print(f"  Face {i+1}: confidence = {prob:.3f}")
                else:
                    print("MTCNN: No faces detected")
            except Exception as e:
                print(f"MTCNN error: {e}")
        
        # Test OpenCV
        if face_cascade is not None:
            print("\nTesting OpenCV...")
            try:
                img_cv = cv2.imread(image_path)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                print(f"OpenCV detected {len(faces)} faces")
                for i, (x, y, w, h) in enumerate(faces):
                    print(f"  Face {i+1}: box = ({x}, {y}, {w}, {h})")
            except Exception as e:
                print(f"OpenCV error: {e}")
        
        # Try extraction
        face, method = extract_face_from_image(image_path, mtcnn, face_cascade)
        if face is not None:
            test_path = f"test_extracted_face_{method.lower()}.jpg"
            face.save(test_path)
            print(f"✓ Face extracted successfully using {method}")
            print(f"  Saved as: {test_path}")
            return True
        else:
            print("✗ No face could be extracted")
            return False
            
    except Exception as e:
        print(f"Error testing image: {e}")
        return False

def process_frames_directory(frames_dir, output_dir, mtcnn=None, face_cascade=None, category="", max_test=5):
    """
    Process frames with multiple detection methods
    """
    # Get all subdirectories
    video_dirs = [d for d in os.listdir(frames_dir) 
                  if os.path.isdir(os.path.join(frames_dir, d))]
    
    if not video_dirs:
        print(f"No video directories found in {frames_dir}")
        return 0
    
    print(f"Processing {len(video_dirs)} video directories for {category} category")
    
    total_faces = 0
    face_count = 0
    processed_images = 0
    mtcnn_count = 0
    opencv_count = 0
    
    # Test first few images for debugging
    test_count = 0
    
    for video_dir in tqdm(video_dirs, desc=f"Processing {category} videos"):
        video_path = os.path.join(frames_dir, video_dir)
        
        # Get all image files
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(video_path, ext)))
        
        # Test first few images for debugging
        if test_count < max_test and len(image_files) > 0:
            print(f"\n--- Testing images from {video_dir} ---")
            for i, img_path in enumerate(image_files[:2]):  # Test first 2 images
                if test_count >= max_test:
                    break
                test_single_image(img_path, mtcnn, face_cascade)
                test_count += 1
        
        # Create subdirectory for this video (similar to extract_frame.py)
        video_output_dir = os.path.join(output_dir, video_dir)
        os.makedirs(video_output_dir, exist_ok=True)
        
        video_face_count = 0
        
        # Process all images
        for image_path in image_files:
            processed_images += 1
            face, method = extract_face_from_image(image_path, mtcnn, face_cascade)
            
            if face is not None:
                # Count method used
                if method == "MTCNN":
                    mtcnn_count += 1
                elif method == "OpenCV":
                    opencv_count += 1
                
                # Save face in video subdirectory with video name prefix
                face_filename = f"{video_dir}_face_{video_face_count:04d}.jpg"
                face_path = os.path.join(video_output_dir, face_filename)
                
                face.save(face_path, 'JPEG', quality=95)
                video_face_count += 1
                face_count += 1
                total_faces += 1
    
    print(f"\n{category.capitalize()} processing summary:")
    print(f"  Total images: {processed_images}")
    print(f"  Total faces: {total_faces}")
    print(f"  MTCNN detections: {mtcnn_count}")
    print(f"  OpenCV detections: {opencv_count}")
    print(f"  Success rate: {total_faces/processed_images*100:.1f}%" if processed_images > 0 else "No images processed")
    
    return total_faces

def split_data_with_subdirs(real_dir, fake_dir, train_real_dir, train_fake_dir, 
                           val_real_dir, val_fake_dir, train_ratio=0.8):
    """
    Split extracted faces into train and validation sets, handling subdirectory structure
    """
    print("\n=== Splitting data into train/val sets ===")
    
    # Get all face images from subdirectories
    real_faces = []
    fake_faces = []
    
    # Collect all .jpg files from subdirectories in real_dir
    for root, dirs, files in os.walk(real_dir):
        for file in files:
            if file.lower().endswith('.jpg'):
                real_faces.append(os.path.join(root, file))
    
    # Collect all .jpg files from subdirectories in fake_dir
    for root, dirs, files in os.walk(fake_dir):
        for file in files:
            if file.lower().endswith('.jpg'):
                fake_faces.append(os.path.join(root, file))
    
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
    
    print(f"\n✓ Data split complete!")
    print(f"Training: {len(train_real)} real + {len(train_fake)} fake = {len(train_real) + len(train_fake)} total")
    print(f"Validation: {len(val_real)} real + {len(val_fake)} fake = {len(val_real) + len(val_fake)} total")

def main():
    """
    Main function with multiple detection methods
    """
    print("=== Multi-Method Face Extraction ===")
    
    # Set random seed
    random.seed(42)
    
    # Setup detectors
    print("\n1. Setting up face detectors...")
    mtcnn = setup_mtcnn_detector()
    face_cascade = setup_opencv_detector()
    
    if mtcnn is None and face_cascade is None:
        print("ERROR: No face detectors could be loaded!")
        return
    
    # Define paths
    real_frames_dir = "data/frames/real_frames"
    fake_frames_dir = "data/frames/fake_frames"
    
    temp_real_dir = "data/temp_faces/real_faces"
    temp_fake_dir = "data/temp_faces/fake_faces"
    
    os.makedirs(temp_real_dir, exist_ok=True)
    os.makedirs(temp_fake_dir, exist_ok=True)
    
    # Check directories
    if not os.path.exists(real_frames_dir):
        print(f"ERROR: {real_frames_dir} not found")
        return
    
    if not os.path.exists(fake_frames_dir):
        print(f"ERROR: {fake_frames_dir} not found")
        return
    
    # Process real frames
    print("\n2. Processing REAL frames...")
    real_faces = process_frames_directory(
        real_frames_dir, temp_real_dir, mtcnn, face_cascade, "real"
    )
    
    # Process fake frames
    print("\n3. Processing FAKE frames...")
    fake_faces = process_frames_directory(
        fake_frames_dir, temp_fake_dir, mtcnn, face_cascade, "fake"
    )
    
    print(f"\n=== Final Results ===")
    print(f"Real faces extracted: {real_faces}")
    print(f"Fake faces extracted: {fake_faces}")
    print(f"Total faces: {real_faces + fake_faces}")
    
    if real_faces > 0 or fake_faces > 0:
        print("\n✓ Face extraction successful!")
        
        # Split into train/val if we have both categories
        if real_faces > 0 and fake_faces > 0:
            # Use our own split function that handles subdirectories
            split_data_with_subdirs(
                temp_real_dir, temp_fake_dir,
                "data/crops/train/real", "data/crops/train/fake",
                "data/crops/val/real", "data/crops/val/fake"
            )
            
            # Clean up
            # import shutil
            # shutil.rmtree("data/temp_faces", ignore_errors=True)
            print("Ready for training!")
        else:
            print("Note: Only one category has faces. Check your dataset.")
    else:
        print("\n✗ Still no faces detected!")
        print("This suggests a deeper issue. Check:")
        print("1. Are the image files corrupted?")
        print("2. Try manual inspection of a few images")
        print("3. Consider using a different dataset")

if __name__ == "__main__":
    main()