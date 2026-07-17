"""Chess with proper piece sprites and a polished board."""

import time
import random

# Piece sprites: 10x10 bitmaps, 1=foreground, 0=background
# Sprites are drawn scaled2x for a20x20 piece on the28x28 square.
_PIECES = {
    'P': [ # Pawn
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0]],
    'R': [ # Rook
        [0,1,0,0,1,1,0,0,1,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0]],
    'N': [ # Knight
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,1,1,0,0,1,1,1,0,0],
        [0,1,0,0,0,0,1,1,0,0],
        [0,1,0,0,0,1,1,1,0,0],
        [0,1,1,0,1,1,1,0,0,0],
        [0,1,1,1,1,1,0,0,0,0],
        [0,1,1,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0]],
    'B': [ # Bishop
        [0,0,0,0,1,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,1,0,1,0,1,0,0,0],
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,1,1,1,1,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0]],
    'Q': [ # Queen
        [0,1,0,0,0,0,0,0,1,0],
        [0,0,1,0,0,0,0,1,0,0],
        [0,0,0,1,0,0,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0]],
    'K': [ # King
        [0,0,0,0,1,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,0,0,1,1,1,0,0,0,0],
        [0,0,1,1,1,1,1,0,0,0],
        [0,1,1,1,1,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0]],
}

SQ = 28
OX, OY = 76, 30
FILES = 'abcdefgh'

def _init_board():
    return [
        list('rnbqkbnr'), list('pppppppp'),
        list('........'), list('........'),
        list('........'), list('........'),
        list('PPPPPPPP'), list('RNBQKBNR'),
    ]

def _find_king(board, color):
    king = 'K' if color == 'w' else 'k'
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                return r, c
    return None, None

def _is_white(p): return p.isupper() if p != '.' else False
def _is_black(p): return p.islower() if p != '.' else False
def _on_board(r, c): return 0 <= r < 8 and 0 <= c < 8

def _pseudo_moves(board, r, c):
    piece = board[r][c]
    if piece == '.': return []
    moves = []
    color = 'w' if piece.isupper() else 'b'
    pt = piece.upper()
    def add(dr, dc):
        nr, nc = r + dr, c + dc
        if _on_board(nr, nc):
            t = board[nr][nc]
            if t == '.' or (color == 'w' and _is_black(t)) or (color == 'b' and _is_white(t)):
                moves.append((nr, nc))
    if pt == 'P':
        d = -1 if color == 'w' else 1
        sr = 6 if color == 'w' else 1
        if _on_board(r + d, c) and board[r + d][c] == '.':
            moves.append((r + d, c))
            if r == sr and board[r + 2 * d][c] == '.':
                moves.append((r + 2 * d, c))
        for dc in [-1, 1]:
            nr, nc = r + d, c + dc
            if _on_board(nr, nc):
                t = board[nr][nc]
                if t != '.' and ((color == 'w' and _is_black(t)) or (color == 'b' and _is_white(t))):
                    moves.append((nr, nc))
    elif pt == 'N':
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            add(dr, dc)
    elif pt == 'K':
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr or dc: add(dr, dc)
    else:
        dirs = []
        if pt in ('R', 'Q'):
            dirs += [(0,1),(0,-1),(1,0),(-1,0)]
        if pt in ('B', 'Q'):
            dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in dirs:
            for i in range(1, 8):
                nr, nc = r + dr * i, c + dc * i
                if not _on_board(nr, nc): break
                t = board[nr][nc]
                if t == '.':
                    moves.append((nr, nc))
                else:
                    if (color == 'w' and _is_black(t)) or (color == 'b' and _is_white(t)):
                        moves.append((nr, nc))
                    break
    return moves

def _all_moves(board, color):
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue
            if (color == 'w' and _is_white(p)) or (color == 'b' and _is_black(p)):
                for tr, tc in _pseudo_moves(board, r, c):
                    moves.append((r, c, tr, tc))
    return moves

def _make_move(board, move):
    r1, c1, r2, c2 = move
    nb = [row[:] for row in board]
    nb[r2][c2] = nb[r1][c1]
    nb[r1][c1] = '.'
    if nb[r2][c2] == 'P' and r2 == 0: nb[r2][c2] = 'Q'
    if nb[r2][c2] == 'p' and r2 == 7: nb[r2][c2] = 'q'
    return nb

def _in_check(board, color):
    kr, kc = _find_king(board, color)
    if kr is None: return True
    opp = 'b' if color == 'w' else 'w'
    for r, c, tr, tc in _all_moves(board, opp):
        if tr == kr and tc == kc: return True
    return False

PVAL = {'K':0,'Q':900,'R':500,'B':330,'N':320,'P':100,
        'k':0,'q':-900,'r':-500,'b':-330,'n':-320,'p':-100}

def _eval(board):
    s = 0
    for r in range(8):
        for c in range(8):
            s += PVAL.get(board[r][c], 0)
    return s

def _minimax(board, depth, alpha, beta, maximizing):
    if depth == 0: return _eval(board), None
    color = 'w' if maximizing else 'b'
    moves = _all_moves(board, color)
    if not moves: return (-99999 if maximizing else 99999), None
    legal = [m for m in moves if not _in_check(_make_move(board, m), color)]
    if not legal: return (-99999 if maximizing else 99999), None
    best = legal[0]
    if maximizing:
        mx = -999999
        for m in legal:
            ev, _ = _minimax(_make_move(board, m), depth - 1, alpha, beta, False)
            if ev > mx: mx = ev; best = m
            alpha = max(alpha, ev)
            if beta <= alpha: break
        return mx, best
    else:
        mn = 999999
        for m in legal:
            ev, _ = _minimax(_make_move(board, m), depth - 1, alpha, beta, True)
            if ev < mn: mn = ev; best = m
            beta = min(beta, ev)
            if beta <= alpha: break
        return mn, best

def _draw_piece(tft, piece, x, y):
    """Draw a chess piece sprite at (x, y) on the board."""
    pt = piece.upper()
    if pt not in _PIECES: return
    fg = 0xFFFF if piece.isupper() else 0x0000
    bg = 0x0000 if piece.isupper() else 0xFFFF
    sprite = _PIECES[pt]
    for r, row in enumerate(sprite):
        for c, v in enumerate(row):
            color = fg if v else bg
            tft.fill_rect(x + c * 2 + 4, y + r * 2 + 4, 2, 2, color)

def chess_loop(tft, read_key):
    board = _init_board()
    cur_r, cur_c = 6, 4
    selected = False
    sel_r, sel_c = 0, 0
    msg = 'You are white. Move cursor + Enter.'
    game_over = False
    player_turn = True

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('CHESS vs CPU', 170, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        # Board
        for r in range(8):
            for c in range(8):
                x = OX + c * SQ
                y = OY + r * SQ
                light = (r + c) % 2 == 0
                bg = 0xC618 if light else 0x5A86
                if selected and r == sel_r and c == sel_c:
                    bg = 0x07FF
                elif r == cur_r and c == cur_c:
                    bg = 0xFFE0
                tft.fill_rect(x, y, SQ, SQ, bg)
                p = board[r][c]
                if p != '.':
                    _draw_piece(tft, p, x, y)
        # Coordinates
        for c in range(8):
            tft.text8(FILES[c], OX + c * SQ + 10, OY + 8 * SQ + 2, 0x8410, 0x0000)
        for r in range(8):
            tft.text8(str(8 - r), OX - 10, OY + r * SQ + 8, 0x8410, 0x0000)
        # Material
        white_mat = sum(PVAL.get(board[r][c], 0) for r in range(8) for c in range(8) if board[r][c].isupper())
        black_mat = sum(-PVAL.get(board[r][c], 0) for r in range(8) for c in range(8) if board[r][c].islower())
        tft.text8(f'W:{white_mat} B:{black_mat}', 360, OY + 8 * SQ + 2, 0x8410, 0x0000)
        tft.text15(msg[:56], 4, OY + 8 * SQ + 14, 0x8410, 0x0000)
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            won = 'YOU WIN' in msg
            if won:
                _hs_set('CHESS_WINS', _hs_get('CHESS_WINS') + 1)
            wins = _hs_get('CHESS_WINS')
            losses = _hs_get('CHESS_LOSSES')
            tft.text15(f'W:{wins} L:{losses}', 160, OY + 8 * SQ + 32, 0x07FF, 0x0000)

    def _parse(s):
        s = s.strip().lower()
        if len(s) < 4: return None
        c1 = ord(s[0]) - ord('a'); r1 = 8 - int(s[1])
        c2 = ord(s[2]) - ord('a'); r2 = 8 - int(s[3])
        if all(_on_board(r, c) for r, c in [(r1,c1),(r2,c2)]):
            return (r1, c1, r2, c2)
        return None

    _render()

    while True:
        ch = read_key()
        if ch is None: continue
        if ch in ('q', 'Q', chr(24)): return
        if game_over:
            if ch == chr(10): return
            continue
        if not player_turn: continue
        if ch in ('\x85', 'a'):
            cur_c = max(0, cur_c - 1); _render()
        elif ch in ('\x84', 's'):
            cur_c = min(7, cur_c + 1); _render()
        elif ch in ('\x80', 'e'):
            cur_r = max(0, cur_r - 1); _render()
        elif ch in ('\x81', 'd'):
            cur_r = min(7, cur_r + 1); _render()
        elif ch == chr(10):
            if not selected:
                p = board[cur_r][cur_c]
                if p != '.' and _is_white(p):
                    selected = True; sel_r, sel_c = cur_r, cur_c
                    msg = f'Selected {p}. Move + Enter.'
                    _render()
            else:
                move = (sel_r, sel_c, cur_r, cur_c)
                is_legal = False
                for m in _all_moves(board, 'w'):
                    if m == move and not _in_check(_make_move(board, m), 'w'):
                        board = _make_move(board, m)
                        is_legal = True; break
                selected = False
                if is_legal:
                    if _find_king(board, 'b') == (None, None):
                        msg = 'YOU WIN! Checkmate!'; game_over = True; _render(); continue
                    msg = 'CPU thinking...'; _render()
                    player_turn = False
                    _, cm = _minimax(board, 2, -999999, 999999, False)
                    if cm:
                        board = _make_move(board, cm)
                        fr, fc, tr, tc = cm
                        msg = f'CPU: {FILES[fc]}{8-fr} -> {FILES[tc]}{8-tr}'
                    if _find_king(board, 'w') == (None, None):
                        from lib.highscores import set as _hs_set, get as _hs_get
                        _hs_set('CHESS_LOSSES', _hs_get('CHESS_LOSSES') + 1)
                        msg = 'CPU WINS!'; game_over = True
                    player_turn = True
                else:
                    msg = 'Illegal move!'
                _render()
        elif ch == chr(27):
            selected = False; msg = 'Deselected.'; _render()
