from ultralytics import YOLO

# Load your custom trained model
model = YOLO("runs/detect/train/weights/best.pt")

# Run validation
metrics = model.val(data="dataset.yaml")