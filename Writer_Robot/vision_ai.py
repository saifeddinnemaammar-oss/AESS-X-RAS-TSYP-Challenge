import cv2
import time
import logging
from ultralytics import YOLO

class VisionAI:
    def __init__(self, model_path="best.tflite"):
        logging.info("[SYS] Loading YOLOv8 Nano TFLite model...")
        self.model = YOLO(model_path, task="detect")
        self.cap = cv2.VideoCapture(0)
        
        # Force low resolution and framerate to prevent Pi 4 thermal throttling
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        self.cap.set(cv2.CAP_PROP_FPS, 10)
        logging.info("[SYS] Vision AI ready. Awaiting hardware triggers.")

    def scan_for_victim(self, timeout=3.0):
        """Wakes up the camera and scans for 'timeout' seconds. Returns (True, confidence)."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            success, frame = self.cap.read()
            if not success:
                continue

            # Run inference. conf=0.6 drops false positives
            results = self.model.predict(frame, imgsz=320, conf=0.6, verbose=False)

            for result in results:
                if len(result.boxes) > 0:
                    confidence = float(result.boxes.conf[0]) * 100
                    logging.info(f"[ALERT] VICTIM VISUALLY CONFIRMED! Conf: {confidence:.1f}%")
                    return True, confidence

        logging.info("[SYS] Scan timeout. No visual confirmation. False alarm dropped.")
        return False, 0.0

    def close(self):
        self.cap.release()