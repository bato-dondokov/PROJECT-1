from ultralytics import YOLO

model = YOLO("models/YOLO11m-OBB4(main)/weights/best.pt")

boxes = model("datasets/dataset/valid/images/650.jpg")
print(boxes)

#TO-DO: install ultralytics, extraxt teeth, git ingore