#Snake class
from enum import Enum
from collections import deque
from Board import Board

class DIRECTION(Enum):
    RIGHT = 'd'
    LEFT  = 'a'
    UP    = 'w'
    DOWN  = 's'
    CRUSE = None  # stay in the same direction

SNAKE_START_LENGTH = 3

class Snake:
    def __init__(self, board: Board) -> None:
        self._length        = SNAKE_START_LENGTH
        self._alive         = True
        self._fruit_counter = 0
        self._board         = board
        self._last_dir      = DIRECTION.RIGHT

        start_x, start_y = board.snake_pos()
        self._body = deque()
        for i in range(SNAKE_START_LENGTH):
            self._body.append((max(0, start_x - i), start_y))

        self._head_pos = self._body[0]
        board.set_snake(self)

    @property
    def alive(self) -> bool:
        return self._alive

    def move(self, direction: DIRECTION) -> None:
        if not self._alive:
            return
        if direction == DIRECTION.CRUSE:
            direction = self._last_dir
        else:
            self._last_dir = direction
        self._board.update_snake(direction)

    def eat(self) -> None:
        self._fruit_counter += 1
        self._length        += 1

    def knot(self) -> None:
        max_fruits = self._board._n ** 2 - SNAKE_START_LENGTH
        if self._fruit_counter >= max_fruits:
            print("You Win!")
        else:
            self._alive = False
            print("Game Over!")
