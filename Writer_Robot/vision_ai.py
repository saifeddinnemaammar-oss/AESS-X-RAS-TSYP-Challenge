"""
Live AI visual confirmation using YOLOv8 (TFLite Export).
Processes webcam frames to detect human targets.
"""
import cv2
import time
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class VisionAI:
    # Update the default path to match the Ultralytics TFLite export structure
    def __init__(self, model_path="yolov8n_saved_model/yolov8n_float32.tflite", camera_index=0):
        self.model_path = model_path
        self.camera_index = camera_index
        self.cap = None
        self.model = None

    def start_camera(self):
        logger.info(f"Loading optimized AI Model: {self.model_path}")
        self.model = YOLO(self.model_path, task='detect')
        
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        logger.info("AI Camera Initialized.")

    def scan_for_victim(self, timeout=10):
        if not self.cap:
            self.start_camera()
            
        logger.info("Commencing visual sweep for live human target...")
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            results = self.model(frame, verbose=False)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    conf = box.conf[0].item()
                    cls_id = int(box.cls[0].item()) 
                    
                    # Class 0 is 'person' in the COCO dataset
                    if cls_id == 0 and conf > 0.75: 
                        logger.info(f">> CONFIRMED: Human target acquired with {conf*100:.1f}% confidence.")
                        return True
                        
            time.sleep(0.1) 
            
        logger.warning("Visual scan timeout. Target not detected.")
        return False

    def close(self):
        if self.cap:
            self.cap.release()