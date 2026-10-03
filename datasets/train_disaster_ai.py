from ultralytics import YOLO

def train_custom_model():
    print("[SYS] Loading base YOLOv8 Nano model...")
    model = YOLO("yolov8n.pt") 

    print("[SYS] Commencing GPU fine-tuning on disaster dataset...")
    model.train(
        data=r"D:\AESS-X-RAS-TSYP-Challenge\datasets\data.yaml",
        epochs=100,         
        imgsz=320,          
        batch=16,            # Fits within the 4GB VRAM limit
        device=0,            # Forces RTX 3050 Ti execution
        workers=4,           # Utilizes Ryzen 5 5600H threads
        name="writer_robot_vision" 
    )

    print("[SYS] Exporting to Raspberry Pi TFLite format...")
    custom_model = YOLO("runs/detect/writer_robot_vision/weights/best.pt")
    custom_model.export(format="tflite", imgsz=320)
    print("[SYS] Training and export complete.")

if __name__ == '__main__':
    train_custom_model()