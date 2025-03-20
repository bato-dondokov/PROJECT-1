from ultralytics import YOLO

model = YOLO("results/YOLO11X-OBB7/weights/best.pt")

model.predict("datasets/dataset/valid/images/649.jpg", save_txt=True)