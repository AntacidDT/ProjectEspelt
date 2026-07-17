"""Nim with stone-stack visuals and a progress indicator."""

import time
import random

PILE_MAX = 7
STONES = [0x8410, 0xC618, 0xA510]  # stone colors

def _nim_sum(piles):
    s = 0
    for p in piles:
        s ^= p
    return s

def _cpu_move(piles):
    ns = _nim_sum(piles)
    if ns != 0:
        for i, p in enumerate(piles):
            t = p ^ ns
            if t < p:
                return i, p - t
    ne = [i for i, p in enumerate(piles) if p > 0]
    return random.choice(ne), 1

def nim_loop(tft, read_key):
    piles = [random.randint(3, PILE_MAX) for _ in range(3)]
    sel_pile = 0
    sel_count = 1
    player_turn = True
    msg = 'Your turn'
    game_over = False

    def _draw_stones(x, y, count, sel=False):
        for j in range(count):
            sx = x + j * 28
            c = STONES[j % len(STONES)]
            if sel and j < sel_count:
                c = 0xFFE0
            # Draw stone (oval)
            for dy in range(-5, 6):
                dx = int((5 - abs(dy)) * 1.8)
                tft.hline(sx - dx, y + dy, dx * 2, c)
            # Highlight
            tft.hline(sx - 3, y - 4, 6, min(0xFFFF, c + 0x4200))

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('NIM', 220, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        y = 40
        for i, count in enumerate(piles):
            label = f'Pile {i + 1}:'
            tft.text15(label, 4, y + 4, 0xFFFF if i != sel_pile else 0xFFE0)
            _draw_stones(120, y + 8, count, sel=(i == sel_pile and player_turn))
            # Count label
            tft.text8(f'{count}', 120 + count * 28 + 10, y + 4, 0x8410)
            y += 40

        # Progress bar
        total_left = sum(piles)
        bar_w = 400
        bar_fill = int(bar_w * total_left / (PILE_MAX * 3))
        tft.fill_rect(40, 180, bar_w, 10, 0x4208)
        tft.fill_rect(40, 180, bar_fill, 10, 0x07E0)
        tft.rect(40, 180, bar_w, 10, 0x8410)

        color = 0x07E0 if player_turn and not game_over else 0x8410
        tft.text15(msg, 4, 200, color, 0x0000)
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            won = ('YOU WIN' in msg)
            if won:
                _hs_set('NIM_WINS', _hs_get('NIM_WINS') + 1)
            wins = _hs_get('NIM_WINS')
            tft.fill_rect(0, 220, 480, 40, 0x0000)
            tft.text15(f'Win streak: {wins}', 170, 220, 0x07FF, 0x0000)
            tft.text15('Enter: rematch  Q: quit', 120, 240, 0x8410, 0x0000)
        if player_turn and not game_over:
            tft.text15('L/R: pile  U/D: count  Enter: take', 4, 230, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch in ('q', 'Q', chr(24)):
            return
        if game_over:
            if ch == chr(10):
                return
            continue
        if not player_turn:
            continue
        if ch in ('\x85', chr(27)):
            sel_pile = (sel_pile - 1) % 3; sel_count = 1; _render()
        elif ch in ('\x84', chr(9)):
            sel_pile = (sel_pile + 1) % 3; sel_count = 1; _render()
        elif ch in ('\x80', 'e'):
            if sel_count < piles[sel_pile]:
                sel_count += 1; _render()
        elif ch in ('\x81', 'd'):
            if sel_count > 1:
                sel_count -= 1; _render()
        elif ch == chr(10):
            piles[sel_pile] -= sel_count
            msg = f'Took {sel_count} from pile {sel_pile + 1}'
            if all(p == 0 for p in piles):
                msg = 'YOU WIN!'; game_over = True; _render(); continue
            player_turn = False; _render()
            time.sleep_ms(600)
            ci, cc = _cpu_move(piles)
            piles[ci] -= cc
            msg = f'CPU took {cc} from pile {ci + 1}'
            player_turn = True
            if all(p == 0 for p in piles):
                msg = 'CPU WINS!'; game_over = True
            _render()
