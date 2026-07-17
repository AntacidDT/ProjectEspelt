"""Tron — Light cycles. Two players (or vs CPU). Don't crash.
Arrow keys to steer. Q to quit.
"""
import time
import random

GRID_W, GRID_H = 40, 28
CELL = 11
OX, OY = 25, 30

DIRS = {'\x84': (1, 0), '\x85': (-1, 0), '\x80': (0, -1), '\x81': (0, 1)}

def _check_win(px, py, ox, oy, trail_p, trail_o):
    cp = (0 <= px < GRID_W and 0 <= py < GRID_H and
          (px, py) not in trail_p and (px, py) not in trail_o)
    co = (0 <= ox < GRID_W and 0 <= oy < GRID_H and
          (ox, oy) not in trail_p and (ox, oy) not in trail_o)
    return cp, co

def tron_loop(tft, read_key):
    px, py = 5, 14
    ox, oy = 34, 14
    pdx, pdy = 1, 0
    odx, ody = -1, 0
    trail_p = set()
    trail_o = set()
    score_p = 0
    score_o = 0
    game_over = False
    speed = 120
    last_move = time.ticks_ms()
    use_cpu = True

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('TRON', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        tft.rect(OX-1, OY-1, GRID_W*CELL+2, GRID_H*CELL+2, 0x8410)
        for x, y in trail_p:
            tft.fill_rect(OX + x*CELL, OY + y*CELL, CELL-1, CELL-1, 0x001F)
        for x, y in trail_o:
            tft.fill_rect(OX + x*CELL, OY + y*CELL, CELL-1, CELL-1, 0xF800)
        if not game_over:
            tft.fill_rect(OX + px*CELL, OY + py*CELL, CELL-1, CELL-1, 0x07FF)
            tft.fill_rect(OX + ox*CELL, OY + oy*CELL, CELL-1, CELL-1, 0xFD20)
        else:
            winner = 'YOU' if score_p > score_o else 'CPU'
            tft.text15('GAME OVER', 170, 160, 0xF800, 0x0000)
            tft.text15(f'{winner} WINS', 170, 180, 0xFFE0, 0x0000)
            tft.text15(f'P1: {score_p}  P2: {score_o}', 170, 200, 0x07FF, 0x0000)
            tft.text15('Enter: restart  Q: quit', 120, 225, 0x8410, 0x0000)

    _render()

    while True:
        now = time.ticks_ms()
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', chr(24)):
                return
            if game_over:
                if ch == chr(10):
                    px, py = 5, 14
                    ox, oy = 34, 14
                    pdx, pdy = 1, 0
                    odx, ody = -1, 0
                    trail_p = set()
                    trail_o = set()
                    game_over = False
                    _render()
                continue
            nd = DIRS.get(ch)
            if nd and (nd[0] != -pdx or nd[1] != -pdy):
                pdx, pdy = nd

        if not game_over and time.ticks_diff(now, last_move) >= speed:
            last_move = now

            if use_cpu and not game_over:
                if random.randint(0, 5) == 0:
                    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
                    random.shuffle(dirs)
                    for d in dirs:
                        if d != (-odx, -ody):
                            nox, noy = ox + d[0], oy + d[1]
                            if (0 <= nox < GRID_W and 0 <= noy < GRID_H and
                                (nox, noy) not in trail_p and (nox, noy) not in trail_o):
                                odx, ody = d
                                break

            np = (px + pdx, py + pdy)
            no = (ox + odx, oy + ody)

            px, py = np
            ox, oy = no

            trail_p.add((px, py))
            trail_o.add((ox, oy))

            pp, po = _check_win(px, py, ox, oy, trail_p, trail_o)

            if not pp or not po:
                game_over = True
                score_p = len(trail_p)
                score_o = len(trail_o)
                _render()
            else:
                _render()
