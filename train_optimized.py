from ultralytics import YOLO

def main():
    # Load base YOLOv8n pretrained weights
    model = YOLO("yolov8n.pt")

    # Train with hyperparameter tuning targeting disaster recall
    results = model.train(
        data="datasets/data.yaml",
        epochs=250,
        patience=40,
        batch=8,           # CRITICAL FIX: Dropped to 8 to protect your 4GB GPU VRAM
        workers=2,         # CRITICAL FIX: Dropped to 2 to stop the WinError 1455 RAM crash
        imgsz=640,         
        device=0,          
        name="writer_robot_vision_v3",
        
        # Loss weight adjustments to boost recall
        cls=1.2,           
        box=7.5,
        dfl=1.5,
        
        # Occlusion & Rubble Augmentations
        degrees=20.0,      
        scale=0.6,         
        flipud=0.2,        
        fliplr=0.5,        
        mosaic=1.0,        
        mixup=0.15,        
        erasing=0.4,       
        
        # Optimizer settings
        optimizer="auto",
        warmup_epochs=3.0,
        save=True,
        plots=True
    )

if __name__ == '__main__':
    main()