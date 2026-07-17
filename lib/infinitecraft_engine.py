"""Infinitecraft — element combining game.
Combine elements to discover new ones. Start with 4 basic elements.
"""
import time
import random

BASIC_ELEMENTS = ['Water', 'Fire', 'Earth', 'Air']

COMBINATIONS = {
    ('Water', 'Fire'): 'Steam',
    ('Water', 'Earth'): 'Mud',
    ('Water', 'Air'): 'Cloud',
    ('Fire', 'Earth'): 'Lava',
    ('Fire', 'Air'): 'Smoke',
    ('Earth', 'Air'): 'Dust',
    ('Steam', 'Earth'): 'Geyser',
    ('Mud', 'Fire'): 'Brick',
    ('Cloud', 'Fire'): 'Lightning',
    ('Lava', 'Water'): 'Stone',
    ('Smoke', 'Water'): 'Fog',
    ('Dust', 'Water'): 'Clay',
    ('Steam', 'Air'): 'Mist',
    ('Mud', 'Air'): 'Swamp',
    ('Cloud', 'Water'): 'Rain',
    ('Lava', 'Air'): 'Rock',
    ('Stone', 'Fire'): 'Metal',
    ('Clay', 'Fire'): 'Pottery',
    ('Rain', 'Earth'): 'Plant',
    ('Lightning', 'Water'): 'Life',
    ('Metal', 'Fire'): 'Sword',
    ('Pottery', 'Water'): 'Jug',
    ('Plant', 'Fire'): 'Tobacco',
    ('Life', 'Earth'): 'Human',
    ('Sword', 'Human'): 'Warrior',
    ('Jug', 'Water'): 'Drinking',
    ('Human', 'Fire'): 'Cooking',
    ('Human', 'Water'): 'Fishing',
    ('Human', 'Earth'): 'House',
    ('Warrior', 'Warrior'): 'Battle',
    ('House', 'Human'): 'Village',
    ('Village', 'Village'): 'City',
    ('City', 'Warrior'): 'Kingdom',
    ('Cooking', 'Water'): 'Soup',
    ('Fishing', 'Fire'): 'Grilled Fish',
    ('Kingdom', 'Kingdom'): 'Empire',
    ('Soup', 'Human'): 'Chef',
    ('Grilled Fish', 'Human'): 'Meal',
}

def infinitecraft_loop(tft, read_key):
    discovered = set(BASIC_ELEMENTS)
    selected = [None, None]
    cursor = 0
    scroll = 0
    message = ''
    message_timer = 0
    last_tick = time.ticks_ms()

    def draw():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('INFINITECRAFT', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        tft.text15(f'Discovered: {len(discovered)}', 320, 4, 0xFFFF, 0x1082)

        tft.fill_rect(0, 30, 230, 200, 0x1082)
        tft.text15('Elements', 70, 34, 0x07FF, 0x1082)

        elements = sorted(discovered)
        visible = elements[scroll:scroll + 10]
        y = 55
        for i, elem in enumerate(visible):
            idx = scroll + i
            if idx == cursor:
                tft.fill_rect(4, y - 2, 222, 16, 0x4208)
            color = 0xFFFF if elem in BASIC_ELEMENTS else 0x07E0
            tft.text15(elem, 10, y, color, 0x0000)
            y += 18

        tft.fill_rect(240, 30, 240, 100, 0x1082)
        tft.text15('Combine', 320, 34, 0x07FF, 0x1082)

        for i in range(2):
            y = 60 + i * 30
            if selected[i]:
                tft.text15(selected[i], 260, y, 0xFFFF, 0x0000)
            else:
                tft.text15(f'Slot {i+1} (Enter)', 260, y, 0x8410, 0x0000)

        if selected[0] and selected[1]:
            tft.text15('Press C to combine!', 260, 130, 0xFFE0, 0x0000)

        if message:
            tft.fill_rect(0, 240, 480, 40, 0x0000)
            tft.text15(message, 10, 250, 0x07E0, 0x0000)

        tft.text('W/S=scroll Enter=select C=combine Q=quit', 4, 300, 0x8410, 0x0000)

    def try_combine():
        nonlocal message, message_timer
        if not selected[0] or not selected[1]:
            return
        pair = tuple(sorted([selected[0], selected[1]]))
        result = COMBINATIONS.get(pair)
        if result:
            if result not in discovered:
                discovered.add(result)
                message = f'Discovered: {result}!'
            else:
                message = f'Already known: {result}'
        else:
            message = 'No combination found...'
        message_timer = 30
        selected[0] = None
        selected[1] = None

    draw()

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_tick) >= 100:
            last_tick = now
            if message_timer > 0:
                message_timer -= 1
                if message_timer == 0:
                    message = ''

        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            if ch == '\x84':
                cursor = max(0, cursor - 1)
                if cursor < scroll:
                    scroll = cursor
            elif ch == '\x85':
                elements = sorted(discovered)
                cursor = min(len(elements) - 1, cursor + 1)
                if cursor >= scroll + 10:
                    scroll = cursor - 9
            elif ch == chr(10):
                elements = sorted(discovered)
                elem = elements[cursor]
                if selected[0] is None:
                    selected[0] = elem
                elif selected[1] is None:
                    selected[1] = elem
                else:
                    selected[0] = elem
                    selected[1] = None
            elif ch == 'c' or ch == 'C':
                try_combine()

        draw()
        time.sleep_ms(16)
