"""Flappy Bird — tap to flap, avoid pipes.
Simple version: pipes are vertical gaps, bird falls with gravity.
"""
import time
import random

def flappy_loop(tft, read_key):
    """Full-screen flappy bird."""
    bird_y = 150
    bird_vy = 0
    gravity = 1
    flap_power = -4
    pipe_x = 480
    pipe_gap = 70
    pipe_top = random.randint(50, 180)
    pipe_w = 40
    score = 0
    game_over = False
    running = True

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('FLAPPY', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        # Pipes
        tft.fill_rect(pipe_x, 26, pipe_w, pipe_top - 26, 0x07E0)
        pipe_bottom = pipe_top + pipe_gap
        tft.fill_rect(pipe_x, pipe_bottom, pipe_w, 300 - pipe_bottom, 0x07E0)
        # Gap highlight
        tft.fill_rect(pipe_x, pipe_top, pipe_w, 4, 0xFFFF)
        tft.fill_rect(pipe_x, pipe_bottom - 4, pipe_w, 4, 0xFFFF)
        # Bird
        tft.fill_rect(100, int(bird_y), 16, 12, 0xFFE0)
        tft.fill_rect(110, int(bird_y) + 2, 6, 4, 0x0000)  # eye
        if game_over:
            from lib.highscores import set as _hs_set, get as _hs_get
            _hs_set('FLAPPY', score)
            best = _hs_get('FLAPPY')
            tft.text15('GAME OVER', 170, 130, 0xF800, 0x0000)
            tft.text15(f'Score: {score}', 180, 155, 0xFFFF, 0x0000)
            tft.text15(f'Best:  {best}', 180, 175, 0x07FF, 0x0000)
            tft.text15('Enter: restart  Q: quit', 120, 200, 0x8410, 0x0000)
        elif not running:
            tft.text15('Press Enter to start', 140, 160, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', chr(24)):
                return
            if game_over:
                if ch == chr(10):
                    bird_y = 150; bird_vy = 0
                    pipe_x = 480; pipe_top = random.randint(50, 180)
                    score = 0; game_over = False; running = True
                    if _oled: _oled.set_mode('game_hud', score=score, game_name='FLAPPY')
                    _render()
                continue
            if not running:
                if ch == chr(10):
                    running = True
                    _render()
                continue
            if ch == chr(10) or ch == ' ':
                bird_vy = flap_power

        if running and not game_over:
            # Physics
            bird_vy += gravity
            bird_y += bird_vy
            # Pipe move
            pipe_x -= 3
            if pipe_x + pipe_w < 0:
                pipe_x = 480
                pipe_top = random.randint(50, 180)
                score += 1
                if _oled: _oled.set_mode('game_hud', score=score, game_name='FLAPPY')
            # Collision
            pipe_bottom = pipe_top + pipe_gap
            if (bird_y < 26 or bird_y + 12 > 300 or
                (100 + 16 > pipe_x and 100 < pipe_x + pipe_w and
                 (bird_y < pipe_top or bird_y + 12 > pipe_bottom))):
                game_over = True
            _render()
            time.sleep_ms(30)
