"""Tetris — unified tetris engine with Classic and Hard Drop/Hold modes.
Arrow keys or WASD to move/rotate. Q to quit.
"""
import time
import random

SHAPES = [
    [[1,1,1,1]],
    [[1,0],[1,0],[1,1]],
    [[0,1],[0,1],[1,1]],
    [[1,1],[1,1]],
    [[0,1,1],[1,1,0]],
    [[1,1,0],[0,1,1]],
    [[1,0,0],[1,1,1]],
]
COLORS = [0x07FF, 0x07E0, 0xF800, 0xFFE0, 0xFD20, 0x001F, 0xF81F]

GRID_W, GRID_H = 10, 20
CELL = 12
OX, OY = 160, 26

def _rotate(shape):
    rows, cols = len(shape), len(shape[0])
    return [[shape[rows-1-j][i] for j in range(rows)] for i in range(cols)]

def _fits(grid, shape, px, py):
    for r, row in enumerate(shape):
        for c, v in enumerate(row):
            if v:
                x, y = px + c, py + r
                if x < 0 or x >= GRID_W or y >= GRID_H:
                    return False
                if y >= 0 and grid[y][x]:
                    return False
    return True

def _lock(grid, shape, px, py, color):
    for r, row in enumerate(shape):
        for c, v in enumerate(row):
            if v and py + r >= 0:
                grid[py + r][px + c] = color

def _clear_lines(grid):
    cleared = 0
    new_grid = []
    for row in grid:
        if all(cell != 0 for cell in row):
            cleared += 1
        else:
            new_grid.append(row)
    for _ in range(cleared):
        new_grid.insert(0, [0] * GRID_W)
    return new_grid, cleared

def _select_mode(tft, read_key):
    modes = ['Classic', 'Hard Drop + Hold']
    selected = 0
    while True:
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('TETRIS - Select Mode', 100, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        for i, mode in enumerate(modes):
            y = 100 + i * 50
            color = 0x07E0 if i == selected else 0x8410
            marker = '>' if i == selected else ' '
            tft.text15(f'{marker} {mode}', 140, y, color, 0x0000)
        tft.text15('W/S=select Enter=confirm Q=quit', 80, 280, 0x8410, 0x0000)
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return None
        if ch in ('\x84', 's'):
            selected = (selected + 1) % len(modes)
        elif ch in ('\x85', 'w'):
            selected = (selected - 1) % len(modes)
        elif ch == chr(10):
            return selected

def tetris_loop(tft, read_key):
    mode = _select_mode(tft, read_key)
    if mode is None:
        return
    has_hard_drop = (mode == 1)

    grid = [[0]*GRID_W for _ in range(GRID_H)]
    shape_idx = random.randint(0, len(SHAPES)-1)
    shape = [row[:] for row in SHAPES[shape_idx]]
    color = COLORS[shape_idx % len(COLORS)]
    px, py = 3, 0
    score = 0
    level = 1
    lines = 0
    game_over = False
    fall_time = time.ticks_ms()
    fall_speed = 800
    hold_shape = None
    hold_used = False
    next_idx = random.randint(0, len(SHAPES)-1)

    def _next_piece():
        nonlocal shape_idx, shape, color, px, py, hold_used, next_idx, game_over
        shape_idx = next_idx
        next_idx = random.randint(0, len(SHAPES)-1)
        shape = [row[:] for row in SHAPES[shape_idx]]
        color = COLORS[shape_idx % len(COLORS)]
        px, py = 3, 0
        hold_used = False
        if not _fits(grid, shape, px, py):
            game_over = True

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        title = 'TETRIS' if not has_hard_drop else 'TETRIS - Enhanced'
        tft.text15(title, 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        tft.rect(OX-2, OY-2, GRID_W*CELL+4, GRID_H*CELL+4, 0x8410)
        for r in range(GRID_H):
            for c in range(GRID_W):
                if grid[r][c]:
                    tft.fill_rect(OX+c*CELL+1, OY+r*CELL+1, CELL-2, CELL-2, grid[r][c])
        gy = py
        while _fits(grid, shape, px, gy+1):
            gy += 1
        for r, row in enumerate(shape):
            for c, v in enumerate(row):
                if v:
                    tft.fill_rect(OX+(px+c)*CELL, OY+(gy+r)*CELL, CELL-1, CELL-1, 0x4208)
        for r, row in enumerate(shape):
            for c, v in enumerate(row):
                if v and py+r >= 0:
                    tft.fill_rect(OX+(px+c)*CELL+1, OY+(py+r)*CELL+1, CELL-2, CELL-2, color)
        RX = OX + GRID_W * CELL + 16
        tft.fill_rect(RX, 32, 100, 80, 0x0000)
        tft.text('Next:', RX, 32, 0xFFFF, 0x0000)
        ns = SHAPES[next_idx]
        nc = COLORS[next_idx % len(COLORS)]
        for r in range(len(ns)):
            for c in range(len(ns[0])):
                if ns[r][c]:
                    tft.fill_rect(RX+4+c*(CELL+2), 48+r*(CELL+2), CELL-1, CELL-1, nc)
        tft.text(f'Score: {score}', RX, 130, 0xFFFF, 0x0000)
        tft.text(f'Level: {level}', RX, 146, 0xFFFF, 0x0000)
        if has_hard_drop and hold_shape:
            tft.text15('HOLD:', 4, 40, 0x8410, 0x0000)
            for r, row in enumerate(hold_shape):
                for c, v in enumerate(row):
                    if v:
                        tft.fill_rect(8+c*10, 55+r*10, 9, 9, 0x07FF)
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            key = 'TETRIS_ENH' if has_hard_drop else 'TETRIS'
            _hs_set(key, score)
            best = _hs_get(key)
            tft.text15('GAME OVER', 170, 180, 0xF800, 0x0000)
            tft.text15(f'Score: {score}', 170, 200, 0xFFE0, 0x0000)
            tft.text15(f'Best:  {best}', 170, 220, 0x07FF, 0x0000)
            tft.text15('Enter: restart  Q: quit', 120, 240, 0x8410, 0x0000)

    _render()

    while True:
        now = time.ticks_ms()
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            if game_over:
                if ch == chr(10):
                    grid = [[0]*GRID_W for _ in range(GRID_H)]
                    score = 0; level = 1; lines = 0
                    hold_shape = None; hold_used = False
                    game_over = False; fall_speed = 800
                    next_idx = random.randint(0, len(SHAPES)-1)
                    _next_piece()
                    _render()
                continue
            if ch in ('\x80', 'a'):
                if _fits(grid, shape, px-1, py):
                    px -= 1
                    _render()
            elif ch in ('\x81', 'd'):
                if _fits(grid, shape, px+1, py):
                    px += 1
                    _render()
            elif ch in ('\x84', 'w', 'e'):
                rotated = _rotate(shape)
                if _fits(grid, rotated, px, py):
                    shape = rotated
                    _render()
            elif ch in ('\x85', 's'):
                if _fits(grid, shape, px, py+1):
                    py += 1
                    _render()
            elif has_hard_drop and ch == ' ':
                while _fits(grid, shape, px, py+1):
                    py += 1
                _lock(grid, shape, px, py, color)
                grid, cleared = _clear_lines(grid)
                if cleared:
                    score += cleared * cleared * 10
                    lines += cleared
                    level = lines // 10 + 1
                    fall_speed = max(100, 800 - (level - 1) * 80)
                _next_piece()
                _render()
            elif has_hard_drop and ch in ('c', 'C') and not hold_used:
                hold_used = True
                if hold_shape is None:
                    hold_shape = [row[:] for row in shape]
                    _next_piece()
                else:
                    hold_shape, shape = [row[:] for row in shape], hold_shape
                    px, py = 3, 0
                _render()

        if not game_over and time.ticks_diff(now, fall_time) >= fall_speed:
            fall_time = now
            if _fits(grid, shape, px, py+1):
                py += 1
            else:
                _lock(grid, shape, px, py, color)
                grid, cleared = _clear_lines(grid)
                if cleared:
                    score += [0, 100, 300, 500, 800][min(cleared, 4)]
                    lines += cleared
                    level = lines // 10 + 1
                    fall_speed = max(100, 800 - (level-1) * 70)
                _next_piece()
            _render()
