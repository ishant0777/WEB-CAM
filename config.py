import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Camera Configuration
    CAMERA_URLS = {
        'Camera 1': 'http://192.168.1.100:8080/video',
        'Camera 2': 'http://192.168.1.101:8080/video',
        'Camera 3': 'http://192.168.1.102:8080/video',
        # Add more cameras as needed
        'Demo Camera': 0  # Use webcam for demo
    }
    
    # YOLO Configuration
    YOLO_MODEL_PATH = 'yolov8n.pt'
    CONFIDENCE_THRESHOLD = 0.5
    
    # Database Configuration
    DATABASE_PATH = 'surveillance.db'
    
    # Authentication
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Recording Configuration
    RECORDING_PATH = 'recordings/'
    MAX_RECORDING_DURATION = 3600  # 1 hour in seconds
