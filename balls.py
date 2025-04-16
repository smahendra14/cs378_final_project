import cv2
import numpy as np

MARGIN = 200


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


def move_based_on_balls(image, box, START_SIZE):
    # determine which direction to display
    dir_text = ""
    if abs(box.rel_x) > abs(box.rel_y):
        dir_text = "right" if box.rel_x > 0 else "left"
    else:
        dir_text = "down" if box.rel_y > 0 else "up"

    if box.w < START_SIZE - MARGIN and box.h < START_SIZE - MARGIN:
        dir_text = "back"
    elif box.w > START_SIZE + MARGIN and box.h > START_SIZE + MARGIN:
        dir_text = "front"

    # draw an X at the center
    size = 10
    thickness = 3
    cv2.line(image, (box.center_x - size, box.center_y - size),
             (box.center_x + size, box.center_y + size), (0, 255, 255), thickness)
    cv2.line(image, (box.center_x - size, box.center_y + size),
             (box.center_x + size, box.center_y - size), (0, 255, 255), thickness)

    # add direction text to bottom right
    text = dir_text
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_x = image.shape[1] - text_size[0] - 10
    text_y = image.shape[0] - 20

    # add white bg for text
    cv2.rectangle(image,
                  (text_x - 5, text_y - text_size[1] - 5),
                  (text_x + text_size[0] + 5, text_y + 5),
                  (255, 255, 255),
                  -1)

    # add text
    cv2.putText(image, text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return dir_text
