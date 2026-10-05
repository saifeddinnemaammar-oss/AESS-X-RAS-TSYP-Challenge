import serial
import time
import logging
from vision_ai import VisionAI
from beacon_deployer import BeaconDeployer

logging.basicConfig(level=logging.INFO)

def main():
    # 1. Initialize hardware connections
    esp32_port = '/dev/ttyUSB0'  # Adjust to your Pi's actual USB port
    baud_rate = 115200
    
    try:
        esp_serial = serial.Serial(esp32_port, baud_rate, timeout=1)
        logging.info(f"[SYS] Connected to ESP32 on {esp32_port}")
    except Exception as e:
        logging.error(f"[ERR] ESP32 not found: {e}")
        return

    # 2. Initialize subsystems
    vision = VisionAI()
    deployer = BeaconDeployer(serial_conn=esp_serial)

    logging.info("[SYS] Writer Robot Master Node Active. Listening for ESP32 Interrupts...")

    try:
        while True:
            if esp_serial.in_waiting > 0:
                # Read incoming alerts from the ESP32 (Thermal, Gas, etc.)
                incoming_msg = esp_serial.readline().decode('utf-8').strip()
                
                if "THERMAL_SPIKE" in incoming_msg:
                    logging.info("[RX] ESP32 detected heat anomaly. Triggering AI Vision...")
                    
                    # Sensor Fusion: Hardware says HOT, now ask AI to confirm it's a HUMAN
                    victim_found, conf = vision.scan_for_victim(timeout=3.0)
                    
                    if victim_found:
                        # Event Type 1 = Victim
                        deployer.deploy_beacon(event_type=1, confidence=conf)
                        time.sleep(5) # Cooldown while beacon drops
                        
                elif "GAS_DETECTED" in incoming_msg:
                    # Gas doesn't need visual confirmation, drop immediately
                    logging.info("[RX] ESP32 detected Gas. Deploying beacon...")
                    # Event Type 3 = Gas
                    deployer.deploy_beacon(event_type=3, confidence=99.0)
                    time.sleep(5)
                    
            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("[SYS] Shutting down...")
    finally:
        vision.close()
        esp_serial.close()

if __name__ == '__main__':
    main()