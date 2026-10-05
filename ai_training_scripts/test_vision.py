from ultralytics import YOLO

def test_webcam():
    print("[SYS] Loading custom trained model...")
    # Pointing to the final v3-4 model
    model = YOLO("runs/detect/writer_robot_vision_v3-4/weights/best.pt")

    print("[SYS] Starting webcam. Press 'q' to quit.")
    model.predict(source="0", show=True, conf=0.34) # Conf set to 0.34 based on your peak F1-score

if __name__ == '__main__':
    test_webcam()