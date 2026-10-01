import cv2
import time
from ultralytics import YOLO

def start_vision_node():
    print("[SYS] Initializing Writer Robot Vision Node...")
    # 1. Load your newly optimized TFLite model
    model = YOLO("best.tflite", task="detect")
    
    # 2. Initialize the USB Webcam or Pi Cam
    cap = cv2.VideoCapture(0)
    
    # 3. Force low resolution to match training (320px) and save Pi CPU
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
    
    # Optional: Lower framerate to prevent thermal throttling on the Pi
    cap.set(cv2.CAP_PROP_FPS, 10)

    print("[SYS] Camera active. Scanning environment for victims...")

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("[ERR] Camera disconnected.")
                break

            # Run inference. conf=0.6 ignores low-confidence debris shadows
            results = model.predict(frame, imgsz=320, conf=0.6, verbose=False)

            # Parse results to trigger the hardware response
            for result in results:
                if len(result.boxes) > 0:
                    confidence = float(result.boxes.conf[0]) * 100
                    print(f"[ALERT] VICTIM DETECTED! Confidence: {confidence:.1f}%")
                    
                    # ---> INTEGRATION POINT <---
                    # Here is where you will call your hardware_sensors.py functions
                    # e.g., trigger_beacon_drop(event_type=1) 
                    # e.g., send_lora_packet(x, y, z, confidence)
                    
                    # Sleep briefly to avoid spamming the LoRa module with 10 packets a second
                    time.sleep(2)

    except KeyboardInterrupt:
        print("\n[SYS] Vision node shutting down.")
    finally:
        cap.release()

if __name__ == '__main__':
    start_vision_node()