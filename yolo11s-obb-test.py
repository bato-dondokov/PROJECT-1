from ultralytics import YOLO

model = YOLO("teeth/YOLO11S-OBB/weights/best.pt")

yaml_file = "/home/bato/PROJECTS/PROJECT-1/datasets/dataset/data.yaml"

metrics = model.val(data=yaml_file,
                    imgsz=640, 
                    batch=16, 
                    project="teeth",
                    name="YOLO11S-OBB-test",
                    device="0",
                    split="test")
print('mAP50-95:', metrics.box.map)
print("mAP50:", metrics.box.map50)