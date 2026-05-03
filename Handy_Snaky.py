#the main pipeline
import Board
import Snake
import pygame as pg
from Snake import DIRECTION
from Board import Block
import threading
import cv2 as cv
from Hand_Control import Hand_controll
from constants import GRID_COLOR, TEST, GAME, BOT, WAIT_FOR_KEY

CELL_COLOR = {
    Block.Clear:      (30,  30,  30),
    Block.Snake_head: (0,  220,  50),
    Block.Snake:      (0,  160,  40),
    Block.Fruit:      (220,  30,  30),
    Block.Next_Fruit: (30, 30, 30)
}

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

    hand_ctrl = Hand_controll(GSnake)
    hand_thread = threading.Thread(target=hand_ctrl.run, daemon=True)
    hand_thread.start()

    cell_size = 400 // board_size
    win_size  = cell_size * board_size

    pg.init()
    screen = pg.display.set_mode((win_size * 2, win_size), pg.RESIZABLE)
    pg.display.set_caption("Snake")
    
    AUTO_MOVE = pg.USEREVENT + 1
    pg.time.set_timer(AUTO_MOVE,WAIT_FOR_KEY)
    
    game_on = True
    while game_on:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_on = False
                break
            
#            #A button have been pressed //
#            if event.type == pg.KEYDOWN:
#                pg.time.set_timer(AUTO_MOVE, WAIT_FOR_KEY)
#                if event.key == pg.K_UP:
#                    GSnake.move(DIRECTION.UP)
#                elif event.key == pg.K_DOWN:
#                    GSnake.move(DIRECTION.DOWN)
#                elif event.key == pg.K_RIGHT:
#                    GSnake.move(DIRECTION.RIGHT)
#                elif event.key == pg.K_LEFT:
#                   GSnake.move(DIRECTION.LEFT)
#               else:                    
#                    GSnake.move(DIRECTION.CRUSE)

            if event.type == AUTO_MOVE:
                GSnake.move(hand_ctrl._direction)
            
        screen.fill(GRID_COLOR)
        draw_board(screen, GBorad, cell_size)

        with hand_ctrl._frame_lock:
            cam_frame = hand_ctrl._display_frame
        if cam_frame is not None:
            cam_resized = cv.resize(cam_frame, (win_size, win_size))
            cam_rgb = cv.cvtColor(cam_resized, cv.COLOR_BGR2RGB)
            cam_surface = pg.image.frombuffer(cam_rgb.tobytes(), (win_size, win_size), 'RGB')
            screen.blit(cam_surface, (win_size, 0))

        pg.display.flip()
    
        
   
_MENU_BG        = (20,  20,  20)
_LABEL          = (200, 200, 200)
_BTN_NORMAL     = (50,  50,  50)
_BTN_HOVER      = (70,  70,  70)
_BTN_SELECTED   = (0,  160,  40)
_INPUT_BG       = (35,  35,  35)
_INPUT_ACTIVE   = (0,  120,  30)
_START_COLOR    = (0,  180,  50)
_START_HOVER    = (0,  220,  70)
_ERROR_COLOR    = (220, 50,  50)
_WHITE          = (255, 255, 255)

_MODE_LABELS = {TEST: "TEST", GAME: "GAME", BOT: "BOT"}

def _draw_text(surf, font, text, color, center):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=center))

def main_menu() -> tuple[int, int]:
    pg.init()
    W, H = 420, 340
    screen = pg.display.set_mode((W, H))
    pg.display.set_caption("Handy Snaky – Main Menu")

    font_title = pg.font.SysFont("segoeui", 34, bold=True)
    font_label = pg.font.SysFont("segoeui", 18)
    font_btn   = pg.font.SysFont("segoeui", 17, bold=True)

    selected_mode = GAME
    size_text     = "10"
    size_active   = False
    error_msg     = ""

    # layout constants
    MODE_BTN_W, MODE_BTN_H = 100, 36
    MODE_BTN_Y  = 130
    mode_rects  = {
        TEST: pg.Rect(30,  MODE_BTN_Y, MODE_BTN_W, MODE_BTN_H),
        GAME: pg.Rect(160, MODE_BTN_Y, MODE_BTN_W, MODE_BTN_H),
        BOT:  pg.Rect(290, MODE_BTN_Y, MODE_BTN_W, MODE_BTN_H),
    }

    size_rect  = pg.Rect(160, 210, 100, 36)
    start_rect = pg.Rect(135, 270, 150, 44)

    clock = pg.time.Clock()

    while True:
        mouse = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # mode buttons
                for mode, rect in mode_rects.items():
                    if rect.collidepoint(event.pos):
                        selected_mode = mode
                        error_msg = ""

                # size input box
                size_active = size_rect.collidepoint(event.pos)

                # start button
                if start_rect.collidepoint(event.pos):
                    try:
                        size = int(size_text)
                    except ValueError:
                        error_msg = "Board size must be a number."
                        continue
                    if size < 5 or size > 50:
                        error_msg = "Board size must be 5 – 50."
                        continue
                    pg.quit()
                    return selected_mode, size

            if event.type == pg.KEYDOWN:
                if size_active:
                    if event.key == pg.K_BACKSPACE:
                        size_text = size_text[:-1]
                        error_msg = ""
                    elif event.unicode.isdigit() and len(size_text) < 2:
                        size_text += event.unicode
                        error_msg = ""
                elif event.key == pg.K_RETURN:
                    # treat Enter as clicking Start
                    try:
                        size = int(size_text)
                    except ValueError:
                        error_msg = "Board size must be a number."
                        continue
                    if size < 5 or size > 50:
                        error_msg = "Board size must be 5 – 50."
                        continue
                    pg.quit()
                    return selected_mode, size

        # ── draw ──────────────────────────────────────────────
        screen.fill(_MENU_BG)

        _draw_text(screen, font_title, "Handy Snaky", _WHITE, (W // 2, 50))

        # mode label
        _draw_text(screen, font_label, "Game mode", _LABEL, (W // 2, 102))

        # mode buttons
        for mode, rect in mode_rects.items():
            hovered = rect.collidepoint(mouse)
            if mode == selected_mode:
                color = _BTN_SELECTED
            elif hovered:
                color = _BTN_HOVER
            else:
                color = _BTN_NORMAL
            pg.draw.rect(screen, color, rect, border_radius=6)
            _draw_text(screen, font_btn, _MODE_LABELS[mode], _WHITE, rect.center)

        # size label + input
        _draw_text(screen, font_label, "Board size (5–50)", _LABEL, (W // 2, 192))
        input_color = _INPUT_ACTIVE if size_active else _INPUT_BG
        pg.draw.rect(screen, input_color, size_rect, border_radius=6)
        display_text = size_text if size_text else ""
        _draw_text(screen, font_btn, display_text, _WHITE, size_rect.center)
        # blinking cursor
        if size_active and (pg.time.get_ticks() // 500) % 2 == 0:
            cx = size_rect.centerx + font_btn.size(display_text)[0] // 2 + 3
            pg.draw.line(screen, _WHITE, (cx, size_rect.top + 8), (cx, size_rect.bottom - 8), 2)

        if error_msg:
            _draw_text(screen, font_label, error_msg, _ERROR_COLOR, (W // 2, 248))

        # start button
        start_color = _START_HOVER if start_rect.collidepoint(mouse) else _START_COLOR
        pg.draw.rect(screen, start_color, start_rect, border_radius=8)
        _draw_text(screen, font_btn, "START", _WHITE, start_rect.center)

        pg.display.flip()
        clock.tick(60)


def start(mode: int, size: int = 10):
    game(size)

if __name__=="__main__":
    mode, size = main_menu()
    start(mode, size)