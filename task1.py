import cv2
import numpy as np

image = cv2.imread("ut_tower.png")

edges = cv2.Canny(image, 100, 200)

cv2.imwrite('ut_tower_edges.png', edges)
cv2.imshow('Edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()