import os

import numpy as np
import cv2

from ultralytics import YOLO
from config import OBB_SCALE, CROP_WIDTH, CROP_LENGTH


class Xray2Teeth():
    """
    Класс для обнаружения зубов на рентгеновском снимке.
    """


    def __init__(self, model_path):
        """
        Создает экземпляр класса

        Args:
            model_path (str): Путь до модели обнаружения.
        """
        self.MODEL = YOLO(model_path)


    def get_obbs(self, model, xray_file, xray_shape):
        """
        Получает obbs из рентгеновского снимка с помощью модели обнаружения и
        денормализует их.

        Args:
            model (ultralytics.models.yolo.model.YOLO): Модель обнаружения.
            xray_file (str): Путь до рентгеновского снимка.
            xray_shape (numpy.ndarray): Размеры снимка.

        Returns:
            obbs (numpy.ndarray): Денормализованные obbs.
        """
        results = model.predict(source=xray_file, 
                                        conf=0.25, 
                                        save=False,
                                        show=False)
        norm_obbs = results[0].obb.xyxyxyxyn.numpy()
        obbs = (norm_obbs * np.array(xray_shape)).astype(np.int32)
        return obbs


    def scale_obbs(self, obb, scale):
        """
        Масштабирует ориентированную ограничивающую рамку (obb).

        Args:
            obb (numpy.ndarray): Координаты obb.
            scale (float): Параметр масштабирования.

        Returns:
            new_points (numpy.ndarray): Координаты масштабированной obb.
            cx, cy (tuple) : Координаты центральной точки obb.
        """
        cx,cy = np.mean(obb, axis=0).astype(int)
        scale = np.sqrt(scale)

        new_points = []
        for x, y in obb:
            new_x = cx + scale * (x - cx)
            new_y = cy + scale * (y - cy)
            new_points.append((new_x, new_y))
        new_points = np.array(new_points, dtype=int)
        return new_points, (cx, cy)
    

    def crop_xray(self, xray, center, length, width):
        """
        Обрезает рентгеновский снимок по координатам obb.

        Args:
            xray (numpy.ndarray): Исходное изображение.
            center (tuple): Координаты центральной точки obb.
            length (int): Длинна обрезанного снимка.
            width (int): Ширина обрезанного снимка.

        Returns:
            cropped_xray (numpy.ndarray): Обрезанный снимок.
        """
        x1 = center[0] - width // 2
        x2 = x1 + width
        y1 = center[1] - length // 2
        y2 = y1 + length
        cropped_xray = xray[y1:y2, x1:x2]
        # print(x1, x2, y1, y2)
        return cropped_xray


    def process(self):
        if self.XRAY_FILE:
            """
            Запускает процесс обнаружения зубов на снимке:
                1) Копируется исходный снимок, для дальнейшей обрезки;
                2) Получает и масштабирует obb;
                3) Рисует на снимке рамки и обрезает копию снимка;
                4) Сохраняет полученные изображения.

            """
            self.XRAY_IMG = cv2.imread(self.XRAY_FILE)
            xray_shape = np.array(self.XRAY_IMG.shape)[1::-1]
            obbs = self.get_obbs(self.MODEL, self.XRAY_FILE, xray_shape)
            for i, obb in enumerate(obbs):
                xray = self.XRAY_IMG.copy()
                xray_for_crop = self.XRAY_IMG.copy()
                obb_img = cv2.polylines(
                    img=xray,
                    pts=[obb],
                    isClosed=True,
                    color=(255, 255, 0),
                    thickness=2
                )

                scaled_obb, center = self.scale_obbs(obb, OBB_SCALE)
                scaled_obb_img = cv2.polylines(
                    img=xray_for_crop,
                    pts=[scaled_obb],
                    isClosed=True,
                    color=(255, 255, 0),
                    thickness=2
                )
                
                cropped_img = self.crop_xray(
                    scaled_obb_img, 
                    center, 
                    CROP_LENGTH, 
                    CROP_WIDTH
                )

                xray_file = os.path.basename(self.XRAY_FILE)
                obbs_dir = os.path.join(self.TEETH_DIR, xray_file[:-4], str(i))
                os.makedirs(obbs_dir, exist_ok=True)

                obb_file_name = os.path.join(obbs_dir, f'{i}.png')
                obb_cropped_file_name = os.path.join(obbs_dir, f'{i}-cropped.png')
                cv2.imwrite(obb_file_name, obb_img)
                cv2.imwrite(obb_cropped_file_name, cropped_img)
        else: print("Нет файла!")