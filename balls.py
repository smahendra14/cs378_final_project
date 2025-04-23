import cv2
import numpy as np


class BoundingBox:
    def __init__(self, name, w, h, center_x, center_y):
        self.name = name
        self.w = w
        self.h = h
        self.center_x = center_x
        self.center_y = center_y

    def __sub__(self, other):
        return BoundingBoxDelta(self, other)

    def __str__(self):
        return (f"'{self.name}' box >> w: {self.w}, h: {self.h}, "
                f"center_x: {self.center_x}, center_y: {self.center_y}")
    

class BoundingBoxDelta:
    def __init__(self, this_box, that_box):
        self.this_box = this_box
        self.that_box = that_box
        self.dw = this_box.w - that_box.w
        self.dh = this_box.h - that_box.h 
        self.dcenter_x = this_box.center_x - that_box.center_x
        self.dcenter_y = this_box.center_y - that_box.center_y

    def __str__(self):
        return (f"'{self.this_box.name}' - '{self.that_box.name}' diff >>  "
                f"dw: {self.dw}, dh: {self.dh}, dcenter_x: {self.dcenter_x}, "
                f"dcenter_y: {self.dcenter_y}")


def calibrate_origin_box(image):
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
        _, _, w, h = cv2.boundingRect(largest_contour)
        print(f"width is {w}, height is {h}")

    origin_x = image.shape[1] // 2
    origin_y = image.shape[0] // 2

    return BoundingBox("origin_box", w, h, origin_x, origin_y)


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

    # draw an X at the center
    size = 10
    thickness = 3
    cv2.line(image, (center_x - size, center_y - size),
             (center_x + size, center_y + size), (0, 255, 255), thickness)
    cv2.line(image, (center_x - size, center_y + size),
             (center_x + size, center_y - size), (0, 255, 255), thickness)

    return BoundingBox("current_box", w, h, center_x, center_y)
