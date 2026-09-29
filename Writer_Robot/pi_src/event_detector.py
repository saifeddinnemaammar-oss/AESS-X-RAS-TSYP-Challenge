"""
Multi-sensor fusion pipeline for detecting events.
Upgraded with YOLOv8 AI visual confirmation for Victim detection.
"""
import time
import logging
from config import THERMAL_FIRE, THERMAL_VICTIM, GAS_HAZARD
from vision_ai import VisionAI

logger = logging.getLogger(__name__)

class EventDetector:
    def __init__(self):
        self.last_detection_time = 0
        self.cooldown = 10.0  # seconds cooldown
        self.vision = VisionAI() # Load YOLOv8 model on boot

    def detect(self, sensor_readings):
        """
        Returns: (event_type, confidence)
        Types: 1=Victim, 2=Fire, 3=Gas, None=No event
        """
        now = time.time()
        if now - self.last_detection_time < self.cooldown:
            return None, 0

        thermal = sensor_readings.get('thermal', {}).get('max_temp', 0)
        gas = sensor_readings.get('mq7', {}).get('ppm', 0)

        event_type = None
        confidence = 0

        # PRIORITY 1: FIRE (Type 2)
        if thermal > THERMAL_FIRE:
            event_type = 2
            confidence = int(min(thermal / 80.0, 1.0) * 255)
            
        # PRIORITY 2: GAS (Type 3)
        elif gas > GAS_HAZARD:
            event_type = 3
            confidence = int(min(gas / 1000.0, 1.0) * 255)
            
        # PRIORITY 3: VICTIM (Type 1)
        elif thermal > THERMAL_VICTIM:
            logger.info("[SENSOR] Thermal anomaly detected. Triggering AI Vision Protocol...")
            # Wake up camera and scan for 3 seconds
            if self.vision.scan_for_victim(timeout=3):
                event_type = 1
                confidence = 255 # 100% confirmed by AI
            else:
                logger.info("[SENSOR] False alarm. No visual confirmation.")

        if event_type is not None:
            self.last_detection_time = now
            return event_type, confidence

        return None, 0

    def cleanup(self):
        self.vision.close()