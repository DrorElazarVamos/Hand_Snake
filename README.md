# Handy Snaky

A classic Snake game controlled by hand gestures via your webcam, built with Python, Pygame, and MediaPipe.

## Features

- Classic snake gameplay on a grid board
- **Hand gesture control** — move the snake by physically moving your hand in front of the camera
- **Keyboard fallback** — arrow keys also work
- Live webcam feed displayed alongside the game board
- Next-fruit preview indicator on the board

## How It Works

| Module | Role |
|---|---|
| `constants.py` | All shared constants (colors, thresholds, game modes) |
| `Board.py` | Grid state — tracks snake body, fruit positions, and collision |
| `Snake.py` | Snake logic — movement, eating, win/lose detection |
| `Hand_Control.py` | Webcam capture + MediaPipe hand landmark detection → direction signals |
| `Handy_Snaky.py` | Main entry point — Pygame rendering loop + hand control thread |

The hand controller runs on a background thread. It tracks the palm center across recent frames and computes displacement to determine direction (`DERIVATIVE_THRESHOLD` pixels minimum to count as a move).

## Controls

| Input | Action |
|---|---|
| Move hand **right** | Turn right |
| Move hand **left** | Turn left |
| Move hand **up** | Turn up |
| Move hand **down** | Turn down |
| Arrow keys | Same as above |
| Close window | Quit |

## Setup

### Requirements

- Python 3.9+
- A webcam

### Install dependencies

```bash
pip install pygame opencv-python mediapipe
```

### Run

```bash
python Handy_Snaky.py
```

The MediaPipe hand landmarker model (`hand_landmarker.task`) is downloaded automatically on first run.

## Configuration

All tunable values live in `constants.py`:

| Constant | Default | Description |
|---|---|---|
| `SNAKE_START_LENGTH` | `3` | Initial snake length |
| `WAIT_FOR_KEY` | `1000` | Auto-move interval in ms (no key pressed) |
| `DERIVATIVE_THRESHOLD` | `5` | Min pixel displacement to register a hand move |
| `HAND_CENTER_SAVE` | `5` | Number of recent palm positions averaged for direction |
| `GRID_COLOR` | `(50,50,50)` | Background/grid color |

## Game Modes

Defined in `constants.py` — `TEST`, `GAME`, `BOT` — passed to `start()` in `Handy_Snaky.py`.
