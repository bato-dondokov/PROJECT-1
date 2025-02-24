import cv2
import sys
import numpy as np
import os
import re

class LabelGenerator():
    def __init__(self, xray_dir, dataset_dir, w, h):
        self.XRAY_DIR = xray_dir
        self.DATASET_DIR = dataset_dir
        self.W = w
        self.H = h


    def find_vertices(self, center_point, farthest_point):
        if center_point[1] > farthest_point[1]:
            vertices = np.array([[center_point[0] + self.W//2, center_point[1] - int(self.H*0.6)],
                                [center_point[0] + self.W//2, center_point[1] + int(self.H*0.4)],
                                [center_point[0] - self.W//2, center_point[1] + int(self.H*0.4)],
                                [center_point[0] - self.W//2, center_point[1] - int(self.H*0.6)]])
            theta = (farthest_point[0] - center_point[0]) // 3
        else:
            vertices = np.array([[center_point[0] + self.W//2, center_point[1] - int(self.H*0.4)],
                                [center_point[0] + self.W//2, center_point[1] + int(self.H*0.6)],
                                [center_point[0] - self.W//2, center_point[1] + int(self.H*0.6)],
                                [center_point[0] - self.W//2, center_point[1] - int(self.H*0.4)]])
            theta = (farthest_point[0] - center_point[0]) // -3
        return vertices, theta


    def rotate_point(self, vertex, center_point, theta):
        theta = np.radians(theta)
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)

        x_shifted = vertex[0] - center_point[0]
        y_shifted = vertex[1] - center_point[1]

        x_rotated = x_shifted * cos_t - y_shifted * sin_t
        y_rotated = x_shifted * sin_t + y_shifted * cos_t

        return (int(center_point[0] + x_rotated), 
                int(center_point[1] + y_rotated))
    

    def draw_boxes(self, mask, rotated_vertices):
        for j in range(len(rotated_vertices)):
            start_point = rotated_vertices[j]
            if j == 0:
                end_point = rotated_vertices[-1]
            else:
                end_point = rotated_vertices[j-1]
            cv2.line(mask,
                     start_point,
                     end_point,
                     color=(255, 255, 255),
                     thickness=2)


    def find_boxes(self, masks):
        boxes = []
        for i in range(masks.shape[2]-1):
            mask = masks[:, :, i]
            y, x = np.where(mask == 1)
            if len(y) != 0 and len(x) != 0:
                points = np.array(list(zip(x, y)))
                center_point = np.mean(points, axis=0).astype(int)
                distances = np.linalg.norm(points - center_point, axis=1)
                max_distance_index = np.argmax(distances)
                farthest_point = points[max_distance_index]

                vertices, theta = self.find_vertices(center_point, 
                                                     farthest_point)
                rotated_vertices = []
                for vertex in vertices:
                    rotated_vertices.append(self.rotate_point(vertex,
                                                              center_point, 
                                                              theta))
                    
                boxes.append(rotated_vertices)
        return np.array(boxes)
                # mask = mask * 255.0    
                # self.draw_boxes(mask, rotated_vertices)
                # cv2.circle(mask, 
                #            center_point, 
                #            radius=2, 
                #            color=(0, 0, 0), 
                #            thickness=2) 
                # cv2.imshow('tooth', mask)
                # cv2.waitKey(0)


    def save_labels(self, dir, image_id, boxes):
        filename = os.path.join(dir, f"{image_id}.txt")
        for box in boxes:
            label = '0 '
            for vertex in box:
                label += f'{vertex[0] / 2048} {vertex[1] / 1024} '
            with open(filename, 'a') as file:
                file.write(label + '\n')


    def process(self):
        files = os.listdir(self.XRAY_DIR)
        idx = np.arange(len(files))
        np.random.shuffle(idx)

        train_idx = idx[:int(len(files) * 0.8)]
        val_idx = idx[int(len(files) * 0.8):int(len(files) * 0.9)]
        test_idx = idx[int(len(files) * 0.9):]

        for i in range(len(files)):
            image_id = re.findall(r"^[^.]+", files[i])[0]
            print(image_id)
            loaded = np.load(os.path.join(self.XRAY_DIR, files[i]), allow_pickle=True)
            image = loaded['x'] * 255.0
            masks = loaded['y']
            boxes = self.find_boxes(masks)

            if i in train_idx:
                labels_dir = os.path.join(self.DATASET_DIR, "train/labels")
                self.save_labels(labels_dir, image_id, boxes)
                image_path = os.path.join(self.DATASET_DIR, 
                                            f"train/images/{image_id}.jpg")
                cv2.imwrite(image_path, image)
            if i in val_idx:
                labels_dir = os.path.join(self.DATASET_DIR, "valid/labels")
                self.save_labels(labels_dir, image_id, boxes)
                image_path = os.path.join(self.DATASET_DIR, 
                                            f"valid/images/{image_id}.jpg")
                cv2.imwrite(image_path, image)                
            if i in test_idx:
                labels_dir = os.path.join(self.DATASET_DIR, "test/labels")
                self.save_labels(labels_dir, image_id, boxes)
                image_path = os.path.join(self.DATASET_DIR, 
                                            f"test/images/{image_id}.jpg")
                cv2.imwrite(image_path, image)

 
if __name__ == "__main__":
    XRAY_DIR = sys.argv[1]
    DATASET_DIR = "dataset/"
    BOX_WIDTH = 200
    BOX_HEIGH = 400
    label_gen = LabelGenerator(XRAY_DIR, DATASET_DIR, BOX_WIDTH, BOX_HEIGH)
    label_gen.process()