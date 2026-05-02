#Board class
from enum import Enum
import random
import threading
from collections import deque

#the blocks in the Board
class Block(Enum):
    Clear      = 'C'
    Fruit      = 'F'
    Snake      = 'S'
    Snake_head = 'H'
    Next_Fruit = 'N'

class Board:
    def __init__(self, n: int) -> None:
        self._n = n #size of the sides
        self._blocks = [[Block.Clear] * n for _ in range(n)] #matrix of clear blocks
        self._snake = None #snake reference
        self._snake_body = deque() 
        self._fruit_pos = None
        self._next_fruit_pos = None
        self._stop_event = threading.Event()
        self._monitor_thread = None

    def __del__(self):
        self._stop_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)

    def snake_pos(self) -> tuple:
        mid = self._n // 2
        return (mid, mid)

    def set_snake(self, snake) -> None:
        self._snake = snake
        self._snake_body = deque(snake._body)
        hx, hy = self._snake_body[0]
        self._blocks[hy][hx] = Block.Snake_head
        for x, y in list(self._snake_body)[1:]:
            if 0 <= x < self._n and 0 <= y < self._n:
                self._blocks[y][x] = Block.Snake
        self.gen_fruit()

    def clear(self) -> None:
        for row in range(self._n):
            for col in range(self._n):
                self._blocks[row][col] = Block.Clear

    def _free_positions(self) -> list:
        free = []
        for row in range(self._n):
            for col in range(self._n):
                if self._blocks[row][col] == Block.Clear:
                    free.append((col, row))
        return free

    def monitor_next_fruit_pos(self) -> None:
        while not self._stop_event.is_set():
            if self._next_fruit_pos is not None:
                nx, ny = self._next_fruit_pos
                current = self._blocks[ny][nx]
                if current not in (Block.Clear, Block.Next_Fruit):
                    free = self._free_positions()
                    if free:
                        new_x, new_y = random.choice(free)
                        if self._blocks[ny][nx] == Block.Next_Fruit:
                            self._blocks[ny][nx] = Block.Clear
                        self._next_fruit_pos = (new_x, new_y)
                        self._blocks[new_y][new_x] = Block.Next_Fruit
            self._stop_event.wait(0.1)

    def gen_fruit(self) -> None:
        free = self._free_positions()
        if not free:
            return

        if self._next_fruit_pos is not None:
            nx, ny = self._next_fruit_pos
            if self._blocks[ny][nx] in (Block.Next_Fruit, Block.Clear):
                self._blocks[ny][nx] = Block.Fruit
                self._fruit_pos = self._next_fruit_pos
            else:
                fx, fy = random.choice(free)
                self._blocks[fy][fx] = Block.Fruit
                self._fruit_pos = (fx, fy)
        else:
            fx, fy = random.choice(free)
            self._blocks[fy][fx] = Block.Fruit
            self._fruit_pos = (fx, fy)

        free = self._free_positions()
        if free:
            nx, ny = random.choice(free)
            self._next_fruit_pos = (nx, ny)
            self._blocks[ny][nx] = Block.Next_Fruit

        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(
                target=self.monitor_next_fruit_pos, daemon=True
            )
            self._monitor_thread.start()

    def update_snake(self, direction,source: bool ) -> None:
        from Snake import DIRECTION

        if not self._snake or not self._snake._alive:
            return

        hx, hy = self._snake_body[0]
        dx, dy = 0, 0
        if   direction == DIRECTION.RIGHT: dx =  1
        elif direction == DIRECTION.LEFT:  dx = -1
        elif direction == DIRECTION.UP:    dy = -1
        elif direction == DIRECTION.DOWN:  dy = 1                
        new_head = (hx + dx, hy + dy)
        nx, ny = new_head

        if not (0 <= nx < self._n and 0 <= ny < self._n):
            self._snake.knot()
            return

        target = self._blocks[ny][nx]

        if target in (Block.Snake, Block.Snake_head):
            self._snake.knot()
            return

        ate_fruit     = (target == Block.Fruit)
        hit_next_slot = (target == Block.Next_Fruit)

        # Advance old head to body block
        self._blocks[hy][hx] = Block.Snake

        # Place new head
        self._snake_body.appendleft(new_head)
        self._blocks[ny][nx] = Block.Snake_head
        self._snake._head_pos = new_head

        if ate_fruit:
            self._snake.eat()
            self.gen_fruit()
        else:
            tx, ty = self._snake_body.pop()
            self._blocks[ty][tx] = Block.Clear
            if hit_next_slot:
                self._next_fruit_pos = None
