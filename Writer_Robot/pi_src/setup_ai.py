"""
AI Model Initialization Script for Writer Robot
Downloads the baseline YOLOv8 model (pre-trained for live human detection)
and exports it to the optimized TFLite format for Raspberry Pi deployment.
"""
from ultralytics import YOLO

def setup_environment():
    print("[SYS] Downloading YOLOv8 Nano architecture...")
    model = YOLO("yolov8n.pt") 

    print("[SYS] Exporting to TensorFlow Lite format (imgsz=320)...")
    # This generates a folder named 'yolov8n_saved_model' containing the .tflite file
    model.export(format="tflite", imgsz=320)
    
    print("[SYS] Setup complete. The Writer Robot AI pipeline is ready.")

if __name__ == '__main__':
    setup_environment()