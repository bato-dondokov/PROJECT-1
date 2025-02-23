import cv2
import sys
import numpy as np

loaded=np.load(sys.argv[1],allow_pickle=True)

img = loaded['x'] * 255.0
cv2.imwrite("xray-599.png", img)

