"""Sensor-based verification of beacon claims."""
import logging
from .config import THERMAL_BODY_MIN, THERMAL_BODY_MAX, THERMAL_FIRE_MIN, MQ2_SMOKE_MIN, MQ7_CO_MIN

logger = logging.getLogger(__name__)

class EventVerifier:
    def __init__(self):
        pass

    def verify_event(self, beacon_data, sensor_readings):
        """Returns (verified, actual_type, new_confidence)"""
        b_type = beacon_data.get('type', 0)
        conf = beacon_data.get('confidence', 0)
        
        verified = False
        new_conf = conf
        actual_type = b_type
        
        thermal_max = sensor_readings.get('thermal_max', 0)
        mq2_val = sensor_readings.get('mq2', 0)
        mq7_val = sensor_readings.get('mq7', 0)
        
        if b_type == 1: # VICTIM
            if THERMAL_BODY_MIN <= thermal_max <= THERMAL_BODY_MAX:
                verified = True
                new_conf = min(255, conf + 50)
            else:
                new_conf = max(0, conf - 50)
                
        elif b_type == 2: # FIRE
            if thermal_max > THERMAL_FIRE_MIN and mq2_val > MQ2_SMOKE_MIN:
                verified = True
                new_conf = min(255, conf + 80)
            else:
                new_conf = max(0, conf - 50)
                
        elif b_type == 3: # GAS
            if mq2_val > MQ2_SMOKE_MIN or mq7_val > MQ7_CO_MIN:
                verified = True
                new_conf = min(255, conf + 80)
            else:
                new_conf = max(0, conf - 50)
                
        logger.info(f"Verified event {b_type}: {verified}, conf: {new_conf}")
        return verified, actual_type, new_conf
