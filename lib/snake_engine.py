"""Snake — unified snake engine with Classic and Obstacles modes.
Arrow keys or WASD to steer. Q to quit.
"""
import time
import random

GRID_W, GRID_H = 20, 15
CELL = 16
OX, OY = 80, 34

DIRS = {'\x84': (0, 1), '\x85': (0, -1), '\x80': (-1, 0), '\x81': (1, 0)}
DIRS_ASD = {'d': (0, 1), 'a': (0, -1), 'w': (0, -1), 's': (0, 1), 'e': (-1, 0)}

def _place_food(snake, obstacles=None):
    obs = obstacles or set()
    while True:
        pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
        if pos not in snake and pos not in obs:
            return pos

def _place_obstacles():
    obs = set()
    for _ in range(8):
        while True:
            x = random.randint(2, GRID_W - 3)
            y = random.randint(2, GRID_H - 3)
            if (x, y) not in obs:
                obs.add((x, y))
                break
    return obs

def _select_mode(tft, read_key):
    modes = ['Classic', 'Obstacles']
    selected = 0
    while True:
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('SNAKE - Select Mode', 120, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        for i, mode in enumerate(modes):
            y = 100 + i * 50
            color = 0x07E0 if i == selected else 0x8410
            marker = '>' if i == selected else ' '
            tft.text15(f'{marker} {mode}', 160, y, color, 0x0000)
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

def snake_loop(tft, read_key):
    mode = _select_mode(tft, read_key)
    if mode is None:
        return
    has_obstacles = (mode == 1)

    snake = [(10, 7), (9, 7), (8, 7)]
    dx, dy = 1, 0
    obstacles = _place_obstacles() if has_obstacles else set()
    food = _place_food(snake, obstacles)
    score = 0
    game_over = False
    speed = 150
    last_move = time.ticks_ms()
    food_pulse = 0

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        title = 'SNAKE' if not has_obstacles else 'SNAKE - Obstacles'
        tft.text15(title, 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        tft.rect(OX - 2, OY - 2, GRID_W * CELL + 4, GRID_H * CELL + 4, 0x8410)
        for ox, oy in obstacles:
            tft.fill_rect(OX + ox * CELL + 2, OY + oy * CELL + 2, CELL - 4, CELL - 4, 0x8410)
        fx, fy = food
        pulse = 2 if food_pulse % 6 < 3 else 0
        tft.fill_rect(OX + fx * CELL + 2 - pulse, OY + fy * CELL + 2 - pulse,
                     CELL - 4 + pulse * 2, CELL - 4 + pulse * 2, 0xF800)
        for i, (sx, sy) in enumerate(snake):
            if i == 0:
                x = OX + sx * CELL + 1
                y = OY + sy * CELL + 1
                tft.fill_rect(x, y, CELL - 2, CELL - 2, 0x07E0)
                if dx == 1:
                    tft.fill_rect(x + CELL - 5, y + 4, 3, 3, 0x0000)
                    tft.fill_rect(x + CELL - 5, y + CELL - 7, 3, 3, 0x0000)
                elif dx == -1:
                    tft.fill_rect(x + 2, y + 4, 3, 3, 0x0000)
                    tft.fill_rect(x + 2, y + CELL - 7, 3, 3, 0x0000)
                elif dy == -1:
                    tft.fill_rect(x + 4, y + 2, 3, 3, 0x0000)
                    tft.fill_rect(x + CELL - 7, y + 2, 3, 3, 0x0000)
                else:
                    tft.fill_rect(x + 4, y + CELL - 5, 3, 3, 0x0000)
                    tft.fill_rect(x + CELL - 7, y + CELL - 5, 3, 3, 0x0000)
            else:
                shade = 0x03E0 if i < len(snake) // 2 else 0x07E0
                tft.fill_rect(OX + sx * CELL + 1, OY + sy * CELL + 1, CELL - 2, CELL - 2, shade)
        tft.text15(f'Score: {score}', 4, 290, 0x8410, 0x0000)
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            key = 'SNAKE_OBS' if has_obstacles else 'SNAKE'
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
                    snake = [(10, 7), (9, 7), (8, 7)]
                    dx, dy = 1, 0
                    obstacles = _place_obstacles() if has_obstacles else set()
                    food = _place_food(snake, obstacles)
                    score = 0
                    game_over = False
                    speed = 150
                    _render()
                continue
            new_dir = DIRS.get(ch) or DIRS_ASD.get(ch)
            if new_dir and (new_dir[0] != -dx or new_dir[1] != -dy):
                dx, dy = new_dir

        if not game_over and time.ticks_diff(now, last_move) >= speed:
            last_move = now
            hx, hy = snake[0]
            nx, ny = hx + dx, hy + dy

            if (nx, ny) in snake or nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H:
                game_over = True
                _render()
                continue
            if has_obstacles and (nx, ny) in obstacles:
                game_over = True
                _render()
                continue

            snake.insert(0, (nx, ny))

            if (nx, ny) == food:
                score += 10
                food = _place_food(snake, obstacles)
                speed = max(60, speed - 3)
                food_pulse = 0
            else:
                snake.pop()

            food_pulse += 1
            _render()
