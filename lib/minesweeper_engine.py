"""Minesweeper — reveal cells, flag mines. Numbers show adjacent mine count.
Arrow keys to move cursor. Enter to reveal. Space to flag.
"""
import time
import random

ROWS, COLS = 10, 10
MINES = 12
CELL = 24
OX, OY = 120, 34

def _place_mines(exclude_r, exclude_c):
    mines = set()
    while len(mines) < MINES:
        r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
        if abs(r - exclude_r) <= 1 and abs(c - exclude_c) <= 1:
            continue
        mines.add((r, c))
    return mines

def _count_adj(mines, r, c):
    return sum(1 for dr in [-1,0,1] for dc in [-1,0,1]
               if (r+dr, c+dc) in mines and (dr, dc) != (0, 0))

def _reveal(board, revealed, mines, r, c):
    """Flood-fill reveal (reveal0-cells and neighbors)."""
    if (r, c) in revealed or r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return
    revealed.add((r, c))
    if _count_adj(mines, r, c) == 0 and (r, c) not in mines:
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                _reveal(board, revealed, mines, r+dr, c+dc)

def minesweeper_loop(tft, read_key):
    """Full-screen minesweeper."""
    cur_r, cur_c = 5, 5
    mines = _place_mines(5, 5)
    revealed = set()
    flagged = set()
    start_ticks = time.ticks_ms()
    game_over = False
    won = False

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('MINESWEEPER', 170, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        tft.text15(f'Mines:{MINES}  Flags:{len(flagged)}', 320, 4, 0xFFE0, 0x1082)
        for r in range(ROWS):
            for c in range(COLS):
                x = OX + c * CELL
                y = OY + r * CELL
                if (r, c) in revealed:
                    if (r, c) in mines:
                        tft.fill_rect(x, y, CELL, CELL, 0xF800)
                        tft.text15('*', x+8, y+4, 0xFFFF, 0xF800)
                    else:
                        tft.fill_rect(x, y, CELL, CELL, 0x4208)
                        cnt = _count_adj(mines, r, c)
                        if cnt > 0:
                            colors = [0, 0x07FF, 0x07E0, 0xF800, 0x001F,
                                      0xF800, 0x07FF, 0xFFFF, 0x8410]
                            tft.text15(str(cnt), x+8, y+4, colors[cnt], 0x4208)
                else:
                    bg = 0x8410 if (r, c) in flagged else 0xC618
                    tft.fill_rect(x, y, CELL, CELL, bg)
                    if (r, c) in flagged:
                        tft.text15('F', x+8, y+4, 0xF800, bg)
                # Cursor
                if r == cur_r and c == cur_c and not game_over:
                    tft.rect(x, y, CELL, CELL, 0xFFE0)
        if game_over:
            msg = 'YOU WIN!' if won else 'GAME OVER'
            color = 0x07E0 if won else 0xF800
            tft.text15(msg, 170, 270, color, 0x0000)
            if won:
                tft.text15(time_msg, 130, 290, 0xFFE0, 0x0000)
            tft.text15('Enter: restart  Q: quit', 120, 306, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch in ('q', 'Q', chr(24)):
            return
        if game_over:
            if ch == chr(10):
                mines = _place_mines(5, 5)
                revealed = set(); flagged = set()
                game_over = False; won = False
                _render()
            continue
        if ch in ('\x85', 'a'):
            cur_c = max(0, cur_c - 1)
        elif ch in ('\x84', 'd'):
            cur_c = min(COLS-1, cur_c + 1)
        elif ch in ('\x80', 'e'):
            cur_r = max(0, cur_r - 1)
        elif ch in ('\x81', 's'):
            cur_r = min(ROWS-1, cur_r + 1)
        elif ch == chr(10):  # Reveal
            if (cur_r, cur_c) not in flagged:
                if (cur_r, cur_c) in mines:
                    game_over = True
                    revealed = set(mines)  # Reveal all
                else:
                    _reveal(None, revealed, mines, cur_r, cur_c)
                    # Win check
                    if len(revealed) == ROWS * COLS - MINES:
                        won = True
                        game_over = True
                        from lib.highscores import set as _hs_set, get as _hs_get
                        elapsed = time.ticks_diff(time.ticks_ms(), start_ticks) // 1000
                        prev_best = _hs_get('MINESWEEPER')
                        if prev_best == 0 or elapsed < prev_best:
                            _hs_set('MINESWEEPER', elapsed)
                        best_time = _hs_get('MINESWEEPER')
                        time_msg = f'{elapsed}s (best: {best_time}s)'
        elif ch == ' ':  # Flag
            if (cur_r, cur_c) not in revealed:
                if (cur_r, cur_c) in flagged:
                    flagged.discard((cur_r, cur_c))
                else:
                    flagged.add((cur_r, cur_c))
        _render()
