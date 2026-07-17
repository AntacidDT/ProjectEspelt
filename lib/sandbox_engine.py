"""Sandbox — pixel art + simple physics sandbox.
Place colored pixels, apply gravity, erase. Creative mode.
"""
import time
import random

GRID_W, GRID_H = 48, 32
CELL = 10
OX, OY = 0, 25

COLORS = [0x0000, 0xF800, 0x07E0, 0x001F, 0xFFE0, 0xF800, 0x07FF, 0xFFFF, 0x8410, 0xFD20, 0xA81F, 0x0420, 0x4208, 0x2104, 0x8010, 0x0010]

def sandbox_loop(tft, read_key):
    grid = [[0] * GRID_W for _ in range(GRID_H)]
    cursor_x = GRID_W // 2
    cursor_y = GRID_H // 2
    color_idx = 1
    gravity_on = False
    last_gravity = time.ticks_ms()

    def draw():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('SANDBOX', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x]:
                    tft.fill_rect(OX + x * CELL, OY + y * CELL, CELL - 1, CELL - 1, grid[y][x])

        cx = OX + cursor_x * CELL
        cy = OY + cursor_y * CELL
        tft.rect(cx - 1, cy - 1, CELL + 1, CELL + 1, 0xFFFF)

        tft.fill_rect(0, 300, 480, 20, 0x1082)
        tft.fill_rect(4, 304, 12, 12, COLORS[color_idx])
        tft.text(f'Color:{color_idx} G=gravity E=erase C=clear Q=quit', 20, 304, 0x8410, 0x1082)
        if gravity_on:
            tft.text('GRAVITY ON', 400, 304, 0x07E0, 0x1082)

    def apply_gravity():
        for y in range(GRID_H - 2, -1, -1):
            for x in range(GRID_W):
                if grid[y][x] and not grid[y + 1][x]:
                    grid[y + 1][x] = grid[y][x]
                    grid[y][x] = 0

    draw()

    while True:
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', '\x1b', '\x03'):
                return
            if ch == '\x80':
                cursor_x = max(0, cursor_x - 1)
            elif ch == '\x81':
                cursor_x = min(GRID_W - 1, cursor_x + 1)
            elif ch == '\x84':
                cursor_y = max(0, cursor_y - 1)
            elif ch == '\x85':
                cursor_y = min(GRID_H - 1, cursor_y + 1)
            elif ch == ' ' or ch == '\n':
                grid[cursor_y][cursor_x] = COLORS[color_idx]
            elif ch == 'e' or ch == 'E':
                grid[cursor_y][cursor_x] = 0
            elif ch == 'g' or ch == 'G':
                gravity_on = not gravity_on
            elif ch == 'c' or ch == 'C':
                grid = [[0] * GRID_W for _ in range(GRID_H)]
            elif ch == 'w' or ch == 'W':
                color_idx = (color_idx + 1) % len(COLORS)
                if color_idx == 0:
                    color_idx = 1
            elif ch == 's' or ch == 'S':
                color_idx = (color_idx - 1) % len(COLORS)
                if color_idx == 0:
                    color_idx = len(COLORS) - 1

        if gravity_on:
            now = time.ticks_ms()
            if time.ticks_diff(now, last_gravity) >= 100:
                last_gravity = now
                apply_gravity()

        draw()
        time.sleep_ms(16)
