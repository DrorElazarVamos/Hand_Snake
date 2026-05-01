import cv2 as cv
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import Snake
import enum
from collections import deque

TWO_HAND = 2
LEFT_HAND = 1
RIGHT_HAND = -1
NO_HAND = 0

class Hand_controll:
    HAND_CENTER_SAVE = 5
    FRAME_RATE = 3  # per second
    DERIVATIVE_THRESHOLD = 30  # pixels of movement to register a direction change

    def __init__(self, snake: Snake):
        self._hand = False                 # bool - is there a hand in the frame
        self._hand_center = deque(maxlen=self.HAND_CENTER_SAVE)  # history of (R_L, cx, cy) tuples
        self._D_y = 0.0                    # change in y axis (up/down)
        self._D_x = 0.0                    # change in x axis (right/left)
        self._snake = snake
        self._cnt_hand = NO_HAND

    def hand_center(self, results, frame, R_L):
        for hand_landmarks in results.multi_hand_landmarks:
            h, w, _ = frame.shape

            palm_center = hand_landmarks.landmark[9]  # Middle finger MCP
            cx = int(palm_center.x * w)
            cy = int(palm_center.y * h)

            self._hand_center.append((R_L, cx, cy))

    def run(self):
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75,
            max_num_hands=2)

        cap = cv.VideoCapture(0)

        while self._snake.alive:
            success, frame = cap.read()

            frame = cv.flip(frame, 1)
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                # Both Hands are present in image(frame)
                if len(results.multi_handedness) == 2:
                    self._cnt_hand = TWO_HAND

                # If any hand present
                else:
                    for i in results.multi_handedness:
                        label = MessageToDict(i)[
                            'classification'][0]['label']

                        if label == 'Left':
                            self._cnt_hand = LEFT_HAND
                            self.hand_center(results, frame, LEFT_HAND)

                        if label == 'Right':
                            self._cnt_hand = RIGHT_HAND
                            self.hand_center(results, frame, RIGHT_HAND)

                        self.find_direction()

            else: #no hands in the frame
                self._cnt_hand = NO_HAND

            if self._cnt_hand in {LEFT_HAND, RIGHT_HAND}:
                self.monitor_hand()

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
                self._snake.move(Snake.DIRECTION.RIGHT)
            elif self._D_x < -t:
                self._snake.move(Snake.DIRECTION.LEFT)
            else:
                self._snake.move(Snake.DIRECTION.CRUSE)
        else:
            if self._D_y > t:
                self._snake.move(Snake.DIRECTION.DOWN)
            elif self._D_y < -t:
                self._snake.move(Snake.DIRECTION.UP)
            else:
                self._snake.move(Snake.DIRECTION.CRUSE)
