from ultralytics import YOLO
import os

class Xray2Img():
    def __init__(self, xray_dir, img_dir, model):
        self.XRAY_DIR = xray_dir
        self.IMG_DIR = img_dir
        self.MODEL = model
    def process(self):
        files = os.listdir(self.XRAY_DIR)
        for filee in files:
            file_path = os.path.join(self.XRAY_DIR, filee)
            boxes = self.MODEL(file_path).obb
            for box in boxes:
                
            



