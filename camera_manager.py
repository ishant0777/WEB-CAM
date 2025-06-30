import cv2
import threading
import time
from queue import Queue
import requests
from config import Config
from database import DatabaseManager

class CameraManager:
    def __init__(self, db_manager):
        self.cameras = {}
        self.camera_threads = {}
        self.camera_queues = {}
        self.db_manager = db_manager
        self.running = True
        
    def add_camera(self, name, url):
        """Add a new camera"""
        if name not in self.cameras:
            self.cameras[name] = url
            self.camera_queues[name] = Queue(maxsize=2)
            self.start_camera_thread(name, url)
    
    def start_camera_thread(self, name, url):
        """Start camera capture thread"""
        def capture_frames():
            cap = None
            retry_count = 0
            max_retries = 5
            
            while self.running and retry_count < max_retries:
                try:
                    # Initialize camera
                    if isinstance(url, int):  # Webcam
                        cap = cv2.VideoCapture(url)
                    else:  # IP camera
                        cap = cv2.VideoCapture(url)
                    
                    if not cap.isOpened():
                        raise Exception(f"Cannot open camera {name}")
                    
                    # Set camera properties
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    
                    self.db_manager.update_camera_status(name, 'online')
                    retry_count = 0
                    
                    while self.running:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        # Add frame to queue (non-blocking)
                        if not self.camera_queues[name].full():
                            self.camera_queues[name].put(frame)
                        else:
                            # Remove old frame and add new one
                            try:
                                self.camera_queues[name].get_nowait()
                                self.camera_queues[name].put(frame)
                            except:
                                pass
                        
                        time.sleep(0.033)  # ~30 FPS
                
                except Exception as e:
                    print(f"Camera {name} error: {e}")
                    self.db_manager.update_camera_status(name, 'offline')
                    retry_count += 1
                    time.sleep(5)  # Wait before retry
                
                finally:
                    if cap:
                        cap.release()
            
            self.db_manager.update_camera_status(name, 'offline')
        
        thread = threading.Thread(target=capture_frames, daemon=True)
        thread.start()
        self.camera_threads[name] = thread
    
    def get_frame(self, camera_name):
        """Get latest frame from camera"""
        if camera_name in self.camera_queues:
            try:
                return self.camera_queues[camera_name].get_nowait()
            except:
                return None
        return None
    
    def get_camera_status(self, camera_name):
        """Get camera status"""
        if camera_name in self.cameras:
            return not self.camera_queues[camera_name].empty()
        return False
    
    def stop_all_cameras(self):
        """Stop all camera threads"""
        self.running = False
        for thread in self.camera_threads.values():
            thread.join(timeout=1)
