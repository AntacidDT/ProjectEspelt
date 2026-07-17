"""Trolley Problem - Moral dilemma game."""

import time
import random

DILEMMAS = [
    {
        'scenario': 'A runaway trolley is heading toward 5 workers. You can pull a lever to divert it to a track with 1 worker.',
        'a': 'Pull the lever (kill 1, save 5)',
        'b': 'Do nothing (5 die)',
        'a_utilitarian': True,
    },
    {
        'scenario': 'A doctor has 5 patients needing different organs. A healthy traveler arrives for a checkup.',
        'a': 'Harvest organs (5 live, 1 dies)',
        'b': 'Do nothing (5 die)',
        'a_utilitarian': True,
    },
    {
        'scenario': 'You can save your child OR 5 strangers from a burning building. Not both.',
        'a': 'Save your child',
        'b': 'Save the 5 strangers',
        'a_utilitarian': False,
    },
    {
        'scenario': 'A self-driving car must choose: hit 3 pedestrians OR swerve and kill the passenger (you).',
        'a': 'Hit pedestrians (3 die)',
        'b': 'Swerve (you die)',
        'a_utilitarian': True,
    },
    {
        'scenario': 'You can push a fat man off a bridge to stop the trolley, saving 5 workers.',
        'a': 'Push him (1 dies, 5 live)',
        'b': 'Do nothing (5 die)',
        'a_utilitarian': True,
    },
    {
        'scenario': 'AAI will save 1000 lives but eliminate 100 jobs. Or shut it down (100 jobs saved, 1000 die).',
        'a': 'Use the AI (100 jobs lost, 1000 saved)',
        'b': 'Shut it down (100 jobs saved, 1000 die)',
        'a_utilitarian': True,
    },
    {
        'scenario': 'You can steal medicine to save a dying child, or respect property rights (child dies).',
        'a': 'Steal medicine',
        'b': 'Respect property',
        'a_utilitarian': True,
    },
    {
        'scenario': 'Torture one innocent terrorist suspect to prevent a bomb that will kill 1000 people.',
        'a': 'Torture (prevent 1000 deaths)',
        'b': 'Don\'t torture (1000 die)',
        'a_utilitarian': True,
    },
]


def trolley_loop(tft, read_key):
    """Moral dilemma game."""
    dilemmas = random.sample(DILEMMAS, min(5, len(DILEMMAS)))
    current = 0
    choices = []
    utilitarian_count = 0

    def _render():
        if current >= len(dilemmas):
            # Show results
            tft.fill(0x0000)
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15('TROLLEY PROBLEM', 160, 4, 0x07FF, 0x1082)
            tft.hline(0, 24, 480, 0x07FF)

            y = 40
            tft.text15('RESULTS', 4, y, 0xFFE0, 0x0000)
            y += 20

            # Calculate moral profile
            pct = int(100 * utilitarian_count / len(dilemmas))
            if pct >= 80:
                profile = 'Utilitarian'
                desc = 'You prioritize the greater good'
            elif pct >= 60:
                profile = 'Pragmatic'
                desc = 'You balance logic and empathy'
            elif pct >= 40:
                profile = 'Balanced'
                desc = 'You weigh each case individually'
            elif pct >= 20:
                profile = 'Deontological'
                desc = 'You follow moral rules'
            else:
                profile = 'Virtue Ethics'
                desc = 'You prioritize character and intent'

            tft.text15(f'Profile: {profile}', 4, y, 0x07E0, 0x0000)
            y += 16
            tft.text15(desc, 4, y, 0x8410, 0x0000)
            y += 16
            tft.text15(f'Utilitarian choices: {utilitarian_count}/{len(dilemmas)} ({pct}%)', 4, y, 0xFFFF, 0x0000)
            y += 24

            tft.text15('Press Enter to exit', 4, y, 0x8410, 0x0000)
            return

        # Show current dilemma
        d = dilemmas[current]
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15(f'TROLLEY {current + 1}/{len(dilemmas)}', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        y = 40
        # Wrap scenario text
        words = d['scenario'].split()
        line = ''
        for word in words:
            if len(line + word) > 55:
                tft.text15(line, 4, y, 0xFFFF, 0x0000)
                y += 16
                line = word + ' '
            else:
                line += word + ' '
        if line:
            tft.text15(line, 4, y, 0xFFFF, 0x0000)
            y += 24

        # Options
        tft.text15('A) ' + d['a'], 4, y, 0x07E0, 0x0000)
        y += 20
        tft.text15('B) ' + d['b'], 4, y, 0xF800, 0x0000)
        y += 24

        tft.text15('Press A or B to choose', 4, y, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch in ('q', 'Q', chr(24), chr(27)):
            return

        if current >= len(dilemmas):
            # Results screen
            if ch == chr(10):  # Enter
                return
            continue

        d = dilemmas[current]
        if ch in ('a', 'A'):
            choices.append('a')
            if d['a_utilitarian']:
                utilitarian_count += 1
            current += 1
            _render()
        elif ch in ('b', 'B'):
            choices.append('b')
            if not d['a_utilitarian']:
                utilitarian_count += 1
            current += 1
            _render()
