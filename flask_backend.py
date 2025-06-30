from flask import Flask, Response, jsonify, request
import cv2
import threading
import time
from config import Config
from yolo_detector import YOLODetector
from camera_manager import CameraManager
from database import DatabaseManager
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize components
db_manager = DatabaseManager(Config.DATABASE_PATH)
yolo_detector = YOLODetector()
camera_manager = CameraManager(db_manager)

# Initialize cameras
for name, url in Config.CAMERA_URLS.items():
    camera_manager.add_camera(name, url)

def generate_frames(camera_name):
    """Generate video frames with YOLO detection"""
    while True:
        try:
            frame = camera_manager.get_frame(camera_name)
            if frame is not None:
                # Apply YOLO detection
                annotated_frame, detections, confidences = yolo_detector.detect_objects(frame)
                
                # Log detections if any objects found
                if detections:
                    db_manager.log_detection(camera_name, detections, confidences)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', annotated_frame, 
                                         [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # Send a black frame if no camera feed
                black_frame = cv2.zeros((480, 640, 3), dtype=cv2.uint8)
                cv2.putText(black_frame, f'Camera {camera_name} Offline', 
                           (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                ret, buffer = cv2.imencode('.jpg', black_frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            print(f"Error generating frames for {camera_name}: {e}")
            time.sleep(1)

@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    """Video streaming route"""
    if camera_name in Config.CAMERA_URLS:
        return Response(generate_frames(camera_name),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify({'error': 'Camera not found'}), 404

@app.route('/camera_status')
def camera_status():
    """Get status of all cameras"""
    status = {}
    for camera_name in Config.CAMERA_URLS.keys():
        status[camera_name] = camera_manager.get_camera_status(camera_name)
    return jsonify(status)

@app.route('/detection_history/<camera_name>')
def detection_history(camera_name):
    """Get detection history for a camera"""
    history = db_manager.get_detection_history(camera_name, limit=50)
    return jsonify(history)

@app.route('/all_detection_history')
def all_detection_history():
    """Get detection history for all cameras"""
    history = db_manager.get_detection_history(limit=100)
    return jsonify(history)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

if __name__ == '__main__':
    try:
        print(f"Starting Flask backend on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
        app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("Shutting down...")
        camera_manager.stop_all_cameras()
