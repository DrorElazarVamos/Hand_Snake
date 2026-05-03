
import os

# Game modes
TEST = 1
GAME = 2
BOT  = 3

# Timing
WAIT_FOR_KEY = 1000  # ms between auto-moves when no key is pressed

# Snake
SNAKE_START_LENGTH = 3

# Hand detection state
TWO_HAND   =  2
LEFT_HAND  =  1
RIGHT_HAND = -1
NO_HAND    =  0

# Hand control tuning
HAND_CENTER_SAVE     = 5  # number of recent palm positions to keep
DERIVATIVE_THRESHOLD = 5  # minimum pixel displacement to register a direction change

# MediaPipe hand-landmarker model
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

# Display colors (RGB)
GRID_COLOR = (50, 50, 50)
