"""Password Game - Progressive password rules."""

import time
import random


def _check_rules(password, current_stage):
    """Check which rules are satisfied."""
    rules = []
    p = password

    # Stage 1: Minimum length
    if current_stage >= 1:
        rules.append(('Length >= 8', len(p) >= 8))

    # Stage 2: Uppercase
    if current_stage >= 2:
        rules.append(('Has uppercase', any(c.isupper() for c in p)))

    # Stage 3: Number
    if current_stage >= 3:
        rules.append(('Has number', any(c.isdigit() for c in p)))

    # Stage 4: Special char
    if current_stage >= 4:
        rules.append(('Has special', any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in p)))

    # Stage 5: No spaces
    if current_stage >= 5:
        rules.append(('No spaces', ' ' not in p))

    # Stage 6: Contains "password"
    if current_stage >= 6:
        rules.append(('Contains "password"', 'password' in p.lower()))

    # Stage 7: Sum of digits = 25
    if current_stage >= 7:
        digits = [int(c) for c in p if c.isdigit()]
        total = sum(digits) if digits else 0
        rules.append((f'Digit sum = 25 (now {total})', total == 25))

    # Stage 8: Prime number length
    if current_stage >= 8:
        n = len(p)
        is_prime = n >= 2 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))
        rules.append(('Prime length', is_prime))

    # Stage 9: Contains month name
    if current_stage >= 9:
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        has_month = any(m in p.lower() for m in months)
        rules.append(('Contains month', has_month))

    # Stage 10: Roman numeral
    if current_stage >= 10:
        import re
        has_roman = bool(re.search(r'[IVXLCDM]+', p))
        rules.append(('Has Roman numeral', has_roman))

    return rules


def password_loop(tft, read_key):
    """Password game with progressive rules."""
    password = ''
    stage = 1
    max_stage = 10
    cursor_visible = True
    last_blink = time.time()

    def _render():
        nonlocal cursor_visible
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('PASSWORD GAME', 150, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        y = 30
        tft.text15(f'Stage {stage}/{max_stage}', 4, y, 0xFFE0, 0x0000)
        y += 20

        # Password input
        display = password if len(password) <= 40 else '...' + password[-37:]
        if cursor_visible:
            display += '_'
        tft.fill_rect(4, y, 472, 20, 0x1082)
        tft.text15(display, 8, y + 2, 0xFFFF, 0x1082)
        y += 24

        # Rules
        rules = _check_rules(password, stage)
        for rule_name, satisfied in rules:
            color = 0x07E0 if satisfied else 0xF800
            mark = '✓' if satisfied else '✗'
            tft.text15(f'{mark} {rule_name}', 4, y, color, 0x0000)
            y += 16

        # Check if all rules satisfied
        all_satisfied = all(s for _, s in rules)
        if all_satisfied and stage < max_stage:
            tft.text15('All rules satisfied! Press Enter for next stage', 4, y + 8, 0x07E0, 0x0000)
        elif all_satisfied and stage == max_stage:
            tft.text15('YOU WIN! Press Enter to exit', 4, y + 8, 0x07E0, 0x0000)

        # Instructions
        tft.text15('Type password  Backspace=del  Enter=next  Q=quit', 4, 304, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            # Blink cursor
            now = time.time()
            if now - last_blink > 0.5:
                cursor_visible = not cursor_visible
                last_blink = now
                _render()
            time.sleep_ms(50)
            continue

        if ch in ('q', 'Q', chr(24), chr(27)):
            return

        if ch == chr(127) or ch == chr(8):  # Backspace
            if password:
                password = password[:-1]
                _render()
        elif ch == chr(10):  # Enter
            rules = _check_rules(password, stage)
            all_satisfied = all(s for _, s in rules)
            if all_satisfied:
                if stage < max_stage:
                    stage += 1
                    _render()
                else:
                    # Win state
                    time.sleep_ms(500)
                    return
        elif len(ch) == 1 and 32 <= ord(ch) <= 126:
            if len(password) < 100:
                password += ch
                _render()
