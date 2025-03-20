import cv2
import numpy as np

idx = 649
img = cv2.imread(f"datasets/dataset/valid/images/{idx}.jpg")

filename = f"datasets/dataset/valid/labels/{idx}.txt"
# filename = "datasets/dataset/test/labels/632.txt"

with open(filename, 'r') as file:
    labels = file.readlines()

labels = [line.strip() for line in labels]
color = (255, 255, 255)
# label = labels[2]
for label in labels:
    points = [float(point) for point in label.split()]
    cv2.line(img,
                (int(points[1] * 2048), int(points[2] * 1024)), 
                (int(points[3] * 2048), int(points[4] * 1024)),
                color=color,
                thickness=2)
    cv2.line(img,
                (int(points[3] * 2048), int(points[4] * 1024)), 
                (int(points[5] * 2048), int(points[6] * 1024)),
                color=color,
                thickness=2)
    cv2.line(img,
                (int(points[5] * 2048), int(points[6] * 1024)), 
                (int(points[7] * 2048), int(points[8] * 1024)),
                color=color,
                thickness=2)
    cv2.line(img,
                (int(points[7] * 2048), int(points[8] * 1024)), 
                (int(points[1] * 2048), int(points[2] * 1024)),
                color=color,
                thickness=2)
    color = tuple(np.random.randint(0, 256, size=3).tolist())
cv2.imshow('xray', img)
cv2.waitKey(0)

cv2.imwrite('/home/bato/Downloads/images/teeth.jpg', img)