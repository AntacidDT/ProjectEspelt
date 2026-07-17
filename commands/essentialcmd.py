import time
import sys
import random
import usb_host
from lib.keyboard import hid_to_char
from lib.sprite import ParticleSystem, draw_3d_rect, gradient_rect, color565
from commands.dispatch import _buzzer

_difficulty = 1

# Difficulty presets: (sleep_ms, speed_mult, extra_params)
DIFF_PRESETS = {
    0: {'label': 'Easy', 'sleep': 1.2, 'speed': 0.7, 'spawn': 1.3},
    1: {'label': 'Medium', 'sleep': 1.0, 'speed': 1.0, 'spawn': 1.0},
    2: {'label': 'Hard', 'sleep': 0.7, 'speed': 1.4, 'spawn': 0.6},
}


def _select_difficulty(tft, title):
    global _difficulty
    tft.fill_rect(0, 25, 480, 295, 0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15(title, 120, 4, 0x07FF, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)
    tft.text('Select difficulty:', 4, 50, 0xFFFF, 0x0000)
    tft.text('  1 - Easy', 4, 80, 0x07E0, 0x0000)
    tft.text('  2 - Medium', 4, 100, 0xFFE0, 0x0000)
    tft.text('  3 - Hard', 4, 120, 0xF800, 0x0000)
    tft.text('  Enter = Medium', 4, 150, 0x8410, 0x0000)
    tft.text('  Q = Quit', 4, 170, 0x8410, 0x0000)
    while True:
        ch = usb_host.read()
        if ch is None:
            time.sleep_ms(50)
            continue
        char = hid_to_char(ch)
        if char == 'q' or char == 'Q':
            return False
        if char == '1':
            _difficulty = 0
            return True
        if char == '2' or char == '\n':
            _difficulty = 1
            return True
        if char == '3':
            _difficulty = 2
            return True


def _diff():
    return DIFF_PRESETS[_difficulty]


def _draw_game_header(tft, title):
    tft.fill_rect(0, 25, 480, 295, 0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15(title, 120, 4, 0x07FF, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)


def math_sqrt(x):
    if x <= 0:
        return 0
    g = x
    for _ in range(10):
        g = (g + x / g) / 2
    return g


def math_sin(x):
    while x > 3.14159:
        x -= 6.28318
    while x < -3.14159:
        x += 6.28318
    # Taylor series
    x2 = x * x
    x3 = x2 * x
    x5 = x3 * x2
    x7 = x5 * x2
    return x - x3/6 + x5/120 - x7/5040


def math_cos(x):
    return math_sin(x + 1.5708)


def math_atan2(y, x):
    if x > 0:
        return math_atan(y / x)
    if x < 0 and y >= 0:
        return math_atan(y / x) + 3.14159
    if x < 0 and y < 0:
        return math_atan(y / x) - 3.14159
    if x == 0 and y > 0:
        return 1.5708
    if x == 0 and y < 0:
        return -1.5708
    return 0


def math_atan(x):
    # Approximation using polynomial
    if x > 1:
        return 1.5708 - math_atan(1.0 / x)
    if x < -1:
        return -1.5708 - math_atan(1.0 / x)
    x2 = x * x
    return x * (0.9998660 - x2 * (0.3302995 - x2 * (0.1801410 - x2 * 0.0851330)))


def _show_highscore(tft, game_name, score, y=56):
    from lib.highscores import get as _hs_get, set as _hs_set
    _hs_set(game_name, score)
    best = _hs_get(game_name)
    tft.text(f'Best: {best}', 4, y, 0x07FF, 0x0000)


def cmd_games(args):
    from lib.snake_engine import snake_loop
    from lib.pong_engine import pong_loop
    from lib.tetris_engine import tetris_loop
    from lib.breakout_engine import breakout_loop
    from lib.simon_engine import simon_loop
    from lib.cooking_engine import cooking_loop
    from lib.sandbox_engine import sandbox_loop
    from lib.infinitecraft_engine import infinitecraft_loop
    game = args.strip().lower() if args.strip() else ''
    dispatch = {
        'snake': snake_loop, '2048': _2048_game, 'guess': _guess_game,
        'rps': _rps_game, 'tictactoe': _tictactoe_game, 'tetris': tetris_loop,
        'flappy': _flappy_game, 'breakout': breakout_loop, 'pong': pong_loop,
        'minesweeper': _minesweeper_game, 'hangman': _hangman_game,
        'memory': simon_loop, 'wordle': _wordle_game, 'asteroids': _asteroids_game,
        'maze': _maze_game, 'connect4': _connect4_game, 'battleship': _battleship_game,
        'trivia': _trivia_game, 'typing': _typing_game, 'mathquiz': _math_game,
        'sudoku': _sudoku_game, 'lightsout': _lightsout_game,
        'platformer': _platformer_game,
        'life': _life_game, 'racing': _racing_game,
        'invaders': _invaders_game, 'checkers': _checkers_game, 'whack': _whack_game,
        'othello': _othello_game, 'pong2p': pong_loop, 'tank': _tank_game,
        'hanoi': _hanoi_game, 'bomber': _bomber_game,
        'fighter': _fighter_game,
        'dodge': _dodge_game,
        'tag': _tag_game,
        'archery': _archery_game,
        'sumo': _sumo_game,
        'maze_cpu': _maze_game_cpu,
        'cooking': cooking_loop,
        'sandbox': sandbox_loop,
        'infinitecraft': infinitecraft_loop,
    }
    if game in dispatch:
        return ('game', dispatch[game])
    if game == '1':
        return ('print_lines', [
            '=== GAMES (1/3) ===',
            '',
            '  snake       Snake',
            '  2048        2048 puzzle',
            '  tetris      Classic Tetris',
            '  flappy      Flappy Bird',
            '  breakout    Brick breaker',
            '  pong        Pong (AI vs AI)',
            '  minesweeper Minesweeper',
            '  hangman     Word guessing',
            '  rps         Rock Paper Scissors',
            '  tictactoe   Tic Tac Toe',
            '  guess       Number guessing',
        ])
    if game == '2':
        return ('print_lines', [
            '=== GAMES (2/3) ===',
            '',
            '  memory      Simon memory',
            '  wordle      Wordle clone',
            '  asteroids   Space shooter',
            '  maze        Maze generator',
            '  connect4    Connect Four',
            '  battleship  Battleship',
            '  trivia      Trivia quiz',
            '  typing      Typing speed test',
            '  mathquiz    Math quiz',
            '  sudoku      4x4 Sudoku',
            '  lightsout   Lights Out puzzle',
            '  platformer  Side-scroll runner',
        ])
    if game == '3':
        return ('print_lines', [
            '=== GAMES (3/3) ===',
            '',
            '  life        Game of Life',
            '  racing      Top-down racing',
            '  invaders    Space Invaders',
            '  checkers    Checkers (2-player)',
            '  whack       Whack-a-mole',
        ])
    if game == '4':
        return ('print_lines', [
            '=== GAMES (4/4) ===',
            '',
            '  othello     Othello (vs CPU)',
            '  pong2p      Pong 2P',
            '  tank        Tank Battle',
            '  hanoi       Tower of Hanoi',
            '  bomber      Bomber',
            '  fighter     Martial arts fighter',
            '  dodge       Dodge enemies',
            '  tag         Chase/tag game',
            '  archery     Archery target shoot',
            '  3d          3D wireframe',
            '  maze_cpu    Maze race vs CPU',
            '  sumo        Sumo wrestling',
            '  cooking     Recipe timing game',
            '  sandbox     Pixel art + physics',
            '  infinitecraft Element combining',
        ])
    return ('print_lines', [
        '50 games. Type:',
        '  games 1  - First 11 games',
        '  games 2  - Middle 12 games',
        '  games 3  - Last 5 games',
        '  games 4  - 15 games',
        '',
        '  Q quits any game',
    ])


def _guess_game(tft, read_key):
    import random
    target = random.randint(1, 100)
    guesses = 0

    _draw_game_header(tft, 'Number Guess (1-100)')
    tft.text('Guesses: 0', 4, 32, 0xFFFF, 0x0000)
    tft.text('Q=quit  Enter=submit', 4, 290, 0x07E0, 0x0000)

    buf = ''
    while True:
        tft.fill_rect(4, 44, 200, 12, 0x0000)
        tft.text(f'> {buf}', 4, 44, 0x07E0, 0x0000)

        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == '\n':
            if not buf:
                continue
            try:
                guess = int(buf)
            except:
                tft.fill_rect(4, 56, 200, 12, 0x0000)
                tft.text('Enter a valid number', 4, 56, 0xFFE0, 0x0000)
                buf = ''
                continue
            guesses += 1
            tft.fill_rect(4, 32, 200, 12, 0x0000)
            tft.text(f'Guesses: {guesses}', 4, 32, 0xFFFF, 0x0000)
            tft.fill_rect(4, 56, 200, 12, 0x0000)
            if guess == target:
                _draw_game_header(tft, 'YOU WIN!')
                tft.text(f'Got it in {guesses} guesses!', 4, 40, 0x07E0, 0x0000)
                tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                read_key()
                return
            elif guess < target:
                tft.text(f'{guess} is TOO LOW', 4, 56, 0xFFE0, 0x0000)
            else:
                tft.text(f'{guess} is TOO HIGH', 4, 56, 0xFFE0, 0x0000)
            buf = ''
        elif ch == '\b':
            buf = buf[:-1]
        elif ch.isdigit() and len(buf) < 3:
            buf += ch


def _rps_game(tft, read_key):
    choices = ['rock', 'paper', 'scissors']
    sel = 0
    SEL_Y = 56

    def draw_choices():
        for i, name in enumerate(choices):
            color = 0xFFE0 if i == sel else 0xFFFF
            prefix = '> ' if i == sel else '  '
            tft.fill_rect(4, SEL_Y + i * 16, 120, 12, 0x0000)
            tft.text(f'{prefix}{name}', 4, SEL_Y + i * 16, color, 0x0000)

    _draw_game_header(tft, 'Rock Paper Scissors')
    tft.text('Choose:', 4, 40, 0xFFFF, 0x0000)
    draw_choices()
    tft.text('W/S=move  Enter=play  Q=quit', 4, 290, 0x07E0, 0x0000)

    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        elif ch == 'w':
            sel = (sel - 1) % 3
            draw_choices()
        elif ch == 's':
            sel = (sel + 1) % 3
            draw_choices()
        elif ch == '\n':
            comp = random.randint(0, 2)
            tft.fill_rect(4, 110, 300, 80, 0x0000)
            tft.text(f'You: {choices[sel]}', 4, 110, 0x07E0, 0x0000)
            tft.text(f'CPU: {choices[comp]}', 4, 126, 0xF800, 0x0000)
            if sel == comp:
                tft.text('DRAW!', 4, 150, 0xFFE0, 0x0000)
            elif (sel == 0 and comp == 2) or \
                 (sel == 1 and comp == 0) or \
                 (sel == 2 and comp == 1):
                tft.text('YOU WIN!', 4, 150, 0x07E0, 0x0000)
            else:
                tft.text('CPU WINS!', 4, 150, 0xF800, 0x0000)

            while True:
                ch2 = read_key()
                if ch2 == 'q' or ch2 == 'Q':
                    return
                elif ch2 == 'w':
                    sel = (sel - 1) % 3
                    draw_choices()
                    tft.fill_rect(4, 110, 300, 80, 0x0000)
                    break
                elif ch2 == 's':
                    sel = (sel + 1) % 3
                    draw_choices()
                    tft.fill_rect(4, 110, 300, 80, 0x0000)
                    break
                elif ch2 == '\n':
                    tft.fill_rect(4, 110, 300, 80, 0x0000)
                    break


def _poll_key():
    report = usb_host.read()
    if report is None:
        return None
    return hid_to_char(report)


def _2048_game(tft, read_key):
    grid = [[0]*4 for _ in range(4)]
    score = 0
    CELL = 56
    OX = 128
    OY = 34

    def spawn():
        empty = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            grid[r][c] = 2 if random.random() < 0.9 else 4

    def draw_cell(r, c):
        x = OX + c * CELL
        y = OY + r * CELL
        val = grid[r][c]
        tile_colors = {
            0: 0x2104, 2: 0xFFE0, 4: 0xFCA0, 8: 0xFD20,
            16: 0xF800, 32: 0xFC1F, 64: 0xA81F, 128: 0x07FF,
            256: 0x07E0, 512: 0x001F, 1024: 0xFFE0, 2048: 0xFFFF
        }
        text_colors = {
            0: 0x0000, 2: 0x0000, 4: 0x0000, 8: 0xFFFF,
            16: 0xFFFF, 32: 0xFFFF, 64: 0xFFFF, 128: 0x0000,
            256: 0x0000, 512: 0xFFFF, 1024: 0x0000, 2048: 0x0000
        }
        color = tile_colors.get(val, 0xFFFF)
        tc = text_colors.get(val, 0x0000)
        if val == 0:
            tft.fill_rect(x, y, CELL - 2, CELL - 2, 0x10A0)
            tft.fill_rect(x + 2, y + 2, CELL - 6, CELL - 6, 0x0904)
        else:
            tft.fill_rect(x, y, CELL - 2, CELL - 2, color)
            light = ((color >> 11) & 0x1F)
            lg = ((color >> 5) & 0x3F)
            lb = color & 0x1F
            lr = min(light + 6, 31)
            lgg = min(lg + 12, 63)
            lbg = min(lb + 6, 31)
            lc = (lr << 11) | (lgg << 5) | lbg
            tft.fill_rect(x, y, CELL - 2, 3, lc)
            tft.fill_rect(x, y, 3, CELL - 2, lc)
            dr = max(light - 6, 0)
            dg = max(lg - 12, 0)
            db = max(lb - 6, 0)
            dc = (dr << 11) | (dg << 5) | db
            tft.fill_rect(x, y + CELL - 5, CELL - 2, 3, dc)
            tft.fill_rect(x + CELL - 5, y, 3, CELL - 2, dc)
            s = str(val)
            tw = len(s) * 12
            tx = x + (CELL - 2 - tw) // 2
            ty = y + (CELL - 2 - 14) // 2
            tft.text15(s, tx, ty, tc, color)

    def draw_score():
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15(f'2048  Score: {score}', 120, 4, 0x07FF, 0x1082)

    def draw():
        _draw_game_header(tft, f'2048  Score: {score}')
        for r in range(4):
            for c in range(4):
                draw_cell(r, c)
        tft.text('WASD=move Q=quit', 4, 290, 0x07E0, 0x0000)

    def slide(row):
        nonlocal score
        nums = [x for x in row if x != 0]
        merged = []
        skip = False
        for i in range(len(nums)):
            if skip:
                skip = False
                continue
            if i + 1 < len(nums) and nums[i] == nums[i + 1]:
                merged.append(nums[i] * 2)
                score += nums[i] * 2
                skip = True
            else:
                merged.append(nums[i])
        merged += [0] * (4 - len(merged))
        return merged

    def move(dx, dy):
        old = [row[:] for row in grid]
        moved = False
        if dx == -1:
            for r in range(4):
                new = slide(grid[r])
                if new != grid[r]:
                    moved = True
                    grid[r] = new
        elif dx == 1:
            for r in range(4):
                rev = [grid[r][i] for i in range(3, -1, -1)]
                slid = slide(rev)
                new = [slid[i] for i in range(3, -1, -1)]
                if new != grid[r]:
                    moved = True
                    grid[r] = new
        elif dy == -1:
            for c in range(4):
                col = [grid[r][c] for r in range(4)]
                new = slide(col)
                if new != [grid[r][c] for r in range(4)]:
                    moved = True
                    for r in range(4):
                        grid[r][c] = new[r]
        elif dy == 1:
            for c in range(4):
                col = [grid[r][c] for r in range(3, -1, -1)]
                slid = slide(col)
                new = [slid[i] for i in range(3, -1, -1)]
                if new != [grid[r][c] for r in range(4)]:
                    moved = True
                    for r in range(4):
                        grid[r][c] = new[r]
        return moved, old

    def is_over():
        for r in range(4):
            for c in range(4):
                if grid[r][c] == 0:
                    return False
                if c + 1 < 4 and grid[r][c] == grid[r][c + 1]:
                    return False
                if r + 1 < 4 and grid[r][c] == grid[r + 1][c]:
                    return False
        return True

    spawn()
    spawn()
    draw()

    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        dx, dy = 0, 0
        if ch == 'a':
            dx = -1
        elif ch == 'd':
            dx = 1
        elif ch == 'w':
            dy = -1
        elif ch == 's':
            dy = 1
        else:
            continue

        moved, old = move(dx, dy)
        if moved:
            spawn()
            for r in range(4):
                for c in range(4):
                    if grid[r][c] != old[r][c]:
                        draw_cell(r, c)
            draw_score()
            if is_over():
                _draw_game_header(tft, 'GAME OVER')
                tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
                _show_highscore(tft, '2048_OLD', score)
                tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                read_key()
                return



def _life_game(tft, read_key):
    if not _select_difficulty(tft, "Conway's Game of Life"):
        return
    d = _diff()
    COLS = 40
    ROWS = 25
    CELL = 11
    OX = 24
    OY = 26
    grid = [[0] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if random.randint(0, 3) == 0:
                grid[r][c] = 1
    running = True
    gen = 0
    pop_hist = []
    particles = ParticleSystem(60)

    def draw_cell(r, c):
        x = OX + c * CELL
        y = OY + r * CELL
        if grid[r][c]:
            tft.fill_rect(x, y, CELL, CELL, 0x18C3)
            tft.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, 0x07E0)
            tft.pixel(x + CELL // 2, y + CELL // 2, 0xBFF7)
        else:
            tft.fill_rect(x, y, CELL, CELL, 0x18C3)
            tft.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, 0x1082)

    def draw_all():
        tft.fill_rect(0, 25, 480, 275, 0x0000)
        for r in range(ROWS):
            for c in range(COLS):
                draw_cell(r, c)
        tft.fill_rect(0, 300, 480, 20, 0x0000)
        tft.text15(f'Gen:{gen}', 4, 301, 0xFFFF, 0x0000)
        tft.text('Space=pause R=random Q=quit', 150, 301, 0x07E0, 0x0000)
        draw_pop_graph()

    def draw_pop_graph():
        gx, gy, gw, gh = 390, 250, 80, 50
        tft.fill_rect(gx, gy, gw, gh, 0x1082)
        tft.rect(gx, gy, gw, gh, 0x4208)
        tft.text15('Pop', gx + 4, gy + 2, 0x8410, 0x1082)
        if len(pop_hist) < 2:
            return
        alive = sum(sum(row) for row in grid)
        max_pop = max(max(pop_hist), 1)
        bar_area_h = gh - 14
        for i in range(min(len(pop_hist), 20)):
            val = pop_hist[-(20 - i)]
            bar_h = max(1, int((val / max_pop) * bar_area_h))
            bx = gx + 4 + i * 3
            bar_top = gy + gh - 2 - bar_h
            gradient_rect(tft, bx, bar_top, 2, bar_h, 0x07E0, 0x0320)

    def count_neighbors(r, c):
        n = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (r + dr) % ROWS, (c + dc) % COLS
                n += grid[nr][nc]
        return n

    def step():
        nonlocal gen
        new = [[0] * COLS for _ in range(ROWS)]
        changed = []
        for r in range(ROWS):
            for c in range(COLS):
                n = count_neighbors(r, c)
                if grid[r][c]:
                    new[r][c] = 1 if n in (2, 3) else 0
                else:
                    new[r][c] = 1 if n == 3 else 0
                if new[r][c] != grid[r][c]:
                    changed.append((r, c))
        for r, c in changed:
            x = OX + c * CELL + CELL // 2
            y = OY + r * CELL + CELL // 2
            if new[r][c] == 1:
                particles.emit(x, y, count=3, speed=0.8,
                               colors=[0x07E0, 0x0FE0, 0xBFF7], life=10)
            else:
                particles.emit(x, y, count=2, speed=0.5,
                               colors=[0x8410, 0x630C, 0x4208], life=8)
        for r, c in changed:
            grid[r][c] = new[r][c]
        gen += 1
        alive = sum(sum(row) for row in grid)
        pop_hist.append(alive)
        if len(pop_hist) > 20:
            pop_hist.pop(0)
        for r, c in changed:
            draw_cell(r, c)

    def randomize():
        for r in range(ROWS):
            for c in range(COLS):
                grid[r][c] = 1 if random.randint(0, 3) == 0 else 0

    _draw_game_header(tft, "Conway's Game of Life")
    draw_all()

    while True:
        ch = read_key(int(d['sleep'] * 100) if running else 0)
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if ch == ' ':
            running = not running
            tft.fill_rect(0, 300, 480, 20, 0x0000)
            tft.text('Space=pause R=random Q=quit', 150, 301, 0x07E0, 0x0000)
        if ch in ('r', 'R'):
            randomize()
            gen = 0
            pop_hist.clear()
            draw_all()
        if running:
            step()
            tft.fill_rect(0, 300, 100, 20, 0x0000)
            tft.text15(f'Gen:{gen}', 4, 301, 0xFFFF, 0x0000)
            draw_pop_graph()
        particles.update()
        particles.draw(tft)


def _racing_game(tft, read_key):
    if not _select_difficulty(tft, 'Racing'):
        return
    d = _diff()
    W = 480
    H = 320
    car_x = 200
    car_y = 230
    car_w = 30
    car_h = 50
    base_speed = [5, 8, 12][_difficulty]
    speed = base_speed
    max_speed = [18, 22, 28][_difficulty]
    boost = 100
    boosting = False
    score = 0
    high_score = 0
    obstacles = []
    next_obs = 0
    road_l = 80
    road_r = 400
    lane_w = (road_r - road_l) // 4
    crashed = False
    prev_car_x = car_x
    prev_car_y = car_y
    strip_y = 0
    particles = ParticleSystem(40)
    tire_trails = []
    frame = 0
    difficulty_timer = 0

    # obstacle types: [w, h, color, name]
    OBS_TYPES = [
        [26, 36, 0xFFE0, 'car'],
        [26, 36, 0xFCA0, 'car'],
        [26, 36, 0xFC1F, 'car'],
        [26, 36, 0xFFFF, 'car'],
        [30, 55, 0x8410, 'truck'],
        [30, 55, 0x6A84, 'truck'],
        [28, 45, 0x001F, 'bus'],
    ]

    def draw_sky():
        for row in range(26):
            ratio = row / 25
            r = int(0x86 * (1 - ratio) + 0x07 * ratio)
            g = int(0x7D * (1 - ratio) + 0xFF * ratio) & 0x3F
            b = int(0xFF * (1 - ratio) + 0xFF * ratio) & 0x1F
            c = (r << 11) | (g << 5) | b
            tft.fill_rect(0, 25 + row, 480, 1, c)

    def draw_road():
        tft.fill_rect(road_l, 25, road_r - road_l, 295, 0x4208)
        tft.fill_rect(0, 25, road_l, 295, 0x03E0)
        tft.fill_rect(road_r, 25, 480 - road_r, 295, 0x03E0)
        sy = int(strip_y) % 24
        for i in range(5):
            x = road_l + i * lane_w
            for y in range(25 - sy, 320, 24):
                tft.fill_rect(x - 1, y, 2, 12, 0x8410)

    def draw_car():
        tft.fill_rect(car_x, car_y, car_w, car_h, 0x0000)
        tft.fill_rect(car_x + 3, car_y + 4, car_w - 6, car_h - 6, 0xF800)
        tft.fill_rect(car_x + 5, car_y + 8, car_w - 10, 10, 0x07FF)
        tft.fill_rect(car_x + 2, car_y + car_h - 12, 7, 9, 0x2104)
        tft.fill_rect(car_x + car_w - 9, car_y + car_h - 12, 7, 9, 0x2104)
        tft.fill_rect(car_x + car_w // 2 - 2, car_y - 2, 4, 6, 0xFFE0)
        if boosting:
            tft.fill_rect(car_x + car_w // 2 - 4, car_y + car_h, 8, 4, 0xFCA0)
            tft.fill_rect(car_x + car_w // 2 - 2, car_y + car_h + 4, 4, 3, 0xFFE0)

    def clear_car():
        tft.fill_rect(prev_car_x - 1, prev_car_y - 2, car_w + 2, car_h + 8, 0x4208)

    def draw_obstacle(o):
        ot = o[3]
        ow, oh = ot[0], ot[1]
        c = ot[2]
        y = max(25, o[1])
        h = oh - (y - o[1])
        if h <= 0:
            return
        tft.fill_rect(o[0], y, ow, h, 0x0000)
        tft.fill_rect(o[0] + 2, y + 2, ow - 4, h - 4, c)
        if ot[3] == 'truck':
            if y + 4 < 25 + h:
                tft.fill_rect(o[0] + 4, max(25, y + 4), ow - 8, min(10, h - 4), 0x4208)
        elif ot[3] == 'bus':
            if y + 6 < 25 + h:
                tft.fill_rect(o[0] + 4, max(25, y + 6), ow - 8, min(8, h - 6), 0x07FF)
            if y + 20 < 25 + h:
                tft.fill_rect(o[0] + 4, max(25, y + 20), ow - 8, min(8, h - 20), 0x07FF)
        else:
            if y + 5 < 25 + h:
                tft.fill_rect(o[0] + 5, max(25, y + 5), ow - 10, min(8, h - 5), 0x07FF if c != 0x07FF else 0xFFFF)

    def clear_obstacle(o):
        ot = o[3]
        y = max(25, o[1])
        h = ot[1] - (y - o[1])
        if h > 0:
            tft.fill_rect(o[0], y, ot[0], h, 0x4208)

    def check_collision():
        for o in obstacles:
            ot = o[3]
            ow, oh = ot[0], ot[1]
            if (car_x < o[0] + ow - 4 and car_x + car_w > o[0] + 4 and
                car_y < o[1] + oh - 4 and car_y + car_h > o[1] + 4):
                return True
        return False

    _draw_game_header(tft, 'Racing')
    draw_sky()
    draw_road()
    draw_car()
    tft.text('A/D=steer W=boost Q=quit', 4, 308, 0x07E0, 0x0000)

    while True:
        frame += 1
        prev_car_x = car_x
        prev_car_y = car_y
        ch = read_key(int([20, 15, 10][_difficulty]))
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if ch in ('a', 'A'):
            car_x = max(road_l + 5, car_x - speed * 2)
        if ch in ('d', 'D'):
            car_x = min(road_r - car_w - 5, car_x + speed * 2)
        if ch in ('w', 'W') and boost > 0:
            boosting = True
            boost = max(0, boost - 3)
        else:
            boosting = False
            boost = min(100, boost + 0.5)

        speed = base_speed + (4 if boosting else 0)
        speed = min(speed, max_speed)

        strip_y += speed + 2
        for o in obstacles:
            clear_obstacle(o)
            o[1] += speed + 2
        obstacles[:] = [o for o in obstacles if o[1] < 360]

        if next_obs <= 0:
            lane = random.randint(0, 3)
            ox = road_l + lane * lane_w + 5
            ot = OBS_TYPES[random.randint(0, len(OBS_TYPES) - 1)]
            obstacles.append([ox, -ot[1] - 10, 0, ot])
            spawn_range = [int([30, 18, 10][_difficulty]), int([55, 35, 20][_difficulty])]
            next_obs = random.randint(spawn_range[0], spawn_range[1])
        next_obs -= 1

        if frame % 8 == 0:
            tire_trails.append([car_x + 4, car_y + car_h - 2])
            tire_trails.append([car_x + car_w - 6, car_y + car_h - 2])
            if len(tire_trails) > 12:
                tire_trails.pop(0)
                tire_trails.pop(0)
        for i in range(0, len(tire_trails), 2):
            tx, ty = tire_trails[i]
            tft.fill_rect(int(tx), int(ty), 3, 2, 0x2945)

        for o in obstacles:
            draw_obstacle(o)

        clear_car()
        draw_car()

        if check_collision():
            crashed = True
            break

        score += 1
        if score > high_score:
            high_score = score

        tft.fill_rect(0, 300, 480, 20, 0x0000)
        tft.text(f'Score: {score}  Best: {high_score}', 4, 300, 0xFFFF, 0x0000)
        boost_bar_w = int(boost * 1.2)
        tft.fill_rect(350, 302, 120, 8, 0x2104)
        tft.fill_rect(350, 302, boost_bar_w, 8, 0x07E0 if boost > 30 else 0xF800)
        tft.text('A/D W=boost Q', 4, 312, 0x8410, 0x0000)

        if score % 100 == 0:
            try:
                _buzzer.score_beep()
            except Exception:
                pass
            base_speed = min(max_speed, base_speed + 1)

    particles.emit(car_x + car_w // 2, car_y + car_h // 2,
                  count=20, speed=5, colors=[0xF800, 0xFFE0, 0xFC1F, 0xFFFF, 0x07FF], life=30)
    for _ in range(25):
        particles.update(tft, 0.15)
        time.sleep_ms(25)
    try:
        _buzzer.game_over_sound()
    except Exception:
        pass
    _draw_game_header(tft, 'CRASH!')
    tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
    tft.text(f'Best: {high_score}', 4, 56, 0x07FF, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _invaders_game(tft, read_key):
    if not _select_difficulty(tft, 'Space Invaders'):
        return
    d = _diff()
    ship_x = 220
    ship_y = 270
    ship_w = 30
    ship_h = 20
    bullets = []
    aliens = []
    alien_dir = 1
    alien_speed = 0
    score = 0
    prev_ship_x = ship_x
    _spd = d['speed']
    move_interval = 1 if _spd > 1.2 else (2 if _spd > 0.85 else 3)
    key_timeout = int(d['sleep'] * 35)
    particles = ParticleSystem()

    shield = bytearray([1] * (40 * 16))
    SHIELD_X = 210
    SHIELD_Y = 250

    def draw_shield():
        for sy in range(16):
            for sx in range(40):
                if shield[sy * 40 + sx]:
                    tft.pixel(SHIELD_X + sx, SHIELD_Y + sy, 0x07FF)

    def erode_shield(bx, by):
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                sx = int(bx - SHIELD_X + dx)
                sy = int(by - SHIELD_Y + dy)
                if 0 <= sx < 40 and 0 <= sy < 16:
                    idx = sy * 40 + sx
                    if shield[idx] and random.randint(0, 1):
                        shield[idx] = 0
                        tft.pixel(SHIELD_X + sx, SHIELD_Y + sy, 0x0000)

    def draw_ship():
        for dy in range(-8, 12):
            w = max(1, 14 - abs(dy) * 1)
            cx = ship_x + ship_w // 2
            tft.fill_rect(cx - w, ship_y + dy, w * 2, 1, 0x07FF)
        tft.fill_rect(ship_x + 10, ship_y - 8, 10, 4, 0xFFE0)

    def clear_ship():
        tft.fill_rect(prev_ship_x - 1, ship_y - 9, ship_w + 2, ship_h + 10, 0x0000)

    alien_colors = [0x07E0, 0xF800, 0xFFE0]
    alien_shapes = [
        lambda x, y, c: (tft.fill_rect(x, y, 24, 16, c), tft.fill_rect(x + 4, y - 4, 16, 4, c), tft.pixel(x + 6, y + 4, 0), tft.pixel(x + 16, y + 4, 0)),
        lambda x, y, c: (tft.fill_rect(x + 4, y, 16, 16, c), tft.fill_rect(x, y + 4, 24, 8, c), tft.pixel(x + 8, y + 4, 0), tft.pixel(x + 14, y + 4, 0)),
        lambda x, y, c: (tft.fill_rect(x + 2, y, 20, 12, c), tft.fill_rect(x + 6, y + 12, 12, 4, c), tft.fill_rect(x + 8, y - 4, 8, 4, c)),
    ]

    def draw_alien(a):
        ci = int(a[0] * 3 / 460) % 3
        alien_shapes[ci](a[0], a[1], alien_colors[ci])

    def clear_alien(a):
        tft.fill_rect(a[0] - 1, a[1] - 5, 26, 22, 0x0000)

    def draw_bullet(b):
        tft.fill_rect(b[0], b[1], 3, 10, 0xFFE0)
        tft.pixel(b[0] + 1, b[1] + 10, 0xFFFF)

    def clear_bullet(b):
        tft.fill_rect(b[0], b[1], 3, 12, 0x0000)

    def spawn_particles(x, y, color):
        for _ in range(8):
            particles.add(x + 12, y + 8, random.randint(-20, 20) / 10, random.randint(-20, 20) / 10, color, 12)

    for row in range(3):
        for col in range(7):
            aliens.append([80 + col * 44, 40 + row * 36, 1])

    _draw_game_header(tft, 'Space Invaders')
    draw_ship()
    for a in aliens:
        draw_alien(a)
    draw_shield()

    while True:
        ch = read_key(key_timeout)
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        prev_ship_x = ship_x
        if ch in ('a', 'A'):
            ship_x = max(10, ship_x - 8)
        if ch in ('d', 'D'):
            ship_x = min(440, ship_x + 8)
        if ch in (' ', '\n'):
            if len(bullets) < 4:
                bullets.append([ship_x + 13, ship_y - 10])
                try:
                    _buzzer.beep(15)
                except Exception:
                    pass

        clear_ship()
        draw_ship()

        for b in bullets:
            clear_bullet(b)
            b[1] -= 12
        bullets[:] = [b for b in bullets if b[1] > 20]
        for b in bullets:
            if SHIELD_X <= b[0] <= SHIELD_X + 40 and SHIELD_Y <= b[1] <= SHIELD_Y + 16:
                erode_shield(b[0], b[1])
                b[1] = -100
                continue
            draw_bullet(b)
        bullets[:] = [b for b in bullets if b[1] > -50]

        alien_speed += 1
        if alien_speed >= move_interval:
            alien_speed = 0
            for a in aliens:
                clear_alien(a)
            move = alien_dir * 8
            edge = False
            for a in aliens:
                a[0] += move
                if a[0] < 10 or a[0] > 440:
                    edge = True
            if edge:
                alien_dir = -alien_dir
                for a in aliens:
                    a[1] += 12
            for a in aliens:
                draw_alien(a)

        hit = []
        for b in bullets:
            for a in aliens:
                if a[0] < b[0] + 3 and a[0] + 24 > b[0] and a[1] < b[1] + 8 and a[1] + 16 > b[1]:
                    ci = int(a[0] * 3 / 460) % 3
                    hit.append((aliens.index(a), bullets.index(b), ci))
        for ai, bi, ci in sorted(hit, reverse=True):
            clear_alien(aliens[ai])
            clear_bullet(bullets[bi])
            spawn_particles(aliens[ai][0], aliens[ai][1], alien_colors[ci])
            aliens.pop(ai)
            bullets.pop(bi)
            score += 10
            try:
                _buzzer.score_beep()
            except Exception:
                pass

        particles.update(tft, 0.05)

        lost = any(a[1] + 16 >= ship_y for a in aliens)
        if lost:
            try:
                _buzzer.game_over_sound()
            except Exception:
                pass
            break
        if not aliens:
            break

        tft.fill_rect(0, 300, 480, 20, 0x0000)
        tft.text(f'Score: {score}  Aliens: {len(aliens)}', 4, 300, 0xFFFF, 0x0000)
        _show_highscore(tft, 'INVADERS', score)

    if not aliens:
        _draw_game_header(tft, 'YOU WIN!')
    else:
        _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _checkers_game(tft, read_key):
    CELL = 36
    OX = 84
    OY = 34
    board = [[0] * 8 for _ in range(8)]
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 1:
                if r < 3:
                    board[r][c] = 2
                elif r > 4:
                    board[r][c] = 1
    sel_r, sel_c = -1, -1
    turn = 1
    score1 = 12
    score2 = 12

    def draw_board():
        draw_3d_rect(tft, OX - 3, OY - 3, 8 * CELL + 4, 8 * CELL + 4, 0x6A8C)
        for r in range(8):
            for c in range(8):
                x = OX + c * CELL
                y = OY + r * CELL
                bg = 0xE7C4 if (r + c) % 2 == 0 else 0x8C52
                tft.fill_rect(x, y, CELL - 1, CELL - 1, bg)
                if board[r][c] == 1:
                    draw_piece(x, y, 0xF800, False)
                elif board[r][c] == 2:
                    draw_piece(x, y, 0x001F, False)

    def draw_piece(x, y, color, king):
        cx = x + CELL // 2
        cy = y + CELL // 2 + 1
        r = 8
        hi = color | 0x1084
        lo = (max((color >> 11) - 4, 0) << 11) | (max(((color >> 5) & 0x3F) - 8, 0) << 5) | max((color & 0x1F) - 4, 0)
        tft.fill_rect(cx - r, cy - r, 2 * r, 2 * r, lo)
        tft.fill_rect(cx - r, cy - r, 2 * r, r, hi)
        tft.fill_rect(cx - r, cy, 2 * r, 1, lo)
        tft.fill_rect(cx - r + 1, cy - r + 1, 2 * r - 2, 1, 0xFFFF)
        if king:
            cr2 = cy - r - 2
            tft.fill_rect(cx - 5, cr2, 3, 4, 0xFFE0)
            tft.fill_rect(cx - 1, cr2 - 1, 3, 5, 0xFFE0)
            tft.fill_rect(cx + 3, cr2, 3, 4, 0xFFE0)

    def draw_cell(r, c):
        x = OX + c * CELL
        y = OY + r * CELL
        bg = 0xE7C4 if (r + c) % 2 == 0 else 0x8C52
        tft.fill_rect(x, y, CELL - 1, CELL - 1, bg)
        if board[r][c] == 1:
            draw_piece(x, y, 0xF800, False)
        elif board[r][c] == 2:
            draw_piece(x, y, 0x001F, False)

    def draw_sel():
        if sel_r >= 0:
            x = OX + sel_c * CELL
            y = OY + sel_r * CELL
            for i in range(2):
                tft.rect(x - i, y - i, CELL - 1 + 2 * i, CELL - 1 + 2 * i, 0xFFE0)

    def draw_cursor():
        x = OX + cc * CELL
        y = OY + cr * CELL
        tft.rect(x, y, CELL - 1, CELL - 1, 0xF800)
        tft.rect(x - 1, y - 1, CELL + 1, CELL + 1, 0xF800)

    _draw_game_header(tft, 'Checkers')
    draw_board()
    tft.text('WASD=move Enter=select Q=quit', 4, 300, 0x07E0, 0x0000)
    prev_cr, prev_cc = cr, cc
    draw_cursor()

    cr, cc = 0, 0
    prev_cr, prev_cc = cr, cc
    draw_cursor()

    while True:
        tft.fill_rect(300, 300, 180, 16, 0x0000)
        tft.text('Red:12 Blue:12' if score1 == 12 and score2 == 12 else f'Red:{score1} Blue:{score2}', 300, 300, 0xFFFF, 0x0000)
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        prev_cr, prev_cc = cr, cc
        if ch in ('w', 'W', '\x80'):
            cr = max(0, cr - 1)
        elif ch in ('s', 'S', '\x81'):
            cr = min(7, cr + 1)
        elif ch in ('a', 'A'):
            cc = max(0, cc - 1)
        elif ch in ('d', 'D'):
            cc = min(7, cc + 1)
        elif ch in ('\n', ' '):
            if sel_r < 0:
                if board[cr][cc] == turn:
                    sel_r, sel_c = cr, cc
            else:
                dr = cr - sel_r
                dc = cc - sel_c
                valid = False
                if board[cr][cc] == 0:
                    if abs(dr) == 1 and abs(dc) == 1:
                        if (turn == 1 and dr == -1) or (turn == 2 and dr == 1):
                            valid = True
                    elif abs(dr) == 2 and abs(dc) == 2:
                        mr, mc = (sel_r + cr) // 2, (sel_c + cc) // 2
                        if board[mr][mc] != 0 and board[mr][mc] != turn:
                            valid = True
                            board[mr][mc] = 0
                            if turn == 1:
                                score2 -= 1
                            else:
                                score1 -= 1
                if valid:
                    board[cr][cc] = board[sel_r][sel_c]
                    board[sel_r][sel_c] = 0
                    if (turn == 1 and cr == 0) or (turn == 2 and cr == 7):
                        board[cr][cc] = turn
                    draw_cell(sel_r, sel_c)
                    draw_cell(cr, cc)
                    if valid and abs(dr) == 2:
                        draw_cell((sel_r + cr) // 2, (sel_c + cc) // 2)
                    turn = 2 if turn == 1 else 1
                sel_r, sel_c = -1, -1

        draw_cell(cr, cc)
        if cr != prev_cr or cc != prev_cc:
            draw_cell(prev_cr, prev_cc)
            draw_cursor()
        draw_sel()

        if score1 == 0 or score2 == 0:
            winner = 'RED' if score1 > 0 else 'BLUE'
            _draw_game_header(tft, f'{winner} WINS!')
            tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
            read_key()
            return


def _whack_game(tft, read_key):
    if not _select_difficulty(tft, 'Whack-a-Mole'):
        return
    d = _diff()
    COLS = 4
    ROWS = 3
    CELL = 80
    OX = 84
    OY = 40
    score = 0
    mole_timer_min = {0: 8, 1: 5, 2: 3}[_difficulty]
    mole_timer_max = {0: 20, 1: 12, 2: 7}[_difficulty]
    time_left = {0: 400, 1: 300, 2: 200}[_difficulty]
    mole_r = -1
    mole_c = -1
    mole_timer = 0
    hit_flash = 0
    particles = ParticleSystem()
    floating_texts = []

    def draw_hole(r, c):
        x = OX + c * CELL
        y = OY + r * CELL
        tft.fill_rect(x + 2, y + 18, CELL - 8, CELL - 24, 0x2010)
        tft.fill_rect(x + 4, y + 14, CELL - 12, 6, 0x4208)
        tft.fill_rect(x + 2, y + CELL - 12, CELL - 8, 8, 0x1082)

    def draw_mole(r, c):
        x = OX + c * CELL + CELL // 2
        y = OY + r * CELL + CELL // 2 - 4
        tft.fill_rect(x - 10, y - 6, 20, 16, 0x8340)
        tft.fill_rect(x - 8, y - 4, 16, 12, 0xA520)
        tft.pixel(x - 4, y - 2, 0x0000)
        tft.pixel(x + 4, y - 2, 0x0000)
        tft.pixel(x, y + 2, 0xF81F)

    def draw_cursor(r, c):
        x = OX + c * CELL + CELL // 2
        y = OY + r * CELL + 6
        tft.fill_rect(x - 1, y + 4, 3, 12, 0x8410)
        tft.fill_rect(x - 4, y, 9, 6, 0x528A)

    def draw_all():
        for r in range(ROWS):
            for c in range(COLS):
                draw_hole(r, c)
        draw_cursor(cr, cc)
        tft.fill_rect(0, 300, 480, 20, 0x0000)
        tft.text(f'Score: {score}  Time: {time_left // 10}', 4, 300, 0xFFFF, 0x0000)
        tft.text('WASD=move Space=whack Q=quit', 200, 300, 0x07E0, 0x0000)

    def draw_floating_texts():
        for ft in floating_texts[:]:
            tft.text(str(ft[3]), int(ft[0]), int(ft[1]), 0x0000, 0x0000)
            ft[1] -= 1.5
            ft[2] -= 1
            if ft[2] <= 0:
                floating_texts.remove(ft)
            else:
                alpha = ft[2] / ft[4]
                color = color565(int(255 * alpha), int(255 * alpha), 0)
                tft.text(str(ft[3]), int(ft[0]), int(ft[1]), color, 0x0000)

    cr, cc = 1, 1

    _draw_game_header(tft, 'Whack-a-Mole')
    draw_all()

    while time_left > 0:
        ch = read_key(int(d['sleep'] * 50))
        time_left -= 1
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if ch in ('w', 'W', '\x80'):
            cr = max(0, cr - 1)
        elif ch in ('s', 'S', '\x81'):
            cr = min(ROWS - 1, cr + 1)
        elif ch in ('a', 'A'):
            cc = max(0, cc - 1)
        elif ch in ('d', 'D'):
            cc = min(COLS - 1, cc + 1)

        mole_timer -= 1
        if mole_timer <= 0:
            if mole_r >= 0:
                draw_hole(mole_r, mole_c)
            mole_r = random.randint(0, ROWS - 1)
            mole_c = random.randint(0, COLS - 1)
            mole_timer = random.randint(mole_timer_min, mole_timer_max)
            draw_mole(mole_r, mole_c)

        if ch in (' ', '\n') and mole_r >= 0:
            if cr == mole_r and cc == mole_c:
                score += 10
                draw_hole(mole_r, mole_c)
                mx = OX + mole_c * CELL + CELL // 2
                my = OY + mole_r * CELL + CELL // 2
                for _ in range(8):
                    angle = random.randint(0, 628) / 100
                    spd = random.randint(8, 20) / 10
                    px = mx + int(math.cos(angle) * spd)
                    py = my + int(math.sin(angle) * spd)
                    particles.add(mx, my, math.cos(angle) * spd * 0.3, math.sin(angle) * spd * 0.3 - 0.5,
                                  0xFFE0 if random.randint(0, 1) else 0xFFFF, 10)
                floating_texts.append([float(mx - 6), float(my - 10), 15, '+10', 15])
                mole_r = -1
                hit_flash = 4
                try:
                    _buzzer.score_beep()
                except Exception:
                    pass
            else:
                try:
                    _buzzer.beep(50)
                except Exception:
                    pass

        if hit_flash > 0:
            x = OX + cc * CELL
            y = OY + cr * CELL
            tft.fill_rect(x, y, CELL - 4, CELL - 4, 0xFFE0)
            hit_flash -= 1
        else:
            draw_hole(cr, cc)
            draw_cursor(cr, cc)

        particles.update(tft, 0.05)
        draw_floating_texts()

        tft.fill_rect(0, 300, 480, 20, 0x0000)
        tft.text(f'Score: {score}  Time: {time_left // 10}', 4, 300, 0xFFFF, 0x0000)

    _draw_game_header(tft, 'TIME UP!')
    tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _tictactoe_game(tft, read_key):
    board = [' '] * 9
    turn = 'X'
    sel = 4
    CELL = 80
    OX = 120
    OY = 40
    cpu_mode = True
    cpu_char = 'O'
    human_char = 'X'

    import math as _tictactoe_math

    def draw_x(x, y, color=0x07E0):
        cx = x + CELL // 2
        cy = y + CELL // 2
        for dx in range(-3, 4):
            for step in range(-25, 26):
                tft.pixel(cx + step, cy + step + dx, color)
                tft.pixel(cx - step, cy + step + dx, color)

    def draw_o(x, y, color=0xF800):
        cx = x + CELL // 2
        cy = y + CELL // 2
        for angle_step in range(60):
            a = angle_step * 6.28318 / 60
            px = int(cx + 22 * _tictactoe_math.cos(a))
            py = int(cy + 22 * _tictactoe_math.sin(a))
            for dw in range(-1, 2):
                for dh in range(-1, 2):
                    tft.pixel(px + dw, py + dh, color)

    def draw_cell(i, flash_win=False):
        r, c = divmod(i, 3)
        x = OX + c * CELL
        y = OY + r * CELL
        if flash_win:
            base = 0xFFE0
        elif i == sel:
            base = 0xC618
        else:
            base = 0x4208
        draw_3d_rect(tft, x, y, CELL - 2, CELL - 2, base)
        if board[i] != ' ':
            if board[i] == 'X':
                draw_x(x, y, 0x07E0 if not flash_win else 0xFFFF)
            else:
                draw_o(x, y, 0xF800 if not flash_win else 0xFFFF)
        else:
            tft.text(str(i + 1), x + CELL // 2 - 3, y + CELL // 2 - 4, 0x4208, base)

    def draw_status():
        winner = check_winner()
        if cpu_mode:
            status = 'Your turn (X)' if turn == 'X' else 'CPU thinking...'
        else:
            status = f'{turn}\'s turn'
        if winner == 'Draw':
            status = 'DRAW!'
        elif winner:
            if cpu_mode:
                status = f'{winner} {"YOU WIN!" if winner == human_char else "CPU WINS!"}'
            else:
                status = f'{winner} WINS!'
        tft.fill_rect(4, 280, 300, 12, 0x0000)
        tft.text(status, 4, 280, 0xFFE0, 0x0000)

    def draw_sel(old_sel):
        draw_cell(old_sel)
        draw_cell(sel)

    def draw():
        _draw_game_header(tft, 'Tic Tac Toe')
        for i in range(9):
            draw_cell(i)
        draw_status()
        tft.text('1-9=place Q=quit', 4, 290, 0x07E0, 0x0000)

    def check_winner():
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in wins:
            if board[a] == board[b] == board[c] and board[a] != ' ':
                return board[a]
        if all(b != ' ' for b in board):
            return 'Draw'
        return None

    def flash_winner(winner_char):
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in wins:
            if board[a] == board[b] == board[c] and board[a] == winner_char:
                for flash in range(3):
                    for idx in (a, b, c):
                        draw_cell(idx, flash_win=True)
                    time.sleep_ms(200)
                    for idx in (a, b, c):
                        draw_cell(idx, flash_win=False)
                    time.sleep_ms(150)
                for idx in (a, b, c):
                    draw_cell(idx, flash_win=True)
                return

    def cpu_move():
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        # 1. Win if possible
        for a, b, c in wins:
            cells = [board[a], board[b], board[c]]
            if cells.count(cpu_char) == 2 and cells.count(' ') == 1:
                return [a, b, c][cells.index(' ')]
        # 2. Block opponent
        for a, b, c in wins:
            cells = [board[a], board[b], board[c]]
            if cells.count(human_char) == 2 and cells.count(' ') == 1:
                return [a, b, c][cells.index(' ')]
        # 3. Take center
        if board[4] == ' ':
            return 4
        # 4. Take corner
        corners = [0, 2, 6, 8]
        empty_corners = [c for c in corners if board[c] == ' ']
        if empty_corners:
            return empty_corners[0]
        # 5. Take any
        empty = [i for i in range(9) if board[i] == ' ']
        if empty:
            return empty[0]
        return None

    # Mode selection
    _draw_game_header(tft, 'Tic Tac Toe')
    tft.text('Select mode:', 4, 40, 0xFFFF, 0x0000)
    tft.text('  1 - vs CPU', 4, 70, 0x07E0, 0x0000)
    tft.text('  2 - vs Player', 4, 90, 0xFFE0, 0x0000)
    tft.text('  Enter = vs CPU', 4, 120, 0x8410, 0x0000)
    while True:
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if ch == '2':
            cpu_mode = False
            break
        if ch == '1' or ch == '\n':
            cpu_mode = True
            break

    draw()
    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return

        if ch in '123456789' and turn == human_char:
            idx = int(ch) - 1
            if board[idx] == ' ':
                board[idx] = turn
                winner = check_winner()
                if winner:
                    draw_cell(idx)
                    draw_status()
                    if winner != 'Draw':
                        flash_winner(winner)
                    _draw_game_header(tft, 'GAME OVER')
                    if winner == 'Draw':
                        tft.text('DRAW!', 4, 40, 0xFFE0, 0x0000)
                    elif cpu_mode:
                        tft.text(f'{winner} {"YOU WIN!" if winner == human_char else "CPU WINS!"}', 4, 40, 0x07E0, 0x0000)
                    else:
                        tft.text(f'{winner} WINS!', 4, 40, 0x07E0, 0x0000)
                    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                    read_key()
                    return
                turn = 'O' if turn == 'X' else 'X'
                draw_cell(idx)
                draw_status()
                # CPU move
                if cpu_mode and turn == cpu_char:
                    time.sleep_ms(300)
                    move = cpu_move()
                    if move is not None:
                        board[move] = cpu_char
                        winner = check_winner()
                        draw_cell(move)
                        draw_status()
                        if winner:
                            if winner != 'Draw':
                                flash_winner(winner)
                            _draw_game_header(tft, 'GAME OVER')
                            if winner == 'Draw':
                                tft.text('DRAW!', 4, 40, 0xFFE0, 0x0000)
                            else:
                                tft.text(f'{winner} {"YOU WIN!" if winner == human_char else "CPU WINS!"}', 4, 40, 0x07E0, 0x0000)
                            tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                            read_key()
                            return
                        turn = human_char


def _flappy_game(tft, read_key):
    if not _select_difficulty(tft, 'Flappy Bird'):
        return
    d = _diff()
    bird_y = 160.0
    bird_v = 0.0
    bird_x = 80
    bird_r = 8
    GRAVITY = [0.8, 1.0, 1.3][_difficulty]
    FLAP = -5.5
    pipe_w = 30
    pipe_gap = [90, 80, 65][_difficulty]
    pipe_speed = [2, 3, 4][_difficulty]
    spawn_ms = [2500, 1800, 1200][_difficulty]
    pipes = []
    score = 0
    game_over = False
    last_time = time.ticks_ms()
    pipe_timer = 0
    particles = ParticleSystem(20)
    shake_frames = 0
    shake_ox = 0
    shake_oy = 0

    def draw_sky():
        for row in range(280):
            ratio = row / 280
            r = int(0x86 * (1 - ratio) + 0x07 * ratio)
            g = int(0x7D * (1 - ratio) + 0xFF * ratio) & 0x3F
            b = int(0xFF * (1 - ratio) + 0xFF * ratio) & 0x1F
            c = (r << 11) | (g << 5) | b
            tft.fill_rect(0, 25 + row, 480, 1, c)
        tft.fill_rect(0, 305, 480, 15, 0x6A84)

    def draw_pipe(px, gap_y):
        cap_h = 6
        cap_color = 0x03E0
        body_color = 0x07E0
        tft.fill_rect(px, 25, pipe_w, gap_y - 25, body_color)
        tft.fill_rect(px - 2, gap_y - cap_h, pipe_w + 4, cap_h, cap_color)
        tft.fill_rect(px, gap_y + pipe_gap, pipe_w, 305 - gap_y - pipe_gap, body_color)
        tft.fill_rect(px - 2, gap_y + pipe_gap, pipe_w + 4, cap_h, cap_color)

    def draw_bird(bx, by):
        tft.fill_rect(bx - bird_r, int(by) - bird_r, bird_r * 2, bird_r * 2, 0x0000)
        tft.fill_rect(bx - bird_r + 1, int(by) - bird_r + 1, bird_r * 2 - 2, bird_r * 2 - 2, 0xFFE0)
        tft.fill_rect(bx + 2, int(by) - 3, 3, 3, 0x0000)
        tft.fill_rect(bx + bird_r - 1, int(by) - 1, 4, 3, 0xFCA0)

    def clear_bird(bx, by):
        tft.fill_rect(bx - bird_r - 1, int(by) - bird_r - 1, bird_r * 2 + 2, bird_r * 2 + 2, 0x0000)

    def collide():
        if bird_y - bird_r < 25 or bird_y + bird_r > 305:
            return True
        for px, gap_y in pipes:
            if px < bird_x + bird_r and px + pipe_w > bird_x - bird_r:
                if bird_y - bird_r < gap_y or bird_y + bird_r > gap_y + pipe_gap:
                    return True
        return False

    _draw_game_header(tft, 'Flappy Bird')
    draw_sky()
    tft.text('WAS/Space=flap Q=quit', 4, 308, 0x07E0, 0x0000)
    draw_bird(bird_x, bird_y)
    score_dirty = True

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch in ('w', 'a', 's', ' '):
            bird_v = FLAP

        now = time.ticks_ms()
        dt = time.ticks_diff(now, last_time)
        last_time = now
        pipe_timer += dt

        bird_v += GRAVITY
        old_bird_y = int(bird_y)
        bird_y += bird_v
        new_bird_y = int(bird_y)

        if pipe_timer >= spawn_ms:
            pipe_timer = 0
            gap_y = random.randint(60, 240 - pipe_gap)
            pipes.append([480.0, gap_y])
            draw_pipe(480, gap_y)

        clear_bird(bird_x, old_bird_y)

        for i in range(len(pipes)):
            old_px = int(pipes[i][0])
            gap_y = pipes[i][1]
            tft.fill_rect(old_px, 25, pipe_speed, gap_y - 25, 0x0000)
            tft.fill_rect(old_px, gap_y + pipe_gap, pipe_speed, 305 - gap_y - pipe_gap, 0x0000)
            pipes[i][0] -= pipe_speed
            new_px = int(pipes[i][0])
            if new_px > -pipe_w:
                draw_x = max(0, new_px + pipe_w - pipe_speed)
                tft.fill_rect(draw_x, 25, pipe_speed, gap_y - 25, 0x07E0)
                tft.fill_rect(draw_x, gap_y + pipe_gap, pipe_speed, 305 - gap_y - pipe_gap, 0x07E0)

        new_pipes = []
        for px, gap_y in pipes:
            if px > -pipe_w:
                new_pipes.append([px, gap_y])
        pipes = new_pipes

        for i in range(len(pipes)):
            if pipes[i][0] + pipe_w < bird_x:
                score += 1
                score_dirty = True
                try:
                    _buzzer.score_beep()
                except Exception:
                    pass
                particles.emit(bird_x, int(bird_y), count=5, speed=2,
                              colors=[0xFFE0, 0x07E0, 0x07FF])
                pipes.pop(i)
                break

        if collide():
            game_over = True
            break

        draw_bird(bird_x, bird_y)
        particles.update(tft, 0.08)

        if score_dirty:
            tft.fill_rect(4, 32, 80, 12, 0x0000)
            tft.text(f'Score: {score}', 4, 32, 0xFFFF, 0x0000)
            score_dirty = False
        time.sleep_ms(15)

    try:
        _buzzer.game_over_sound()
    except Exception:
        pass
    _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
    _show_highscore(tft, 'LIGHTS_OUT', score)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _minesweeper_game(tft, read_key):
    GRID = 10
    MINES = 15
    CELL = 20
    OX = 140
    OY = 36
    board = [[0]*GRID for _ in range(GRID)]
    revealed = [[False]*GRID for _ in range(GRID)]
    flagged = [[False]*GRID for _ in range(GRID)]
    cur_x = 0
    cur_y = 0
    first = True
    mines_left = MINES
    game_over = False
    pulse = 0

    # 1=blue 2=green 3=red 4=purple 5=maroon 6=cyan 7=black 8=gray
    NUM_COLORS = [0x0000, 0x001F, 0x07E0, 0xF800, 0xA81F, 0x8000, 0x07FF, 0x0000, 0x8410]

    def place_mines(sx, sy):
        placed = 0
        while placed < MINES:
            mx = random.randint(0, GRID-1)
            my = random.randint(0, GRID-1)
            if board[my][mx] != -1 and not (abs(mx-sx) <= 1 and abs(my-sy) <= 1):
                board[my][mx] = -1
                placed += 1
        for r in range(GRID):
            for c in range(GRID):
                if board[r][c] == -1:
                    continue
                cnt = 0
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        nr, nc = r+dr, c+dc
                        if 0<=nr<GRID and 0<=nc<GRID and board[nr][nc]==-1:
                            cnt += 1
                board[r][c] = cnt

    def count_flags():
        return sum(1 for r in range(GRID) for c in range(GRID) if flagged[r][c])

    def check_win():
        for r in range(GRID):
            for c in range(GRID):
                if board[r][c] != -1 and not revealed[r][c]:
                    return False
        return True

    def draw_mine_sprite(x, y):
        cx = x + CELL // 2
        cy = y + CELL // 2
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                if dx*dx + dy*dy <= 16:
                    tft.pixel(cx+dx, cy+dy, 0x0000)
        tft.pixel(cx-1, cy-1, 0x8410)
        dirs = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
        for ddx, ddy in dirs:
            for d in range(5, 9):
                tft.pixel(cx + ddx*d, cy + ddy*d, 0x0000)

    def draw_flag_sprite(x, y):
        cx = x + CELL // 2
        tft.fill_rect(cx, y+4, 2, 13, 0x8410)
        for row in range(7):
            w = 8 - row
            tft.fill_rect(cx+2, y+4+row, w, 1, 0xF800)
        tft.fill_rect(cx-2, y+16, 6, 2, 0x8410)

    def draw_cell(r, c, exploded=False):
        x = OX + c * CELL
        y = OY + r * CELL
        sel = (r == cur_y and c == cur_x)
        if revealed[r][c]:
            if board[r][c] == -1:
                is_clicked = exploded and r == cur_y and c == cur_x
                bg = 0xF800 if is_clicked else 0x6000
                tft.fill_rect(x, y, CELL-1, CELL-1, bg)
                draw_mine_sprite(x, y)
            elif board[r][c] == 0:
                tft.fill_rect(x, y, CELL-1, CELL-1, 0x2104)
            else:
                tft.fill_rect(x, y, CELL-1, CELL-1, 0x2104)
                nc = NUM_COLORS[board[r][c]] if board[r][c] < len(NUM_COLORS) else 0x07FF
                tft.text(str(board[r][c]), x+6, y+4, nc, 0x2104)
        elif flagged[r][c]:
            draw_3d_rect(tft, x, y, CELL-1, CELL-1, 0x6B4D)
            draw_flag_sprite(x, y)
        else:
            draw_3d_rect(tft, x, y, CELL-1, CELL-1, 0x8410)
            if sel and (pulse & 2):
                tft.rect(x-1, y-1, CELL+1, CELL+1, 0xFFE0)

    def draw_all(exploded=False):
        _draw_game_header(tft, 'Minesweeper')
        for r in range(GRID):
            for c in range(GRID):
                draw_cell(r, c, exploded=exploded)

    def draw_status():
        tft.fill_rect(4, 32, 200, 12, 0x0000)
        tft.text(f'Mines: {mines_left-count_flags()}', 4, 32, 0xFFFF, 0x0000)
        tft.fill_rect(4, 44, 200, 12, 0x0000)
        tft.text(f'Flags: {count_flags()}', 4, 44, 0xFFE0, 0x0000)

    def reveal(r, c, changed=None):
        if flagged[r][c] or revealed[r][c]:
            return
        revealed[r][c] = True
        if changed is not None:
            changed.append((r, c))
        if board[r][c] == 0:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    nr, nc = r+dr, c+dc
                    if 0<=nr<GRID and 0<=nc<GRID:
                        reveal(nr, nc, changed)

    draw_all()
    draw_status()
    tft.text('WASD=move Enter=reveal', 4, 270, 0x07E0, 0x0000)
    tft.text('Space=flag Q=quit', 4, 282, 0x07E0, 0x0000)

    while not game_over:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'w' and cur_y > 0:
            draw_cell(cur_y, cur_x)
            cur_y -= 1
        elif ch == 's' and cur_y < GRID-1:
            draw_cell(cur_y, cur_x)
            cur_y += 1
        elif ch == 'a' and cur_x > 0:
            draw_cell(cur_y, cur_x)
            cur_x -= 1
        elif ch == 'd' and cur_x < GRID-1:
            draw_cell(cur_y, cur_x)
            cur_x += 1
        elif ch == '\n':
            if first:
                place_mines(cur_x, cur_y)
                first = False
            if board[cur_y][cur_x] == -1:
                game_over = True
                for r in range(GRID):
                    for c in range(GRID):
                        if board[r][c] == -1:
                            revealed[r][c] = True
                draw_all(exploded=True)
                ex = OX + cur_x * CELL
                ey = OY + cur_y * CELL
                for _ in range(3):
                    tft.fill_rect(ex, ey, CELL-1, CELL-1, 0xFFFF)
                    time.sleep_ms(80)
                    tft.fill_rect(ex, ey, CELL-1, CELL-1, 0xF800)
                    draw_mine_sprite(ex, ey)
                    time.sleep_ms(80)
                break
            changed = []
            reveal(cur_y, cur_x, changed)
            for r, c in changed:
                draw_cell(r, c)
            draw_status()
            if check_win():
                _draw_game_header(tft, 'YOU WIN!')
                tft.text('All cells cleared!', 4, 40, 0x07E0, 0x0000)
                tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                read_key()
                return
        elif ch == ' ':
            flagged[cur_y][cur_x] = not flagged[cur_y][cur_x]
            draw_cell(cur_y, cur_x)
            draw_status()
        elif ch:
            draw_cell(cur_y, cur_x)
        pulse = (pulse + 1) % 12
        time.sleep_ms(50)

    _draw_game_header(tft, 'GAME OVER')
    tft.text('Hit a mine!', 4, 40, 0xF800, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _hangman_game(tft, read_key):
    words = ['python','rocket','bridge','garden','castle','frozen','island','jungle','master','ocean']
    word = random.choice(words)
    guessed = set()
    wrong = 0
    max_wrong = 6
    game_won = False
    game_lost = False

    def draw_word():
        tft.fill_rect(4, 40, 300, 20, 0x0000)
        display = ''
        for ch in word:
            if ch in guessed:
                display += ch + ' '
            else:
                display += '_ '
        tft.text(display, 4, 40, 0xFFE0, 0x0000)

    def draw_hangman():
        tft.fill_rect(320, 30, 140, 200, 0x0000)
        tft.hline(330, 200, 60, 0xFFFF)
        tft.vline(360, 40, 160, 0xFFFF)
        tft.hline(360, 40, 60, 0xFFFF)
        tft.vline(420, 40, 20, 0xFFFF)
        parts = [
            (395, 60, 10),
            (395, 80, 20),
            (385, 80, 10),
            (405, 80, 10),
            (395, 100, 15),
            (385, 130, 10),
            (405, 130, 10),
        ]
        for i in range(wrong):
            if i < len(parts):
                px, py, sz = parts[i]
                if i == 0:
                    tft.fill_rect(px, py, sz*2, sz*2, 0xFFFF)
                elif i == 1:
                    tft.fill_rect(px, py, 10, sz, 0xFFFF)
                elif i in (2,3):
                    tft.fill_rect(px, py, sz, 10, 0xFFFF)
                elif i == 4:
                    tft.fill_rect(px, py, 10, sz, 0xFFFF)
                elif i in (5,6):
                    tft.fill_rect(px, py, sz, 10, 0xFFFF)

    def draw_status():
        tft.fill_rect(4, 60, 200, 12, 0x0000)
        tft.text(f'Wrong: {wrong}/{max_wrong}', 4, 60, 0xF800 if wrong > 0 else 0x07E0, 0x0000)
        tft.fill_rect(4, 72, 200, 12, 0x0000)
        tft.text(f'Letters: {" ".join(sorted(guessed))}', 4, 72, 0xFFFF, 0x0000)

    _draw_game_header(tft, 'Hangman')
    draw_word()
    draw_hangman()
    draw_status()
    tft.text('Type a letter  Q=quit', 4, 290, 0x07E0, 0x0000)

    while not game_won and not game_lost:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if not ch or not ch.isalpha():
            continue
        ch = ch.lower()
        if ch in guessed:
            continue
        guessed.add(ch)
        if ch not in word:
            wrong += 1
            if wrong >= max_wrong:
                game_lost = True
        draw_word()
        draw_hangman()
        draw_status()
        if all(c in guessed for c in word):
            game_won = True

    if game_won:
        _draw_game_header(tft, 'YOU WIN!')
    else:
        _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Word: {word}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()




def cmd_deen(args):
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 2:
        return ('print_lines', [
            'deen: usage: deen [type] [query]',
            '  Types: quran, hadith, surah, dua',
            '  Example: deen quran al-fatiha',
            '  Example: deen dua protection',
        ])
    dtype = parts[0].lower()
    query = parts[1]

    if dtype == 'surah':
        try:
            import usocket
            import ujson
            num = int(query)
            host = 'api.alquran.cloud'
            path = f'/v1/surah/{num}/en.asad'
            sock = usocket.socket()
            sock.settimeout(10)
            addr = usocket.getaddrinfo(host, 443)[0][-1]
            import ssl
            ctx = ssl.SSLContext()
            ssock = ctx.wrap_socket(sock, server_hostname=host)
            ssock.connect(addr)
            ssock.sendall(f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
            data = b''
            while True:
                chunk = ssock.read(1024)
                if not chunk:
                    break
                data += chunk
            ssock.close()
            body = data.decode().split('\r\n\r\n', 1)[-1]
            j = ujson.loads(body)
            name = j.get('data', {}).get('englishName', f'Surah {num}')
            ayahs = j.get('data', {}).get('ayahs', [])
            lines = [f'=== {name} ===']
            for a in ayahs[:5]:
                lines.append(a.get('text', '')[:60])
            if len(ayahs) > 5:
                lines.append(f'... ({len(ayahs)} ayahs total)')
            return ('print_lines', lines)
        except Exception as e:
            return ('print', f'deen: {e}')

    elif dtype == 'dua':
        try:
            import usocket
            import ujson
            host = 'www.duas.muslim'
            path = '/api/duas.json'
            sock = usocket.socket()
            sock.settimeout(10)
            addr = usocket.getaddrinfo(host, 443)[0][-1]
            import ssl
            ctx = ssl.SSLContext()
            ssock = ctx.wrap_socket(sock, server_hostname=host)
            ssock.connect(addr)
            ssock.sendall(f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
            data = b''
            while True:
                chunk = ssock.read(1024)
                if not chunk:
                    break
                data += chunk
            ssock.close()
            return ('print', 'deen: dua database fetched (offline mode limited)')
        except:
            return ('print', 'deen: dua lookup requires network')

    else:
        return ('print', f'deen: unknown type "{dtype}".\n  Use: surah, dua')


def cmd_timer(args, oled_ctrl=None):
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            'timer: usage:',
            '  timer pomodoro [minutes]  (default 25)',
            '  timer countdown [seconds]',
        ])

    ttype = parts[0].lower()
    try:
        if ttype == 'pomodoro':
            mins = int(parts[1]) if len(parts) > 1 else 25
            secs = mins * 60
            if oled_ctrl:
                oled_ctrl.set_mode('timer', seconds=secs)
            return ('print_lines', [
                f'=== Pomodoro: {mins} minutes ===',
                'Timer started. Focus!',
                'Showing on OLED.',
            ])
        elif ttype == 'countdown':
            secs = int(parts[1]) if len(parts) > 1 else 60
            if oled_ctrl:
                oled_ctrl.set_mode('timer', seconds=secs)
            mins = secs // 60
            s = secs % 60
            return ('print_lines', [
                f'=== Countdown: {mins}m {s}s ===',
                'Timer started!',
                'Showing on OLED.',
            ])
        else:
            return ('print', f'timer: unknown type "{ttype}"')
    except ValueError:
        return ('print', 'timer: invalid time value')


def cmd_encrypt(args):
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 2:
        return ('print_lines', [
            'encrypt: usage: encrypt [binary|ASCII|HEX] [text]',
            '  Example: encrypt binary hello',
        ])
    mode = parts[0].lower()
    text = parts[1]
    try:
        if mode == 'binary':
            result = ' '.join(['0' * (8 - len(bin(ord(c))[2:])) + bin(ord(c))[2:] for c in text])
        elif mode in ('hex', 'ascii'):
            result = ' '.join(['0' * (2 - len(hex(ord(c))[2:])) + hex(ord(c))[2:].upper() for c in text])
        else:
            return ('print', f'encrypt: unknown mode "{mode}".\n  Use: binary, ASCII, HEX')
        return ('print', f'  {result}')
    except Exception as e:
        return ('print', f'encrypt: {e}')


def cmd_decrypt(args):
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 2:
        return ('print_lines', [
            'decrypt: usage: decrypt [binary|ASCII|HEX] [data]',
            '  Example: decrypt binary 01101000 01100101',
        ])
    mode = parts[0].lower()
    data = parts[1]
    try:
        if mode == 'binary':
            chunks = data.split()
            result = ''.join([chr(int(c, 2)) for c in chunks])
        elif mode in ('hex', 'ascii'):
            chunks = data.split()
            result = ''.join([chr(int(c, 16)) for c in chunks])
        else:
            return ('print', f'decrypt: unknown mode "{mode}".\n  Use: binary, ASCII, HEX')
        return ('print', f'  {result}')
    except Exception as e:
        return ('print', f'decrypt: {e}')


def cmd_draw(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'draw: usage: draw [filename.bmp]')
    if not tft:
        return ('print', 'draw: no display available')
    try:
        with open(filename, 'rb') as f:
            header = f.read(54)
            if header[:2] != b'BM':
                return ('print', 'draw: not a BMP file')
            width = int.from_bytes(header[18:22], 'little')
            height = int.from_bytes(header[22:26], 'little')
            planes = int.from_bytes(header[26:28], 'little')
            bits = int.from_bytes(header[28:30], 'little')
            compression = int.from_bytes(header[30:34], 'little')
            if planes != 1 or bits != 24 or compression != 0:
                return ('print', 'draw: only 24-bit uncompressed BMP supported')
            data_offset = int.from_bytes(header[10:14], 'little')
            f.seek(data_offset)
            row_size = (width * 3 + 3) & ~3
            max_w = min(width, tft.width)
            max_h = min(height, tft.height)
            scale_x = width / max_w if width > max_w else 1
            scale_y = height / max_h if height > max_h else 1
            buf = bytearray(max_w * 2)
            for y in range(max_h - 1, -1, -1):
                src_y = int(y * scale_y) if scale_y != 1 else y
                f.seek(data_offset + (height - 1 - src_y) * row_size)
                row = f.read(row_size)
                for x in range(max_w):
                    src_x = int(x * scale_x) if scale_x != 1 else x
                    idx = src_x * 3
                    b = row[idx]
                    g = row[idx + 1]
                    r = row[idx + 2]
                    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    buf[x * 2] = (color >> 8) & 0xFF
                    buf[x * 2 + 1] = color & 0xFF
                tft._set_window(0, y, max_w - 1, y)
                tft._dc(1)
                tft._cs(0)
                tft._spi.write(buf)
                tft._cs(1)
        return ('print', f'drew {filename} ({max_w}x{max_h})')
    except Exception as e:
        return ('print', f'draw: {e}')


def cmd_flag(args, tft=None):
    country = args.strip().lower()
    if not country:
        from lib.flagapi import COUNTRIES_44
        lines = ['=== FLAGS (44 countries) ===', '']
        lines.append('Stored locally in /flags/')
        lines.append('Type: flag <country>')
        lines.append('')
        per = 8
        for page in range(1, 7):
            start = (page - 1) * per
            end = min(start + per, len(COUNTRIES_44))
            chunk = COUNTRIES_44[start:end]
            lines.append(f'--- page {page}/6 ---')
            for c in chunk:
                lines.append(f'  {c}')
            lines.append('')
        return ('print_lines', lines)

    if country.isdigit() and 1 <= int(country) <= 6:
        from lib.flagapi import COUNTRIES_44
        page = int(country)
        per = 8
        start = (page - 1) * per
        end = min(start + per, len(COUNTRIES_44))
        chunk = COUNTRIES_44[start:end]
        lines = [f'=== FLAGS page {page}/6 ===', '']
        for c in chunk:
            lines.append(f'  {c}')
        return ('print_lines', lines)

    if not tft:
        return ('print', 'flag: no display available')

    try:
        from lib.flagapi import name_to_code, fetch_flag_svg
        from lib.svgparse import parse_svg

        code = name_to_code(country)
        if code is None:
            return ('print', f'flag: unknown country "{country}"')

        svg = fetch_flag_svg(code)
        if svg is None:
            return ('print', f'flag: local file not found\n  /flags/{code}.svg')

        ops = parse_svg(svg)
        if ops is None:
            return ('print', f'flag: {country} too complex\n  (coats of arms, crescents)')

        from lib.svgparse import _parse_viewbox
        vb = _parse_viewbox(svg)
        if vb is None:
            return ('print', 'flag: no viewBox')
        vb_x, vb_y, vb_w, vb_h = vb

        OUTPUT_Y = 28
        OUTPUT_H = 242

        src_w, src_h = vb_w, vb_h
        scale = min(480.0 / src_w, OUTPUT_H / src_h)
        dst_w = int(src_w * scale)
        dst_h = int(src_h * scale)
        dst_x = (480 - dst_w) // 2
        dst_y = OUTPUT_Y + (OUTPUT_H - dst_h) // 2

        ops_list = list(ops)

        def draw_flag_fn(tft):
            tft.fill(0x0000)
            tft.fill_rect(0, OUTPUT_Y, 480, OUTPUT_H, 0x0000)
            for op in ops_list:
                kind = op[0]
                if kind == 'rect':
                    rx = op[1] - vb_x
                    ry = op[2] - vb_y
                    rw = op[3]
                    rh = op[4]
                    color = op[5]
                    px = int(dst_x + rx * scale)
                    py = int(dst_y + ry * scale)
                    pw = int(rw * scale)
                    ph = int(rh * scale)
                    if pw < 1:
                        pw = 1
                    if ph < 1:
                        ph = 1
                    if 0 <= px < 480 and 0 <= py < 320:
                        if px + pw > 480:
                            pw = 480 - px
                        if py + ph > 320:
                            ph = 320 - py
                        tft.fill_rect(px, py, pw, ph, color)

        return ('flag_display', draw_flag_fn)
    except Exception as e:
        return ('print', f'flag: {e}')


def _wordle_game(tft, read_key):
    WORDS = ['apple', 'brain', 'crane', 'dream', 'eagle', 'flame', 'grape', 'house', 'input', 'joker']
    target = random.choice(WORDS).upper()
    guesses = []
    max_guesses = 6
    CELL = 40
    OX = 120
    OY = 36
    letter_colors = {}

    def draw_tile(x, y, letter, bg, active_row=False):
        border = 0x4208 if not active_row else 0x8410
        draw_3d_rect(tft, x, y, CELL, CELL, bg)
        tft.rect(x, y, CELL, CELL, border)
        if letter:
            tft.text15(letter, x + 10, y + 8, 0x0000, bg)

    def draw_grid():
        for r in range(max_guesses):
            if r < len(guesses):
                word = guesses[r]
                for c in range(5):
                    x = OX + c * (CELL + 4)
                    y = OY + r * (CELL + 4)
                    if word[c] == target[c]:
                        color = 0x07E0
                    elif word[c] in target:
                        color = 0xFFE0
                    else:
                        color = 0x4208
                    letter_colors[word[c]] = color
                    draw_tile(x, y, word[c], color)
            else:
                for c in range(5):
                    x = OX + c * (CELL + 4)
                    y = OY + r * (CELL + 4)
                    draw_tile(x, y, '', 0x2104, active_row=(r == len(guesses)))
        kb_y = OY + max_guesses * (CELL + 4) + 8
        kb = 'QWERTYUIOPASDFGHJKLZXCVBNM'
        kb_row1 = 'QWERTYUIOP'
        kb_row2 = 'ASDFGHJKL'
        kb_row3 = 'ZXCVBNM'
        for row_i, row_str in enumerate([kb_row1, kb_row2, kb_row3]):
            kw = len(row_str) * 22
            kx = OX + (5 * (CELL + 4) - kw) // 2
            ky = kb_y + row_i * 24
            for ki, ch in enumerate(row_str):
                cx = kx + ki * 22
                if ch in letter_colors:
                    kc = letter_colors[ch]
                    tft.fill_rect(cx, ky, 20, 20, kc)
                    tft.rect(cx, ky, 20, 20, 0x8410)
                else:
                    tft.fill_rect(cx, ky, 20, 20, 0x4208)
                    tft.rect(cx, ky, 20, 20, 0x630C)
                tft.text(ch, cx + 6, ky + 4, 0x0000)

    def animate_check(word):
        row = len(guesses) - 1
        for c in range(5):
            x = OX + c * (CELL + 4)
            y = OY + row * (CELL + 4)
            if word[c] == target[c]:
                color = 0x07E0
            elif word[c] in target:
                color = 0xFFE0
            else:
                color = 0x4208
            tft.fill_rect(x, y, CELL, CELL, 0xFFFF)
            tft.text15(word[c], x + 10, y + 8, 0x0000, 0xFFFF)
            time.sleep_ms(60)
            tft.fill_rect(x, y, CELL, CELL, 0x2104)
            tft.text15(word[c], x + 10, y + 8, 0x0000, 0x2104)
            time.sleep_ms(30)
            draw_tile(x, y, word[c], color)
            time.sleep_ms(40)

    _draw_game_header(tft, 'Wordle')
    draw_grid()
    tft.text('Type 5 letters, Enter=submit', 4, 290, 0x07E0, 0x0000)

    buf = ''
    while len(guesses) < max_guesses:
        tft.fill_rect(4, 28, 400, 12, 0x0000)
        tft.text(f'> {buf}', 4, 28, 0x07E0, 0x0000)
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == '\n' and len(buf) == 5:
            guesses.append(buf.upper())
            animate_check(buf.upper())
            draw_grid()
            if buf.upper() == target:
                _draw_game_header(tft, 'YOU WIN!')
                tft.text(f'Solved in {len(guesses)}!', 4, 40, 0x07E0, 0x0000)
                tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
                read_key()
                return
            buf = ''
        elif ch == '\b':
            buf = buf[:-1]
        elif ch.isalpha() and len(buf) < 5:
            buf += ch.upper()

    _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Word was: {target}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
    read_key()


def _asteroids_game(tft, read_key):
    if not _select_difficulty(tft, 'Asteroids'):
        return
    d = _diff()
    import math as _math
    try:
        from lib.buzzer import Buzzer as _Bz
        _bz = _Bz()
    except Exception:
        _bz = None
    particles = ParticleSystem(40)
    ship_x, ship_y = 240, 160
    ship_angle = 0.0
    ship_dx, ship_dy = 0.0, 0.0
    bullets = []
    rocks = []
    lives = 3
    rock_count = [4, 6, 8][_difficulty]
    for _ in range(rock_count):
        rocks.append({'x': random.randint(20, 460), 'y': random.randint(40, 300),
                      'dx': random.uniform(-2, 2), 'dy': random.uniform(-2, 2), 'r': 16})

    old_ship_x, old_ship_y = ship_x, ship_y
    old_ship_angle = ship_angle
    old_rocks = [{'x': r['x'], 'y': r['y'], 'r': r['r']} for r in rocks]
    old_bullets = []
    lives_dirty = True

    # Parallax stars: list of (x, y, speed, brightness)
    stars = []
    for _ in range(15):
        sx = random.randint(0, 479)
        sy = random.randint(25, 319)
        spd = random.uniform(0.3, 1.5)
        bri = random.choice([0x4208, 0x8410, 0xC618])
        stars.append([sx, sy, spd, bri])
    old_star_positions = [(s[0], s[1]) for s in stars]

    def draw_ship():
        nonlocal old_ship_x, old_ship_y, old_ship_angle
        cx, cy = int(old_ship_x), int(old_ship_y)
        tft.fill_rect(cx - 16, cy - 16, 32, 32, 0x0000)
        pts = []
        for a in [ship_angle, ship_angle + 2.3, ship_angle - 2.3]:
            pts.append((int(ship_x + 14 * _math.cos(a)), int(ship_y + 14 * _math.sin(a))))
        for i in range(3):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 3]
            steps = max(abs(x2 - x1), abs(y2 - y1), 1)
            for s in range(0, steps, 2):
                t = s / steps
                tft.pixel(int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t), 0xFFFF)
        # Engine glow at back of ship
        back_a = ship_angle + 3.14159
        ex = int(ship_x + 8 * _math.cos(back_a))
        ey = int(ship_y + 8 * _math.sin(back_a))
        if 0 <= ex < 480 and 0 <= ey < 320:
            tft.fill_rect(ex, ey, 2, 2, 0xFE80)
        old_ship_x, old_ship_y, old_ship_angle = ship_x, ship_y, ship_angle

    def draw_rock(r):
        rx, ry, rr = int(r['x']), int(r['y']), r['r']
        tft.fill_rect(rx - rr - 1, ry - rr - 1, rr * 2 + 2, rr * 2 + 2, 0x0000)
        # Irregular polygon via multiple offset rects
        offsets = [(-4, -2, 8, 4), (0, -4, 6, 8), (-2, 2, 10, 4), (-3, -3, 6, 6),
                   (2, -1, 4, 6), (-1, 3, 6, 3)]
        for ox, oy, ow, oh in offsets:
            tft.fill_rect(rx + ox, ry + oy, ow, oh, 0xC618)
        tft.rect(rx - rr + 1, ry - rr + 1, rr * 2 - 2, rr * 2 - 2, 0x8410)

    def clear_rock(r):
        rx, ry, rr = int(r['x']), int(r['y']), r['r']
        tft.fill_rect(rx - rr - 1, ry - rr - 1, rr * 2 + 2, rr * 2 + 2, 0x0000)

    _draw_game_header(tft, f'Asteroids  Lives: {lives}')
    tft.text('WASD=move/space Q=quit', 4, 290, 0x07E0, 0x0000)

    while True:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'w':
            ship_dx += _math.cos(ship_angle) * 0.5
            ship_dy += _math.sin(ship_angle) * 0.5
        if ch == 'a':
            ship_angle -= 0.3
        if ch == 'd':
            ship_angle += 0.3
        if ch == ' ':
            bullets.append({'x': ship_x, 'y': ship_y,
                            'dx': _math.cos(ship_angle) * 5, 'dy': _math.sin(ship_angle) * 5,
                            'life': 40, 'trail': []})
            if _bz:
                try:
                    _bz.beep(20)
                except Exception:
                    pass

        # Erase old bullet trails
        for ob in old_bullets:
            for tp in ob.get('trail', []):
                tft.pixel(int(tp[0]), int(tp[1]), 0x0000)
            tft.pixel(int(ob['x']), int(ob['y']), 0x0000)

        # Update stars (parallax)
        for si, star in enumerate(stars):
            ox, oy = old_star_positions[si]
            tft.pixel(int(ox), int(oy), 0x0000)
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = 479
                star[1] = random.randint(25, 319)
            tft.pixel(int(star[0]), int(star[1]), star[3])
            old_star_positions[si] = (star[0], star[1])

        ship_x = max(10, min(470, ship_x + ship_dx))
        ship_y = max(34, min(310, ship_y + ship_dy))
        ship_dx *= 0.98
        ship_dy *= 0.98

        for b in bullets:
            b['trail'].append((b['x'], b['y']))
            if len(b['trail']) > 2:
                b['trail'].pop(0)
            b['x'] += b['dx']
            b['y'] += b['dy']
            b['life'] -= 1
            # Draw trail: dimmer older positions
            for ti, tp in enumerate(b['trail']):
                age = len(b['trail']) - ti
                c = 0x4208 if age > 1 else 0x8410
                tft.pixel(int(tp[0]), int(tp[1]), c)
            tft.pixel(int(b['x']), int(b['y']), 0xFFFF)

        old_bullets = [{'x': b['x'], 'y': b['y'], 'trail': list(b['trail'])} for b in bullets]
        bullets = [b for b in bullets if b['life'] > 0 and 0 < b['x'] < 480 and 0 < b['y'] < 320]

        for i, rock in enumerate(rocks[:]):
            ox_r = old_rocks[i] if i < len(old_rocks) else None
            if ox_r:
                clear_rock(ox_r)

            rock['x'] += rock['dx']
            rock['y'] += rock['dy']
            if rock['x'] < -20: rock['x'] = 500
            if rock['x'] > 500: rock['x'] = -20
            if rock['y'] < 20: rock['y'] = 330
            if rock['y'] > 330: rock['y'] = 20
            draw_rock(rock)
            for b in bullets[:]:
                if ((b['x'] - rock['x']) ** 2 + (b['y'] - rock['y']) ** 2) < (rock['r'] ** 2):
                    # Explosion particles
                    particles.emit(int(rock['x']), int(rock['y']), count=12, speed=3,
                                   colors=[0xFFE0, 0xF800, 0xFE80, 0xFFFF], life=20)
                    if _bz:
                        try:
                            _bz.score_beep()
                        except Exception:
                            pass
                    bullets.remove(b)
                    rocks.remove(rock)
                    break

        old_rocks = [{'x': r['x'], 'y': r['y'], 'r': r['r']} for r in rocks]

        draw_ship()
        if lives_dirty:
            tft.fill_rect(4, 28, 400, 8, 0x0000)
            tft.text(f'Lives: {len(rocks)}', 4, 28, 0xFFFF, 0x0000)
            lives_dirty = False

        if not rocks:
            _draw_game_header(tft, 'YOU WIN!')
            tft.text('Press any key', 4, 40, 0x07E0, 0x0000)
            read_key()
            return

        time.sleep_ms(int(30 * d['sleep']))
        particles.update(tft)


def _maze_game(tft, read_key):
    COLS = 15
    ROWS = 10
    CELL = 28
    OX = 30
    OY = 40
    grid = [[1] * COLS for _ in range(ROWS)]

    def gen_maze(x, y):
        grid[y][x] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 1:
                grid[y + dy // 2][x + dx // 2] = 0
                gen_maze(nx, ny)

    gen_maze(0, 0)
    px, py = 0, 0
    gx, gy = COLS - 1, ROWS - 1
    visited = [[False] * COLS for _ in range(ROWS)]
    visited[py][px] = True

    def draw_wall(x, y):
        tft.fill_rect(x, y, CELL, CELL, 0x4208)
        tft.fill_rect(x + 1, y + 1, CELL - 2, 3, 0x630C)
        tft.fill_rect(x + 1, y + CELL - 4, CELL - 2, 3, 0x3186)
        if (x + y) % (CELL * 2) < CELL:
            tft.fill_rect(x + 3, y + 3, CELL // 2 - 2, 2, 0x528C)
            tft.fill_rect(x + CELL // 2 + 2, y + 3, CELL // 2 - 5, 2, 0x4A4A)
        tft.fill_rect(x, y + CELL // 2 - 1, CELL, 1, 0x39C7)
        tft.fill_rect(x + CELL // 2 - 1, y, 1, CELL, 0x39C7)

    def draw_floor(x, y, is_visited):
        base = 0x18E3 if is_visited else 0x10A2
        tft.fill_rect(x, y, CELL, CELL, base)
        if (x // CELL + y // CELL) % 3 == 0:
            tft.fill_rect(x + 2, y + 2, 3, 3, 0x2104)
        if (x // CELL + y // CELL) % 5 == 0:
            tft.fill_rect(x + CELL - 6, y + CELL - 6, 4, 4, 0x18C3)

    def draw_player(cx, cy):
        tft.fill_rect(cx + 4, cy + 6, CELL - 8, CELL - 10, 0x07E0)
        tft.fill_rect(cx + 6, cy + 4, CELL - 12, CELL - 8, 0x07E0)
        tft.fill_rect(cx + 8, cy + 8, 4, 4, 0x0000)
        tft.fill_rect(cx + CELL - 12, cy + 8, 4, 4, 0x0000)
        tft.fill_rect(cx + 9, cy + 9, 2, 2, 0xFFFF)
        tft.fill_rect(cx + CELL - 11, cy + 9, 2, 2, 0xFFFF)

    def draw_goal(cx, cy):
        mid = CELL // 2
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if abs(dx) + abs(dy) <= 6:
                    tft.fill_rect(cx + mid + dx, cy + mid + dy, 1, 1, 0x07E0)
        tft.fill_rect(cx + mid - 2, cy + mid - 2, 4, 4, 0xFE00)
        tft.fill_rect(cx + mid - 1, cy + mid - 1, 2, 2, 0xFFFF)

    def draw():
        tft.fill_rect(OX, OY, COLS * CELL, ROWS * CELL, 0x0000)
        for r in range(ROWS):
            for c in range(COLS):
                x = OX + c * CELL
                y = OY + r * CELL
                if grid[r][c] == 1:
                    draw_wall(x, y)
                else:
                    draw_floor(x, y, visited[r][c])
        draw_goal(OX + gx * CELL, OY + gy * CELL)
        draw_player(OX + px * CELL, OY + py * CELL)

    _draw_game_header(tft, 'Maze')
    draw()
    tft.text('WASD=move Q=quit', 4, 290, 0x07E0, 0x0000)

    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        nx, ny = px, py
        if ch == 'w': ny -= 1
        elif ch == 's': ny += 1
        elif ch == 'a': nx -= 1
        elif ch == 'd': nx += 1
        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
            px, py = nx, ny
            visited[py][px] = True
            draw()
            if px == gx and py == gy:
                _draw_game_header(tft, 'YOU WIN!')
                tft.text('Press any key', 4, 40, 0x07E0, 0x0000)
                read_key()
                return


def _connect4_game(tft, read_key):
    COLS = 7
    ROWS = 6
    CELL = 50
    OX = 65
    OY = 50
    board = [[0] * COLS for _ in range(ROWS)]
    turn = 1
    sel = 3
    anim_frame = 0

    # Mode selection
    _draw_game_header(tft, 'Connect 4')
    tft.text('Select mode:', 4, 40, 0xFFFF, 0x0000)
    tft.text('  1 - vs CPU', 4, 70, 0x07E0, 0x0000)
    tft.text('  2 - vs Player', 4, 90, 0xFFE0, 0x0000)
    tft.text('  Enter = vs CPU', 4, 120, 0x8410, 0x0000)
    cpu_mode = True
    while True:
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        if ch == '2':
            cpu_mode = False
            break
        if ch == '1' or ch == '\n':
            cpu_mode = True
            break

    def draw_piece(cx, cy, color):
        tft.fill_rect(cx + 2, cy + 2, CELL - 4, CELL - 4, 0x0000)
        tft.fill_rect(cx + 4, cy + 4, CELL - 8, CELL - 8, color)
        light = color
        r = (color >> 11) & 0x1F
        g = (color >> 5) & 0x3F
        b = color & 0x1F
        light = (min(r + 8, 31) << 11) | (min(g + 16, 63) << 5) | min(b + 8, 31)
        dark = (max(r - 8, 0) << 11) | (max(g - 16, 0) << 5) | max(b - 8, 0)
        tft.fill_rect(cx + 4, cy + 4, CELL - 8, 3, light)
        tft.fill_rect(cx + 4, cy + 4, 3, CELL - 8, light)
        tft.fill_rect(cx + 4, cy + CELL - 7, CELL - 8, 3, dark)
        tft.fill_rect(cx + CELL - 7, cy + 4, 3, CELL - 8, dark)

    def draw():
        tft.fill_rect(OX - 6, OY - 6, COLS * CELL + 12, ROWS * CELL + 12, 0x001F)
        tft.fill_rect(OX - 4, OY - 4, COLS * CELL + 8, ROWS * CELL + 8, 0x18DF)
        tft.fill_rect(OX - 2, OY - 2, COLS * CELL + 4, ROWS * CELL + 4, 0x001F)
        for r in range(ROWS):
            for c in range(COLS):
                x = OX + c * CELL
                y = OY + r * CELL
                tft.fill_rect(x + 2, y + 2, CELL - 4, CELL - 4, 0x0000)
                tft.fill_rect(x + 3, y + 3, CELL - 6, CELL - 6, 0x0841)
                if board[r][c] == 1:
                    draw_piece(x, y, 0xF800)
                elif board[r][c] == 2:
                    draw_piece(x, y, 0xFFE0)
        ax = OX + sel * CELL + CELL // 2
        ay = OY - 14
        tft.fill_rect(ax - 6, ay, 12, 10, 0x07E0)
        tft.fill_rect(ax - 4, ay + 2, 8, 6, 0x07E0)
        tft.fill_rect(ax - 2, ay + 4, 4, 4, 0x07E0)
        tft.fill_rect(ax + 2, ay + 4, 4, 4, 0x07E0)
        if anim_frame > 0:
            anim_color = 0xF800 if turn == 2 else 0xFFE0
            draw_piece(OX + sel * CELL, OY + (ROWS - anim_frame) * CELL, anim_color)

    def check_win(p):
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(board[r][c + i] == p for i in range(4)):
                    return [(r, c + i) for i in range(4)]
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(board[r + i][c] == p for i in range(4)):
                    return [(r + i, c) for i in range(4)]
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(board[r + i][c + i] == p for i in range(4)):
                    return [(r + i, c + i) for i in range(4)]
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if all(board[r - i][c + i] == p for i in range(4)):
                    return [(r - i, c + i) for i in range(4)]
        return None

    def flash_winning(winning, color):
        for _ in range(3):
            for wr, wc in winning:
                x = OX + wc * CELL
                y = OY + wr * CELL
                tft.fill_rect(x + 2, y + 2, CELL - 4, CELL - 4, 0xFFFF)
                tft.text15('WIN', x + 8, y + 14, 0x0000, 0xFFFF)
            time.sleep_ms(150)
            for wr, wc in winning:
                draw_piece(OX + wc * CELL, OY + wr * CELL, color)
            time.sleep_ms(150)

    def cpu_move():
        cpu = 2
        human = 1
        # Check each column for win/block/center preference
        for col in range(COLS):
            if board[0][col] == 0:
                # Try placing
                for r in range(ROWS - 1, -1, -1):
                    if board[r][col] == 0:
                        board[r][col] = cpu
                        if check_win(cpu):
                            board[r][col] = 0
                            return col
                        board[r][col] = 0
                        break
        for col in range(COLS):
            if board[0][col] == 0:
                for r in range(ROWS - 1, -1, -1):
                    if board[r][col] == 0:
                        board[r][col] = human
                        if check_win(human):
                            board[r][col] = 0
                            return col
                        board[r][col] = 0
                        break
        center = COLS // 2
        if board[0][center] == 0:
            return center
        for col in [center - 1, center + 1]:
            if 0 <= col < COLS and board[0][col] == 0:
                return col
        for col in range(COLS):
            if board[0][col] == 0:
                return col
        return None

    _draw_game_header(tft, 'Connect 4' + (' (vs CPU)' if cpu_mode else ''))
    draw()
    tft.text('W/A/D move  Enter drop  Q quit', 4, 290, 0x07E0, 0x0000)

    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'a' and sel > 0:
            sel -= 1
            draw()
        elif ch == 'd' and sel < COLS - 1:
            sel += 1
            draw()
        elif ch == '\n':
            for r in range(ROWS - 1, -1, -1):
                if board[r][sel] == 0:
                    board[r][sel] = turn
                    anim_frame = r + 1
                    for af in range(r + 1):
                        anim_frame = af + 1
                        draw()
                        time.sleep_ms(40)
                    anim_frame = 0
                    draw()
                    win_cells = check_win(turn)
                    if win_cells:
                        pc = 0xF800 if turn == 1 else 0xFFE0
                        flash_winning(win_cells, pc)
                        name = 'Red' if turn == 1 else 'Yellow'
                        _draw_game_header(tft, f'{name} WINS!')
                        tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
                        read_key()
                        return
                    turn = 3 - turn
                    if cpu_mode and turn == 2:
                        time.sleep_ms(200)
                        cpu_col = cpu_move()
                        if cpu_col is not None:
                            for r in range(ROWS - 1, -1, -1):
                                if board[r][cpu_col] == 0:
                                    board[r][cpu_col] = 2
                                    anim_frame = r + 1
                                    for af in range(r + 1):
                                        anim_frame = af + 1
                                        draw()
                                        time.sleep_ms(40)
                                    anim_frame = 0
                                    draw()
                                    win_cells = check_win(2)
                                    if win_cells:
                                        flash_winning(win_cells, 0xFFE0)
                                        _draw_game_header(tft, 'CPU WINS!')
                                        tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
                                        read_key()
                                        return
                                    turn = 1
                                    break
                    break


def _battleship_game(tft, read_key):
    COLS = 10
    ROWS = 10
    CELL = 28
    OX = 100
    OY = 36
    cpu_board = [[0] * COLS for _ in range(ROWS)]
    player_board = [[0] * COLS for _ in range(ROWS)]
    player_shots = [[0] * COLS for _ in range(ROWS)]
    ships = [2, 3, 4]
    cpu_ships = []
    player_ships = []
    phase = 'place'
    sel_x, sel_y = 0, 0
    ship_idx = 0
    ship_dir = 0
    cursor_x, cursor_y = 0, 0
    cursor_tick = 0

    for s in ships:
        placed = False
        while not placed:
            x = random.randint(0, COLS - s)
            y = random.randint(0, ROWS - 1)
            if all(cpu_board[y][x + i] == 0 for i in range(s)):
                for i in range(s):
                    cpu_board[y][x + i] = 1
                cpu_ships.append({'x': x, 'y': y, 'len': s, 'hits': 0})
                placed = True

    def draw_ocean_cell(x, y, base_blue=0x001F):
        wave = ((x + y) % 6 < 3)
        c = 0x085F if wave else 0x001F
        tft.fill_rect(x, y, CELL, CELL, c)
        tft.fill_rect(x + 2, y + 2, CELL - 4, 1, 0x107F)
        tft.fill_rect(x + 4, y + CELL - 4, CELL - 8, 1, 0x0013)

    def draw_hit_marker(cx, cy):
        mid = CELL // 2
        tft.fill_rect(cx + mid - 3, cy + mid - 1, 6, 2, 0xF800)
        tft.fill_rect(cx + mid - 1, cy + mid - 3, 2, 6, 0xF800)
        tft.fill_rect(cx + mid - 2, cy + mid - 2, 4, 4, 0xFE00)
        tft.fill_rect(cx + mid - 1, cy + mid - 1, 2, 2, 0xFFFF)
        tft.fill_rect(cx + mid - 4, cy + mid - 4, 2, 2, 0xF800)
        tft.fill_rect(cx + mid + 2, cy + mid - 4, 2, 2, 0xF800)
        tft.fill_rect(cx + mid - 4, cy + mid + 2, 2, 2, 0xF800)
        tft.fill_rect(cx + mid + 2, cy + mid + 2, 2, 2, 0xF800)

    def draw_miss_marker(cx, cy):
        mid = CELL // 2
        dots = [(mid - 3, mid - 2), (mid + 2, mid - 3), (mid - 1, mid + 2),
                (mid + 3, mid + 1), (mid, mid)]
        for dx, dy in dots:
            tft.fill_rect(cx + dx, cy + dy, 2, 2, 0xC618)
        tft.fill_rect(cx + mid - 1, cy + mid - 1, 2, 2, 0xFFFF)

    def draw_ship_preview():
        s = ships[ship_idx]
        for i in range(s):
            if ship_dir == 0:
                x = OX + (sel_x + i) * CELL
                y = OY + sel_y * CELL
            else:
                x = OX + sel_x * CELL
                y = OY + (sel_y + i) * CELL
            if 0 <= sel_x + (i if ship_dir == 0 else 0) < COLS and 0 <= sel_y + (i if ship_dir == 1 else 0) < ROWS:
                draw_ocean_cell(x + 1, y + 1)
                tft.fill_rect(x + 3, y + 3, CELL - 6, CELL - 6, 0x07FF)
                tft.fill_rect(x + 3, y + 3, CELL - 6, 2, 0x87FF)
                tft.fill_rect(x + 3, y + 3, 2, CELL - 6, 0x87FF)
                tft.fill_rect(x + 3, y + CELL - 5, CELL - 6, 2, 0x03EF)
                tft.fill_rect(x + CELL - 5, y + 3, 2, CELL - 6, 0x03EF)

    def draw():
        tft.fill_rect(OX, OY, COLS * CELL, ROWS * CELL, 0x0000)
        tft.text('Your Grid', OX, OY - 14, 0xFFFF, 0x0000)
        for r in range(ROWS):
            for c in range(COLS):
                x = OX + c * CELL
                y = OY + r * CELL
                if player_board[r][c] == 1 and player_shots[r][c] == 0:
                    tft.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, 0x630C)
                    tft.fill_rect(x + 3, y + 3, CELL - 6, CELL - 6, 0x8410)
                    tft.fill_rect(x + 3, y + 3, CELL - 6, 2, 0xA514)
                    tft.fill_rect(x + 3, y + 3, 2, CELL - 6, 0xA514)
                    tft.fill_rect(x + 3, y + CELL - 5, CELL - 6, 2, 0x4208)
                elif player_shots[r][c] == 1:
                    draw_ocean_cell(x + 1, y + 1)
                    draw_hit_marker(x, y)
                elif player_shots[r][c] == 2:
                    draw_ocean_cell(x + 1, y + 1)
                    draw_miss_marker(x, y)
                else:
                    draw_ocean_cell(x + 1, y + 1)
        if phase == 'place' and ship_idx < len(ships):
            draw_ship_preview()
        if phase == 'fire':
            cursor_tick += 1
            pulse = (cursor_tick // 4) % 2
            cc = 0xFFE0 if pulse == 0 else 0xFFFF
            cx = OX + cursor_x * CELL
            cy = OY + cursor_y * CELL
            tft.rect(cx, cy, CELL, CELL, cc)
            tft.rect(cx + 1, cy + 1, CELL - 2, CELL - 2, 0x0000)

    _draw_game_header(tft, 'Battleship')
    draw()
    tft.text('WASD=move  R=rotate  Enter=place/fire  Q=quit', 4, 290, 0x07E0, 0x0000)

    old_sel_x, old_sel_y = sel_x, sel_y
    old_cursor_x, old_cursor_y = cursor_x, cursor_y

    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if phase == 'place':
            old_sel_x, old_sel_y = sel_x, sel_y
            if ch == 'w' and sel_y > 0: sel_y -= 1
            elif ch == 's': sel_y += 1
            elif ch == 'a' and sel_x > 0: sel_x -= 1
            elif ch == 'd': sel_x += 1
            elif ch == 'r': ship_dir = 1 - ship_dir
            elif ch == '\n':
                s = ships[ship_idx]
                ok = True
                for i in range(s):
                    if ship_dir == 0:
                        cx, cy = sel_x + i, sel_y
                    else:
                        cx, cy = sel_x, sel_y + i
                    if cx >= COLS or cy >= ROWS or player_board[cy][cx] == 1:
                        ok = False
                if ok:
                    for i in range(s):
                        if ship_dir == 0:
                            player_board[sel_y][sel_x + i] = 1
                        else:
                            player_board[sel_y + i][sel_x] = 1
                    player_ships.append({'x': sel_x, 'y': sel_y, 'len': s, 'hits': 0})
                    ship_idx += 1
                    if ship_idx >= len(ships):
                        phase = 'fire'
                        tft.fill_rect(4, 28, 400, 12, 0x0000)
                        tft.text('Fire at the enemy!', 4, 28, 0xFFE0, 0x0000)
            draw()
        elif phase == 'fire':
            old_cursor_x, old_cursor_y = cursor_x, cursor_y
            if ch == 'w' and cursor_y > 0: cursor_y -= 1
            elif ch == 's' and cursor_y < ROWS - 1: cursor_y += 1
            elif ch == 'a' and cursor_x > 0: cursor_x -= 1
            elif ch == 'd' and cursor_x < COLS - 1: cursor_x += 1
            elif ch == '\n' and player_shots[cursor_y][cursor_x] == 0:
                if cpu_board[cursor_y][cursor_x] == 1:
                    player_shots[cursor_y][cursor_x] = 1
                    for ship in cpu_ships:
                        if ship['y'] == cursor_y and ship['x'] <= cursor_x < ship['x'] + ship['len']:
                            ship['hits'] += 1
                            break
                else:
                    player_shots[cursor_y][cursor_x] = 2
                if all(s['hits'] >= s['len'] for s in cpu_ships):
                    _draw_game_header(tft, 'YOU WIN!')
                    tft.text('All enemy ships sunk!', 4, 40, 0x07E0, 0x0000)
                    tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
                    read_key()
                    return
                cx = random.randint(0, COLS - 1)
                cy = random.randint(0, ROWS - 1)
                while player_shots[cy][cx] != 0:
                    cx = random.randint(0, COLS - 1)
                    cy = random.randint(0, ROWS - 1)
                draw()
                time.sleep_ms(200)
            elif ch:
                draw()


def _trivia_game(tft, read_key):
    questions = [
        ('What planet is Red?', 'A:Mars B:Venus C:Jupiter D:Saturn', 0),
        ('How many legs spider?', 'A:6 B:4 C:8 D:10', 2),
        ('Capital of France?', 'A:London B:Berlin C:Paris D:Madrid', 2),
        ('Largest ocean?', 'A:Atlantic B:Indian C:Arctic D:Pacific', 3),
        ('12x12=?', 'A:124 B:144 C:132 D:148', 1),
        ('Gas humans need?', 'A:CO2 B:Nitrogen C:Oxygen D:Helium', 2),
        ('Speed of light?', 'A:300k km/s B:150k C:500k D:1M', 0),
        ('Largest mammal?', 'A:Elephant B:Blue whale C:Giraffe D:Shark', 1),
        ('Water formula?', 'A:HO2 B:H2O C:H2O2 D:OH', 1),
        ('Sun is a?', 'A:Planet B:Asteroid C:Star D:Moon', 2),
    ]
    score = 0
    _draw_game_header(tft, 'Trivia')
    tft.text('WASD=select  Enter=answer  Q=quit', 4, 290, 0x07E0, 0x0000)

    for qi, (q, opts, correct) in enumerate(questions):
        tft.fill_rect(0, 28, 480, 260, 0x0000)
        tft.text(f'Q{qi + 1}/10: {q}', 4, 36, 0xFFFF, 0x0000)
        parts = opts.split(' ')
        options = [p.split(':')[1] for p in parts]
        sel = 0
        for i, opt in enumerate(options):
            color = 0xFFE0 if i == sel else 0xFFFF
            tft.text(f'  {chr(65 + i)}) {opt}', 4, 60 + i * 20, color, 0x0000)

        while True:
            ch = read_key()
            if ch == 'q' or ch == 'Q':
                return
            if ch == 'w':
                sel = max(0, sel - 1)
            elif ch == 's':
                sel = min(3, sel + 1)
            elif ch == '\n':
                for i, opt in enumerate(options):
                    color = 0x07E0 if i == correct else (0xF800 if i == sel else 0x8410)
                    tft.text(f'  {chr(65 + i)}) {opt}', 4, 60 + i * 20, color, 0x0000)
                if sel == correct:
                    score += 1
                time.sleep_ms(800)
                break
            for i, opt in enumerate(options):
                color = 0xFFE0 if i == sel else 0xFFFF
                tft.text(f'  {chr(65 + i)}) {opt}', 4, 60 + i * 20, color, 0x0000)

    _draw_game_header(tft, 'Trivia Complete!')
    tft.text(f'Score: {score}/10', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
    read_key()


def _typing_game(tft, read_key):
    WORDS = ['python', 'keyboard', 'cyberdeck', 'esp32', 'micro', 'keyboard', 'terminal', 'compile']
    word = random.choice(WORDS)
    buf = ''
    start = time.ticks_ms()

    _draw_game_header(tft, 'Typing Speed')
    tft.text('Type this word:', 4, 36, 0xFFFF, 0x0000)
    tft.text15(word, 4, 60, 0x07FF, 0x0000)
    tft.text('Q=quit', 4, 290, 0x07E0, 0x0000)

    while True:
        tft.fill_rect(4, 100, 400, 20, 0x0000)
        tft.text(f'> {buf}', 4, 100, 0x07E0, 0x0000)
        elapsed = time.ticks_diff(time.ticks_ms(), start) // 1000
        tft.fill_rect(4, 130, 200, 12, 0x0000)
        tft.text(f'Time: {elapsed}s', 4, 130, 0xFFFF, 0x0000)

        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == '\n':
            elapsed = time.ticks_diff(time.ticks_ms(), start) / 1000
            chars = len(word)
            wpm = int((chars / 5) / (elapsed / 60)) if elapsed > 0 else 0
            correct = buf == word
            _draw_game_header(tft, 'Result!')
            tft.text(f'Word: {word}', 4, 40, 0xFFFF, 0x0000)
            tft.text(f'Correct: {"YES" if correct else "NO"}', 4, 60, 0x07E0 if correct else 0xF800, 0x0000)
            tft.text(f'WPM: {wpm}', 4, 80, 0xFFE0, 0x0000)
            tft.text(f'Time: {elapsed:.1f}s', 4, 100, 0xFFFF, 0x0000)
            tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
            read_key()
            return
        if ch == '\b':
            buf = buf[:-1]
        elif ch.isalpha() and len(buf) < 20:
            buf += ch


def _math_game(tft, read_key):
    ops = ['+', '-', '*']
    score = 0
    total = 10

    _draw_game_header(tft, 'Math Quiz')
    tft.text('WASD=type  Enter=submit  Q=quit', 4, 290, 0x07E0, 0x0000)

    for qi in range(total):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(ops)
        if op == '+':
            answer = a + b
        elif op == '-':
            answer = a - b
        else:
            answer = a * b

        buf = ''
        tft.fill_rect(0, 28, 480, 260, 0x0000)
        tft.text(f'Q{qi + 1}/{total}', 4, 36, 0xFFFF, 0x0000)
        tft.text15(f'{a} {op} {b} = ?', 4, 60, 0x07FF, 0x0000)

        while True:
            tft.fill_rect(4, 110, 300, 20, 0x0000)
            tft.text(f'> {buf}', 4, 110, 0x07E0, 0x0000)

            ch = read_key()
            if ch == 'q' or ch == 'Q':
                return
            if ch == '\n' and buf:
                try:
                    if int(buf) == answer:
                        score += 1
                        tft.text('Correct!', 4, 140, 0x07E0, 0x0000)
                    else:
                        tft.text(f'Answer: {answer}', 4, 140, 0xF800, 0x0000)
                except:
                    tft.text(f'Answer: {answer}', 4, 140, 0xF800, 0x0000)
                time.sleep_ms(600)
                break
            if ch == '\b':
                buf = buf[:-1]
            elif ch in '0123456789-':
                buf += ch

    _draw_game_header(tft, 'Math Complete!')
    tft.text(f'Score: {score}/{total}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
    read_key()


def _sudoku_game(tft, read_key):
    CELL = 60
    OX = 120
    OY = 40
    puzzle = [
        [1, 0, 0, 4],
        [0, 3, 1, 0],
        [0, 1, 4, 0],
        [4, 0, 0, 2],
    ]
    board = [row[:] for row in puzzle]
    cur_r, cur_c = 0, 0

    def draw():
        for r in range(4):
            for c in range(4):
                x = OX + c * CELL
                y = OY + r * CELL
                if r == cur_r and c == cur_c:
                    draw_3d_rect(tft, x + 1, y + 1, CELL - 2, CELL - 2, 0x54BF)
                    tft.rect(x, y, CELL, CELL, 0x07FF)
                elif board[r][c] == 0:
                    draw_3d_rect(tft, x + 1, y + 1, CELL - 2, CELL - 2, 0x18C6)
                    tft.fill_rect(x + 2, y + 2, CELL - 4, 1, 0x1082)
                    tft.fill_rect(x + 2, y + 2, 1, CELL - 4, 0x1082)
                elif puzzle[r][c] != 0:
                    draw_3d_rect(tft, x + 1, y + 1, CELL - 2, CELL - 2, 0x31A6)
                    tft.text15(str(board[r][c]), x + 20, y + 18, 0xFFFF, 0x31A6)
                else:
                    draw_3d_rect(tft, x + 1, y + 1, CELL - 2, CELL - 2, 0x2104)
                    tft.text15(str(board[r][c]), x + 20, y + 18, 0x07E0, 0x2104)
        for i in range(5):
            thick = 3 if i % 2 == 0 else 1
            bx = OX + i * CELL
            by = OY + i * CELL
            tft.hline(OX, by, 4 * CELL, 0xFFFF)
            tft.vline(bx, OY, 4 * CELL, 0xFFFF)
            if thick > 1:
                tft.hline(OX, by + 1, 4 * CELL, 0xC618)
                tft.vline(bx + 1, OY, 4 * CELL, 0xC618)

    def check_valid(r, c, num):
        for i in range(4):
            if board[r][i] == num and i != c:
                return False
            if board[i][c] == num and i != r:
                return False
        br, bc = (r // 2) * 2, (c // 2) * 2
        for rr in range(br, br + 2):
            for cc in range(bc, bc + 2):
                if board[rr][cc] == num and (rr, cc) != (r, c):
                    return False
        return True

    _draw_game_header(tft, 'Sudoku 4x4')
    draw()
    tft.text('WASD=move  1-4=fill  Q=quit', 4, 290, 0x07E0, 0x0000)

    while True:
        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        old_r, old_c = cur_r, cur_c
        if ch == 'w' and cur_r > 0: cur_r -= 1
        elif ch == 's' and cur_r < 3: cur_r += 1
        elif ch == 'a' and cur_c > 0: cur_c -= 1
        elif ch == 'd' and cur_c < 3: cur_c += 1
        elif ch in '1234' and puzzle[cur_r][cur_c] == 0:
            num = int(ch)
            board[cur_r][cur_c] = num
            draw()
            if not check_valid(cur_r, cur_c, num):
                cx = OX + cur_c * CELL
                cy = OY + cur_r * CELL
                draw_3d_rect(tft, cx + 1, cy + 1, CELL - 2, CELL - 2, 0xD000)
                tft.text15(str(num), cx + 20, cy + 18, 0xFFFF, 0xD000)
                tft.rect(cx, cy, CELL, CELL, 0xF800)
                time.sleep_ms(300)
                board[cur_r][cur_c] = 0
                draw()
            elif all(board[r][c] != 0 for r in range(4) for c in range(4)):
                _draw_game_header(tft, 'YOU WIN!')
                tft.text15('Sudoku complete!', 4, 40, 0x07E0, 0x0000)
                tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
                read_key()
                return
            continue
        if cur_r != old_r or cur_c != old_c:
            draw()


def cmd_qr(args, tft=None):
    text = args.strip()
    if not text:
        return ('print', 'qr: usage: qr [text]')
    if not tft:
        return ('print', 'qr: display not available')
    try:
        data = text.encode('utf-8')
        if len(data) > 70:
            return ('print', 'qr: text too long (max ~70 chars)')
        version = 1
        size = 21
        modules = [[False] * size for _ in range(size)]
        reserved = [[False] * size for _ in range(size)]

        def _place_finder(row, col):
            for r in range(-1, 8):
                for c in range(-1, 8):
                    mr, mc = row + r, col + c
                    if 0 <= mr < size and 0 <= mc < size:
                        if r == -1 or r == 7 or c == -1 or c == 7:
                            modules[mr][mc] = False
                        elif r == 0 or r == 6 or c == 0 or c == 6:
                            modules[mr][mc] = True
                        elif 2 <= r <= 4 and 2 <= c <= 4:
                            modules[mr][mc] = True
                        else:
                            modules[mr][mc] = False
                        reserved[mr][mc] = True

        _place_finder(0, 0)
        _place_finder(0, size - 7)
        _place_finder(size - 7, 0)
        for i in range(8):
            if not reserved[6][i]:
                modules[6][i] = i % 2 == 0
                reserved[6][i] = True
            if not reserved[i][6]:
                modules[i][6] = i % 2 == 0
                reserved[i][6] = True
        for r in range(size):
            for c in range(size):
                if not reserved[r][c] and (r + c) % 2 == 0:
                    modules[r][c] = True
                    reserved[r][c] = True

        bits = []
        for b in data:
            for i in range(7, -1, -1):
                bits.append((b >> i) & 1)
        mask = 0
        idx = 0
        for r in range(size - 1, -1, -2):
            if r == 6:
                r = 5
            for c in range(size):
                for dr in [0, 1]:
                    mr = r - dr
                    mc = c if (size - 1 - r) % 4 < 2 else size - 1 - c
                    if 0 <= mr < size and 0 <= mc < size and not reserved[mr][mc]:
                        val = False
                        if idx < len(bits):
                            val = bool(bits[idx])
                            idx += 1
                        if (mr + mc) % 2 == 0:
                            val = not val
                        modules[mr][mc] = val

        tft.fill(0x0000)
        qr_size_px = min(tft.width, tft.height) - 40
        module_size = qr_size_px // size
        offset_x = (tft.width - module_size * size) // 2
        offset_y = (tft.height - module_size * size) // 2
        tft.text15(f'QR: {text[:30]}', 4, 4, 0x07FF, 0x0000)
        for r in range(size):
            for c in range(size):
                if modules[r][c]:
                    x = offset_x + c * module_size
                    y = offset_y + r * module_size
                    tft.fill_rect(x, y, module_size, module_size, 0xFFFF)
        return ('print', f'qr: displayed ({size}x{size})')
    except Exception as e:
        return ('print', f'qr: {e}')


def _lightsout_game(tft, read_key):
    SIZE = 5
    CELL = 44
    OX = (480 - SIZE * CELL) // 2
    OY = 40
    grid = [[False] * SIZE for _ in range(SIZE)]
    import random as _r
    for _ in range(_r.randint(8, 15)):
        r, c = _r.randint(0, SIZE - 1), _r.randint(0, SIZE - 1)
        for dr, dc in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                grid[nr][nc] = not grid[nr][nc]
    cursor = [0, 0]
    moves = 0
    ripple_cells = []
    ripple_timer = 0
    win_flash = 0
    win_flash_dir = 1

    def draw_cell(r, c):
        x = OX + c * CELL
        y = OY + r * CELL
        on = grid[r][c]
        if on:
            gradient_rect(tft, x + 3, y + 3, CELL - 6, CELL - 6, 0xFFE0, 0xFE60)
            tft.fill_rect(x + 6, y + 6, CELL - 12, CELL - 12, 0xFFFF)
            draw_3d_rect(tft, x + 1, y + 1, CELL - 2, CELL - 2, 0xC600)
            tft.fill_rect(x + 5, y + 5, CELL - 10, 2, 0xFFFF)
            tft.fill_rect(x + 5, y + 5, 2, CELL - 10, 0xFFFF)
        else:
            draw_3d_rect(tft, x + 1, y + 1, CELL - 2, CELL - 2, 0x2945)
            tft.fill_rect(x + 2, y + 2, CELL - 4, 1, 0x18C3)
            tft.fill_rect(x + 2, y + 2, 1, CELL - 4, 0x18C3)
        if r == cursor[0] and c == cursor[1]:
            tft.rect(x, y, CELL, CELL, 0x07FF)
            tft.rect(x + 1, y + 1, CELL - 2, CELL - 2, 0x07FF)

    def draw_ripple():
        if ripple_timer > 0:
            alpha = ripple_timer
            for cr, cc in ripple_cells:
                x = OX + cc * CELL
                y = OY + cr * CELL
                if 0 <= cr < SIZE and 0 <= cc < SIZE:
                    color = 0xFFE0 if grid[cr][cc] else 0x4208
                    fade = min(alpha * 4, 15)
                    r_c = (color >> 11) & 0x1F
                    g_c = (color >> 5) & 0x3F
                    b_c = color & 0x1F
                    r_c = min(r_c + fade, 31)
                    g_c = min(g_c + fade, 63)
                    b_c = min(b_c + fade, 31)
                    glow = (r_c << 11) | (g_c << 5) | b_c
                    tft.rect(x + 1, y + 1, CELL - 2, CELL - 2, glow)
            ripple_timer -= 1

    def draw_all():
        for r in range(SIZE):
            for c in range(SIZE):
                draw_cell(r, c)
        draw_ripple()

    def check_win():
        return not any(grid[r][c] for r in range(SIZE) for c in range(SIZE))

    def toggle(r, c):
        nonlocal ripple_cells, ripple_timer
        affected = []
        for dr, dc in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                grid[nr][nc] = not grid[nr][nc]
                affected.append((nr, nc))
        ripple_cells = affected
        ripple_timer = 5

    def win_celebrate():
        nonlocal win_flash, win_flash_dir
        win_flash += win_flash_dir * 2
        if win_flash > 8:
            win_flash_dir = -1
        elif win_flash < 0:
            win_flash_dir = 1
        for r in range(SIZE):
            for c in range(SIZE):
                x = OX + c * CELL
                y = OY + r * CELL
                phase = (r + c + win_flash) % 3
                if phase == 0:
                    gradient_rect(tft, x + 3, y + 3, CELL - 6, CELL - 6, 0xFFFF, 0xFFE0)
                elif phase == 1:
                    gradient_rect(tft, x + 3, y + 3, CELL - 6, CELL - 6, 0xFFE0, 0xFE60)
                else:
                    gradient_rect(tft, x + 3, y + 3, CELL - 6, CELL - 6, 0xFE60, 0xF800)

    _draw_game_header(tft, 'Lights Out')
    tft.text('WASD=move Enter=toggle', 4, 290, 0x07E0, 0x0000)
    draw_all()

    while True:
        tft.fill_rect(4, 30, 200, 8, 0x0000)
        tft.text15(f'Moves: {moves}', 4, 30, 0xFFFF, 0x0000)
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        elif ch == 'w' and cursor[0] > 0:
            cursor[0] -= 1
        elif ch == 's' and cursor[0] < SIZE - 1:
            cursor[0] += 1
        elif ch == 'a' and cursor[1] > 0:
            cursor[1] -= 1
        elif ch == 'd' and cursor[1] < SIZE - 1:
            cursor[1] += 1
        elif ch == '\n':
            toggle(cursor[0], cursor[1])
            moves += 1
            if check_win():
                _draw_game_header(tft, 'YOU WIN!')
                tft.text15(f'Cleared in {moves} moves!', 4, 40, 0x07E0, 0x0000)
                tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                read_key()
                return
        draw_all()
        time.sleep_ms(20)


def _platformer_game(tft, read_key):
    if not _select_difficulty(tft, 'Platformer'):
        return
    d = _diff()
    try:
        from lib.buzzer import Buzzer as _Bz
        _bz = _Bz()
    except Exception:
        _bz = None
    particles = ParticleSystem(20)
    GRAVITY = [1, 1.5, 2][_difficulty]
    JUMP = -7
    SCROLL_SPEED = [2, 3, 4][_difficulty]
    GROUND_Y = 260
    PLAYER_X = 80
    PLAYER_W = 12
    PLAYER_H = 16

    px = PLAYER_X
    py = GROUND_Y - PLAYER_H
    vy = 0
    on_ground = True
    score = 0
    scroll_x = 0
    game_over = False
    next_obstacle = 600
    squash_timer = 0  # for squash/stretch animation
    was_in_air = False

    platforms = []
    obstacles = []
    coins = []

    import random as _r

    # Parallax hills: (base_x_offset, y, width, height, color)
    hills_far = []
    hills_near = []
    for i in range(8):
        hx = i * 120
        hy = GROUND_Y - _r.randint(60, 120)
        hw = _r.randint(80, 140)
        hh = GROUND_Y - hy
        hills_far.append([hx, hy, hw, hh])
    for i in range(10):
        hx = i * 100
        hy = GROUND_Y - _r.randint(30, 70)
        hw = _r.randint(60, 100)
        hh = GROUND_Y - hy
        hills_near.append([hx, hy, hw, hh])

    def spawn_segment(x):
        platforms.append([x + _r.randint(0, 60), GROUND_Y - _r.randint(40, 80), _r.randint(40, 80)])
        if _r.random() < 0.6:
            ox = x + _r.randint(20, 100)
            obstacles.append([ox, GROUND_Y - _r.randint(20, 60), 10, 16])
        if _r.random() < 0.4:
            cx = x + _r.randint(10, 100)
            coins.append([cx, GROUND_Y - _r.randint(50, 100), True])

    for i in range(5):
        spawn_segment(600 + i * 200)

    def draw_player():
        # Pixel-art character: head, body, legs with squash/stretch
        hw = PLAYER_W // 2
        cx = px + hw
        if squash_timer > 0:
            # Squash on landing: wider, shorter
            sw = PLAYER_W + 2
            sh = PLAYER_H - 3
            draw_x = cx - sw // 2
            draw_y = py + PLAYER_H - sh
            tft.fill_rect(draw_x, draw_y, sw, sh, 0x07E0)
            # Head
            tft.fill_rect(draw_x + 2, draw_y, sw - 4, 5, 0xFEA0)
            # Eyes
            tft.fill_rect(draw_x + 3, draw_y + 1, 2, 2, 0x0000)
            tft.fill_rect(draw_x + sw - 5, draw_y + 1, 2, 2, 0x0000)
            # Body
            tft.fill_rect(draw_x + 1, draw_y + 5, sw - 2, sh - 8, 0x001F)
            # Legs
            tft.fill_rect(draw_x + 2, draw_y + sh - 3, 3, 3, 0x4208)
            tft.fill_rect(draw_x + sw - 5, draw_y + sh - 3, 3, 3, 0x4208)
        elif not on_ground and vy < 0:
            # Stretch on jump: taller, thinner
            sw = PLAYER_W - 2
            sh = PLAYER_H + 3
            draw_x = cx - sw // 2
            draw_y = py + PLAYER_H - sh
            tft.fill_rect(draw_x, draw_y, sw, sh, 0x07E0)
            # Head
            tft.fill_rect(draw_x + 1, draw_y, sw - 2, 5, 0xFEA0)
            tft.fill_rect(draw_x + 2, draw_y + 1, 2, 2, 0x0000)
            tft.fill_rect(draw_x + sw - 4, draw_y + 1, 2, 2, 0x0000)
            # Body
            tft.fill_rect(draw_x, draw_y + 5, sw, sh - 8, 0x001F)
            # Legs
            tft.fill_rect(draw_x + 1, draw_y + sh - 3, 3, 3, 0x4208)
            tft.fill_rect(draw_x + sw - 4, draw_y + sh - 3, 3, 3, 0x4208)
        else:
            # Normal pose
            tft.fill_rect(px, py, PLAYER_W, PLAYER_H, 0x07E0)
            # Head
            tft.fill_rect(px + 2, py, 8, 5, 0xFEA0)
            # Eyes
            tft.fill_rect(px + 3, py + 1, 2, 2, 0x0000)
            tft.fill_rect(px + 7, py + 1, 2, 2, 0x0000)
            # Body
            tft.fill_rect(px + 1, py + 5, 10, 6, 0x001F)
            # Legs
            tft.fill_rect(px + 2, py + 11, 3, 5, 0x4208)
            tft.fill_rect(px + 7, py + 11, 3, 5, 0x4208)

    def clear_player():
        tft.fill_rect(px - 2, py - 3, PLAYER_W + 4, PLAYER_H + 6, 0x0000)

    def draw_platform(p):
        x = p[0] - scroll_x
        if -80 < x < 560:
            # Textured platform with alternating pattern
            tft.fill_rect(x, p[1], p[2], 4, 0x8410)
            for px_i in range(0, p[2], 4):
                tft.fill_rect(x + px_i, p[1], 2, 2, 0x630C)
                tft.fill_rect(x + px_i + 2, p[1] + 2, 2, 2, 0x630C)

    def draw_obstacle(o):
        x = o[0] - scroll_x
        if -20 < x < 500:
            tft.fill_rect(x, o[1], o[2], o[3], 0xF800)

    def draw_coin(c):
        if not c[2]:
            return
        x = c[0] - scroll_x
        if -10 < x < 490:
            tft.fill_rect(x, c[1], 8, 8, 0xFFE0)

    def draw_hills():
        # Far hills (slower parallax)
        for h in hills_far:
            hx = h[0] - scroll_x * 0.3
            # Wrap around
            total_w = len(hills_far) * 120
            hx = ((hx % total_w) + total_w) % total_w - 120
            if -140 < hx < 500:
                tft.fill_rect(int(hx), h[1], h[2], h[3], 0x0320)
        # Near hills (faster parallax)
        for h in hills_near:
            hx = h[0] - scroll_x * 0.6
            total_w = len(hills_near) * 100
            hx = ((hx % total_w) + total_w) % total_w - 100
            if -110 < hx < 500:
                tft.fill_rect(int(hx), h[1], h[2], h[3], 0x0400)

    _draw_game_header(tft, 'Platformer')
    tft.text('W=jump S=duck Q=quit', 4, 290, 0x07E0, 0x0000)

    def draw_ground():
        tft.hline(0, GROUND_Y, 480, 0x4208)
        for i in range(0, 480, 20):
            tft.hline(i, GROUND_Y + 1, 10, 0x4208)

    draw_hills()
    draw_ground()
    draw_player()

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        if (ch == 'w' or ch == ' ') and on_ground:
            vy = JUMP
            on_ground = False
            if _bz:
                try:
                    _bz.beep(30)
                except Exception:
                    pass

        vy += GRAVITY
        old_py = py
        py += vy
        if py >= GROUND_Y - PLAYER_H:
            # Landing detection for squash
            if not on_ground and old_py < GROUND_Y - PLAYER_H:
                squash_timer = 4
                # Dust particles on landing
                particles.emit(px + PLAYER_W // 2, GROUND_Y, count=5, speed=1,
                               colors=[0x8410, 0xC618, 0x630C], life=15)
            py = GROUND_Y - PLAYER_H
            vy = 0
            on_ground = True

        for p in platforms:
            px_check = p[0] - scroll_x
            if PLAYER_X + PLAYER_W > px_check and PLAYER_X < px_check + p[2]:
                if old_py + PLAYER_H <= p[1] and py + PLAYER_H >= p[1]:
                    py = p[1] - PLAYER_H
                    if not on_ground:
                        squash_timer = 4
                        particles.emit(px + PLAYER_W // 2, p[1], count=5, speed=1,
                                       colors=[0x8410, 0xC618, 0x630C], life=15)
                    vy = 0
                    on_ground = True

        scroll_x += SCROLL_SPEED
        score += 1

        for o in obstacles:
            ox = o[0] - scroll_x
            if (PLAYER_X + PLAYER_W > ox + 2 and PLAYER_X < ox + o[2] - 2 and
                    py + PLAYER_H > o[1] + 2 and py < o[1] + o[3] - 2):
                game_over = True

        for c in coins:
            if c[2]:
                cx = c[0] - scroll_x
                if (PLAYER_X + PLAYER_W > cx and PLAYER_X < cx + 8 and
                        py + PLAYER_H > c[1] and py < c[1] + 8):
                    c[2] = False
                    score += 50

        if scroll_x > next_obstacle:
            spawn_segment(next_obstacle + 600)
            next_obstacle += 200

        platforms[:] = [p for p in platforms if p[0] - scroll_x > -100]
        obstacles[:] = [o for o in obstacles if o[0] - scroll_x > -50]
        coins[:] = [c for c in coins if c[0] - scroll_x > -50]

        clear_player()
        tft.fill_rect(0, 25, 480, GROUND_Y - 25, 0x0000)
        draw_hills()
        draw_ground()
        for p in platforms:
            draw_platform(p)
        for o in obstacles:
            draw_obstacle(o)
        for c in coins:
            draw_coin(c)
        draw_player()

        tft.fill_rect(300, 30, 180, 10, 0x0000)
        tft.text(f'Score: {score}', 300, 30, 0xFFFF, 0x0000)
        if squash_timer > 0:
            squash_timer -= 1
        time.sleep_ms(16)

    if _bz:
        try:
            _bz.game_over_sound()
        except Exception:
            pass
    _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
    _show_highscore(tft, 'BOMBER', score)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _othello_game(tft, read_key):
    SIZE = 8
    CELL = 30
    OX = (480 - SIZE * CELL) // 2
    OY = 50
    EMPTY = 0
    PLAYER = 1
    CPU = 2
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def new_board():
        b = [[EMPTY]*SIZE for _ in range(SIZE)]
        b[3][3] = CPU
        b[3][4] = PLAYER
        b[4][3] = PLAYER
        b[4][4] = CPU
        return b

    def valid_moves(b, color):
        opp = CPU if color == PLAYER else PLAYER
        moves = []
        for r in range(SIZE):
            for c in range(SIZE):
                if b[r][c] != EMPTY:
                    continue
                for dr, dc in DIRS:
                    nr, nc = r+dr, c+dc
                    flipped = False
                    while 0 <= nr < SIZE and 0 <= nc < SIZE and b[nr][nc] == opp:
                        nr += dr
                        nc += dc
                        flipped = True
                    if flipped and 0 <= nr < SIZE and 0 <= nc < SIZE and b[nr][nc] == color:
                        moves.append((r, c))
                        break
        return moves

    def apply_move(b, r, c, color):
        opp = CPU if color == PLAYER else PLAYER
        b[r][c] = color
        for dr, dc in DIRS:
            nr, nc = r+dr, c+dc
            path = []
            while 0 <= nr < SIZE and 0 <= nc < SIZE and b[nr][nc] == opp:
                path.append((nr, nc))
                nr += dr
                nc += dc
            if path and 0 <= nr < SIZE and 0 <= nc < SIZE and b[nr][nc] == color:
                for pr, pc in path:
                    b[pr][pc] = color

    def cpu_move(b):
        moves = valid_moves(b, CPU)
        if not moves:
            return None
        best = None
        best_score = -1
        corners = [(0,0),(0,SIZE-1),(SIZE-1,0),(SIZE-1,SIZE-1)]
        for r, c in moves:
            score = 0
            if (r, c) in corners:
                score = 100
            elif r == 0 or r == SIZE-1 or c == 0 or c == SIZE-1:
                score = 10
            else:
                score = 1
            if score > best_score:
                best_score = score
                best = (r, c)
        return best

    WOOD_LIGHT = 0xE7C4
    WOOD_DARK = 0x8C52

    def draw_board(b, cursor, hints):
        for r in range(SIZE):
            for c in range(SIZE):
                x = OX + c * CELL
                y = OY + r * CELL
                wood = WOOD_LIGHT if (r + c) % 2 == 0 else WOOD_DARK
                tft.fill_rect(x, y, CELL, CELL, wood)
                tft.rect(x, y, CELL, CELL, 0x5A49)
                if b[r][c] == PLAYER:
                    cx = x + CELL // 2
                    cy = y + CELL // 2
                    pr = 10
                    for dy in range(-pr, pr + 1):
                        row_w = int((pr * pr - dy * dy) ** 0.5) * 2
                        if row_w > 0:
                            if dy < -3:
                                gc = 0xD69A
                            elif dy > 3:
                                gc = 0xC618
                            else:
                                gc = 0xFFFF
                            tft.fill_rect(cx - row_w // 2, cy + dy, row_w, 1, gc)
                    tft.rect(cx - pr, cy - pr, pr * 2 + 1, pr * 2 + 1, 0xC618)
                elif b[r][c] == CPU:
                    cx = x + CELL // 2
                    cy = y + CELL // 2
                    pr = 10
                    for dy in range(-pr, pr + 1):
                        row_w = int((pr * pr - dy * dy) ** 0.5) * 2
                        if row_w > 0:
                            if dy < -3:
                                gc = 0x2945
                            elif dy > 3:
                                gc = 0x18C3
                            else:
                                gc = 0x0000
                            tft.fill_rect(cx - row_w // 2, cy + dy, row_w, 1, gc)
                    tft.rect(cx - pr, cy - pr, pr * 2 + 1, pr * 2 + 1, 0x4208)
                if (r, c) in hints and b[r][c] == EMPTY:
                    tft.fill_rect(x + CELL // 2 - 2, y + CELL // 2 - 2, 4, 4, 0x07E0)
                    tft.fill_rect(x + CELL // 2 - 1, y + CELL // 2 - 1, 2, 2, 0x0FE0)
                if (r, c) == cursor:
                    tft.rect(x, y, CELL, CELL, 0xF800)
                    tft.rect(x + 1, y + 1, CELL - 2, CELL - 2, 0xF800)

    def count(b):
        p = 0
        c = 0
        for r in range(SIZE):
            for c_ in range(SIZE):
                if b[r][c_] == PLAYER:
                    p += 1
                elif b[r][c_] == CPU:
                    c += 1
        return p, c

    b = new_board()
    cr, cc = 0, 0
    _draw_game_header(tft, 'Othello (PvCPU)')
    tft.text('WASD=move  Enter=place  Q=quit', 4, 290, 0x07E0, 0x0000)

    while True:
        moves = valid_moves(b, PLAYER)
        draw_board(b, (cr, cc), moves)
        p, c = count(b)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15(f'You: {p}  CPU: {c}', 150, 4, 0x07FF, 0x1082)

        if not moves and not valid_moves(b, CPU):
            break
        if not moves:
            cpu = cpu_move(b)
            if cpu:
                apply_move(b, cpu[0], cpu[1], CPU)
            continue

        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'w' and cr > 0:
            cr -= 1
        elif ch == 's' and cr < SIZE-1:
            cr += 1
        elif ch == 'a' and cc > 0:
            cc -= 1
        elif ch == 'd' and cc < SIZE-1:
            cc += 1
        elif ch == '\n':
            if (cr, cc) in moves:
                apply_move(b, cr, cc, PLAYER)
                cm = cpu_move(b)
                if cm:
                    apply_move(b, cm[0], cm[1], CPU)

    _draw_game_header(tft, 'GAME OVER')
    p, c = count(b)
    if p > c:
        tft.text(f'You WIN! {p}-{c}', 4, 40, 0x07E0, 0x0000)
    elif c > p:
        tft.text(f'CPU wins {c}-{p}', 4, 40, 0xF800, 0x0000)
    else:
        tft.text(f'Tie {p}-{p}', 4, 40, 0xFFFF, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _tank_game(tft, read_key):
    if not _select_difficulty(tft, 'Tank Battle'):
        return
    d = _diff()
    try:
        from lib.buzzer import Buzzer as _Bz
        _bz = _Bz()
    except Exception:
        _bz = None
    particles = ParticleSystem(30)
    TX, TY = 40, 260
    TANK_W, TANK_H = 20, 24
    bullets = []
    enemies = []
    score = 0
    fire_cooldown = 0
    spawn_timer = 0
    spawn_interval = [30, 20, 12][_difficulty]
    enemy_colors = [0xF800, 0x001F, 0xFFE0]

    def draw_tank(x, y, color):
        # Tank body
        tft.fill_rect(x, y, TANK_W, TANK_H, color)
        # Turret: extends from center upward
        tft.fill_rect(x + TANK_W // 2 - 2, y - 6, 4, 8, 0x8410)
        # Treads
        tft.fill_rect(x + 1, y + TANK_H, 5, 3, 0x4208)
        tft.fill_rect(x + TANK_W - 6, y + TANK_H, 5, 3, 0x4208)

    def clear_tank(x, y):
        tft.fill_rect(x - 1, y - 7, TANK_W + 2, TANK_H + 11, 0x0000)

    def draw_bullet(b):
        tft.fill_rect(b[0] - 2, b[1] - 4, 4, 8, 0xFFE0)

    def clear_bullet(b):
        tft.fill_rect(b[0] - 3, b[1] - 5, 6, 10, 0x0000)

    def draw_enemy(e):
        tft.fill_rect(e[0], e[1], TANK_W, TANK_H, e[3])
        # Turret
        tft.fill_rect(e[0] + TANK_W // 2 - 2, e[1] - 4, 4, 6, 0x8410)

    def clear_enemy(e):
        tft.fill_rect(e[0] - 1, e[1] - 5, TANK_W + 2, TANK_H + 10, 0x0000)

    _draw_game_header(tft, 'Tank Battle')
    tft.text('A/D=move  W=fire  Q=quit', 4, 290, 0x07E0, 0x0000)
    draw_tank(TX, TY, 0x07E0)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15(f'Score: {score}', 180, 4, 0x07FF, 0x1082)

    while True:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'a' and TX > 0:
            clear_tank(TX, TY)
            TX -= 8
            if TX < 0:
                TX = 0
            draw_tank(TX, TY, 0x07E0)
        elif ch == 'd' and TX < 460:
            clear_tank(TX, TY)
            TX += 8
            if TX > 460:
                TX = 460
            draw_tank(TX, TY, 0x07E0)
        elif ch == 'w' and fire_cooldown <= 0:
            bullets.append([TX + TANK_W // 2, TY - 6, -6])
            fire_cooldown = 8
            if _bz:
                try:
                    _bz.beep(15)
                except Exception:
                    pass

        if fire_cooldown > 0:
            fire_cooldown -= 1

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            ex = random.randint(0, 460)
            edx = random.choice([-2, -1, 1, 2])
            ecolor = random.choice(enemy_colors)
            enemies.append([ex, 30, edx, ecolor])

        for b in bullets[:]:
            clear_bullet(b)
            b[1] += b[2]
            if b[1] < 24:
                bullets.remove(b)
            else:
                draw_bullet(b)

        for e in enemies[:]:
            clear_enemy(e)
            e[0] += e[2]
            e[1] += 1
            if e[0] < 0:
                e[0] = 0
                e[2] = -e[2]
            if e[0] > 460:
                e[0] = 460
                e[2] = -e[2]
            if e[1] > 320:
                enemies.remove(e)
                score = max(0, score - 1)
            else:
                draw_enemy(e)

        for b in bullets[:]:
            for e in enemies[:]:
                if (b[0] >= e[0] and b[0] <= e[0] + TANK_W and
                        b[1] >= e[1] and b[1] <= e[1] + TANK_H):
                    clear_bullet(b)
                    clear_enemy(e)
                    # Explosion particles
                    particles.emit(e[0] + TANK_W // 2, e[1] + TANK_H // 2,
                                   count=10, speed=2,
                                   colors=[0xFFE0, 0xF800, 0xFE80, 0xFFFF], life=20)
                    if _bz:
                        try:
                            _bz.score_beep()
                        except Exception:
                            pass
                    if b in bullets:
                        bullets.remove(b)
                    if e in enemies:
                        enemies.remove(e)
                    score += 10
                    tft.fill_rect(0, 0, 480, 24, 0x1082)
                    tft.text15(f'Score: {score}', 180, 4, 0x07FF, 0x1082)
                    break

        for e in enemies:
            if (e[0] < TX + TANK_W and e[0] + TANK_W > TX and
                    e[1] + TANK_H >= TY):
                if _bz:
                    try:
                        _bz.game_over_sound()
                    except Exception:
                        pass
                _draw_game_header(tft, 'GAME OVER')
                tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
                _show_highscore(tft, 'BATTLESHIP', score)
                tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                read_key()
                return

        time.sleep_ms(int(50 * d['sleep']))
        particles.update(tft)


def _hanoi_game(tft, read_key):
    DISKS = 4
    PEGS = 3
    pegs = [list(range(DISKS, 0, -1)), [], []]
    moves = 0
    selected = 0
    min_moves = (2 ** DISKS) - 1

    PEG_X = [80, 240, 400]
    BASE_Y = 280
    DISK_W = 40
    DISK_H = 14

    def draw_pegs():
        for i in range(PEGS):
            tft.fill_rect(PEG_X[i] - 30, BASE_Y - 6, 60, 6, 0x4208)
            tft.fill_rect(PEG_X[i] - 3, 50, 6, 230, 0x4208)

    def draw_disks():
        tft.fill_rect(0, 50, 480, 230, 0x0000)
        draw_pegs()
        for i in range(PEGS):
            for j, d in enumerate(pegs[i]):
                w = DISK_W + d * 8
                x = PEG_X[i] - w // 2
                y = BASE_Y - (j + 1) * DISK_H
                colors = [0x07FF, 0x07E0, 0xFFE0, 0xF800, 0xF81F, 0x001F, 0xFFFF]
                tft.fill_rect(x, y, w, DISK_H, colors[(d-1) % len(colors)])
                tft.rect(x, y, w, DISK_H, 0x0000)

    def can_move(src, dst):
        if not pegs[src]:
            return False
        if not pegs[dst]:
            return True
        return pegs[src][-1] < pegs[dst][-1]

    _draw_game_header(tft, 'Tower of Hanoi')
    tft.text('A/D=peg  Enter=move  Q=quit', 4, 290, 0x07E0, 0x0000)
    tft.fill_rect(0, 30, 480, 4, 0x07FF)
    tft.fill_rect(PEG_X[selected] - 35, 30, 70, 4, 0xF800)
    draw_disks()
    tft.text15(f'Moves: {moves}', 10, 32, 0x07FF, 0x0000)
    tft.text15(f'Min: {min_moves}', 350, 32, 0x07FF, 0x0000)

    while True:
        if len(pegs[2]) == DISKS:
            _draw_game_header(tft, 'YOU WIN!')
            tft.text(f'Moves: {moves} (min {min_moves})', 4, 40, 0x07E0, 0x0000)
            tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
            read_key()
            return

        ch = read_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'a' and selected > 0:
            tft.fill_rect(PEG_X[selected] - 35, 30, 70, 4, 0x07FF)
            selected -= 1
            tft.fill_rect(PEG_X[selected] - 35, 30, 70, 4, 0xF800)
        elif ch == 'd' and selected < PEGS - 1:
            tft.fill_rect(PEG_X[selected] - 35, 30, 70, 4, 0x07FF)
            selected += 1
            tft.fill_rect(PEG_X[selected] - 35, 30, 70, 4, 0xF800)
        elif ch == '\n':
            for dst in range(PEGS):
                if dst != selected and can_move(selected, dst):
                    pegs[dst].append(pegs[selected].pop())
                    moves += 1
                    draw_disks()
                    tft.fill_rect(0, 30, 480, 4, 0x07FF)
                    tft.fill_rect(PEG_X[selected] - 35, 30, 70, 4, 0xF800)
                    tft.text15(f'Moves: {moves}', 10, 32, 0x07FF, 0x0000)
                    tft.text15(f'Min: {min_moves}', 350, 32, 0x07FF, 0x0000)
                    break


def _bomber_game(tft, read_key):
    if not _select_difficulty(tft, 'Bomber'):
        return
    d = _diff()
    try:
        from lib.buzzer import Buzzer as _Bz
        _bz = _Bz()
    except Exception:
        _bz = None
    particles = ParticleSystem(40)
    PX, PY = 240, 280
    PW, PH = 16, 8
    bombs = []
    enemies = []
    score = 0
    enemy_dir = 2
    bomb_cooldown = 0
    enemy_count = [3, 5, 7][_difficulty]
    smoke_trail = []  # [(x, y), ...] for plane smoke

    def draw_player():
        # Top-down plane with wings
        # Body
        tft.fill_rect(PX - PW // 2, PY, PW, PH, 0x8410)
        # Wings
        tft.fill_rect(PX - PW // 2 - 6, PY + 1, 6, 3, 0x07FF)
        tft.fill_rect(PX + PW // 2, PY + 1, 6, 3, 0x07FF)
        # Tail
        tft.fill_rect(PX - 2, PY + PH - 2, 4, 2, 0x07FF)
        # Nose highlight
        tft.fill_rect(PX - 1, PY, 2, 2, 0xFFFF)

    def clear_player():
        tft.fill_rect(PX - PW // 2 - 7, PY - 1, PW + 14, PH + 2, 0x0000)

    def draw_enemy(e):
        # Varied building colors
        bcolor = e[3] if len(e) > 3 else 0xF800
        tft.fill_rect(e[0] - 6, e[1] - 4, 12, 8, bcolor)
        # Window detail
        tft.fill_rect(e[0] - 4, e[1] - 2, 2, 2, 0x0000)
        tft.fill_rect(e[0] + 2, e[1] - 2, 2, 2, 0x0000)

    def clear_enemy(e):
        tft.fill_rect(e[0] - 7, e[1] - 5, 14, 10, 0x0000)

    def draw_bomb(b):
        # Bomb with shadow
        tft.fill_rect(b[0] - 2, b[1], 4, 4, 0x4208)  # shadow offset 2px below
        tft.fill_rect(b[0] - 2, b[1] - 2, 4, 4, 0xFFE0)  # bomb body

    def clear_bomb(b):
        tft.fill_rect(b[0] - 3, b[1] - 3, 6, 8, 0x0000)

    def setup_enemies():
        nonlocal enemy_dir
        enemies.clear()
        colors = [0xF800, 0xFC1F, 0xFFE0]
        for row in range(enemy_count):
            for col in range(8):
                ex = 60 + col * 50
                ey = 50 + row * 30
                ecolor = colors[row % len(colors)]
                enemies.append([ex, ey, True, ecolor])
        enemy_dir = 2

    _draw_game_header(tft, 'Bomber')
    tft.text('A/D=move  W=bomb  Q=quit', 4, 290, 0x07E0, 0x0000)
    setup_enemies()
    draw_player()
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15(f'Score: {score}', 180, 4, 0x07FF, 0x1082)

    while True:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return

        if ch == 'a' and PX > 10:
            clear_player()
            PX -= 10
            draw_player()
        elif ch == 'd' and PX < 470:
            clear_player()
            PX += 10
            draw_player()
        elif ch == 'w' and bomb_cooldown <= 0:
            bombs.append([PX, PY - 6, -4])
            bomb_cooldown = 10
            if _bz:
                try:
                    _bz.beep(50)
                except Exception:
                    pass

        if bomb_cooldown > 0:
            bomb_cooldown -= 1

        # Smoke trail behind plane
        smoke_trail.append((PX, PY + PH))
        if len(smoke_trail) > 6:
            old_sx, old_sy = smoke_trail.pop(0)
            tft.fill_rect(int(old_sx) - 1, int(old_sy), 2, 2, 0x0000)
        for si, (sx, sy) in enumerate(smoke_trail):
            age = len(smoke_trail) - si
            c = 0x4208 if age > 3 else 0x8410
            tft.fill_rect(int(sx) - 1, int(sy), 2, 2, c)

        hit_edge = False
        for e in enemies:
            if e[2]:
                if e[0] <= 10 or e[0] >= 470:
                    hit_edge = True
                    break
        if hit_edge:
            enemy_dir = -enemy_dir
            for e in enemies:
                if e[2]:
                    clear_enemy(e)
                    e[1] += 15
                    if e[1] >= PY - 10:
                        if _bz:
                            try:
                                _bz.game_over_sound()
                            except Exception:
                                pass
                        _draw_game_header(tft, 'GAME OVER')
                        tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
                        _show_highscore(tft, 'PLATFORMER', score)
                        tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
                        read_key()
                        return

        for e in enemies:
            if e[2]:
                clear_enemy(e)
                e[0] += enemy_dir
                draw_enemy(e)

        for b in bombs[:]:
            clear_bomb(b)
            b[1] += b[2]
            if b[1] < 24:
                bombs.remove(b)
            else:
                draw_bomb(b)
                for e in enemies:
                    if e[2] and abs(b[0] - e[0]) < 8 and abs(b[1] - e[1]) < 6:
                        clear_enemy(e)
                        clear_bomb(b)
                        # Large explosion
                        particles.emit(e[0], e[1], count=15, speed=3,
                                       colors=[0xF800, 0xFE80, 0xFFE0, 0xFFFF, 0xFC1F], life=25)
                        if _bz:
                            try:
                                _bz.score_beep()
                            except Exception:
                                pass
                        bombs.remove(b)
                        e[2] = False
                        score += 10
                        tft.fill_rect(0, 0, 480, 24, 0x1082)
                        tft.text15(f'Score: {score}', 180, 4, 0x07FF, 0x1082)
                        break

        alive = sum(1 for e in enemies if e[2])
        if alive == 0:
            _draw_game_header(tft, 'VICTORY!')
            tft.text(f'Score: {score}', 4, 40, 0x07E0, 0x0000)
            tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
            read_key()
            return

        time.sleep_ms(int(40 * d['sleep']))
        particles.update(tft)


def _fighter_game(tft, read_key):
    particles = ParticleSystem(40)
    FLOOR_Y = 260
    FW, FH = 24, 48
    PUNCH_RANGE = 35
    PUNCH_REACH = 14
    KICK_RANGE = 45
    KICK_REACH = 20
    SPECIAL_RANGE = 50
    SPECIAL_REACH = 25
    BLOCK_REDUCTION = 0.3
    ROUND_TIME = 90
    JUMP_HEIGHT = 30
    SPECIAL_COOLDOWN = 60

    px, py = 100, FLOOR_Y - FH
    cx, cy = 350, FLOOR_Y - FH
    p_hp = 100
    c_hp = 100
    p_block = False
    p_crouch = False
    p_jumping = False
    p_jump_vel = 0
    p_punching = 0
    p_kicking = 0
    p_special = 0
    p_special_cd = 0
    c_block = False
    c_crouch = False
    c_jumping = False
    c_jump_vel = 0
    c_punching = 0
    c_kicking = 0
    c_special = 0
    c_special_cd = 0
    c_ai_timer = 0
    c_ai_action = 0
    c_retreat = False
    shake_x = 0
    shake_y = 0
    shake_timer = 0
    timer = ROUND_TIME
    last_tick = time.ticks_ms()
    game_over = False
    result_msg = ''
    dmg_texts = []

    def draw_arena():
        tft.fill_rect(0, 25, 480, 295, 0x0000)
        for y in range(FLOOR_Y, 320):
            ratio = (y - FLOOR_Y) / 60
            r = int(10 * ratio)
            g = int(30 * ratio)
            b = int(20 * ratio)
            c = (r << 11) | (g << 5) | b
            tft.hline(0, y, 480, c)
        tft.hline(0, FLOOR_Y, 480, 0x4208)
        for i in range(0, 480, 24):
            tft.fill_rect(i, FLOOR_Y + 1, 12, 1, 0x39C7)

    def draw_health_bars():
        tft.fill_rect(0, 25, 480, 14, 0x1082)
        bar_w = 180
        p_fill = max(0, p_hp) * bar_w // 100
        c_fill = max(0, c_hp) * bar_w // 100
        tft.fill_rect(10, 27, bar_w, 10, 0x4208)
        tft.fill_rect(290, 27, bar_w, 10, 0x4208)
        if p_fill > 0:
            for i in range(p_fill):
                ratio = i / bar_w
                if ratio < 0.5:
                    r = int(31 * (ratio * 2))
                    g = 31
                else:
                    r = 31
                    g = int(31 * ((1 - ratio) * 2))
                c = (r << 11) | (g << 5)
                tft.fill_rect(10 + i, 27, 1, 10, c)
        if c_fill > 0:
            for i in range(c_fill):
                ratio = i / bar_w
                if ratio < 0.5:
                    r = int(31 * (ratio * 2))
                    g = 31
                else:
                    r = 31
                    g = int(31 * ((1 - ratio) * 2))
                c = (r << 11) | (g << 5)
                tft.fill_rect(290 + bar_w - i, 27, 1, 10, c)
        tft.text('YOU', 10, 28, 0xFFFF, 0x1082)
        tft.text('CPU', 290, 28, 0xFFFF, 0x1082)
        mins = timer // 60
        secs = timer % 60
        tft.text15(f'{mins}:{secs:02d}', 220, 27, 0x07FF, 0x1082)

    def draw_fighter(fx, fy, color, punching, kicking, special, blocking, crouching, jumping, facing_right):
        draw_y = fy
        if crouching:
            body_h = 24
            head_w, head_h = 8, 8
            body_w, bh = 12, 10
            leg_w, leg_h = 4, 8
            draw_y = fy + FH - body_h
            tft.fill_rect(fx + 1, draw_y + head_h, body_w, bh, color)
            tft.fill_rect(fx + 1, draw_y, head_w, head_h, 0xFEA0)
            eye_x = fx + (3 if facing_right else head_w - 3)
            tft.fill_rect(eye_x, draw_y + 2, 2, 2, 0x0000)
            tft.fill_rect(fx + 3, draw_y + head_h + bh, leg_w, leg_h, 0x4208)
            tft.fill_rect(fx + body_w - leg_w - 1, draw_y + head_h + bh, leg_w, leg_h, 0x4208)
            if blocking:
                arm_x = fx + (body_w if facing_right else -4)
                tft.fill_rect(arm_x, draw_y + head_h, 4, bh, 0x8410)
            elif punching > 0:
                arm_len = PUNCH_REACH
                arm_x = fx + (FW if facing_right else -arm_len)
                tft.fill_rect(arm_x, draw_y + head_h + 2, arm_len, 4, 0xFEA0)
                tft.fill_rect(arm_x + (arm_len - 4 if facing_right else 0), draw_y + head_h, 6, 6, 0xFEA0)
            elif kicking > 0:
                kick_len = KICK_REACH
                leg_x = fx + (FW if facing_right else -kick_len)
                tft.fill_rect(leg_x, draw_y + head_h + bh + 2, kick_len, 4, 0xFEA0)
                tft.fill_rect(leg_x + (kick_len - 4 if facing_right else 0), draw_y + head_h + bh, 6, 6, 0xFEA0)
            elif special > 0:
                spec_len = SPECIAL_REACH
                spec_x = fx + (FW if facing_right else -spec_len)
                tft.fill_rect(spec_x, draw_y + head_h + 1, spec_len, 6, 0x07FF)
                tft.fill_rect(spec_x + (spec_len - 6 if facing_right else 0), draw_y, 8, 8, 0x07FF)
            return
        tft.fill_rect(fx, fy, FW, FH, 0x0000)
        tft.fill_rect(fx + 2, fy, 10, 10, 0xFEA0)
        eye_x = fx + (4 if facing_right else 8)
        tft.fill_rect(eye_x, fy + 2, 2, 2, 0x0000)
        tft.fill_rect(fx + 1, fy + 10, 12, 16, color)
        tft.fill_rect(fx + 2, fy + 26, 5, 14, 0x4208)
        tft.fill_rect(fx + 9, fy + 26, 5, 14, 0x4208)
        arm_y = fy + 12
        arm_h = 12
        if blocking:
            tft.fill_rect(fx + 3, arm_y, 8, arm_h, 0x8410)
            tft.fill_rect(fx + (FW - 2 if facing_right else -1), arm_y, 4, arm_h, 0x8410)
        elif punching > 0:
            arm_len = PUNCH_REACH
            if facing_right:
                tft.fill_rect(fx + FW, fy + 14, arm_len, 5, 0xFEA0)
                tft.fill_rect(fx + FW + arm_len - 4, fy + 13, 6, 7, 0xFEA0)
            else:
                tft.fill_rect(fx - arm_len, fy + 14, arm_len, 5, 0xFEA0)
                tft.fill_rect(fx - arm_len - 2, fy + 13, 6, 7, 0xFEA0)
            tft.fill_rect(fx + 2, arm_y, 4, arm_h, color)
        elif kicking > 0:
            kick_len = KICK_REACH
            if facing_right:
                tft.fill_rect(fx + FW, fy + 30, kick_len, 5, 0xFEA0)
                tft.fill_rect(fx + FW + kick_len - 4, fy + 29, 6, 7, 0xFEA0)
            else:
                tft.fill_rect(fx - kick_len, fy + 30, kick_len, 5, 0xFEA0)
                tft.fill_rect(fx - kick_len - 2, fy + 29, 6, 7, 0xFEA0)
            tft.fill_rect(fx - 4, arm_y, 4, arm_h, color)
            tft.fill_rect(fx + FW, arm_y, 4, arm_h, color)
        elif special > 0:
            spec_len = SPECIAL_REACH
            if facing_right:
                tft.fill_rect(fx + FW, fy + 12, spec_len, 8, 0x07FF)
                tft.fill_rect(fx + FW + spec_len - 6, fy + 10, 8, 12, 0x07FF)
            else:
                tft.fill_rect(fx - spec_len, fy + 12, spec_len, 8, 0x07FF)
                tft.fill_rect(fx - spec_len - 2, fy + 10, 8, 12, 0x07FF)
            tft.fill_rect(fx + 2, arm_y, 4, arm_h, 0x07FF)
        else:
            tft.fill_rect(fx - 4, arm_y, 4, arm_h, color)
            tft.fill_rect(fx + FW, arm_y, 4, arm_h, color)

    def clear_fighter(fx, fy):
        max_reach = SPECIAL_REACH + 4
        tft.fill_rect(fx - max_reach, fy - 2, FW + max_reach * 2, FH + 4, 0x0000)

    def update_display():
        draw_arena()
        draw_health_bars()
        clear_fighter(px + shake_x, py + shake_y)
        clear_fighter(cx + shake_x, cy + shake_y)
        draw_fighter(px + shake_x, py + shake_y, 0x07FF, p_punching, p_kicking, p_special, p_block, p_crouch, p_jumping, True)
        draw_fighter(cx + shake_x, cy + shake_y, 0xF800, c_punching, c_kicking, c_special, c_block, c_crouch, c_jumping, False)

    draw_arena()
    draw_health_bars()
    draw_fighter(px, py, 0x07FF, 0, 0, 0, False, False, False, True)
    draw_fighter(cx, cy, 0xF800, 0, 0, 0, False, False, False, False)

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return

        p_block = False
        p_crouch = False
        if ch == 'a':
            px -= 4
            if px < 5:
                px = 5
        elif ch == 'd':
            px += 4
            if px > cx - FW - 5:
                px = cx - FW - 5
        elif ch == 'w' and not p_jumping:
            p_jumping = True
            p_jump_vel = -6
        elif ch == 's':
            p_crouch = True
        elif ch == ' ' and p_punching <= 0 and p_kicking <= 0 and p_special <= 0 and p_special_cd <= 0 and not p_block:
            p_punching = 6
        elif ch == 'e' and p_punching <= 0 and p_kicking <= 0 and p_special <= 0 and p_special_cd <= 0 and not p_block:
            p_kicking = 8
        elif ch == 'r' and p_punching <= 0 and p_kicking <= 0 and p_special <= 0 and p_special_cd <= 0 and not p_block:
            p_special = 10
            p_special_cd = SPECIAL_COOLDOWN

        if p_jumping:
            p_jump_vel += 1
            py += p_jump_vel
            if py >= FLOOR_Y - FH:
                py = FLOOR_Y - FH
                p_jumping = False
                p_jump_vel = 0

        if p_punching > 0:
            p_punching -= 1
        if p_kicking > 0:
            p_kicking -= 1
        if p_special > 0:
            p_special -= 1
        if p_special_cd > 0:
            p_special_cd -= 1

        dist = cx - px
        c_retreat = c_hp < 30 and p_hp > 50

        if c_punching <= 0 and c_kicking <= 0 and c_special <= 0:
            if c_special_cd > 0:
                c_special_cd -= 1
            if dist < PUNCH_RANGE and random.random() < 0.08:
                c_punching = 6
            elif dist < KICK_RANGE and random.random() < 0.05:
                c_kicking = 8
            elif dist < SPECIAL_RANGE and random.random() < 0.03 and c_special_cd <= 0:
                c_special = 10
                c_special_cd = SPECIAL_COOLDOWN
            elif dist < PUNCH_RANGE + 30 and random.random() < 0.04:
                c_block = True
        if c_punching > 0:
            c_punching -= 1
        if c_kicking > 0:
            c_kicking -= 1
        if c_special > 0:
            c_special -= 1

        c_ai_timer += 1
        if c_ai_timer > 20:
            c_ai_timer = 0
            c_ai_action = random.randint(0, 2)
            c_block = False

        if c_retreat:
            cx += 2
            if cx > 445:
                cx = 445
        else:
            if dist > PUNCH_RANGE + 10:
                cx -= 2
            elif dist < PUNCH_RANGE - 10:
                cx += 2
            if cx > 445:
                cx = 445
            if cx < px + FW + 5:
                cx = px + FW + 5

        if c_jumping:
            c_jump_vel += 1
            cy += c_jump_vel
            if cy >= FLOOR_Y - FH:
                cy = FLOOR_Y - FH
                c_jumping = False
                c_jump_vel = 0
            if random.random() < 0.02 and not c_jumping:
                c_jumping = True
                c_jump_vel = -6

        if p_punching == 3 and dist < PUNCH_RANGE:
            dmg = random.randint(5, 10)
            if c_block:
                dmg = int(dmg * BLOCK_REDUCTION)
            if c_crouch:
                dmg = int(dmg * 0.5)
            c_hp -= dmg
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-1, 1)
            shake_timer = 3
            particles.emit(cx + FW // 2, cy + 20, count=8, speed=2,
                           colors=[0xFFE0, 0xFFFF, 0xF800], life=15)
            dmg_texts.append([cx + FW // 2, cy, str(dmg), 0xFFFF, 20])
        if p_kicking == 4 and dist < KICK_RANGE:
            dmg = random.randint(10, 20)
            if c_block:
                dmg = int(dmg * BLOCK_REDUCTION)
            if c_crouch:
                dmg = int(dmg * 0.5)
            c_hp -= dmg
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-2, 2)
            shake_timer = 3
            particles.emit(cx + FW // 2, cy + 30, count=8, speed=3,
                           colors=[0xFFE0, 0xFFFF, 0xF800], life=15)
            dmg_texts.append([cx + FW // 2, cy, str(dmg), 0xFFE0, 20])
        if p_special == 5 and dist < SPECIAL_RANGE:
            dmg = random.randint(15, 25)
            if c_block:
                dmg = int(dmg * BLOCK_REDUCTION)
            if c_crouch:
                dmg = int(dmg * 0.5)
            c_hp -= dmg
            shake_x = random.randint(-4, 4)
            shake_y = random.randint(-3, 3)
            shake_timer = 4
            particles.emit(cx + FW // 2, cy + 15, count=12, speed=4,
                           colors=[0x07FF, 0xFFFF, 0x87FF], life=20)
            dmg_texts.append([cx + FW // 2, cy, str(dmg), 0x07FF, 25])

        if c_punching == 3:
            c_dist = cx - px
            if c_dist < PUNCH_RANGE:
                dmg = random.randint(5, 10)
                if p_block:
                    dmg = int(dmg * BLOCK_REDUCTION)
                if p_crouch:
                    dmg = int(dmg * 0.5)
                p_hp -= dmg
                shake_x = random.randint(-2, 2)
                shake_y = random.randint(-1, 1)
                shake_timer = 3
                particles.emit(px + FW // 2, py + 20, count=8, speed=2,
                               colors=[0xFFE0, 0xFFFF, 0xF800], life=15)
                dmg_texts.append([px + FW // 2, py, str(dmg), 0xF800, 20])
        if c_kicking == 4:
            c_dist = cx - px
            if c_dist < KICK_RANGE:
                dmg = random.randint(10, 20)
                if p_block:
                    dmg = int(dmg * BLOCK_REDUCTION)
                if p_crouch:
                    dmg = int(dmg * 0.5)
                p_hp -= dmg
                shake_x = random.randint(-3, 3)
                shake_y = random.randint(-2, 2)
                shake_timer = 3
                particles.emit(px + FW // 2, py + 30, count=8, speed=3,
                               colors=[0xFFE0, 0xFFFF, 0xF800], life=15)
                dmg_texts.append([px + FW // 2, py, str(dmg), 0xF800, 20])
        if c_special == 5:
            c_dist = cx - px
            if c_dist < SPECIAL_RANGE:
                dmg = random.randint(15, 25)
                if p_block:
                    dmg = int(dmg * BLOCK_REDUCTION)
                if p_crouch:
                    dmg = int(dmg * 0.5)
                p_hp -= dmg
                shake_x = random.randint(-4, 4)
                shake_y = random.randint(-3, 3)
                shake_timer = 4
                particles.emit(px + FW // 2, py + 15, count=12, speed=4,
                               colors=[0xF800, 0xFFFF, 0xFF00], life=20)
                dmg_texts.append([px + FW // 2, py, str(dmg), 0xF800, 25])

        now = time.ticks_ms()
        if time.ticks_diff(now, last_tick) >= 1000:
            last_tick = now
            timer -= 1

        if shake_timer > 0:
            shake_timer -= 1
            if shake_timer == 0:
                shake_x = 0
                shake_y = 0

        for dt in dmg_texts:
            dt[1] -= 1
            dt[4] -= 1
        dmg_texts = [dt for dt in dmg_texts if dt[4] > 0]

        if p_hp <= 0 or c_hp <= 0 or timer <= 0:
            game_over = True
            if p_hp <= 0:
                result_msg = 'K.O.! CPU WINS!'
            elif c_hp <= 0:
                result_msg = 'K.O.! YOU WIN!'
            elif p_hp > c_hp:
                result_msg = 'TIME UP! YOU WIN!'
            elif c_hp > p_hp:
                result_msg = 'TIME UP! CPU WINS!'
            else:
                result_msg = 'TIME UP! DRAW!'

        update_display()
        particles.update(tft)
        for dt in dmg_texts:
            tft.text15(dt[2], dt[0], dt[1], dt[3], 0x0000)
        time.sleep_ms(30)

    _draw_game_header(tft, result_msg)
    tft.text(f'You: {max(0, p_hp)}  CPU: {max(0, c_hp)}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _dodge_game(tft, read_key):
    import time
    import random
    from lib.sprite import ParticleSystem

    W = 480
    H = 320
    PLAYER_W = 20
    PLAYER_H = 30
    player_x = W // 2
    player_y = H - 60
    player_vy = 0
    score = 0
    high_score = 0
    gravity = 0.5
    jump_power = -8
    on_ground = True
    enemies = []
    spawn_timer = 0
    spawn_rate = 60
    speed = 3
    particles = ParticleSystem(40)
    game_over = False
    difficulty_timer = 0

    GROUND_Y = H - 40
    LANE_COUNT = 5
    LANE_W = 80
    LANE_START = (W - LANE_COUNT * LANE_W) // 2

    def draw_player():
        x, y = int(player_x), int(player_y)
        tft.fill_rect(x, y, PLAYER_W, PLAYER_H, 0x07FF)
        tft.fill_rect(x + 4, y - 5, PLAYER_W - 8, 8, 0x07FF)
        tft.fill_rect(x + 6, y - 3, 3, 3, 0x0000)
        tft.fill_rect(x + PLAYER_W - 9, y - 3, 3, 3, 0x0000)
        if not on_ground:
            tft.fill_rect(x + 2, y + PLAYER_H, 5, 3, 0xFFE0)
            tft.fill_rect(x + PLAYER_W - 7, y + PLAYER_H, 5, 3, 0xFFE0)

    def clear_player():
        x, y = int(player_x), int(player_y)
        tft.fill_rect(x - 2, y - 6, PLAYER_W + 4, PLAYER_H + 8, 0x0000)

    def draw_enemy(e):
        ex, ey = int(e['x']), int(e['y'])
        color = e.get('color', 0xF800)
        tft.fill_rect(ex, ey, 16, 16, color)
        tft.fill_rect(ex + 3, ey + 2, 4, 4, 0x0000)
        tft.fill_rect(ex + 9, ey + 2, 4, 4, 0x0000)

    def clear_enemy(e):
        ex, ey = int(e['x']), int(e['y'])
        tft.fill_rect(ex - 1, ey - 1, 18, 18, 0x0000)

    def draw_ground():
        tft.fill_rect(0, GROUND_Y, W, H - GROUND_Y, 0x03E0)
        tft.hline(0, GROUND_Y, W, 0x07E0)

    def draw_bg():
        tft.fill_rect(0, 25, W, GROUND_Y - 25, 0x0000)
        for i in range(8):
            lx = LANE_START + i * LANE_W
            tft.vline(lx, 25, GROUND_Y - 25, 0x2104)

    def check_collision():
        px, py = int(player_x), int(player_y)
        for e in enemies:
            ex, ey = int(e['x']), int(e['y'])
            if (px < ex + 16 and px + PLAYER_W > ex and
                py < ey + 16 and py + PLAYER_H > ey):
                return True
        return False

    def spawn_enemy():
        lane = random.randint(0, LANE_COUNT - 1)
        ex = LANE_START + lane * LANE_W + LANE_W // 2 - 8
        colors = [0xF800, 0xFFE0, 0xFC1F, 0xA81F]
        enemies.append({
            'x': float(ex),
            'y': float(25),
            'vy': speed + random.random() * 2,
            'color': colors[random.randint(0, len(colors) - 1)]
        })

    _draw_game_header(tft, 'Dodge')
    draw_bg()
    draw_ground()
    draw_player()
    tft.text('Space=jump Q=quit', 4, 300, 0x07E0, 0x0000)

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == ' ' and on_ground:
            player_vy = jump_power
            on_ground = False

        player_vy += gravity
        old_y = int(player_y)
        player_y += player_vy
        new_y = int(player_y)

        if player_y >= GROUND_Y - PLAYER_H:
            player_y = GROUND_Y - PLAYER_H
            player_vy = 0
            on_ground = True
        if player_y < 25:
            player_y = 25
            player_vy = 0

        clear_player()
        draw_player()

        spawn_timer += 1
        difficulty_timer += 1
        if difficulty_timer > 300:
            speed = min(8, speed + 0.5)
            spawn_rate = max(20, spawn_rate - 2)
            difficulty_timer = 0

        if spawn_timer >= spawn_rate:
            spawn_enemy()
            spawn_timer = 0

        for e in enemies:
            clear_enemy(e)
        for e in enemies:
            e['y'] += e['vy']
        enemies[:] = [e for e in enemies if e['y'] < H + 20]
        for e in enemies:
            draw_enemy(e)

        if check_collision():
            particles.emit(int(player_x), int(player_y),
                          count=15, speed=4,
                          colors=[0xF800, 0xFFE0, 0x07FF, 0xFFFF], life=25)
            for _ in range(15):
                particles.update(tft, 0.1)
                time.sleep_ms(20)
            game_over = True
            break

        score += 1
        if score > high_score:
            high_score = score

        tft.fill_rect(0, 300, 480, 20, 0x0000)
        tft.text(f'Score: {score}  Best: {high_score}', 4, 300, 0xFFFF, 0x0000)
        tft.text('Space=jump Q=quit', 250, 300, 0x07E0, 0x0000)

        time.sleep_ms(20)

    try:
        from commands.dispatch import _buzzer
        _buzzer.game_over_sound()
    except:
        pass
    _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Score: {score}  Best: {high_score}', 4, 40, 0xFFE0, 0x0000)
    _show_highscore(tft, 'LIFE', score)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _sumo_game(tft, read_key):
    particles = ParticleSystem(30)
    W = 480
    H = 320
    CX = W // 2
    CY = H // 2 + 10
    RING_R = 100
    BODY_R = 14
    PUSH_DIST = 32
    PUSH_FORCE = 18
    FRICTION = 0.88

    px, py = float(CX - 60), float(CY)
    pvx, pvy = 0.0, 0.0
    cx, cy = float(CX + 60), float(CY)
    cvx, cvy = 0.0, 0.0

    p_pushes = 0
    c_pushes = 0
    timer = 60
    last_tick = time.ticks_ms()
    game_over = False
    result_msg = ''
    shake_x = 0
    shake_y = 0
    shake_timer = 0
    push_flash_p = 0
    push_flash_c = 0
    p_in_ring = True
    c_in_ring = True
    p_slide_x, p_slide_y = 0.0, 0.0
    c_slide_x, c_slide_y = 0.0, 0.0
    c_ai_timer = 0
    c_ai_dodge = 0

    def in_ring(x, y):
        dx = x - CX
        dy = y - CY
        return dx * dx + dy * dy <= RING_R * RING_R

    def draw_ring():
        tft.fill_rect(0, 25, W, H - 25, 0x0000)
        for angle_step in range(60):
            a = angle_step * 6.28318 / 60
            rx = int(CX + RING_R * math_cos(a))
            ry = int(CY + RING_R * math_sin(a))
            tft.fill_rect(rx - 1, ry - 1, 3, 3, 0xFFFF)
        for angle_step in range(30):
            a = angle_step * 6.28318 / 30
            ir = RING_R - 20
            rx = int(CX + ir * math_cos(a))
            ry = int(CY + ir * math_sin(a))
            tft.fill_rect(rx, ry, 2, 2, 0x4208)

    def draw_fighter(fx, fy, color, flash):
        ix, iy = int(fx), int(fy)
        if flash > 0:
            tft.fill_rect(ix - BODY_R - 2, iy - BODY_R - 2, BODY_R * 2 + 4, BODY_R * 2 + 4, 0xFFFF)
        tft.fill_rect(ix - BODY_R, iy - BODY_R, BODY_R * 2, BODY_R * 2, 0x0000)
        for dy in range(-BODY_R, BODY_R + 1):
            row_w = int((BODY_R * BODY_R - dy * dy) ** 0.5) * 2
            if row_w > 0:
                if dy < -4:
                    gc = color | 0x1084
                elif dy > 4:
                    gc = (max((color >> 11) - 6, 0) << 11) | (max(((color >> 5) & 0x3F) - 12, 0) << 5) | max((color & 0x1F) - 6, 0)
                else:
                    gc = color
                tft.fill_rect(ix - row_w // 2, iy + dy, row_w, 1, gc)
        tft.fill_rect(ix - 5, iy - 4, 4, 4, 0x0000)
        tft.fill_rect(ix + 2, iy - 4, 4, 4, 0x0000)
        tft.fill_rect(ix - 4, iy - 3, 2, 2, 0xFFFF)
        tft.fill_rect(ix + 3, iy - 3, 2, 2, 0xFFFF)

    def clear_fighter(fx, fy):
        ix, iy = int(fx), int(fy)
        tft.fill_rect(ix - BODY_R - 3, iy - BODY_R - 3, BODY_R * 2 + 6, BODY_R * 2 + 6, 0x0000)

    def update_display():
        draw_ring()
        draw_fighter(cx + shake_x, cy + shake_y, 0xF800, push_flash_c)
        draw_fighter(px + shake_x, py + shake_y, 0x001F, push_flash_p)

    draw_ring()
    draw_fighter(px, py, 0x001F, 0)
    draw_fighter(cx, cy, 0xF800, 0)
    tft.text('A/D=left/right W/S=up/down Q=quit', 4, 300, 0x07E0, 0x0000)

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return

        pmx, pmy = 0.0, 0.0
        if ch == 'a':
            pmx = -3
        elif ch == 'd':
            pmx = 3
        elif ch == 'w':
            pmy = -3
        elif ch == 's':
            pmy = 3

        if p_in_ring:
            pvx += pmx
            pvy += pmy
            pvx *= FRICTION
            pvy *= FRICTION
            old_px, old_py = px, py
            px += pvx
            py += pvy
            if not in_ring(px, py):
                px, py = old_px, old_py
                pvx, pvy = -pvx * 0.3, -pvy * 0.3
        else:
            px += p_slide_x
            py += p_slide_y
            p_slide_x *= 0.95
            p_slide_y *= 0.95

        c_ai_timer += 1
        if c_in_ring:
            to_cx = CX - cx
            to_cy = CY - cy
            dist_to_center = math_sqrt(to_cx * to_cx + to_cy * to_cy)
            if dist_to_center > 5:
                cvx += to_cx / dist_to_center * 0.5
                cvy += to_cy / dist_to_center * 0.5

            dx_to_p = px - cx
            dy_to_p = py - cy
            dist_to_p = math_sqrt(dx_to_p * dx_to_p + dy_to_p * dy_to_p)

            if c_ai_dodge > 0:
                c_ai_dodge -= 1
                if dist_to_p < 60:
                    perp_x = -dy_to_p
                    perp_y = dx_to_p
                    plen = math_sqrt(perp_x * perp_x + perp_y * perp_y)
                    if plen > 0:
                        cvx += perp_x / plen * 2
                        cvy += perp_y / plen * 2
            elif dist_to_p < PUSH_DIST and c_ai_timer % 20 == 0:
                if dist_to_p > 0:
                    cvx += dx_to_p / dist_to_p * 4
                    cvy += dy_to_p / dist_to_p * 4
            elif dist_to_p < 80 and random.random() < 0.02:
                c_ai_dodge = 15

            cvx *= FRICTION
            cvy *= FRICTION
            old_cx, old_cy = cx, cy
            cx += cvx
            cy += cvy
            if not in_ring(cx, cy):
                cx, cy = old_cx, old_cy
                cvx, cvy = -cvx * 0.3, -cvy * 0.3
        else:
            cx += c_slide_x
            cy += c_slide_y
            c_slide_x *= 0.95
            c_slide_y *= 0.95

        dx = px - cx
        dy = py - cy
        dist = math_sqrt(dx * dx + dy * dy)

        if dist < PUSH_DIST and dist > 0:
            nx = dx / dist
            ny = dy / dist
            if abs(pvx) + abs(pvy) > 1.5:
                cvx += nx * PUSH_FORCE
                cvy += ny * PUSH_FORCE
                push_flash_c = 5
                shake_x = random.randint(-3, 3)
                shake_y = random.randint(-2, 2)
                shake_timer = 4
                p_pushes += 1
                particles.emit(int(cx), int(cy), count=8, speed=3,
                               colors=[0xFFE0, 0xFFFF, 0x07FF], life=15)
                try:
                    _buzzer.beep(30)
                except Exception:
                    pass
            elif abs(cvx) + abs(cvy) > 1.5:
                pvx -= nx * PUSH_FORCE
                pvy -= ny * PUSH_FORCE
                push_flash_p = 5
                shake_x = random.randint(-3, 3)
                shake_y = random.randint(-2, 2)
                shake_timer = 4
                c_pushes += 1
                particles.emit(int(px), int(py), count=8, speed=3,
                               colors=[0xFFE0, 0xFFFF, 0xF800], life=15)
                try:
                    _buzzer.beep(30)
                except Exception:
                    pass

        p_in_ring = in_ring(px, py)
        c_in_ring = in_ring(cx, cy)

        if not p_in_ring and p_in_ring is not None:
            p_slide_x = pvx * 2
            p_slide_y = pvy * 2
        if not c_in_ring and c_in_ring is not None:
            c_slide_x = cvx * 2
            c_slide_y = cvy * 2

        now = time.ticks_ms()
        if time.ticks_diff(now, last_tick) >= 1000:
            last_tick = now
            timer -= 1

        if shake_timer > 0:
            shake_timer -= 1
            if shake_timer == 0:
                shake_x = 0
                shake_y = 0
        if push_flash_p > 0:
            push_flash_p -= 1
        if push_flash_c > 0:
            push_flash_c -= 1

        if timer <= 0:
            game_over = True
            if p_pushes > c_pushes:
                result_msg = 'YOU WIN!'
            elif c_pushes > p_pushes:
                result_msg = 'CPU WINS!'
            else:
                result_msg = 'DRAW!'
        elif not p_in_ring and px < -50 or px > W + 50 or py < -50 or py > H + 50:
            game_over = True
            result_msg = 'K.O.! CPU WINS!'
        elif not c_in_ring and cx < -50 or cx > W + 50 or cy < -50 or cy > H + 50:
            game_over = True
            result_msg = 'K.O.! YOU WIN!'

        if not game_over:
            update_display()
            particles.update(tft)
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15(f'YOU:{p_pushes}  CPU:{c_pushes}  {timer}s', 140, 4, 0x07FF, 0x1082)
            time.sleep_ms(30)

    _draw_game_header(tft, result_msg)
    tft.text(f'Pushes - You: {p_pushes}  CPU: {c_pushes}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _archery_game(tft, read_key):
    if not _select_difficulty(tft, 'Archery'):
        return
    d = _diff()

    W = 480
    H = 320
    HEADER_H = 25

    launcher_x = 20
    launcher_y = H // 2
    launcher_speed = 4 * d['speed']

    target_x = W - 60
    target_y = H // 2
    target_vy = 2.0 * d['speed']
    target_radius = 30
    target_bounce_dir = 1

    arrow_x = 0.0
    arrow_y = 0.0
    arrow_vx = 12 * d['speed']
    arrow_active = False
    arrows_left = 10

    score = 0
    particles = ParticleSystem(40)
    stuck_arrows = []

    def draw_background():
        tft.fill_rect(0, HEADER_H, W, H - HEADER_H, 0x0000)
        tft.hline(0, H - 30, W, 0x03E0)
        tft.fill_rect(0, H - 30, W, 30, 0x0280)

    def draw_target():
        tx, ty = int(target_x), int(target_y)
        tft.fill_rect(tx - target_radius - 2, ty - target_radius - 2,
                      target_radius * 2 + 4, target_radius * 2 + 4, 0x0000)
        rings = [
            (target_radius, 0xFFFF),
            (target_radius - 6, 0xF800),
            (target_radius - 12, 0xFFFF),
            (target_radius - 18, 0xF800),
            (8, 0xFFE0),
        ]
        for r, c in rings:
            for dy in range(-r, r + 1):
                dx = int(math_sqrt(max(0, r * r - dy * dy)))
                if dx > 0:
                    tft.hline(tx - dx, ty + dy, dx * 2, c)

    def clear_target():
        tx, ty = int(target_x), int(target_y)
        tft.fill_rect(tx - target_radius - 2, ty - target_radius - 2,
                      target_radius * 2 + 4, target_radius * 2 + 4, 0x0000)

    def draw_launcher():
        ly = int(launcher_y)
        tft.fill_rect(launcher_x - 5, ly - 15, 10, 30, 0x4208)
        tft.fill_rect(launcher_x, ly - 3, 20, 6, 0x07FF)
        tft.fill_rect(launcher_x + 18, ly - 1, 4, 2, 0xFFE0)

    def clear_launcher():
        ly = int(launcher_y)
        tft.fill_rect(launcher_x - 7, ly - 17, 26, 34, 0x0000)

    def draw_arrow():
        if arrow_active:
            ax, ay = int(arrow_x), int(arrow_y)
            tft.fill_rect(ax - 12, ay - 1, 12, 2, 0xFFE0)
            tft.fill_rect(ax, ay - 2, 4, 4, 0xF800)
            tft.fill_rect(ax - 14, ay - 3, 3, 2, 0x07FF)
            tft.fill_rect(ax - 14, ay + 1, 3, 2, 0x07FF)

    def clear_arrow():
        if arrow_active:
            ax, ay = int(arrow_x), int(arrow_y)
            tft.fill_rect(ax - 16, ay - 5, 20, 10, 0x0000)

    def draw_stuck():
        for sa in stuck_arrows:
            tft.fill_rect(sa['x'] - 12, sa['y'] - 1, 12, 2, 0x8410)
            tft.fill_rect(sa['x'], sa['y'] - 2, 4, 4, 0x8410)

    def draw_hud():
        tft.fill_rect(0, HEADER_H, W, 16, 0x1082)
        tft.text(f'Score: {score}', 4, HEADER_H + 2, 0xFFFF, 0x1082)
        tft.text(f'Arrows: {arrows_left}', 200, HEADER_H + 2, 0xFFE0, 0x1082)
        tft.text('W/S aim  Space fire  Q quit', 300, HEADER_H + 2, 0x07E0, 0x1082)

    def check_hit():
        dx = arrow_x - target_x
        dy = arrow_y - target_y
        dist = math_sqrt(dx * dx + dy * dy)
        if dist <= target_radius:
            if dist <= 8:
                return 30
            elif dist <= 18:
                return 20
            else:
                return 10
        return 0

    draw_background()
    draw_hud()
    draw_launcher()
    draw_target()

    game_over = False

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return
        if ch == 'w' or ch == 'W':
            clear_launcher()
            launcher_y = max(HEADER_H + 20, launcher_y - launcher_speed)
            draw_launcher()
        if ch == 's' or ch == 'S':
            clear_launcher()
            launcher_y = min(H - 50, launcher_y + launcher_speed)
            draw_launcher()
        if ch == ' ' and not arrow_active and arrows_left > 0:
            arrow_x = float(launcher_x + 20)
            arrow_y = float(launcher_y)
            arrow_active = True
            arrows_left -= 1
            try:
                _buzzer.beep(50)
            except:
                pass

        clear_target()
        target_y += target_vy * target_bounce_dir
        if target_y >= H - 30 - target_radius:
            target_bounce_dir = -1
        if target_y <= HEADER_H + target_radius + 5:
            target_bounce_dir = 1
        draw_target()

        if arrow_active:
            clear_arrow()
            arrow_x += arrow_vx
            draw_arrow()

            hit_score = check_hit()
            if hit_score > 0:
                score += hit_score
                arrow_active = False
                particles.emit(int(target_x), int(target_y),
                               count=20, speed=5,
                               colors=[0xF800, 0xFFE0, 0x07FF, 0xFFFF], life=30)
                for _ in range(10):
                    particles.update(tft, 0.1)
                    time.sleep_ms(15)
                clear_target()
                tft.fill_rect(int(target_x) - target_radius, int(target_y) - target_radius,
                              target_radius * 2, target_radius * 2, 0xFFFF)
                time.sleep_ms(100)
                draw_target()
                target_vy += 0.3 * d['speed']
                try:
                    _buzzer.beep(100)
                except:
                    pass
            elif arrow_x > W:
                arrow_active = False
                stuck_arrows.append({'x': W - 5, 'y': int(arrow_y)})
                if len(stuck_arrows) > 5:
                    stuck_arrows.pop(0)
                draw_stuck()

        draw_hud()

        if arrows_left <= 0 and not arrow_active:
            game_over = True

        time.sleep_ms(int(20 * d['sleep']))

    try:
        _buzzer.game_over_sound()
    except:
        pass
    _draw_game_header(tft, 'GAME OVER')
    tft.text(f'Score: {score}', 4, 40, 0xFFE0, 0x0000)
    _show_highscore(tft, 'TYPING', score)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _tag_game(tft, read_key):
    import time
    import random
    from lib.sprite import ParticleSystem

    W = 480
    H = 320
    PLAYER_R = 12
    CPU_R = 12
    player_x = 100.0
    player_y = 160.0
    cpu_x = 380.0
    cpu_y = 160.0
    player_speed = 4
    cpu_speed = 3
    score = 0
    high_score = 0
    tagged = False
    tag_timer = 0
    tag_duration = 120
    particles = ParticleSystem(30)
    game_over = False
    timer = 1800
    cpu_vx = 0
    cpu_vy = 0
    cpu_target_x = 380.0
    cpu_target_y = 160.0

    def draw_player():
        x, y = int(player_x), int(player_y)
        color = 0x07FF if not tagged else 0xFFE0
        tft.fill_rect(x - PLAYER_R, y - PLAYER_R, PLAYER_R * 2, PLAYER_R * 2, color)
        tft.fill_rect(x - 3, y - 8, 6, 6, color)
        tft.fill_rect(x - 2, y - 6, 2, 2, 0x0000)
        tft.fill_rect(x + 2, y - 6, 2, 2, 0x0000)

    def clear_player():
        x, y = int(player_x), int(player_y)
        tft.fill_rect(x - PLAYER_R - 2, y - PLAYER_R - 10, PLAYER_R * 2 + 4, PLAYER_R * 2 + 12, 0x0000)

    def draw_cpu():
        x, y = int(cpu_x), int(cpu_y)
        color = 0xF800 if tagged else 0x07E0
        tft.fill_rect(x - CPU_R, y - CPU_R, CPU_R * 2, CPU_R * 2, color)
        tft.fill_rect(x - 3, y - 8, 6, 6, color)
        tft.fill_rect(x - 2, y - 6, 2, 2, 0x0000)
        tft.fill_rect(x + 2, y - 6, 2, 2, 0x0000)

    def clear_cpu():
        x, y = int(cpu_x), int(cpu_y)
        tft.fill_rect(x - CPU_R - 2, y - CPU_R - 10, CPU_R * 2 + 4, CPU_R * 2 + 12, 0x0000)

    def draw_arena():
        tft.fill_rect(0, 25, W, H - 25, 0x0000)
        tft.rect(10, 35, W - 20, H - 50, 0x4208)
        tft.rect(12, 37, W - 24, H - 54, 0x2104)

    def draw_status():
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        t = timer // 60
        s = timer % 60
        state = 'TAGGED!' if tagged else 'You are IT!'
        tft.text15(f'{state}  {t:02d}:{s:02d}  Score: {score}', 4, 4, 0xFFFF, 0x1082)

    def check_tag():
        dx = player_x - cpu_x
        dy = player_y - cpu_y
        dist = (dx * dx + dy * dy) ** 0.5
        return dist < PLAYER_R + CPU_R

    _draw_game_header(tft, 'Tag')
    draw_arena()
    draw_player()
    draw_cpu()
    draw_status()
    tft.text('WASD=move Q=quit', 4, 300, 0x07E0, 0x0000)

    while not game_over:
        ch = _poll_key()
        if ch == 'q' or ch == 'Q':
            return

        dx, dy = 0, 0
        if ch == 'w':
            dy = -player_speed
        if ch == 's':
            dy = player_speed
        if ch == 'a':
            dx = -player_speed
        if ch == 'd':
            dx = player_speed

        old_px, old_py = player_x, player_y
        player_x = max(14, min(W - 14, player_x + dx))
        player_y = max(37, min(H - 14, player_y + dy))

        if tagged:
            tag_timer -= 1
            if tag_timer <= 0:
                tagged = False
                score += 1
                cpu_speed = min(6, cpu_speed + 0.3)
                try:
                    from commands.dispatch import _buzzer
                    _buzzer.score_beep()
                except:
                    pass

        dx_cpu = cpu_target_x - cpu_x
        dy_cpu = cpu_target_y - cpu_y
        dist = (dx_cpu * dx_cpu + dy_cpu * cpu_y ** 0.5) if False else (dx_cpu ** 2 + dy_cpu ** 2) ** 0.5
        if dist > 5:
            cpu_x += (dx_cpu / dist) * cpu_speed
            cpu_y += (dy_cpu / dist) * cpu_speed
        else:
            if tagged:
                cpu_target_x = random.randint(20, W - 20)
                cpu_target_y = random.randint(45, H - 20)
            else:
                flee_dx = player_x - cpu_x
                flee_dy = player_y - cpu_y
                flee_dist = (flee_dx ** 2 + flee_dy ** 2) ** 0.5
                if flee_dist < 150:
                    cpu_target_x = cpu_x - flee_dx * 2
                    cpu_target_y = cpu_y - flee_dy * 2
                else:
                    cpu_target_x = cpu_x + random.randint(-50, 50)
                    cpu_target_y = cpu_y + random.randint(-50, 50)
            cpu_target_x = max(20, min(W - 20, cpu_target_x))
            cpu_target_y = max(45, min(H - 20, cpu_target_y))

        cpu_x = max(14, min(W - 14, cpu_x))
        cpu_y = max(37, min(H - 14, cpu_y))

        clear_player()
        clear_cpu()
        draw_player()
        draw_cpu()

        if not tagged and check_tag():
            tagged = True
            tag_timer = tag_duration
            particles.emit(int(cpu_x), int(cpu_y),
                          count=10, speed=3,
                          colors=[0xFFE0, 0xF800, 0x07FF], life=20)
            try:
                from commands.dispatch import _buzzer
                _buzzer.beep(50)
            except:
                pass

        particles.update(tft, 0.05)

        timer -= 1
        if timer <= 0:
            game_over = True
            break

        draw_status()
        time.sleep_ms(30)

    try:
        from commands.dispatch import _buzzer
        _buzzer.game_over_sound()
    except:
        pass
    if score > high_score:
        high_score = score
    _draw_game_header(tft, 'TIME UP!')
    tft.text(f'Score: {score}  Best: {high_score}', 4, 40, 0xFFE0, 0x0000)
    tft.text('Press any key to return', 4, 290, 0x07E0, 0x0000)
    read_key()


def _3d_game(tft, read_key):
    import math

    def rotate_point(x, y, z, ax, ay):
        cos_a = math.cos(ax)
        sin_a = math.sin(ax)
        y1 = y * cos_a - z * sin_a
        z1 = y * sin_a + z * cos_a
        cos_b = math.cos(ay)
        sin_b = math.sin(ay)
        x1 = x * cos_b + z1 * sin_b
        z2 = -x * sin_b + z1 * cos_b
        return x1, y1, z2

    def project(x, y, z, fov=400):
        scale = fov / (fov + z)
        return int(x * scale + 240), int(y * scale + 160)

    def bresenham_line(x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        steps = dx + dy
        if steps > 500:
            return
        for _ in range(steps + 1):
            if 0 <= x0 < 480 and 0 <= y0 < 320:
                tft.pixel(x0, y0, color)
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_triangle(x0, y0, x1, y1, x2, y2, color):
        verts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda v: v[1])
        vx0, vy0 = verts[0]
        vx1, vy1 = verts[1]
        vx2, vy2 = verts[2]
        if vy0 == vy2:
            return
        for y in range(max(0, vy0), min(320, vy2 + 1)):
            xa = vx0 + (y - vy0) * (vx2 - vx0) // (vy2 - vy0) if vy2 != vy0 else vx0
            if y < vy1:
                xb = vx0 + (y - vy0) * (vx1 - vx0) // (vy1 - vy0) if vy1 != vy0 else vx0
            else:
                xb = vx1 + (y - vy1) * (vx2 - vx1) // (vy2 - vy1) if vy2 != vy1 else vx1
            if xa > xb:
                xa, xb = xb, xa
            xa = max(0, min(479, xa))
            xb = max(0, min(479, xb))
            if xa <= xb:
                tft.hline(xa, y, xb - xa + 1, color)

    shapes = ['cube', 'pyramid', 'sphere', 'torus']
    shape_idx = 0
    ang_x = 0.0
    ang_y = 0.0
    filled = False

    def get_shape(name):
        if name == 'cube':
            verts = [
                (-80, -80, -80), (80, -80, -80), (80, 80, -80), (-80, 80, -80),
                (-80, -80, 80), (80, -80, 80), (80, 80, 80), (-80, 80, 80),
            ]
            edges = [
                (0,1),(1,2),(2,3),(3,0),
                (4,5),(5,6),(6,7),(7,4),
                (0,4),(1,5),(2,6),(3,7),
            ]
            faces = [
                (0,1,2,3),(4,5,6,7),(0,1,5,4),
                (2,3,7,6),(0,3,7,4),(1,2,6,5),
            ]
            return verts, edges, faces
        elif name == 'pyramid':
            verts = [
                (0, -100, 0),
                (-80, 60, -80), (80, 60, -80), (80, 60, 80), (-80, 60, 80),
            ]
            edges = [
                (0,1),(0,2),(0,3),(0,4),
                (1,2),(2,3),(3,4),(4,1),
            ]
            faces = [
                (0,1,2),(0,2,3),(0,3,4),(0,4,1),(1,2,3,4),
            ]
            return verts, edges, faces
        elif name == 'sphere':
            verts = [(0, -100, 0), (0, 100, 0)]
            edges = []
            rings = 8
            segs = 12
            for i in range(1, rings):
                phi = 3.14159 * i / rings
                for j in range(segs):
                    theta = 6.28318 * j / segs
                    x = int(90 * math.sin(phi) * math.cos(theta))
                    y = int(90 * math.cos(phi))
                    z = int(90 * math.sin(phi) * math.sin(theta))
                    verts.append((x, y, z))
            for j in range(segs):
                edges.append((0, 2 + j))
                edges.append((1, 2 + (rings - 2) * segs + j))
            for i in range(rings - 1):
                for j in range(segs):
                    idx = 2 + i * segs + j
                    idx_next = 2 + i * segs + (j + 1) % segs
                    edges.append((idx, idx_next))
                    if i < rings - 2:
                        below = 2 + (i + 1) * segs + j
                        edges.append((idx, below))
            faces = []
            return verts, edges, faces
        elif name == 'torus':
            verts = []
            edges = []
            faces = []
            R = 80
            r = 35
            tube_segs = 12
            ring_segs = 16
            for i in range(ring_segs):
                theta = 6.28318 * i / ring_segs
                for j in range(tube_segs):
                    phi = 6.28318 * j / tube_segs
                    x = int((R + r * math.cos(phi)) * math.cos(theta))
                    y = int(r * math.sin(phi))
                    z = int((R + r * math.cos(phi)) * math.sin(theta))
                    verts.append((x, y, z))
            for i in range(ring_segs):
                for j in range(tube_segs):
                    idx = i * tube_segs + j
                    next_j = i * tube_segs + (j + 1) % tube_segs
                    next_i = ((i + 1) % ring_segs) * tube_segs + j
                    edges.append((idx, next_j))
                    edges.append((idx, next_i))
            return verts, edges, faces
        return [], [], []

    def draw():
        tft.fill_rect(0, 25, 480, 295, 0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15(f'3D - {shapes[shape_idx].upper()}', 170, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        verts, edges, faces = get_shape(shapes[shape_idx])
        projected = []
        for v in verts:
            rx, ry, rz = rotate_point(v[0], v[1], v[2], ang_x, ang_y)
            px, py = project(rx, ry, rz)
            projected.append((px, py, rz))
        if filled and faces:
            face_data = []
            for face in faces:
                pts = [projected[i] for i in face]
                avg_z = sum(p[2] for p in pts) / len(pts)
                face_data.append((avg_z, pts))
            face_data.sort(key=lambda f: f[0], reverse=True)
            face_colors = [0x0400, 0x0500, 0x0600, 0x0700, 0x0300, 0x0200]
            for fi, (az, pts) in enumerate(face_data):
                col = face_colors[fi % len(face_colors)]
                for k in range(len(pts) - 2):
                    fill_triangle(
                        pts[0][0], pts[0][1],
                        pts[k + 1][0], pts[k + 1][1],
                        pts[k + 2][0], pts[k + 2][1],
                        col,
                    )
        for i, j in edges:
            if i < len(projected) and j < len(projected):
                x0, y0, _ = projected[i]
                x1, y1, _ = projected[j]
                bresenham_line(x0, y0, x1, y1, 0xFFFF)
        for px, py, _ in projected:
            if 0 <= px < 480 and 0 <= py < 320:
                tft.pixel(px, py, 0xFFE0)
        mode_txt = 'FILL' if filled else 'WIRE'
        tft.text15(f'X:{int(math.degrees(ang_x) % 360):3d}  Y:{int(math.degrees(ang_y) % 360):3d}  [{mode_txt}]', 4, 302, 0x8410, 0x0000)
        tft.text('Arrows=rot 1-4=shape Space=mode Q=quit', 4, 290, 0x07E0, 0x0000)

    _draw_game_header(tft, '3D Wireframe')
    draw()

    while True:
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        elif ch == '\x80':
            ang_x -= 0.15
        elif ch == '\x81':
            ang_x += 0.15
        elif ch == '\x82':
            ang_y -= 0.15
        elif ch == '\x83':
            ang_y += 0.15
        elif ch == '1':
            shape_idx = 0
        elif ch == '2':
            shape_idx = 1
        elif ch == '3':
            shape_idx = 2
        elif ch == '4':
            shape_idx = 3
        elif ch == ' ':
            filled = not filled
        else:
            continue
        draw()


def _maze_game_cpu(tft, read_key):
    import time
    import random

    COLS, ROWS = 12, 8
    CELL_W, CELL_H = 36, 30
    OX = (480 - COLS * CELL_W) // 2
    OY = 30
    walls = [[[True, True, True, True] for _ in range(COLS)] for _ in range(ROWS)]
    visited_maze = [[False] * COLS for _ in range(ROWS)]

    stack = [(0, 0)]
    visited_maze[0][0] = True
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    wall_idx = [(0, 2), (1, 3), (2, 0), (3, 1)]

    while stack:
        cx_m, cy_m = stack[-1]
        neighbors = []
        for i, (dx, dy) in enumerate(dirs):
            nx, ny = cx_m + dx, cy_m + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and not visited_maze[ny][nx]:
                neighbors.append((nx, ny, i))
        if neighbors:
            nx, ny, di = random.choice(neighbors)
            walls[cy_m][cx_m][di] = False
            walls[ny][nx][wall_idx[di][0]][wall_idx[di][1]] = False
            visited_maze[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()

    player_r, player_c = 0, 0
    cpu_r, cpu_c = COLS - 1, ROWS - 1
    p_hp, c_hp = 100, 100
    player_px = OX + player_c * CELL_W + CELL_W // 2
    player_py = OY + player_r * CELL_H + CELL_H // 2
    cpu_px = OX + cpu_c * CELL_W + CELL_W // 2
    cpu_py = OY + cpu_r * CELL_H + CELL_H // 2
    timer = 1200
    p_vis = set()
    c_vis = set()

    def draw():
        tft.fill_rect(0, 25, 480, 295, 0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        t = timer // 10
        tft.text15(f'You:{p_hp} CPU:{c_hp} {t//60}:{t%60:02d}', 4, 4, 0xFFFF, 0x1082)
        for r in range(ROWS):
            for c in range(COLS):
                x = OX + c * CELL_W
                y = OY + r * CELL_H
                if (c, r) in p_vis:
                    tft.fill_rect(x + 1, y + 1, CELL_W - 2, CELL_H - 2, 0x0420)
                if (c, r) in c_vis:
                    tft.fill_rect(x + 1, y + 1, CELL_W - 2, CELL_H - 2, 0x4200)
                if walls[r][c][0]:
                    tft.hline(x, y, CELL_W, 0xFFFF)
                if walls[r][c][1]:
                    tft.vline(x + CELL_W, y, CELL_H, 0xFFFF)
                if walls[r][c][2]:
                    tft.hline(x, y + CELL_H, CELL_W, 0xFFFF)
                if walls[r][c][3]:
                    tft.vline(x, y, CELL_H, 0xFFFF)
        tft.fill_rect(OX + cpu_c * CELL_W + 10, OY + cpu_r * CELL_H + 8, 16, 16, 0xF800)
        tft.fill_rect(player_px - 6, player_py - 6, 12, 12, 0x07FF)
        tft.text('WASD=move Q=quit', 4, 300, 0x07E0, 0x0000)

    def can_move(r, c, di):
        return not walls[r][c][di]

    def cpu_move():
        nonlocal cpu_r, cpu_c
        best_dir = None
        best_dist = 9999
        for i, (dx, dy) in enumerate(dirs):
            nr, nc = cpu_r + dx, cpu_c + dy
            if 0 <= nr < ROWS and 0 <= nc < COLS and can_move(cpu_r, cpu_c, i):
                dist = abs(nc - 0) + abs(nr - 0)
                if dist < best_dist:
                    best_dist = dist
                    best_dir = i
        if best_dir is not None:
            dx, dy = dirs[best_dir]
            cpu_r += dy
            cpu_c += dx
            c_vis.add((cpu_c, cpu_r))

    draw()
    while True:
        ch = _poll_key()
        if ch in ('q', 'Q', '\x1b', '\x03'):
            return
        moved = False
        if ch == 'w' and can_move(player_r, player_c, 0):
            player_r -= 1
            moved = True
        elif ch == 'd' and can_move(player_r, player_c, 1):
            player_c += 1
            moved = True
        elif ch == 's' and can_move(player_r, player_c, 2):
            player_r += 1
            moved = True
        elif ch == 'a' and can_move(player_r, player_c, 3):
            player_c -= 1
            moved = True

        if moved:
            player_px = OX + player_c * CELL_W + CELL_W // 2
            player_py = OY + player_r * CELL_H + CELL_H // 2
            p_vis.add((player_c, player_r))

        cpu_move()

        if player_r == cpu_r and player_c == cpu_c:
            if p_hp > c_hp:
                c_hp -= 10
            else:
                p_hp -= 10

        if player_r == ROWS - 1 and player_c == COLS - 1:
            _draw_game_header(tft, 'YOU WIN!')
            tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
            read_key()
            return
        if cpu_r == 0 and cpu_c == 0:
            _draw_game_header(tft, 'CPU WINS!')
            tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
            read_key()
            return

        timer -= 1
        if timer <= 0 or p_hp <= 0 or c_hp <= 0:
            winner = 'YOU WIN!' if p_hp > c_hp else 'CPU WINS!' if c_hp > p_hp else 'DRAW!'
            _draw_game_header(tft, f'TIME UP! {winner}')
            tft.text('Press any key', 4, 290, 0x07E0, 0x0000)
            read_key()
            return

        draw()
        time.sleep_ms(80)


def cmd_stopwatch(args, oled_ctrl=None):
    if not oled_ctrl:
        return ('print', 'stopwatch: display not available')
    return ('stopwatch',)
