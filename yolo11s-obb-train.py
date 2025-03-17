from ultralytics import YOLO

model = YOLO("yolo11s-obb.pt")

yaml_file = "/home/bato/PROJECTS/PROJECT-1/datasets/dataset/data.yaml"

results = model.train(data=yaml_file, 
                      epochs=100,  
                      imgsz=640,
                      project="teeth",
                      name="YOLO11S-OBB",
                      batch=16,
                      device=0,
                      val=True,
                      single_cls=True)
