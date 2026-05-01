import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import Snake
from collections import deque
from constants import (
    TWO_HAND, LEFT_HAND, RIGHT_HAND, NO_HAND,
    MODEL_URL, MODEL_PATH,
    HAND_CENTER_SAVE, DERIVATIVE_THRESHOLD,
)


def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand landmarker model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")


class Hand_controll:
    HAND_CENTER_SAVE     = HAND_CENTER_SAVE
    DERIVATIVE_THRESHOLD = DERIVATIVE_THRESHOLD

    def __init__(self, snake: Snake):
        self._hand_center = deque(maxlen=self.HAND_CENTER_SAVE)
        self._D_y = 0.0
        self._D_x = 0.0
        self._snake = snake
        self._cnt_hand = NO_HAND
        self._display_frame = None
        self._last_direction = Snake.DIRECTION.CRUSE

    def display_frame(self, frame, hand_landmarks, R_L):
        h, w, _ = frame.shape
        palm = hand_landmarks[9]
        cx = int(palm.x * w)
        cy = int(palm.y * h)

        cv.circle(frame, (cx, cy), 12, (0, 255, 0), -1)

        label = "Left" if R_L == LEFT_HAND else "Right"
        cv.putText(frame, label, (cx + 16, cy + 6),
                   cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        dir_name = self._last_direction.name
        cv.putText(frame, f"Dir: {dir_name}", (10, 40),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

    def hand_center(self, hand_landmarks, frame, R_L):
        h, w, _ = frame.shape
        palm_center = hand_landmarks[9]  # Middle finger MCP
        cx = int(palm_center.x * w)
        cy = int(palm_center.y * h)
        self._hand_center.append((R_L, cx, cy))

    def run(self):
        _ensure_model()

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.75,
            min_hand_presence_confidence=0.75,
            min_tracking_confidence=0.75,
            running_mode=vision.RunningMode.IMAGE,
        )
        detector = vision.HandLandmarker.create_from_options(options)

        cap = cv.VideoCapture(0)

        while self._snake.alive:
            success, frame = cap.read()
            if not success:
                continue

            frame = cv.flip(frame, 1)
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            results = detector.detect(mp_image)

            if results.hand_landmarks:
                num_hands = len(results.hand_landmarks)

                if num_hands == 2:
                    self._cnt_hand = TWO_HAND
                else:
                    for i, handedness in enumerate(results.handedness):
                        label = handedness[0].category_name

                        if label == 'Left':
                            self._cnt_hand = LEFT_HAND
                            self.hand_center(results.hand_landmarks[i], frame, LEFT_HAND)
                            self.display_frame(frame, results.hand_landmarks[i], LEFT_HAND)

                        if label == 'Right':
                            self._cnt_hand = RIGHT_HAND
                            self.hand_center(results.hand_landmarks[i], frame, RIGHT_HAND)
                            self.display_frame(frame, results.hand_landmarks[i], RIGHT_HAND)

                        self.find_direction()
            else:
                self._cnt_hand = NO_HAND
                cv.putText(frame, "No Hand", (10, 40),
                           cv.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 255), 2)

            self._display_frame = frame

            if self._cnt_hand in {LEFT_HAND, RIGHT_HAND}:
                self.monitor_hand()

        cap.release()
        detector.close()

    def find_direction(self):
        if len(self._hand_center) < 2:
            return
        oldest = self._hand_center[0]
        newest = self._hand_center[-1]
        self._D_x = newest[1] - oldest[1]
        self._D_y = newest[2] - oldest[2]

    def monitor_hand(self):
        t = self.DERIVATIVE_THRESHOLD
        if abs(self._D_x) >= abs(self._D_y):
            if self._D_x > t:
                self._last_direction = Snake.DIRECTION.RIGHT
                self._snake.move(Snake.DIRECTION.RIGHT)
            elif self._D_x < -t:
                self._last_direction = Snake.DIRECTION.LEFT
                self._snake.move(Snake.DIRECTION.LEFT)
            else:
                self._last_direction = Snake.DIRECTION.CRUSE
                self._snake.move(Snake.DIRECTION.CRUSE)
        else:
            if self._D_y > t:
                self._last_direction = Snake.DIRECTION.DOWN
                self._snake.move(Snake.DIRECTION.DOWN)
            elif self._D_y < -t:
                self._last_direction = Snake.DIRECTION.UP
                self._snake.move(Snake.DIRECTION.UP)
            else:
                self._last_direction = Snake.DIRECTION.CRUSE
                self._snake.move(Snake.DIRECTION.CRUSE)
