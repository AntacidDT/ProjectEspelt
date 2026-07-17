"""2048 puzzle — slide tiles, merge matching numbers, reach2048.
Uses arrow keys to slide. Tiles merge when they collide.
CPU is the random tile spawner (2 or 4 after each move).
"""
import time
import random

def _new_tile(grid):
    """Place a random2 or4 on an empty cell."""
    empty = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
    if not empty:
        return False
    r, c = random.choice(empty)
    grid[r][c] = 2 if random.random() < 0.9 else 4
    return True

def _slide_row_left(row):
    """Slide and merge a single row left."""
    # Remove zeros
    tiles = [x for x in row if x != 0]
    merged = []
    skip = False
    for i in range(len(tiles)):
        if skip:
            skip = False
            continue
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            merged.append(tiles[i] * 2)
            skip = True
        else:
            merged.append(tiles[i])
    merged += [0] * (4 - len(merged))
    return merged

def _move(grid, direction):
    """Move tiles in direction. Returns (new_grid, changed, score)."""
    g = [row[:] for row in grid]
    score = 0
    changed = False
    if direction == 'left':
        for r in range(4):
            new_row = _slide_row_left(g[r])
            if new_row != g[r]:
                changed = True
            score += sum(new_row)
            if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
            g[r] = new_row
    elif direction == 'right':
        for r in range(4):
            new_row = _slide_row_left(g[r][::-1])[::-1]
            if new_row != g[r]:
                changed = True
            score += sum(new_row)
            if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
            g[r] = new_row
    elif direction == 'up':
        for c in range(4):
            col = [g[r][c] for r in range(4)]
            new_col = _slide_row_left(col)
            if new_col != col:
                changed = True
            score += sum(new_col)
            if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
            for r in range(4):
                g[r][c] = new_col[r]
    elif direction == 'down':
        for c in range(4):
            col = [g[r][c] for r in range(4)][::-1]
            new_col = _slide_row_left(col)[::-1]
            if new_col != [g[r][c] for r in range(4)]:
                changed = True
            score += sum(new_col)
            if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
            for r in range(4):
                g[r][c] = new_col[r]
    return g, changed, score

def _game_over(grid):
    for r in range(4):
        for c in range(4):
            if grid[r][c] == 0:
                return False
            if c + 1 < 4 and grid[r][c] == grid[r][c + 1]:
                return False
            if r + 1 < 4 and grid[r][c] == grid[r + 1][c]:
                return False
    return True

def _max_tile(grid):
    return max(max(row) for row in grid)

TILE_COLORS = {
    0: 0x4208, 2: 0xC618, 4: 0xBDE0, 8: 0xFD20,
    16: 0xF800, 32: 0xFA00, 64: 0xFC00, 128: 0xFFE0,
    256: 0xFFC0, 512: 0xFF80, 1024: 0xFF40, 2048: 0x07FF,
}

def _2048_loop(tft, read_key):
    """Full-screen 2048 game."""
    grid = [[0]*4 for _ in range(4)]
    _new_tile(grid)
    _new_tile(grid)
    score = 0
    if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
    game_over = False
    sq = 56  # cell size
    ox, oy = 128, 34  # board origin

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('2048', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        for r in range(4):
            for c in range(4):
                x = ox + c * (sq + 4)
                y = oy + r * (sq + 4)
                val = grid[r][c]
                bg = TILE_COLORS.get(val, 0xFFE0)
                tft.fill_rect(x, y, sq, sq, bg)
                if val > 0:
                    txt = str(val)
                    color = 0x0000 if val < 8 else 0xFFFF
                    tft.text15(txt, x + (sq - len(txt) * 12) // 2, y + 20, color, bg)
        y = oy + 4 * (sq + 4) + 10
        tft.text15('Arrows: slide  Q: quit', 4, y, 0x8410, 0x0000)
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            _hs_set('2048', score)
            best = _hs_get('2048')
            tft.fill_rect(0, 240, 480, 60, 0x0000)
            tft.text15('GAME OVER', 170, 240, 0xF800, 0x0000)
            tft.text15(f'Score: {score}  Best: {best}', 100, 262, 0xFFE0, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch in ('q', 'Q', chr(24)):
            return
        if game_over:
            if ch == chr(10):
                grid = [[0]*4 for _ in range(4)]
                _new_tile(grid)
                _new_tile(grid)
                score = 0
                if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
                game_over = False
                _render()
            continue
        direction = None
        if ch in ('\x85', 'a'):  # Left
            direction = 'left'
        elif ch in ('\x84', 'd'):  # Right
            direction = 'right'
        elif ch in ('\x80', 'e'):  # Up
            direction = 'up'
        elif ch in ('\x81', 's'):  # Down
            direction = 'down'
        if direction:
            grid, changed, gained = _move(grid, direction)
            if changed:
                score += gained
                if _oled: _oled.set_mode('game_hud', score=score, game_name='2048')
                _new_tile(grid)
                if _max_tile(grid) >= 2048:
                    tft.text15('YOU WIN! Hit2048!', 140, 280, 0x07E0, 0x0000)
                if _game_over(grid):
                    game_over = True
            _render()
