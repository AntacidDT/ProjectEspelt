"""Pong — unified pong engine with Classic CPU, 2 Player, and 3D modes.
Arrow keys or W/S to move paddle. Q to quit.
"""
import time
import random

PADDLE_W = 10
WIN_SCORE_CLASSIC = 5
WIN_SCORE_2P = 7
WIN_SCORE_3D = 5

def _select_mode(tft, read_key):
    modes = ['Classic CPU', '2 Player', '3D Perspective']
    selected = 0
    while True:
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('PONG - Select Mode', 120, 4, 0x07FF, 0x1082)
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

def _select_classic_submode(tft, read_key):
    modes = ['vs CPU (you=left)', 'vs CPU (you=right)', 'CPU vs CPU']
    selected = 0
    while True:
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('Classic CPU - Select Side', 100, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        for i, mode in enumerate(modes):
            y = 100 + i * 50
            color = 0x07E0 if i == selected else 0x8410
            marker = '>' if i == selected else ' '
            tft.text15(f'{marker} {mode}', 120, y, color, 0x0000)
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

def pong_loop(tft, read_key):
    mode = _select_mode(tft, read_key)
    if mode is None:
        return

    if mode == 0:
        _play_classic(tft, read_key)
    elif mode == 1:
        _play_2p(tft, read_key)
    else:
        _play_3d(tft, read_key)

def _play_classic(tft, read_key):
    submode = _select_classic_submode(tft, read_key)
    if submode is None:
        return

    ball_speeds = [4, 6, 8]
    paddle_heights = [60, 48, 36]
    difficulty = 1

    pw = PADDLE_W
    ph = paddle_heights[difficulty]
    lp_y = 130
    rp_y = 130
    bs = ball_speeds[difficulty]
    bx = 240.0
    by = 160.0
    bdx = bs
    bdy = bs
    lscore = 0
    rscore = 0
    win_score = WIN_SCORE_CLASSIC
    trail = []
    left_flash = 0
    right_flash = 0

    human_side = ['left', 'right', None][submode]

    old_lp_y = lp_y
    old_rp_y = rp_y
    old_bx = bx
    old_by = by
    score_dirty = True

    def draw():
        nonlocal old_lp_y, old_rp_y, old_bx, old_by, score_dirty, left_flash, right_flash
        tft.fill_rect(7, int(old_lp_y)-1, pw+2, ph+2, 0x0000)
        tft.fill_rect(461, int(old_rp_y)-1, pw+2, ph+2, 0x0000)
        tft.fill_rect(int(old_bx)-4, int(old_by)-4, 8, 8, 0x0000)
        for i, (tx, ty) in enumerate(trail):
            alpha = 0x4208 if i == 0 else 0x2108
            tft.fill_rect(int(tx)-2, int(ty)-2, 4, 4, alpha)
        lcol = 0xFFFF if left_flash > 0 else 0x07FF
        rcol = 0xFFFF if right_flash > 0 else 0xF800
        tft.fill_rect(8, int(lp_y), pw, ph, lcol)
        tft.fill_rect(462, int(rp_y), pw, ph, rcol)
        tft.fill_rect(int(bx)-3, int(by)-3, 6, 6, 0xFFE0)
        if score_dirty:
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15(f'{lscore}  -  {rscore}', 210, 4, 0x07FF, 0x1082)
            score_dirty = False
        if left_flash > 0:
            left_flash -= 1
        if right_flash > 0:
            right_flash -= 1
        old_lp_y = lp_y
        old_rp_y = rp_y
        old_bx = bx
        old_by = by

    def draw_center_line():
        for y in range(24, 320, 20):
            tft.vline(240, y, min(y+10, 319), 0x4208)

    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15('Pong Classic', 4, 4, 0x07FF, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)
    draw_center_line()
    draw()
    if human_side == 'left':
        tft.text('W/S=Left  Q=quit', 4, 290, 0x07E0, 0x0000)
    elif human_side == 'right':
        tft.text('W/S=Right  Q=quit', 4, 290, 0x07E0, 0x0000)
    else:
        tft.text('Q=quit', 4, 290, 0x07E0, 0x0000)
    time.sleep_ms(500)

    while True:
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if human_side == 'left':
            if ch == 'w':
                lp_y = max(24, lp_y - 20)
            if ch == 's':
                lp_y = min(319 - ph, lp_y + 20)
        elif human_side == 'right':
            if ch == 'w':
                rp_y = max(24, rp_y - 20)
            if ch == 's':
                rp_y = min(319 - ph, rp_y + 20)

        if human_side != 'left':
            if by < lp_y + ph // 2:
                lp_y -= 3
            elif by > lp_y + ph // 2:
                lp_y += 3
            lp_y = max(24, min(319 - ph, lp_y))
        if human_side != 'right':
            if by < rp_y + ph // 2:
                rp_y -= 3
            elif by > rp_y + ph // 2:
                rp_y += 3
            rp_y = max(24, min(319 - ph, rp_y))

        trail.append((bx, by))
        if len(trail) > 2:
            trail.pop(0)

        bx += bdx
        by += bdy

        if by - 3 <= 24 or by + 3 >= 319:
            bdy = -bdy

        if bx - 3 <= 18 and by >= lp_y and by <= lp_y + ph:
            bdx = abs(bdx)
            bdy = int((by - (lp_y + ph/2)) / 8)
            left_flash = 3
        if bx + 3 >= 462 and by >= rp_y and by <= rp_y + ph:
            bdx = -abs(bdx)
            bdy = int((by - (rp_y + ph/2)) / 8)
            right_flash = 3

        if bx < 0:
            rscore += 1
            bx, by = 240.0, 160.0
            bdx, bdy = bs, bs
            trail.clear()
            score_dirty = True
            if rscore >= win_score:
                break
        if bx > 480:
            lscore += 1
            bx, by = 240.0, 160.0
            bdx, bdy = -bs, bs
            trail.clear()
            score_dirty = True
            if lscore >= win_score:
                break

        draw()
        time.sleep_ms(15)

    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15('GAME OVER', 4, 4, 0xF800, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)
    winner = 'Left' if lscore >= win_score else 'Right'
    tft.text(f'{winner} wins! {lscore}-{rscore}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()

def _play_2p(tft, read_key):
    ball_speeds = [4, 6, 8]
    paddle_heights = [60, 48, 36]
    difficulty = 1

    pw = PADDLE_W
    ph = paddle_heights[difficulty]
    lp_y = 130
    rp_y = 130
    bs = ball_speeds[difficulty]
    bx = 240.0
    by = 160.0
    bdx = bs
    bdy = bs
    lscore = 0
    rscore = 0
    win_score = WIN_SCORE_2P
    trail = []
    left_flash = 0
    right_flash = 0

    old_lp_y = lp_y
    old_rp_y = rp_y
    old_bx = bx
    old_by = by
    score_dirty = True

    def draw():
        nonlocal old_lp_y, old_rp_y, old_bx, old_by, score_dirty, left_flash, right_flash
        tft.fill_rect(7, int(old_lp_y)-1, pw+2, ph+2, 0x0000)
        tft.fill_rect(461, int(old_rp_y)-1, pw+2, ph+2, 0x0000)
        tft.fill_rect(int(old_bx)-4, int(old_by)-4, 8, 8, 0x0000)
        for i, (tx, ty) in enumerate(trail):
            alpha = 0x4208 if i == 0 else 0x2108
            tft.fill_rect(int(tx)-2, int(ty)-2, 4, 4, alpha)
        lcol = 0xFFFF if left_flash > 0 else 0x07FF
        rcol = 0xFFFF if right_flash > 0 else 0xF800
        tft.fill_rect(8, int(lp_y), pw, ph, lcol)
        tft.fill_rect(462, int(rp_y), pw, ph, rcol)
        tft.fill_rect(int(bx)-3, int(by)-3, 6, 6, 0xFFE0)
        if score_dirty:
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15(f'P1:{lscore}  P2:{rscore}', 170, 4, 0x07FF, 0x1082)
            score_dirty = False
        if left_flash > 0:
            left_flash -= 1
        if right_flash > 0:
            right_flash -= 1
        old_lp_y = lp_y
        old_rp_y = rp_y
        old_bx = bx
        old_by = by

    def draw_center_line():
        for y in range(24, 320, 20):
            tft.vline(240, y, min(y+10, 319), 0x4208)

    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15('Pong 2 Player', 4, 4, 0x07FF, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)
    draw_center_line()
    draw()
    tft.text('W/S=P1  O/L=P2  Q=quit', 4, 290, 0x07E0, 0x0000)
    time.sleep_ms(500)

    while True:
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if ch == 'w':
            lp_y = max(24, lp_y - 20)
        if ch == 's':
            lp_y = min(319 - ph, lp_y + 20)
        if ch == 'o':
            rp_y = max(24, rp_y - 20)
        if ch == 'l':
            rp_y = min(319 - ph, rp_y + 20)

        trail.append((bx, by))
        if len(trail) > 2:
            trail.pop(0)

        bx += bdx
        by += bdy

        if by - 3 <= 24 or by + 3 >= 319:
            bdy = -bdy

        if bx - 3 <= 18 and by >= lp_y and by <= lp_y + ph:
            bdx = abs(bdx)
            bdy = int((by - (lp_y + ph/2)) / 8)
            left_flash = 3
        if bx + 3 >= 462 and by >= rp_y and by <= rp_y + ph:
            bdx = -abs(bdx)
            bdy = int((by - (rp_y + ph/2)) / 8)
            right_flash = 3

        if bx < 0:
            rscore += 1
            bx, by = 240.0, 160.0
            bdx, bdy = bs, bs
            trail.clear()
            score_dirty = True
            if rscore >= win_score:
                break
        if bx > 480:
            lscore += 1
            bx, by = 240.0, 160.0
            bdx, bdy = -bs, bs
            trail.clear()
            score_dirty = True
            if lscore >= win_score:
                break

        draw()
        time.sleep_ms(15)

    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15('GAME OVER', 4, 4, 0xF800, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)
    winner = 'P1' if lscore >= win_score else 'P2'
    tft.text(f'{winner} wins! {lscore}-{rscore}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()

def _play_3d(tft, read_key):
    VIEW_W, VIEW_H = 480, 300
    PADDLE_W_3D = 60
    PADDLE_H_3D = 10
    BALL_R = 5

    paddle_y = 280
    paddle_x = 210
    ball_x = 240.0
    ball_y = 150.0
    ball_dx = random.choice([-2.0, 2.0])
    ball_dy = random.choice([-1.5, 1.5])
    score_p = 0
    score_cpu = 0
    game_over = False
    won = False
    speed = 60
    last_move = time.ticks_ms()
    cpu_y = 280
    combo = 0

    def _draw_pseudo_3d():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('PONG 3D', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        for y in range(25, 300, 20):
            shade = 0x0001 + (y * 0x0020 // 300)
            tft.hline(0, y, 480, shade)

        tft.vline(240, 25, 300, 0x8410)
        for y in range(25, 300, 30):
            tft.fill_rect(238, y, 4, 15, 0x8410)

        size_p = int(40 + (score_p * 5))
        size_cpu = int(40 + (score_cpu * 5))
        tft.fill_rect(paddle_x, paddle_y, PADDLE_W_3D, PADDLE_H_3D, 0x07FF)
        tft.fill_rect(240 - size_cpu // 2, 30, size_cpu, 8, 0xFD20)

        bx = int(ball_x)
        by = int(ball_y)
        perspective = 1.0 + (by - 150) / 300
        br = int(BALL_R * perspective)
        tft.fill_rect(bx - br, by - br, br * 2, br * 2, 0xFFE0)

        tft.text15(f'YOU: {score_p}  CPU: {score_cpu}  Combo: {combo}', 4, 310, 0x8410, 0x0000)

    _draw_pseudo_3d()

    while True:
        now = time.ticks_ms()
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            if game_over:
                if ch == chr(10):
                    ball_x, ball_y = 240.0, 150.0
                    ball_dx = random.choice([-2.0, 2.0])
                    ball_dy = random.choice([-1.5, 1.5])
                    score_p = 0
                    score_cpu = 0
                    game_over = False
                    won = False
                    combo = 0
                    _draw_pseudo_3d()
                continue
            if ch == '\x80':
                paddle_x = max(0, paddle_x - 15)
            elif ch == '\x81':
                paddle_x = min(VIEW_W - PADDLE_W_3D, paddle_x + 15)

        if not game_over and time.ticks_diff(now, last_move) >= speed:
            last_move = now

            ball_x += ball_dx
            ball_y += ball_dy

            if ball_x <= BALL_R or ball_x >= VIEW_W - BALL_R:
                ball_dx = -ball_dx

            if ball_y <= 25 + BALL_R:
                ball_dy = abs(ball_dy)

            if ball_y >= paddle_y - BALL_R and paddle_x <= ball_x <= paddle_x + PADDLE_W_3D:
                ball_dy = -abs(ball_dy)
                hit_pos = (ball_x - paddle_x) / PADDLE_W_3D
                ball_dx = (hit_pos - 0.5) * 4
                combo += 1

            cpu_target = ball_x - 30 + random.randint(-20, 20)
            if cpu_y < cpu_target:
                cpu_y += 3
            elif cpu_y > cpu_target:
                cpu_y -= 3
            cpu_y = max(0, min(VIEW_W - PADDLE_W_3D, cpu_y))

            if ball_y >= 300:
                score_cpu += 1
                combo = 0
                if score_cpu >= WIN_SCORE_3D:
                    game_over = True
                else:
                    ball_x, ball_y = 240.0, 150.0
                    ball_dx = random.choice([-2.0, 2.0])
                    ball_dy = random.choice([-1.5, 1.5])
            elif ball_y <= 25:
                score_p += 1
                if score_p >= WIN_SCORE_3D:
                    game_over = True
                    won = True
                else:
                    ball_x, ball_y = 240.0, 150.0
                    ball_dx = random.choice([-2.0, 2.0])
                    ball_dy = random.choice([-1.5, 1.5])

            if game_over:
                from lib.highscores import set as _hs_set, get as _hs_get
                _hs_set('PONG3D', score_p)
                best = _hs_get('PONG3D')
                tft.fill(0x0000)
                msg = 'YOU WIN!' if won else 'CPU WINS'
                color = 0x07E0 if won else 0xF800
                tft.text15(msg, 170, 140, color, 0x0000)
                tft.text15(f'Score: {score_p}-{score_cpu}', 170, 160, 0xFFE0, 0x0000)
                tft.text15(f'Best:  {best}', 170, 180, 0x07FF, 0x0000)
                tft.text15('Enter: restart  Q: quit', 120, 205, 0x8410, 0x0000)
            else:
                _draw_pseudo_3d()
