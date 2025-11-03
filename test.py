import cv2
import numpy as np
from PIL import Image
import os

def test_sample_image():
    """
    Test face detection on your sample image
    """
    print("=== Testing Your Sample Image ===")
    
    # First, let's find a sample image from your dataset
    sample_paths = [
        #"data/frames/fake_frames/000_003/000_003_frame_0000.jpg",
        "data/frames/fake_frames/000_003/000_003_frame_0001.jpg",
        "data/frames/fake_frames/000_003/000_003_frame_0002.jpg",
    ]
    
    # Find first existing image
    sample_image = None
    for path in sample_paths:
        if os.path.exists(path):
            sample_image = path
            break
    
    if not sample_image:
        print("No sample image found. Please check your paths.")
        print("Looking for images in:")
        for path in sample_paths:
            print(f"  {path}")
        return False
    
    print(f"Testing image: {sample_image}")
    
    # Test OpenCV detection (this should definitely work)
    print("\n1. Testing OpenCV Haar Cascade...")
    try:
        # Load cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Read image
        img = cv2.imread(sample_image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        print(f"Image shape: {img.shape}")
        
        # Detect faces with different parameters
        for scale in [1.05, 1.1, 1.2, 1.3]:
            for neighbors in [3, 4, 5, 6]:
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=scale,
                    minNeighbors=neighbors,
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    print(f"✓ Found {len(faces)} faces with scale={scale}, neighbors={neighbors}")
                    
                    # Save result with bounding boxes
                    img_with_faces = img.copy()
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img_with_faces, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(img_with_faces, f'Face', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # Save debug image
                    debug_path = f"debug_opencv_scale{scale}_neighbors{neighbors}.jpg"
                    cv2.imwrite(debug_path, img_with_faces)
                    print(f"  Debug image saved: {debug_path}")
                    
                    # Extract and save first face
                    x, y, w, h = faces[0]
                    padding = 20
                    x1 = max(0, x - padding)
                    y1 = max(0, y - padding)
                    x2 = min(img.shape[1], x + w + padding)
                    y2 = min(img.shape[0], y + h + padding)
                    
                    face_crop = img[y1:y2, x1:x2]
                    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                    face_pil = Image.fromarray(face_rgb)
                    face_pil = face_pil.resize((224, 224), Image.Resampling.LANCZOS)
                    
                    extracted_path = f"extracted_face_opencv_scale{scale}.jpg"
                    face_pil.save(extracted_path)
                    print(f"  Extracted face saved: {extracted_path}")
                    
                    return True
        
        print("✗ No faces detected with OpenCV")
        
    except Exception as e:
        print(f"Error with OpenCV: {e}")
    
    # Test MTCNN if available
    print("\n2. Testing MTCNN...")
    try:
        from facenet_pytorch import MTCNN
        import torch
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Try with very lenient settings
        mtcnn = MTCNN(
            image_size=224,
            margin=20,
            min_face_size=15,
            thresholds=[0.2, 0.3, 0.3],
            factor=0.709,
            post_process=False,
            device=device,
            keep_all=True
        )
        
        # Load image
        img_pil = Image.open(sample_image).convert('RGB')
        print(f"PIL image size: {img_pil.size}")
        
        # Detect faces
        boxes, probs = mtcnn.detect(img_pil)
        
        if boxes is not None:
            print(f"✓ MTCNN detected {len(boxes)} faces")
            for i, (box, prob) in enumerate(zip(boxes, probs)):
                print(f"  Face {i+1}: confidence = {prob:.3f}, box = {box}")
            
            # Save result with bounding boxes
            img_array = np.array(img_pil)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            for box, prob in zip(boxes, probs):
                x1, y1, x2, y2 = box.astype(int)
                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(img_bgr, f'{prob:.3f}', (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            debug_path = "debug_mtcnn.jpg"
            cv2.imwrite(debug_path, img_bgr)
            print(f"  Debug image saved: {debug_path}")
            
            # Extract first face
            best_idx = np.argmax(probs)
            box = boxes[best_idx]
            x1, y1, x2, y2 = box.astype(int)
            
            padding = 20
            h, w = img_array.shape[:2]
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(w, x2 + padding)
            y2 = min(h, y2 + padding)
            
            face_crop = img_array[y1:y2, x1:x2]
            face_pil = Image.fromarray(face_crop)
            face_pil = face_pil.resize((224, 224), Image.Resampling.LANCZOS)
            
            extracted_path = "extracted_face_mtcnn.jpg"
            face_pil.save(extracted_path)
            print(f"  Extracted face saved: {extracted_path}")
            
            return True
        else:
            print("✗ No faces detected with MTCNN")
            
    except Exception as e:
        print(f"Error with MTCNN: {e}")
        print("MTCNN might not be properly installed or configured")
    
    # Test with different image preprocessing
    print("\n3. Testing with image preprocessing...")
    try:
        img = cv2.imread(sample_image)
        
        # Try different preprocessing
        preprocessed_images = {
            "original": img,
            "histogram_eq": cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
            "gaussian_blur": cv2.GaussianBlur(img, (3, 3), 0),
            "contrast": cv2.convertScaleAbs(img, alpha=1.2, beta=10)
        }
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        for name, processed_img in preprocessed_images.items():
            if len(processed_img.shape) == 3:
                gray = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
            else:
                gray = processed_img
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                print(f"✓ Found {len(faces)} faces with {name} preprocessing")
                return True
        
        print("✗ No faces found with any preprocessing")
        
    except Exception as e:
        print(f"Error with preprocessing: {e}")
    
    return False

def check_opencv_installation():
    """
    Check if OpenCV is properly installed with face detection data
    """
    print("\n=== Checking OpenCV Installation ===")
    
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
        
        # Check if cascade file exists
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if os.path.exists(cascade_path):
            print(f"✓ Haar cascade found: {cascade_path}")
            
            # Try to load it
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if not face_cascade.empty():
                print("✓ Haar cascade loaded successfully")
                return True
            else:
                print("✗ Haar cascade failed to load")
        else:
            print(f"✗ Haar cascade not found at: {cascade_path}")
            
    except Exception as e:
        print(f"✗ OpenCV error: {e}")
    
    return False

def main():
    """
    Main testing function
    """
    print("=== Face Detection Diagnostic ===")
    
    # Check OpenCV first
    if not check_opencv_installation():
        print("Please reinstall OpenCV: pip install opencv-python")
        return
    
    # Test your sample image
    success = test_sample_image()
    
    if success:
        print("\n🎉 SUCCESS! Face detection is working!")
        print("You can now run the main extraction script.")
    else:
        print("\n❌ FAILED! No faces could be detected.")
        print("\nTroubleshooting steps:")
        print("1. Check if your image files are valid:")
        print("   - Try opening them manually")
        print("   - Check file sizes (should not be 0 bytes)")
        print("2. Try different detection parameters")
        print("3. Consider using a different dataset")
        print("4. Manual inspection: Are there clear frontal faces in the images?")

if __name__ == "__main__":
    main()