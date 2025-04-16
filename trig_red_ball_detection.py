import cv2
import numpy as np
import math

START_SIZE = 0
MARGIN = 50

cap = cv2.VideoCapture(0)  # use 1 if 0 doesn't work

while True:
    ret, image = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.add(mask1, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        detected_size = max(w, h)

        if cv2.waitKey(1) & 0xFF == ord(' '):
            START_SIZE = detected_size
            print(f"START_SIZE set to: {START_SIZE}")

        center_x = x + w // 2
        center_y = y + h // 2

        img_center_x = image.shape[1] // 2
        img_center_y = image.shape[0] // 2

        rel_x = center_x - img_center_x

        # Calculate approximate distance change
        distance_diff = START_SIZE - detected_size

        # Convert relative horizontal offset to angle
        angle_rad = math.atan2(abs(rel_x), max(1, abs(distance_diff)))  # avoid division by zero
        angle_deg = math.degrees(angle_rad)

        # Decide direction based on dominant axis
        dir_text = ""

        if abs(distance_diff) < MARGIN:
            dir_text = "centered"
        elif abs(distance_diff) >= abs(rel_x):
            dir_text = "front" if distance_diff < 0 else "back"
        else:
            dir_text = "right" if rel_x > 0 else "left"

        # Draw bounding box and crosshair
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.line(image, (center_x - 10, center_y - 10), (center_x + 10, center_y + 10), (0, 255, 255), 2)
        cv2.line(image, (center_x - 10, center_y + 10), (center_x + 10, center_y - 10), (0, 255, 255), 2)

        # Draw direction text
        text = f"{dir_text}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = image.shape[1] - text_size[0] - 10
        text_y = image.shape[0] - 20

        cv2.rectangle(image,
                      (text_x - 5, text_y - text_size[1] - 5),
                      (text_x + text_size[0] + 5, text_y + 5),
                      (255, 255, 255), -1)
        cv2.putText(image, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    cv2.imshow('Red Ball Tracker', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
