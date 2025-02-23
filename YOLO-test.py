from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model("dental.jpeg", show=True, save=True)
