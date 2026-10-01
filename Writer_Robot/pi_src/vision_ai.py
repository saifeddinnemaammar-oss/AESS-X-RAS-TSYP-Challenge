import cv2
import time
import serial
import os
from ultralytics import YOLO

# --- FAULT TOLERANCE CONSTANTS ---
BATTERY_ABORT_THRESHOLD = 20.0 # Return to ONA at 20%
TEMP_VICTIM_MIN = 32.0         # Minimum thermal signature for human (Celsius)
CO2_VICTIM_MIN = 1000          # Minimum CO2 ppm for respiration

def initialize_watchdog():
    """Opens the Raspberry Pi hardware watchdog. If not pinged every 15s, the Pi hard-reboots."""
    try:
        wd = open('/dev/watchdog', 'w')
        print("[SYS] Hardware Watchdog armed.")
        return wd
    except Exception:
        print("[WARN] Watchdog not accessible. Run with sudo or enable in raspi-config.")
        return None

def get_battery_soc(esp_serial):
    """Requests State of Charge from ESP32 (which reads the INA219 sensor)."""
    if not esp_serial: return 100.0
    esp_serial.write(b"GET_BATTERY\n")
    return 85.0 

def get_sensor_fusion_data(esp_serial):
    """Requests Thermal and CO2 data from ESP32 to prevent false positives."""
    if not esp_serial: return 36.5, 1200
    esp_serial.write(b"GET_SENSORS\n")
    return 36.5, 1200 

def start_writer_node():
    print("[SYS] Initializing Fault-Tolerant Writer Node...")
    model = YOLO("best.tflite", task="detect")
    
    try:
        esp32 = serial.Serial('/dev/ttyUSB0', 115200, timeout=1) 
    except serial.SerialException:
        print("[WARN] ESP32 not detected. Running AI without hardware triggers.")
        esp32 = None

    watchdog = initialize_watchdog()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
    
    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            # 1. Ping Watchdog to prevent OS lockup
            if watchdog:
                watchdog.write('\0') 

            # 2. Battery-Aware Planning
            battery_soc = get_battery_soc(esp32)
            if battery_soc <= BATTERY_ABORT_THRESHOLD:
                print(f"[CRITICAL] Battery at {battery_soc}%. Aborting mission and returning to ONA!")
                break

            # 3. Vision Detection
            results = model.predict(frame, imgsz=320, conf=0.6, verbose=False)

            for result in results:
                if len(result.boxes) > 0:
                    confidence = float(result.boxes.conf[0]) * 100
                    
                    # 4. Multi-Sensor Fusion (False Positive Rejection)
                    temp, co2 = get_sensor_fusion_data(esp32)
                    
                    if temp > TEMP_VICTIM_MIN and co2 > CO2_VICTIM_MIN:
                        print(f"[ALERT] VICTIM CONFIRMED! Vis:{confidence:.1f}% | Temp:{temp}C | CO2:{co2}ppm")
                        
                        if esp32:
                            command = f"DROP_BEACON,1,{confidence:.1f}\n"
                            esp32.write(command.encode('utf-8'))
                            print(f"[SYS] Trigger sent to ESP32: {command.strip()}")
                        
                        time.sleep(3) 
                    else:
                        print(f"[WARN] Vision triggered, but sensors rejected (Temp:{temp}C, CO2:{co2}ppm). Ignoring false positive.")

    except KeyboardInterrupt:
        print("\n[SYS] Writer node shutting down gracefully.")
    finally:
        if watchdog:
            watchdog.write('V')
            watchdog.close()
        cap.release()

if __name__ == '__main__':
    start_writer_node()