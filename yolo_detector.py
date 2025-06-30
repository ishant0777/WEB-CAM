from ultralytics import YOLO
import cv2
import numpy as np
from config import Config

class YOLODetector:
    def __init__(self):
        self.model = YOLO(Config.YOLO_MODEL_PATH)
        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD
        
    def detect_objects(self, frame):
        """Detect objects in frame and return annotated frame with detection info"""
        try:
            # Run YOLO detection
            results = self.model(frame, conf=self.confidence_threshold)
            
            # Extract detection information
            detections = []
            confidences = []
            
            # Annotate frame
            annotated_frame = frame.copy()
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Get class name
                        class_name = self.model.names[class_id]
                        
                        # Store detection info
                        detections.append(class_name)
                        confidences.append(float(confidence))
                        
                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Draw label
                        label = f"{class_name}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                        cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 255, 0), -1)
                        cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            return annotated_frame, detections, confidences
            
        except Exception as e:
            print(f"Error in object detection: {e}")
            return frame, [], []
