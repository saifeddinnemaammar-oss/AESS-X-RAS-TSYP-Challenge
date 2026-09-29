"""
Live AI visual confirmation using YOLOv8 (TFLite Export).
Processes webcam frames to detect custom trained hazard/victim classes.
"""
import cv2
import time
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class VisionAI:
    def __init__(self, model_path="best_saved_model.tflite", camera_index=0):
        self.model_path = model_path
        self.camera_index = camera_index
        self.cap = None
        self.model = None

    def start_camera(self):
        logger.info(f"Loading optimized AI Model: {self.model_path}")
        # The ultralytics library natively wraps the TFLite runtime for YOLO models
        self.model = YOLO(self.model_path, task='detect')
        
        self.cap = cv2.VideoCapture(self.camera_index)
        # Compress resolution to 320x320 to match the TFLite training dimensions for speed
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        logger.info("AI Camera Initialized.")

    def scan_for_victim(self, timeout=10):
        if not self.cap:
            self.start_camera()
            
        logger.info("Commencing visual sweep for Victim...")
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Run inference on the current frame
            results = self.model(frame, verbose=False)
            
            # Parse bounding boxes
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    conf = box.conf[0].item()
                    # Assuming class 0 is the victim in your Roboflow dataset
                    cls_id = int(box.cls[0].item()) 
                    
                    if cls_id == 0 and conf > 0.75: # 75% confidence threshold
                        logger.info(f">> CONFIRMED: Target acquired with {conf*100:.1f}% confidence.")
                        return True
                        
            time.sleep(0.1) # Prevent CPU pegging
            
        logger.warning("Visual scan timeout. Target not detected.")
        return False

    def close(self):
        if self.cap:
            self.cap.release()