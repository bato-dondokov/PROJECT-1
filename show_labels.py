import cv2

img = cv2.imread("datasets/dataset/train/images/599.jpg")

filename = "datasets/dataset/train/labels/599.txt"

with open(filename, 'r') as file:
    labels = file.readlines()

labels = [line.strip() for line in labels]

label = labels[0]
points = [float(point) for point in label.split()]
cv2.line(img,
            (int(points[1] * 2048), int(points[2] * 1024)), 
            (int(points[3] * 2048), int(points[4] * 1024)),
            color=(255, 255, 255),
            thickness=2)
cv2.line(img,
            (int(points[3] * 2048), int(points[4] * 1024)), 
            (int(points[5] * 2048), int(points[6] * 1024)),
            color=(255, 255, 255),
            thickness=2)
cv2.line(img,
            (int(points[5] * 2048), int(points[6] * 1024)), 
            (int(points[7] * 2048), int(points[8] * 1024)),
            color=(255, 255, 255),
            thickness=2)
cv2.line(img,
            (int(points[7] * 2048), int(points[8] * 1024)), 
            (int(points[1] * 2048), int(points[2] * 1024)),
            color=(255, 255, 255),
            thickness=2)
cv2.imshow('xray', img)
cv2.waitKey(0)