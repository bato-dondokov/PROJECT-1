import cv2
import sys
import numpy as np
import os
import re

class LabelGenerator():
    def __init__(self, xray_dir, dataset_dir):
        self.XRAY_DIR = xray_dir
        self.DATASET_DIR = dataset_dir


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


    def find_rotation_angle(self, points, center, k):
        distances = np.linalg.norm(points - center, axis=1)
        max_distance_index = np.argmax(distances)
        farthest_point = points[max_distance_index]

        if center[1] < farthest_point[1]:
            k *= -1
        rotation_angle = (farthest_point[0] - center[0]) // k
        return rotation_angle
    

    def find_vertices(self, center_point, rotation_angle, mask):
                    rot_mat = cv2.getRotationMatrix2D((int(center_point[0]), int(center_point[1])), rotation_angle, 1.0)
                    rotated_mask = cv2.warpAffine(mask * 255.0, rot_mat, mask.shape[1::-1], flags=cv2.INTER_LINEAR)
                
                    rotated_y, rotated_x = np.where(rotated_mask == 255.0)
                    upper_point = min(rotated_y)
                    lowest_point = max(rotated_y)
                    left_point = min(rotated_x)
                    right_point = max(rotated_x)
                    vertices = np.array([(left_point, upper_point),
                                         (right_point, upper_point),
                                         (right_point, lowest_point),
                                         (left_point, lowest_point)])
                    return vertices


    def find_boxes(self, masks):
        boxes = []
        for i in range(masks.shape[2]-1):
            mask = masks[:, :, i]
            y, x = np.where(mask == 1)
            if len(y) != 0 and len(x) != 0:
                points = np.array(list(zip(x, y)))
                center_point = np.mean(points, axis=0).astype(int)
                rotation_angle = self.find_rotation_angle(points=points, 
                                                          center=center_point, 
                                                          k=3)
                vertices = self.find_vertices(center_point, 
                                                rotation_angle, 
                                                mask)
                rotated_vertices = []
                for vertex in vertices:
                    rotated_vertices.append(self.rotate_point(vertex,
                                                              center_point, 
                                                              rotation_angle))   
                boxes.append(rotated_vertices)
                # print(i, rotation_angle)

                # self.draw_boxes(image, rotated_vertices)
                # cv2.imshow('image', image)
                # cv2.waitKey(0)
        return np.array(boxes)


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
    DATASET_DIR = "datasets/dataset"
    label_gen = LabelGenerator(XRAY_DIR, DATASET_DIR)
    label_gen.process()