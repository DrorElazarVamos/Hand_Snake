#the main pipeline
import Board
import Snake
import pygame as pg
from pygame.locals import *
from Snake import DIRECTION
from Board import Block

CELL_COLOR = {
    Block.Clear:      (30,  30,  30),
    Block.Snake_head: (0,  220,  50),
    Block.Snake:      (0,  160,  40),
    Block.Fruit:      (220,  30,  30),
    Block.Next_Fruit: (30, 30, 30)
}
GRID_COLOR = (50, 50, 50)

WAIT_FOR_KEY = 1000

def draw_board(surface: pg.Surface, board: Board.Board, cell: int) -> None:
    for row in range(board._n):
        for col in range(board._n):
            block = board._blocks[row][col]
            color = CELL_COLOR.get(block, CELL_COLOR[Block.Clear])
            rect = pg.Rect(col * cell, row * cell, cell - 1, cell - 1)
            pg.draw.rect(surface, color, rect)


def game(board_size: int):
    GBorad = Board.Board(board_size)
    GSnake = Snake.Snake(GBorad)

    cell_size = 400 // board_size
    win_size  = cell_size * board_size

    pg.init()
    screen = pg.display.set_mode((win_size, win_size), pg.RESIZABLE)
    pg.display.set_caption("Snake")
    
    AUTO_MOVE = pg.USEREVENT + 1
    pg.time.set_timer(AUTO_MOVE,WAIT_FOR_KEY)
    
    game_on = True
    while game_on:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_on = False
                break
            
            #A button have been pressed
            if event.type == KEYDOWN:
                pg.time.set_timer(AUTO_MOVE, WAIT_FOR_KEY)
                if event.key == K_UP:
                    GSnake.move(DIRECTION.UP)
                elif event.key == K_DOWN:
                    GSnake.move(DIRECTION.DOWN)
                elif event.key == K_RIGHT:
                    GSnake.move(DIRECTION.RIGHT)
                elif event.key == K_LEFT:
                    GSnake.move(DIRECTION.LEFT)
                else:                    
                    GSnake.move(DIRECTION.CRUSE)

            if event.type == AUTO_MOVE:
                GSnake.move(DIRECTION.CRUSE)
            
        screen.fill(GRID_COLOR)
        draw_board(screen, GBorad, cell_size)
        pg.display.flip()
    
        
   
def start():
    game(10)
        
if __name__=="__main__":
    start()