"""
System health monitoring.
"""
import time
import threading
import logging

try:
    from src.writer import config
except ImportError:
    import config

class StatusMonitor:
    def __init__(self, battery_monitor, lora_handler, beacons_ref):
        self.battery = battery_monitor
        self.lora = lora_handler
        self.beacons_ref = beacons_ref
        
        self.sensor_health = {"lidar_ok": True, "imu_ok": True, "lora_ok": True}
        self.last_broadcast = time.time()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _loop(self):
        while self.running:
            now = time.time()
            if now - self.last_broadcast >= 30.0:
                self.lora.broadcast_status(self.get_status())
                self.last_broadcast = now
            time.sleep(1.0)

    def get_status(self):
        batt = self.battery.read() if self.battery else {"voltage": 12.0, "percentage": 100.0, "ok": True}
        return {
            "battery": batt,
            "beacons_remaining": self.beacons_ref() if callable(self.beacons_ref) else self.beacons_ref,
            "health": self.sensor_health
        }

    def is_battery_low(self):
        batt = self.battery.read() if self.battery else {"percentage": 100.0}
        return batt.get("percentage", 100.0) < config.BATT_LOW

    def is_critical(self):
        batt = self.battery.read() if self.battery else {"percentage": 100.0}
        return batt.get("percentage", 100.0) < config.BATT_CRITICAL

    def get_health_report(self):
        return self.sensor_health
