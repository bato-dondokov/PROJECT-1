import cv2
import sys
import numpy as np
import matplotlib.pyplot as pp
import re

pattern = r"(?<=/)[^/.]+(?=\.)"

loaded=np.load(sys.argv[1],allow_pickle=True)
xray_id = re.findall(pattern, sys.argv[1])[0]

print(xray_id)

W = 200
H = 400

masks=loaded['y']
xray = loaded['x'] * 255.0

for i in range(masks.shape[2]-1):
    print(i)
    mask = masks[:, :, i]
    y, x = np.where(mask == 1)
    if len(y) != 0 and len(x) != 0:
        points = list(zip(x, y))
        center_x = int(np.mean([p[0] for p in points]))
        center_y = int(np.mean([p[1] for p in points]))
        center = (center_x, center_y)
        cv2.circle(xray, center, radius=2, color=(255, 255, 255), thickness=2) 
        start_point = (center_x - W // 2, center_y - H // 2)
        end_point = (center_x + W // 2, center_y + H // 2)
        cv2.rectangle(xray, start_point, end_point, color=(255, 255, 255), thickness=2)

cv2.imwrite(f"data/y/xray-{xray_id}.png", xray)
cv2.imwrite(f"data/y/xrayy-{xray_id}.png", masks[:, :, 66]*255.0)

#TODO: Создать датасет
#TODO: Попробовать потренировать


# img[center_y, center_x] = 0.0
# img = img * 255.0
# cv2.putText(img, f'{center_x}, {center_y}', center, fontFace=1, fontScale=1.0, color=(255))
# cv2.rectangle(img, start_point, end_point, color=(255, 255, 255), thickness=2)
 