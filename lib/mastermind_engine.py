"""Mastermind with proper color peg graphics."""

import time
import random

COLORS = ['R', 'G', 'B', 'Y', 'O', 'P']
TFT_HEX = {'R': 0xF800, 'G': 0x07E0, 'B': 0x001F, 'Y': 0xFFE0, 'O': 0xFD20, 'P': 0xF81F}
TRIES = 10
CODE_LEN = 4
PEG_R = 8

def _feedback(secret, guess):
    black = sum(s == g for s, g in zip(secret, guess))
    sf = {}; gf = {}
    for s, g in zip(secret, guess):
        sf[s] = sf.get(s, 0) + 1
        gf[g] = gf.get(g, 0) + 1
    common = sum(min(sf.get(c, 0), gf.get(c, 0)) for c in COLORS)
    return black, common - black

def _draw_peg(tft, cx, cy, color_hex, r=PEG_R):
    """Draw a filled circle peg."""
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        tft.hline(cx - dx, cy + dy, dx * 2 + 1, color_hex)
    # Highlight
    tft.fill_rect(cx - r // 2, cy - r // 2, r // 2, r // 2,
                  min(0xFFFF, color_hex + 0x4200))

def _draw_peg_small(tft, cx, cy, color_hex):
    _draw_peg(tft, cx, cy, color_hex, 5)

def _draw_feedback(tft, cx, cy, black, white):
    """Draw key-style feedback pegs."""
    for i in range(black):
        tft.fill_rect(cx + i * 10, cy, 7, 7, 0xFFFF)
    for i in range(white):
        tft.fill_rect(cx + (black + i) * 10, cy, 7, 7, 0x8410)

def mastermind_loop(tft, read_key):
    secret = [random.choice(COLORS) for _ in range(CODE_LEN)]
    guesses = []
    sel = 0
    current = ['R'] * CODE_LEN
    won = False

    def _render():
        tft.fill(0x0000)
        # Header
        tft.fill_rect(0, 0, 480, 28, 0x1082)
        tft.text15('MASTERMIND', 170, 6, 0x07FF, 0x1082)
        tft.text15(f'{TRIES - len(guesses)} left', 400, 6, 0xFFE0, 0x1082)

        # Previous guesses
        y = 36
        for i, (guess, bl, wh) in enumerate(guesses):
            row_x = 20
            for j, c in enumerate(guess):
                _draw_peg(tft, row_x + j * 36, y + 8, TFT_HEX[c], 7)
            _draw_feedback(tft, 200, y + 3, bl, wh)
            color = 0x07E0 if bl == CODE_LEN else 0x8410
            tft.text8(str(i + 1), 170, y + 2, color)

        # Current guess row
        y_cur = 36 + len(guesses) * 22
        tft.fill_rect(10, y_cur - 2, 460, 22, 0x2104)
        tft.rect(10, y_cur - 2, 460, 22, 0x07FF)
        for i in range(CODE_LEN):
            cx = 38 + i * 36
            if i == sel:
                tft.rect(cx - PEG_R - 3, y_cur + 8 - PEG_R - 3,
                         PEG_R * 2 + 6, PEG_R * 2 + 6, 0xFFE0)
            _draw_peg(tft, cx, y_cur + 8, TFT_HEX[current[i]])

        # Color palette
        y_pal = 260
        tft.text8('Colors:', 10, y_pal, 0x8410)
        for i, c in enumerate(COLORS):
            cx = 80 + i * 50
            _draw_peg(tft, cx, y_pal + 8, TFT_HEX[c], 9)

        # Controls
        tft.text8('L/R:peg U/D:color Enter:ok', 10, 290, 0x8410)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch in ('q', 'Q', chr(24)):
            return
        if ch in ('\x85', chr(27)):
            sel = (sel - 1) % CODE_LEN
            _render()
        elif ch in ('\x84', chr(9)):
            sel = (sel + 1) % CODE_LEN
            _render()
        elif ch in ('\x80', 'e'):
            current[sel] = COLORS[(COLORS.index(current[sel]) - 1) % len(COLORS)]
            _render()
        elif ch in ('\x81', 'd'):
            current[sel] = COLORS[(COLORS.index(current[sel]) + 1) % len(COLORS)]
            _render()
        elif ch == chr(10):
            bl, wh = _feedback(secret, list(current))
            guesses.append((list(current), bl, wh))
            if bl == CODE_LEN:
                won = True
                break
            if len(guesses) >= TRIES:
                break
            _render()

    # End screen
    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 28, 0x1082)
    tft.text15('MASTERMIND', 170, 6, 0x07FF, 0x1082)
    if won:
        from lib.highscores import get as _hs_get
        from lib.highscores import _load, _save
        tries = len(guesses)
        data = _load()
        prev = data.get('MASTERMIND', 99)
        if prev == 99 or tries < prev:
            data['MASTERMIND'] = tries
            _save()
        best = _hs_get('MASTERMIND')
        tft.text15('YOU WIN!', 190, 90, 0x07E0, 0x0000)
        tft.text15(f'Solved in {tries} tries', 140, 120, 0xFFFF, 0x0000)
        tft.text15(f'Best: {best} tries', 140, 140, 0x07FF, 0x0000)
    else:
        tft.text15('GAME OVER', 190, 100, 0xF800, 0x0000)
        tft.text15('The code was:', 160, 130, 0xFFFF, 0x0000)
        for i, c in enumerate(secret):
            _draw_peg(tft, 170 + i * 40, 170, TFT_HEX[c], 10)
    tft.text15('Press any key to exit', 130, 240, 0x8410, 0x0000)
    while True:
        if read_key() is not None:
            return
