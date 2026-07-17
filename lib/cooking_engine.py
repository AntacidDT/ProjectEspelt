"""Cooking — recipe timing game under pressure.
Follow recipes by pressing keys in sequence before time runs out.
"""
import time
import random

RECIPES = [
    {'name': 'Soup', 'steps': [('Stir', 'a'), ('Add salt', 's'), ('Simmer', 'd'), ('Serve', 'f')]},
    {'name': 'Salad', 'steps': [('Chop', 'a'), ('Mix', 's'), ('Dress', 'd'), ('Plate', 'f')]},
    {'name': 'Pasta', 'steps': [('Boil', 'a'), ('Drain', 's'), ('Sauce', 'd'), ('Garnish', 'f')]},
    {'name': 'Cake', 'steps': [('Mix', 'a'), ('Bake', 's'), ('Cool', 'd'), ('Frost', 'f')]},
    {'name': 'Pizza', 'steps': [('Dough', 'a'), ('Sauce', 's'), ('Toppings', 'd'), ('Bake', 'f')]},
    {'name': 'Stir Fry', 'steps': [('Heat', 'a'), ('Veggies', 's'), ('Protein', 'd'), ('Season', 'f')]},
    {'name': 'Sushi', 'steps': [('Rice', 'a'), ('Fish', 's'), ('Roll', 'd'), ('Cut', 'f')]},
    {'name': 'Burger', 'steps': [('Grill', 'a'), ('Bun', 's'), ('Stack', 'd'), ('Serve', 'f')]},
]

STEP_COLORS = [0x07FF, 0x07E0, 0xFFE0, 0xF800]

def cooking_loop(tft, read_key):
    score = 0
    level = 1
    time_left = 300
    current_recipe = None
    current_step = 0
    last_tick = time.ticks_ms()
    game_over = False
    combo = 0
    best_combo = 0

    def new_recipe():
        nonlocal current_recipe, current_step
        current_recipe = random.choice(RECIPES)
        current_step = 0

    def draw():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15(f'COOKING  L{level}', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        tft.text15(f'Score: {score}', 350, 4, 0xFFFF, 0x1082)

        secs = time_left // 10
        bar_w = int(secs * 480 / 300)
        tft.fill_rect(0, 24, 480, 6, 0x4208)
        color = 0x07E0 if secs > 10 else (0xFFE0 if secs > 5 else 0xF800)
        tft.fill_rect(0, 24, bar_w, 6, color)

        if current_recipe:
            tft.text15(f'Recipe: {current_recipe["name"]}', 120, 50, 0xFFFF, 0x0000)

            y = 100
            for i, (step_name, key) in enumerate(current_recipe['steps']):
                if i < current_step:
                    c = 0x4208
                    marker = '✓'
                elif i == current_step:
                    c = STEP_COLORS[i]
                    marker = '>'
                else:
                    c = 0x8410
                    marker = ' '
                tft.text15(f'{marker} {step_name} [{key.upper()}]', 100, y, c, 0x0000)
                y += 40

        if combo > 1:
            tft.text15(f'Combo x{combo}!', 180, 280, 0xFFE0, 0x0000)

        tft.text('Press key for current step  Q=quit', 80, 300, 0x8410, 0x0000)

        if game_over:
            tft.fill_rect(0, 0, 480, 320, 0x0000)
            tft.text15('TIME UP!', 170, 100, 0xF800, 0x0000)
            tft.text15(f'Score: {score}', 170, 140, 0xFFE0, 0x0000)
            tft.text15(f'Best Combo: {best_combo}', 170, 170, 0x07FF, 0x0000)
            tft.text15('Enter: retry  Q: quit', 120, 220, 0x8410, 0x0000)

    new_recipe()
    draw()

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_tick) >= 100:
            last_tick = now
            if not game_over:
                time_left -= 1
                if time_left <= 0:
                    game_over = True

        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            if game_over:
                if ch == chr(10):
                    score = 0
                    level = 1
                    time_left = 300
                    combo = 0
                    game_over = False
                    new_recipe()
                continue

            if current_recipe and current_step < len(current_recipe['steps']):
                expected_key = current_recipe['steps'][current_step][1]
                if ch == expected_key:
                    current_step += 1
                    combo += 1
                    if combo > best_combo:
                        best_combo = combo
                    score += 10 * combo
                    if current_step >= len(current_recipe['steps']):
                        score += 50
                        level += 1
                        time_left += 50
                        new_recipe()
                else:
                    combo = 0
                    time_left = max(0, time_left - 20)

        draw()
        time.sleep_ms(16)
