"""
Multi-sensor fusion pipeline for detecting events.
"""
import time
import logging
try:
    from src.writer import config
except ImportError:
    import config

class EventDetector:
    def __init__(self):
        self.last_detection_time = 0
        self.cooldown = 10.0  # seconds cooldown

    def detect(self, sensor_readings):
        """
        sensor_readings: dict of readings
        Returns: (event_type, confidence)
        Types: 1=Victim, 2=Fire, 3=Gas, None=No event
        """
        now = time.time()
        if now - self.last_detection_time < self.cooldown:
            return None, 0

        thermal = sensor_readings.get('thermal', {}).get('max_temp', 0)
        co2 = sensor_readings.get('mq2', {}).get('ppm', 0)
        gas = sensor_readings.get('mq7', {}).get('ppm', 0)

        event_type = None
        confidence = 0

        # FIRE (type 2): highest priority
        if thermal > config.THERMAL_FIRE:
            event_type = 2
            confidence = int(min(thermal / 80.0, 1.0) * 255)
        # VICTIM (type 1)
        elif thermal > config.THERMAL_VICTIM and co2 > config.CO2_VICTIM:
            event_type = 1
            confidence = int((min(thermal / 37.0, 1.0) * 0.5 + min(co2 / 2000.0, 1.0) * 0.5) * 255)
        # GAS (type 3)
        elif gas > config.GAS_HAZARD:
            event_type = 3
            confidence = int(min(gas / 1000.0, 1.0) * 255)

        if event_type is not None:
            self.last_detection_time = now
            return event_type, confidence

        return None, 0
