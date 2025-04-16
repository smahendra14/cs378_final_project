import cv2
import numpy as np

START_SIZE = 0
MARGIN = 100

# Read the image
cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()
    if not ret:
        print("Failed to grab frame")
        break 

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
        # print(f"x is {x}, y is {y}, w is {w}, h is {h}")
        print(START_SIZE)
        print(f"width is {w}, height is {h}")

        # update start size on first iteration only
        if (START_SIZE == 0): 
            START_SIZE = max(w, h)

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

        # determine which direction to display
        dir_text = ""
        if (abs(rel_x) > abs(rel_y)):
            dir_text = "right" if rel_x > 0 else "left"
        else: 
            dir_text = "down" if rel_y > 0 else "up"

        if (w < START_SIZE - MARGIN and h < START_SIZE - MARGIN):
            dir_text = "back"
        elif (w > START_SIZE + MARGIN and h > START_SIZE + MARGIN):
            dir_text = "front"

        # draw an X at the center
        size = 10  
        thickness = 3 
        cv2.line(image, (center_x - size, center_y - size),
                (center_x + size, center_y + size), (0, 255, 255), thickness)
        cv2.line(image, (center_x - size, center_y + size),
                (center_x + size, center_y - size), (0, 255, 255), thickness)

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

    cv2.imshow('Detected Red Circle', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()