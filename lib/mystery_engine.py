"""Mystery Game (?) - Random mini-game each time."""

import time
import random


def _guess_number(tft, read_key):
    """Guess the number 1-100."""
    target = random.randint(1, 100)
    guess = ''
    attempts = 0
    msg = 'Guess 1-100'

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('MYSTERY: GUESS NUMBER', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        y = 40
        tft.text15(msg, 4, y, 0xFFFF, 0x0000)
        y += 20
        tft.text15(f'Attempt: {attempts}', 4, y, 0x8410, 0x0000)
        y += 20
        tft.text15(f'Guess: {guess or "_"}', 4, y, 0xFFE0, 0x0000)
        y += 24
        tft.text15('Type number  Enter=submit  Q=quit', 4, 304, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            time.sleep_ms(50)
            continue
        if ch in ('q', 'Q', chr(24), chr(27)):
            return
        if ch == chr(127) or ch == chr(8):
            if guess:
                guess = guess[:-1]
                _render()
        elif ch == chr(10):
            if guess:
                try:
                    g = int(guess)
                    attempts += 1
                    if g == target:
                        msg = f'WIN! It was {target} ({attempts} attempts)'
                        _render()
                        time.sleep_ms(2000)
                        return
                    elif g < target:
                        msg = f'{g} is too LOW'
                    else:
                        msg = f'{g} is too HIGH'
                    guess = ''
                    _render()
                except:
                    msg = 'Enter a valid number'
                    _render()
        elif len(ch) == 1 and ch.isdigit():
            if len(guess) < 3:
                guess += ch
                _render()


def _rps(tft, read_key):
    """Rock Paper Scissors vs CPU."""
    choices = ['rock', 'paper', 'scissors']
    sel = 0
    wins = 0
    losses = 0
    ties = 0
    msg = 'Choose your weapon'
    cpu_choice = None

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('MYSTERY: ROCK PAPER SCISSORS', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        y = 40
        tft.text15(f'W:{wins} L:{losses} T:{ties}', 4, y, 0xFFE0, 0x0000)
        y += 24

        for i, c in enumerate(choices):
            color = 0x07E0 if i == sel else 0x8410
            prefix = '> ' if i == sel else '  '
            tft.text15(prefix + c.upper(), 4, y, color, 0x0000)
            y += 20

        y += 10
        tft.text15(msg, 4, y, 0xFFFF, 0x0000)
        if cpu_choice:
            tft.text15(f'CPU chose: {cpu_choice.upper()}', 4, y + 20, 0xF800, 0x0000)

        tft.text15('Up/Down: select  Enter: play  Q: quit', 4, 304, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            time.sleep_ms(50)
            continue
        if ch in ('q', 'Q', chr(24), chr(27)):
            return
        if ch == '\x80':  # Up
            sel = (sel - 1) % 3
            _render()
        elif ch == '\x81':  # Down
            sel = (sel + 1) % 3
            _render()
        elif ch == chr(10):  # Enter
            player = choices[sel]
            cpu_choice = random.choice(choices)

            if player == cpu_choice:
                ties += 1
                msg = 'TIE!'
            elif (player == 'rock' and cpu_choice == 'scissors') or \
                 (player == 'paper' and cpu_choice == 'rock') or \
                 (player == 'scissors' and cpu_choice == 'paper'):
                wins += 1
                msg = 'YOU WIN!'
            else:
                losses += 1
                msg = 'YOU LOSE!'
            _render()
            time.sleep_ms(1000)
            msg = 'Choose your weapon'
            cpu_choice = None
            _render()


def _coin_flip(tft, read_key):
    """Coin flip prediction game."""
    score = 0
    attempts = 0
    msg = 'Heads or Tails?'
    result = None
    sel = 0  # 0=heads, 1=tails

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('MYSTERY: COIN FLIP', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        y = 40
        tft.text15(f'Score: {score}/{attempts}', 4, y, 0xFFE0, 0x0000)
        y += 24

        options = ['HEADS', 'TAILS']
        for i, opt in enumerate(options):
            color = 0x07E0 if i == sel else 0x8410
            prefix = '> ' if i == sel else '  '
            tft.text15(prefix + opt, 4, y, color, 0x0000)
            y += 20

        y += 10
        tft.text15(msg, 4, y, 0xFFFF, 0x0000)
        if result:
            tft.text15(f'Result: {result.upper()}', 4, y + 20, 0xF800, 0x0000)

        tft.text15('Up/Down: select  Enter: flip  Q: quit', 4, 304, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            time.sleep_ms(50)
            continue
        if ch in ('q', 'Q', chr(24), chr(27)):
            return
        if ch == '\x80':  # Up
            sel = 0
            _render()
        elif ch == '\x81':  # Down
            sel = 1
            _render()
        elif ch == chr(10):  # Enter
            attempts += 1
            choice = 'heads' if sel == 0 else 'tails'
            result = random.choice(['heads', 'tails'])
            if choice == result:
                score += 1
                if _oled: _oled.set_mode('game_hud', score=score, game_name='MYSTERY')
                msg = 'CORRECT!'
            else:
                msg = 'WRONG!'
            _render()
            time.sleep_ms(1000)
            msg = 'Heads or Tails?'
            result = None
            _render()


def _dice_roll(tft, read_key):
    """Dice roll prediction game."""
    score = 0
    if _oled: _oled.set_mode('game_hud', score=score, game_name='MYSTERY')
    attempts = 0
    msg = 'Guess the roll (1-6)'
    result = None
    guess = 1

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('MYSTERY: DICE ROLL', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        y = 40
        tft.text15(f'Score: {score}/{attempts}', 4, y, 0xFFE0, 0x0000)
        y += 24

        tft.text15(f'Guess: {guess}', 4, y, 0xFFE0, 0x0000)
        y += 24

        tft.text15(msg, 4, y, 0xFFFF, 0x0000)
        if result is not None:
            tft.text15(f'Rolled: {result}', 4, y + 20, 0xF800, 0x0000)

        tft.text15('Up/Down: change  Enter: roll  Q: quit', 4, 304, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            time.sleep_ms(50)
            continue
        if ch in ('q', 'Q', chr(24), chr(27)):
            return
        if ch == '\x80':  # Up
            guess = min(6, guess + 1)
            _render()
        elif ch == '\x81':  # Down
            guess = max(1, guess - 1)
            _render()
        elif ch == chr(10):  # Enter
            attempts += 1
            result = random.randint(1, 6)
            if guess == result:
                score += 1
                if _oled: _oled.set_mode('game_hud', score=score, game_name='MYSTERY')
                msg = 'CORRECT!'
            else:
                msg = 'WRONG!'
            _render()
            time.sleep_ms(1000)
            msg = 'Guess the roll (1-6)'
            result = None
            _render()


def mystery_loop(tft, read_key):
    """Random mini-game each time."""
    games = [_guess_number, _rps, _coin_flip, _dice_roll]
    game = random.choice(games)
    game(tft, read_key)
