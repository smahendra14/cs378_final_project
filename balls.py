import cv2
import numpy as np


class BoundingBox:
    def __init__(self, w, h, center_x, center_y, rel_x, rel_y):
        self.w = w
        self.h = h
        self.center_x = center_x
        self.center_y = center_y
        self.rel_x = rel_x
        self.rel_y = rel_y

    def __str__(self):
        return (f"w: {self.w}, h: {self.h}, center_x: {self.center_x}, center_y: {self.center_y}, "
                "rel_x: {self.rel_x}, rel_y: {self.rel_y}")


def get_bounding_box(image):
    # convert to hsv
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # define ranges for red color
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # create masks
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.add(mask1, mask2)

    # determine contours
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # find the largest contour for the red circle
        largest_contour = max(contours, key=cv2.contourArea)

        # get bounding box coordinates
        x, y, w, h = cv2.boundingRect(largest_contour)
        print(f"width is {w}, height is {h}")

        # draw bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # find bounding box center
        center_x = x + w // 2
        center_y = y + h // 2

        # find image center
        img_center_x = image.shape[1] // 2
        img_center_y = image.shape[0] // 2

        # find position relative to center
        rel_x = center_x - img_center_x
        rel_y = center_y - img_center_y

    return BoundingBox(w, h, center_x, center_y, rel_x, rel_y)
