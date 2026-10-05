from ultralytics import YOLO

def main():
    # Load your final custom trained model
    model = YOLO("runs/detect/writer_robot_vision_v3-4/weights/best.pt")

    # Run validation against the correct dataset
    metrics = model.val(data="datasets/data.yaml")

if __name__ == '__main__':
    main()