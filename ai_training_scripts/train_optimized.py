from ultralytics import YOLO

def main():
    print("[SYS] Loading base YOLOv8n pretrained weights...")
    model = YOLO("yolov8n.pt")

    print("[SYS] Commencing hyperparameter-tuned training...")
    results = model.train(
        data="datasets/data.yaml",
        epochs=250,
        patience=40,
        batch=8,           
        workers=2,         
        imgsz=640,         
        device=0,          
        name="writer_robot_vision_v3-4", # Updated to match your final folder
        
        cls=1.2,           
        box=7.5,
        dfl=1.5,
        
        degrees=20.0,      
        scale=0.6,         
        flipud=0.2,        
        fliplr=0.5,        
        mosaic=1.0,        
        mixup=0.15,        
        erasing=0.4,       
        
        optimizer="auto",
        warmup_epochs=3.0,
        save=True,
        plots=True
    )

    print("[SYS] Training complete. Exporting to Raspberry Pi INT8 TFLite format...")
    # Load the newly trained weights and export them for Edge AI deployment
    final_model = YOLO("runs/detect/writer_robot_vision_v3-4/weights/best.pt")
    final_model.export(format="tflite", imgsz=320, int8=True)
    
    print("[SYS] Pipeline Finished.")

if __name__ == '__main__':
    main()