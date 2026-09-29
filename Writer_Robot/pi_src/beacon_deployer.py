"""
Beacon deployment mechanism.
Modified to trigger physical deployment via ESP32 Serial commands.
"""
import time
import logging

try:
    from src.common.beacon_schema import pack_beacon
except ImportError:
    pack_beacon = lambda *args: b'dummy_packet_20bytes'

try:
    from src.writer import config
except ImportError:
    import config

class BeaconDeployer:
    def __init__(self, lora_handler, esp_command_func, max_beacons=10):
        self.lora = lora_handler
        self.send_esp = esp_command_func
        self.beacons_remaining = max_beacons

    def _activate_servo(self):
        logging.info("Sending DROP_BEACON command to ESP32")
        if self.send_esp:
            self.send_esp("DROP_BEACON")
        else:
            logging.info("Simulating servo activation")
            time.sleep(1.0)

    def deploy_beacon(self, beacon_id, event_type, x_cm, y_cm, z_cm, confidence):
        if self.beacons_remaining <= 0:
            logging.warning("No beacons left!")
            return False

        logging.info(f"Deploying beacon {beacon_id} for event {event_type}")
        
        self._activate_servo()
        time.sleep(0.5)  # Wait for mechanical drop

        ttl = 3600
        next_id = beacon_id + 1
        packet = pack_beacon(beacon_id, config.WRITER_ID, event_type, x_cm, y_cm, z_cm, ttl, confidence, next_id)

        success = False
        for attempt in range(3):
            self.lora.send_beacon_config(packet)
            ack = self.lora.wait_for_ack(timeout=2.0)
            if ack:
                logging.info(f"Beacon {beacon_id} ACK received")
                success = True
                break
            logging.warning(f"ACK timeout, retrying ({attempt+1}/3)...")

        if success:
            self.beacons_remaining -= 1
        else:
            logging.error(f"Failed to configure beacon {beacon_id}")

        return success

    def cleanup(self):
        pass # GPIO cleanup is now handled strictly on the ESP32