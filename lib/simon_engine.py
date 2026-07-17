"""Simon — unified simon engine with Classic and Speed Challenge modes.
Keys 1-4 to input. Q to quit. Repeat the pattern.
"""
import time
import random

COLORS = [0xF800, 0x07E0, 0x001F, 0xFFE0]
LABELS = ['1', '2', '3', '4']
POS = [(40, 60, 180, 90), (260, 60, 180, 90),
       (40, 180, 180, 90), (260, 180, 180, 90)]

def _select_mode(tft, read_key):
    modes = ['Classic', 'Speed Challenge']
    selected = 0
    while True:
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('SIMON - Select Mode', 100, 4, 0x07FF, 0x1082)
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

def simon_loop(tft, read_key):
    mode = _select_mode(tft, read_key)
    if mode is None:
        return
    has_speed = (mode == 1)

    sequence = []
    score = 0
    phase = 'watch'
    input_idx = 0
    flash_speed = 400

    def _draw_btn(idx, bright=False):
        x, y, w, h = POS[idx]
        c = 0xFFFF if bright else COLORS[idx]
        for dy in range(h):
            dx = int((w / 2) * (1 - (dy / (h / 2)) ** 2) ** 0.5) if dy < h // 2 else int((w / 2) * (1 - ((h - dy) / (h / 2)) ** 2) ** 0.5)
            if dx > 0:
                tft.hline(x + w // 2 - dx, y + dy, dx * 2, c)
        if not bright:
            tft.rect(x + 2, y + 2, w - 4, h - 4, min(0xFFFF, c + 0x2108))

    def _flash(idx):
        _draw_btn(idx, True)
        time.sleep_ms(flash_speed)
        _draw_btn(idx, False)
        time.sleep_ms(150)

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        title = 'SIMON' if not has_speed else 'SIMON - Speed'
        tft.text15(title, 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        for i in range(4):
            _draw_btn(i)
        for i, (x, y, w, h) in enumerate(POS):
            tft.text15(LABELS[i], x + w // 2 - 4, y + h // 2 - 7, 0xFFFF, COLORS[i])
        if phase == 'input':
            tft.text15('Your turn!', 4, 280, 0x07E0, 0x0000)
        tft.text15(f'Score: {score}  Round: {len(sequence)}', 200, 280, 0x8410, 0x0000)

    _render()

    while True:
        if phase == 'watch':
            sequence.append(random.randint(0, 3))
            score = len(sequence) - 1
            if has_speed and flash_speed > 200:
                flash_speed -= 20
            msg = f'Round {len(sequence)}...'
            _render()
            time.sleep_ms(800)
            for c in sequence:
                _flash(c)
            phase = 'input'
            input_idx = 0
            _render()
        elif phase == 'input':
            ch = read_key()
            if ch is None:
                continue
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            km = {'1': 0, '2': 1, '3': 2, '4': 3}
            idx = km.get(ch, -1)
            if idx == -1:
                continue
            _flash(idx)
            if idx == sequence[input_idx]:
                input_idx += 1
                if input_idx >= len(sequence):
                    score = len(sequence)
                    phase = 'watch'
                    _render()
                    time.sleep_ms(1000)
            else:
                phase = 'over'
        elif phase == 'over':
            tft.fill(0x0000)
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15('SIMON', 210, 4, 0x07FF, 0x1082)
            from lib.highscores import set as _hs_set, get as _hs_get
            key = 'SIMON_SPEED' if has_speed else 'SIMON'
            _hs_set(key, score)
            best = _hs_get(key)
            tft.text15('GAME OVER', 170, 110, 0xF800, 0x0000)
            tft.text15(f'Score: {score}', 190, 140, 0xFFFF, 0x0000)
            tft.text15(f'Best:  {best}', 190, 160, 0x07FF, 0x0000)
            tft.text15('Enter: play again  Q: quit', 100, 210, 0x8410, 0x0000)
            while True:
                ch = read_key()
                if ch is None:
                    continue
                if ch in ('q', 'Q', '\x1b', '\x03'):
                    return
                if ch == chr(10):
                    sequence = []; score = 0; phase = 'watch'
                    flash_speed = 400
                    _render()
                    break
