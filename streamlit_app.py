import streamlit as st
import requests
import json
from PIL import Image
import io
import time
import os

# Page configuration
st.set_page_config(
    page_title="Deepfake Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    
    .real-result {
        background-color: #d4edda;
        border-left-color: #28a745;
        color: #155724;
    }
    
    .fake-result {
        background-color: #f8d7da;
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    .error-result {
        background-color: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .upload-section {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        background-color: #fafafa;
    }
    
    .feature-box {
        background-color: #000000;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
        border-right: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = "https://deepfake-backend-qe2c.onrender.com"

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def make_prediction(file, file_type, max_frames=30):
    """Make prediction request to backend"""
    try:
        files = {"file": (file.name, file, file.type)}
        
        if file_type == "auto":
            endpoint = f"{BACKEND_URL}/predict/auto"
            params = {"max_frames": max_frames}
        elif file_type == "image":
            endpoint = f"{BACKEND_URL}/predict/image"
            params = {}
        elif file_type == "video":
            endpoint = f"{BACKEND_URL}/predict/video"
            params = {"max_frames": max_frames}
        
        response = requests.post(endpoint, files=files, params=params, timeout=60)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return None, "Request timeout. The file might be too large or processing is taking too long."
    except Exception as e:
        return None, f"Error making request: {str(e)}"

def display_prediction_results(result):
    """Display prediction results in a formatted way"""
    if not result:
        return
    
    prediction = result.get("prediction", "Unknown")
    confidence = result.get("confidence", 0)
    is_deepfake = result.get("is_deepfake", False)
    details = result.get("details", {})
    
    # Main result
    if prediction == "Error":
        st.markdown(f"""
        <div class="result-box error-result">
            <h3>⚠️ Error in Processing</h3>
            <p><strong>Error:</strong> {result.get('error', 'Unknown error occurred')}</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Success result
    result_class = "fake-result" if is_deepfake else "real-result"
    icon = "🚨" if is_deepfake else "✅"
    
    st.markdown(f"""
    <div class="result-box {result_class}">
        <h3>{icon} Prediction: {prediction}</h3>
        <p><strong>Confidence:</strong> {confidence:.1%}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Prediction Details")
        
        if result.get("file_type") == "image":
            st.metric("Real Probability", f"{details.get('real_probability', 0):.1%}")
            st.metric("Fake Probability", f"{details.get('fake_probability', 0):.1%}")
            st.metric("Model Confidence", f"{details.get('model_confidence', 0):.1%}")
            
        elif result.get("file_type") == "video":
            st.metric("Frames Analyzed", details.get('frames_analyzed', 0))
            st.metric("Average Real Probability", f"{details.get('average_real_probability', 0):.1%}")
            st.metric("Average Fake Probability", f"{details.get('average_fake_probability', 0):.1%}")
    
    with col2:
        st.markdown("### ⚙️ Technical Info")
        st.info(f"**File Type:** {result.get('file_type', 'Unknown').title()}")
        st.info(f"**Threshold:** {details.get('threshold', 0.51):.1%}")
        
        if result.get("file_type") == "video":
            fake_frames = details.get('fake_frames', 0)
            real_frames = details.get('real_frames', 0)
            fake_percentage = details.get('fake_frame_percentage', 0)
            
            st.info(f"**Fake Frames:** {fake_frames}")
            st.info(f"**Real Frames:** {real_frames}")
            st.info(f"**Fake Frame %:** {fake_percentage:.1f}%")
    
    # Video frame analysis
    if result.get("file_type") == "video" and "sample_frame_predictions" in details:
        st.markdown("### 🎬 Sample Frame Analysis")
        frame_data = details["sample_frame_predictions"]
        
        if frame_data:
            # Create a simple table
            frame_df_data = []
            for frame_info in frame_data[:5]:  # Show first 5 frames
                frame_df_data.append({
                    "Frame": frame_info.get("frame", 0),
                    "Prediction": frame_info.get("prediction", "Unknown"),
                    "Fake Prob": f"{frame_info.get('fake_prob', 0):.1%}",
                    "Real Prob": f"{frame_info.get('real_prob', 0):.1%}"
                })
            
            st.dataframe(frame_df_data, use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 Deepfake Detection System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload an image or video to detect if it\'s AI-generated or real</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🛠️ Settings")
        
        # Backend status
        backend_healthy = check_backend_health()
        status_color = "🟢" if backend_healthy else "🔴"
        status_text = "Online" if backend_healthy else "Offline"
        st.markdown(f"**Backend Status:** {status_color} {status_text}")
        
        if not backend_healthy:
            st.error("⚠️ Backend is not running! Please start the FastAPI backend first.")
            st.code("python backend.py", language="bash")
            return
        
        st.markdown("---")
        
        # File type selection
        file_type = st.selectbox(
            "Detection Mode",
            ["auto", "image", "video"],
            format_func=lambda x: {
                "auto": "🤖 Auto-detect",
                "image": "🖼️ Image Only", 
                "video": "🎥 Video Only"
            }[x]
        )
        
        # Video settings
        if file_type in ["auto", "video"]:
            st.markdown("### 🎥 Video Settings")
            max_frames = st.slider(
                "Max Frames to Analyze",
                min_value=5,
                max_value=50,
                value=30,
                help="More frames = more accurate but slower processing"
            )
        else:
            max_frames = 30
        
        st.markdown("---")
        
        # Supported formats
        with st.expander("📋 Supported Formats"):
            st.markdown("""
            **Images:**
            - JPG, JPEG, PNG
            - BMP, TIFF, WebP
            
            **Videos:**
            - MP4, AVI, MOV
            - MKV, WMV, FLV, WebM
            """)
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            This system uses a ResNet50-based deep learning model 
            to detect deepfake and AI-generated content.
            
            **How it works:**
            1. Extracts faces from images/videos
            2. Analyzes facial features
            3. Predicts authenticity with confidence score
            4. Uses 51% threshold for classification
            """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload section
        st.markdown("## 📤 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an image or video file",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp', 'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'],
            help="Upload an image or video file to analyze"
        )
        
        if uploaded_file is not None:
            # File info
            file_size = len(uploaded_file.getvalue())
            st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size/1024/1024:.1f} MB)")
            
            # Show preview for images
            if uploaded_file.type.startswith('image/'):
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                except:
                    st.warning("Could not display image preview")
            
            # Prediction button
            if st.button("🔍 Analyze File", type="primary", use_container_width=True):
                with st.spinner("🤖 Analyzing file... This may take a moment."):
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Make prediction
                    result, error = make_prediction(uploaded_file, file_type, max_frames)
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ Analysis complete!")
                        display_prediction_results(result)
    
    with col2:
        # Features and tips
        st.markdown("## 🌟 Features")
        
        st.markdown("""
        <div class="feature-box">
            <h4>🖼️ Image Analysis</h4>
            <p>Detect deepfake faces in photos with high accuracy</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h4>🎥 Video Analysis</h4>
            <p>Analyze multiple frames for comprehensive video detection</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h4>🤖 Auto Detection</h4>
            <p>Automatically determines file type and processing method</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## 💡 Tips")
        st.info("""
        **For best results:**
        - Use clear, well-lit images
        - Ensure faces are visible and not too small
        - Videos should have good quality
        - Avoid heavily compressed files
        """)
        
        st.warning("""
        **Note:** This system detects faces first, then analyzes them. 
        If no face is detected, it will analyze the entire image.
        """)

if __name__ == "__main__":
    main()
