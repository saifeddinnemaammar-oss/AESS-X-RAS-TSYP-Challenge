import logging
import serial

class BeaconDeployer:
    def __init__(self, serial_conn, max_beacons=10):
        self.esp32_serial = serial_conn
        self.beacons_remaining = max_beacons

    def deploy_beacon(self, event_type, confidence):
        if self.beacons_remaining <= 0:
            logging.warning("[ERR] Magazine empty! Cannot deploy beacon.")
            return False

        if self.esp32_serial and self.esp32_serial.is_open:
            # Format explicitly matches the ESP32 C++ parser: DROP_BEACON,<type>,<conf>
            command = f"DROP_BEACON,{event_type},{confidence:.1f}\n"
            self.esp32_serial.write(command.encode('utf-8'))
            logging.info(f"[TX] Sent to ESP32: {command.strip()}")
            
            self.beacons_remaining -= 1
            return True
        else:
            logging.error("[ERR] Serial connection to ESP32 is down.")
            return False