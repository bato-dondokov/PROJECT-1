from ultralytics import YOLO

model = YOLO("yolo11n-obb.pt")

yaml_file = "/home/bato/PROJECTS/PROJECT-1/datasets/dataset/data.yaml"

results = model.train(data=yaml_file, 
                      epochs=100,  
                      imgsz=1024,
                      project="teeth",
                      name="YOLO11nn-OBB",
                      batch=8,
                      device=0,
                      val=True,
                      single_cls=True)
