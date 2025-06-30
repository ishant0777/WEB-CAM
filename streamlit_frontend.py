import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from config import Config
from database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Multi-Camera Surveillance System",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db_manager = DatabaseManager(Config.DATABASE_PATH)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .camera-status-online {
        color: #28a745;
        font-weight: bold;
    }
    .camera-status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    .detection-alert {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def check_flask_backend():
    """Check if Flask backend is running"""
    try:
        response = requests.get(f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def authenticate_user(username, password):
    """Authenticate user"""
    return db_manager.verify_user(username, password)

def get_camera_status():
    """Get camera status from Flask backend"""
    try:
        response = requests.get(f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/camera_status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}

def get_detection_history(camera_name=None):
    """Get detection history"""
    try:
        if camera_name:
            url = f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/detection_history/{camera_name}"
        else:
            url = f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/all_detection_history"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ''

    # Check Flask backend
    if not check_flask_backend():
        st.error("⚠️ Flask backend is not running! Please start the backend server first.")
        st.code("python flask_backend.py")
        return

    # Authentication
    if not st.session_state.authenticated:
        st.markdown('<div class="main-header">🔐 Multi-Camera Surveillance Login</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                login_button = st.form_submit_button("Login", use_container_width=True)
                
                if login_button:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
        
        # Show default credentials
        st.info("Default credentials: admin / admin123")
        return

    # Main application
    st.markdown('<div class="main-header">📹 Multi-Camera Surveillance System</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}!")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ''
            st.rerun()
        
        st.markdown("---")
        
        # Camera selection
        st.markdown("### 📹 Camera Selection")
        camera_names = list(Config.CAMERA_URLS.keys())
        selected_camera = st.selectbox("Select Camera", camera_names)
        
        # Camera status
        st.markdown("### 📊 Camera Status")
        camera_status = get_camera_status()
        
        for camera_name in camera_names:
            status = camera_status.get(camera_name, False)
            status_text = "🟢 Online" if status else "🔴 Offline"
            status_class = "camera-status-online" if status else "camera-status-offline"
            st.markdown(f'<div class="{status_class}">{camera_name}: {status_text}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto Refresh (5s)", value=True)
        
        # Manual refresh button
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🎥 Live Feed - {selected_camera}")
        
        # Video stream
        video_url = f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/video_feed/{selected_camera}"
        st.image(video_url, use_column_width=True)
        
        # Camera info
        status = camera_status.get(selected_camera, False)
        if status:
            st.success(f"✅ {selected_camera} is online and streaming")
        else:
            st.error(f"❌ {selected_camera} is offline")
    
    with col2:
        st.markdown("### 🎯 Recent Detections")
        
        # Get recent detections for selected camera
        detections = get_detection_history(selected_camera)
        
        if detections:
            # Show latest detections
            for detection in detections[:5]:
                timestamp = detection[4]
                objects = json.loads(detection[2])
                confidences = json.loads(detection[3])
                
                with st.expander(f"🔍 Detection at {timestamp}"):
                    for obj, conf in zip(objects, confidences):
                        st.write(f"**{obj}**: {conf:.2f}")
        else:
            st.info("No recent detections")
        
        st.markdown("---")
        
        # Detection statistics
        st.markdown("### 📈 Detection Statistics")
        
        all_detections = get_detection_history()
        if all_detections:
            # Create DataFrame
            df_data = []
            for detection in all_detections:
                objects = json.loads(detection[2])
                timestamp = detection[4]
                camera = detection[1]
                
                for obj in objects:
                    df_data.append({
                        'Object': obj,
                        'Camera': camera,
                        'Timestamp': timestamp
                    })
            
            if df_data:
                df = pd.DataFrame(df_data)
                
                # Object count chart
                obj_counts = df['Object'].value_counts()
                fig = px.bar(x=obj_counts.index, y=obj_counts.values, 
                           title="Object Detection Count")
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No detection data available")

    # Advanced Features Section
    st.markdown("---")
    st.markdown("## 🚀 Advanced Features")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Analytics Dashboard", 
        "⚠️ Alert System", 
        "📹 Recording Manager", 
        "🔧 System Settings",
        "📱 Mobile View"
    ])
    
    with tab1:
        st.markdown("### 📊 Analytics Dashboard")
        
        # Time-based detection analysis
        if all_detections:
            df_data = []
            for detection in all_detections:
                objects = json.loads(detection[2])
                timestamp = datetime.strptime(detection[4], '%Y-%m-%d %H:%M:%S')
                camera = detection[1]
                
                df_data.append({
                    'Count': len(objects),
                    'Timestamp': timestamp,
                    'Camera': camera,
                    'Hour': timestamp.hour
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                
                # Hourly detection pattern
                hourly_data = df.groupby('Hour')['Count'].sum().reset_index()
                fig = px.line(hourly_data, x='Hour', y='Count', 
                            title="Detection Pattern by Hour")
                st.plotly_chart(fig, use_container_width=True)
                
                # Camera-wise detection comparison
                camera_data = df.groupby('Camera')['Count'].sum().reset_index()
                fig = px.pie(camera_data, values='Count', names='Camera', 
                           title="Detection Distribution by Camera")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### ⚠️ Alert System")
        
        # Alert configuration
        st.subheader("Alert Configuration")
        alert_objects = st.multiselect(
            "Objects to Alert On",
            ["person", "car", "truck", "bicycle", "motorcycle", "bus"],
            default=["person"]
        )
        
        alert_threshold = st.slider("Detection Confidence Threshold", 0.1, 1.0, 0.7)
        
        # Recent alerts
        st.subheader("Recent Alerts")
        if all_detections:
            alert_count = 0
            for detection in all_detections[:10]:
                objects = json.loads(detection[2])
                confidences = json.loads(detection[3])
                
                for obj, conf in zip(objects, confidences):
                    if obj in alert_objects and conf >= alert_threshold:
                        st.warning(f"🚨 **ALERT**: {obj} detected with {conf:.2f} confidence at {detection[4]} on {detection[1]}")
                        alert_count += 1
            
            if alert_count == 0:
                st.info("No recent alerts based on current settings")
    
    with tab3:
        st.markdown("### 📹 Recording Manager")
        
        st.subheader("Recording Controls")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔴 Start Recording", use_container_width=True):
                st.success("Recording started for all cameras")
        
        with col2:
            if st.button("⏹️ Stop Recording", use_container_width=True):
                st.info("Recording stopped")
        
        # Recording settings
        st.subheader("Recording Settings")
        record_quality = st.selectbox("Recording Quality", ["High", "Medium", "Low"])
        record_duration = st.number_input("Max Recording Duration (minutes)", 1, 120, 30)
        
        # Recorded files (mock data)
        st.subheader("Recorded Files")
        st.info("Recording feature will be implemented in the next version")
    
    with tab4:
        st.markdown("### 🔧 System Settings")
        
        st.subheader("Detection Settings")
        new_confidence = st.slider("YOLO Confidence Threshold", 0.1, 1.0, Config.CONFIDENCE_THRESHOLD)
        
        st.subheader("Camera Settings")
        st.text_area("Camera URLs (JSON format)", 
                    value=json.dumps(Config.CAMERA_URLS, indent=2),
                    height=200)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")
        
        st.subheader("System Information")
        st.info(f"Flask Backend: {Config.FLASK_HOST}:{Config.FLASK_PORT}")
        st.info(f"Database: {Config.DATABASE_PATH}")
        st.info(f"YOLO Model: {Config.YOLO_MODEL_PATH}")
    
    with tab5:
        st.markdown("### 📱 Mobile-Optimized View")
        
        # Simplified mobile view
        st.subheader("Quick Camera Access")
        
        # Camera grid for mobile
        cols = st.columns(2)
        for i, camera_name in enumerate(camera_names):
            with cols[i % 2]:
                status = camera_status.get(camera_name, False)
                status_emoji = "🟢" if status else "🔴"
                
                if st.button(f"{status_emoji} {camera_name}", use_container_width=True):
                    st.session_state.selected_mobile_camera = camera_name
        
        # Show selected camera
        if hasattr(st.session_state, 'selected_mobile_camera'):
            selected_mobile = st.session_state.selected_mobile_camera
            st.markdown(f"### 📱 {selected_mobile}")
            mobile_video_url = f"http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/video_feed/{selected_mobile}"
            st.image(mobile_video_url, use_column_width=True)

    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
