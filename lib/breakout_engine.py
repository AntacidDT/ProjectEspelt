"""Breakout — unified breakout engine with Classic and Multi-ball/Levels modes.
Arrow keys or A/D to move paddle. Q to quit.
"""
import time
import random

PADDLE_W = 60
PADDLE_H = 8
BALL_R = 4
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_W = 54
BRICK_H = 12
BRICK_OX = 6
BRICK_OY = 40

def _make_bricks(level=1):
    bricks = []
    colors = [0xF800, 0xFD20, 0xFFE0, 0x07E0, 0x07FF]
    for r in range(BRICK_ROWS):
        row = []
        for c in range(BRICK_COLS):
            x = BRICK_OX + c * (BRICK_W + 2)
            y = BRICK_OY + r * (BRICK_H + 2)
            hp = 1 if level == 1 else (2 if r < 2 and level > 2 else 1)
            row.append({'x': x, 'y': y, 'color': colors[r % len(colors)], 'hp': hp, 'alive': True})
        bricks.append(row)
    return bricks

def _select_mode(tft, read_key):
    modes = ['Classic', 'Multi-ball + Levels']
    selected = 0
    while True:
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('BREAKOUT - Select Mode', 100, 4, 0x07FF, 0x1082)
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

def breakout_loop(tft, read_key):
    mode = _select_mode(tft, read_key)
    if mode is None:
        return
    has_multi = (mode == 1)

    paddle_x = 210
    balls = [{'x': 240.0, 'y': 280.0, 'dx': 2.0, 'dy': -2.0}]
    bricks = _make_bricks(1)
    score = 0
    lives = 3 if has_multi else 1
    level = 1
    game_over = False
    won = False
    multi_ready = True
    multi_cooldown = 0

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        title = 'BREAKOUT' if not has_multi else f'BREAKOUT L{level}'
        tft.text15(title, 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        for row in bricks:
            for b in row:
                if b['alive']:
                    color = b['color'] if b['hp'] == 1 else 0xFFFF
                    tft.fill_rect(b['x'], b['y'], BRICK_W, BRICK_H, color)
        tft.fill_rect(paddle_x, 300, PADDLE_W, PADDLE_H, 0xFFFF)
        for b in balls:
            tft.fill_rect(int(b['x'])-BALL_R, int(b['y'])-BALL_R, BALL_R*2, BALL_R*2, 0x07FF)
        if has_multi:
            tft.text15(f'S:{score}  L:{lives}  Multi:{"ON" if multi_ready else "OFF"}', 4, 290, 0x8410, 0x0000)
        else:
            tft.text15(f'Score: {score}', 4, 290, 0x8410, 0x0000)
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            key = 'BREAKOUT2' if has_multi else 'BREAKOUT'
            _hs_set(key, score)
            best = _hs_get(key)
            msg = 'YOU WIN!' if won else 'GAME OVER'
            color = 0x07E0 if won else 0xF800
            tft.text15(msg, 180, 170, color, 0x0000)
            tft.text15(f'Score: {score}', 180, 190, 0xFFE0, 0x0000)
            tft.text15(f'Best:  {best}', 180, 210, 0x07FF, 0x0000)
            tft.text15('Enter: restart  Q: quit', 120, 235, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        now = time.ticks_ms()
        if ch is not None:
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            if game_over:
                if ch == chr(10):
                    paddle_x = 210
                    balls = [{'x': 240.0, 'y': 280.0, 'dx': 2.0, 'dy': -2.0}]
                    bricks = _make_bricks(1)
                    score = 0
                    lives = 3 if has_multi else 1
                    level = 1
                    game_over = False
                    won = False
                    multi_ready = True
                    _render()
                continue
            if ch in ('\x80', 'a'):
                paddle_x = max(0, paddle_x - 20)
            elif ch in ('\x81', 'd'):
                paddle_x = min(480 - PADDLE_W, paddle_x + 20)
            elif has_multi and ch == ' ' and multi_ready and len(balls) < 4:
                b = balls[0]
                balls.append({'x': b['x'], 'y': b['y'], 'dx': -b['dx'], 'dy': b['dy']})
                multi_ready = False
                multi_cooldown = now

        if not game_over:
            if has_multi and not multi_ready and time.ticks_diff(now, multi_cooldown) > 5000:
                multi_ready = True

            new_balls = []
            for b in balls:
                b['x'] += b['dx']
                b['y'] += b['dy']

                if b['x'] <= BALL_R or b['x'] >= 480 - BALL_R:
                    b['dx'] = -b['dx']
                if b['y'] <= 24 + BALL_R:
                    b['dy'] = -b['dy']

                if b['y'] >= 300 - BALL_R and paddle_x <= b['x'] <= paddle_x + PADDLE_W:
                    b['dy'] = -abs(b['dy'])
                    hit_pos = (b['x'] - paddle_x) / PADDLE_W
                    b['dx'] = (hit_pos - 0.5) * 4

                for row in bricks:
                    for brick in row:
                        if brick['alive']:
                            if (brick['x'] <= b['x'] <= brick['x'] + BRICK_W and
                                brick['y'] <= b['y'] <= brick['y'] + BRICK_H):
                                b['dy'] = -b['dy']
                                if brick['hp'] > 1:
                                    brick['hp'] -= 1
                                else:
                                    brick['alive'] = False
                                    score += 10
                                break

                if b['y'] >= 320:
                    continue
                new_balls.append(b)

            balls = [b for b in new_balls]

            all_clear = all(not b['alive'] for row in bricks for b in row)
            if all_clear:
                if has_multi:
                    level += 1
                    bricks = _make_bricks(level)
                    balls = [{'x': 240.0, 'y': 280.0, 'dx': 2.0, 'dy': -2.0}]
                else:
                    won = True
                    game_over = True

            if not balls:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    balls = [{'x': 240.0, 'y': 280.0, 'dx': 2.0, 'dy': -2.0}]

            _render()
            time.sleep_ms(16)
