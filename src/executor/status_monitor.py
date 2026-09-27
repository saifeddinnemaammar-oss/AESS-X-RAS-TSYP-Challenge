"""Executor health monitoring."""
import logging
from .config import BATTERY_LOW, BATTERY_CRITICAL

logger = logging.getLogger(__name__)

class StatusMonitor:
    def __init__(self):
        self.battery = 100.0
        self.lidar_ok = True
        self.imu_ok = True
        self.lora_ok = True

    def get_status(self):
        return {
            'battery': self.battery,
            'lidar': self.lidar_ok,
            'imu': self.imu_ok,
            'lora': self.lora_ok
        }

    def should_abort(self):
        if self.battery < BATTERY_LOW:
            logger.error("Battery LOW! Abort mission.")
            return True
        if not self.lidar_ok:
            logger.error("LiDAR died! Abort mission.")
            return True
        return False

    def get_failure_report(self):
        failures = []
        if not self.lidar_ok: failures.append("LIDAR_FAIL")
        if not self.imu_ok: failures.append("IMU_FAIL")
        if not self.lora_ok: failures.append("LORA_FAIL")
        if self.battery < BATTERY_LOW: failures.append("BATTERY_LOW")
        return failures
