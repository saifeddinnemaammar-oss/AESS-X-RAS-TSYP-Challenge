from ultralytics import YOLO

def test_webcam():
    print("[SYS] Loading custom trained model...")
    # Using your locally trained PyTorch weights for the test
    model = YOLO(r"runs\detect\writer_robot_vision-2\weights\best.pt")

    print("[SYS] Starting webcam. Press 'q' to quit.")
    # source="0" opens your default laptop webcam
    # conf=0.5 means it will only show detections it is at least 50% confident about
    model.predict(source="0", show=True, conf=0.5)

if __name__ == '__main__':
    test_webcam()