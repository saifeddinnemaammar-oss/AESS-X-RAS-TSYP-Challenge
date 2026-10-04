from ultralytics import YOLO

def train_custom_model():
    print("[SYS] Loading base YOLOv8 Nano model...")
    model = YOLO("yolov8n.pt") 

    print("[SYS] Commencing fine-tuning on disaster dataset...")
    # Point this to the data.yaml file inside your extracted folder
    model.train(
        data="datasets/data.yaml",
        epochs=100,         
        imgsz=320,          
        batch=16,
        name="writer_robot_vision" 
    )

    print("[SYS] Training complete. Exporting to Raspberry Pi TFLite format...")
    custom_model = YOLO("runs/detect/writer_robot_vision/weights/best.pt")
    custom_model.export(format="tflite", imgsz=320)
    
    print("[SYS] Done! Check runs/detect/writer_robot_vision/weights/")

if __name__ == '__main__':
    train_custom_model()