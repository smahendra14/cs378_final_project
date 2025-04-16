import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Function to determine if fingers are up or down
def get_finger_states(hand_landmarks):
    finger_tips_ids = [4, 8, 12, 16, 20]
    finger_states = []

    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        finger_states.append(1)
    else:
        finger_states.append(0)

    # Other four fingers
    for tip_id in finger_tips_ids[1:]:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            finger_states.append(1)
        else:
            finger_states.append(0)

    return finger_states  # [Thumb, Index, Middle, Ring, Pinky]

# Start webcam feed
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Flip image horizontally for mirror effect
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process image and find hands
    results = hands.process(image_rgb)

    gesture = "No Hand Detected"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get finger states
            finger_states = get_finger_states(hand_landmarks)

            # Recognize simple gestures
            if finger_states == [0, 1, 0, 0, 0]:
                gesture = "Pointing"
            elif finger_states == [0, 1, 1, 0, 0]:
                gesture = "Peace ✌️"
            elif finger_states == [1, 0, 0, 0, 0]:
                gesture = "Thumbs Up 👍"
            elif finger_states == [0, 0, 0, 0, 0]:
                gesture = "Fist 👊"
            elif finger_states == [1, 1, 1, 1, 1]:
                gesture = "Open Palm 🖐️"
            else:
                gesture = "Unknown"

    # Display gesture
    cv2.putText(image, f'Gesture: {gesture}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the image
    cv2.imshow('Gesture Recognition', image)

    # Exit with ESC
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
