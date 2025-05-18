from ultralytics import YOLO
import os

class Xray2Teeth():
    def __init__(self, xray_file_path, teeth_dir, model):
        self.XRAY_FILE_PATH = xray_file_path
        self.TEETH_DIR = teeth_dir
        self.MODEL = model
        print('x2t innit')
    def process(self):
        if self.XRAY_FILE_PATH:
            boxes = self.MODEL(self.XRAY_FILE_PATH, 
                               conf=0.7, 
                               show_labels=False,
                               show_conf=False)[0]
            xray_file = os.path.basename(self.XRAY_FILE_PATH)
            boxes_dir = os.path.join(self.TEETH_DIR, xray_file[:-4])
            os.makedirs(boxes_dir, exist_ok=True)
            for i, box in enumerate(boxes):
                box_file_name = os.path.join(boxes_dir, f'{i}.png')
                box.save(box_file_name, conf=False, labels=False)

if __name__=="__main__":
    XRAY_FILE_PATH = "xrays/"
    TEETH_DIR = "teeth_img/"
    MODEL = YOLO("models/YOLO11m-OBB4(main)/weights/best.pt")
    x2i = Xray2Teeth(XRAY_FILE_PATH, TEETH_DIR, MODEL) 
    x2i.process()
                