"""Game of Life — Conway's cellular automaton.
Watch patterns evolve. Space to randomize, Enter to step, Q to quit.
"""
import time
import random

GRID_W, GRID_H = 30, 20
CELL = 14
OX, OY = 30, 40

def _count_neighbors(grid, x, y):
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % GRID_W
            ny = (y + dy) % GRID_H
            if grid[ny][nx]:
                count += 1
    return count

def _step(grid):
    new = [[0]*GRID_W for _ in range(GRID_H)]
    for y in range(GRID_H):
        for x in range(GRID_W):
            n = _count_neighbors(grid, x, y)
            if grid[y][x]:
                new[y][x] = 1 if n in (2, 3) else 0
            else:
                new[y][x] = 1 if n == 3 else 0
    return new

def _randomize():
    return [[1 if random.randint(0, 3) == 0 else 0 for _ in range(GRID_W)] for _ in range(GRID_H)]

def _count_pop(grid):
    return sum(cell for row in grid for cell in row)

def life_loop(tft, read_key):
    grid = _randomize()
    gen = 0
    paused = True
    speed = 200
    last_step = time.ticks_ms()

    def _render():
        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('GAME OF LIFE', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)
        pop = _count_pop(grid)
        tft.text15(f'Gen: {gen}  Pop: {pop}  {"PAUSED" if paused else "RUNNING"}', 4, 28, 0x8410, 0x0000)
        tft.rect(OX-1, OY-1, GRID_W*CELL+2, GRID_H*CELL+2, 0x8410)
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x]:
                    tft.fill_rect(OX + x*CELL, OY + y*CELL, CELL-1, CELL-1, 0x07E0)
        tft.text15('Space:random Enter:step R:reset Q:quit', 4, 310, 0x8410, 0x0000)

    _render()

    while True:
        now = time.ticks_ms()
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', chr(24)):
                return
            elif ch == ' ':
                grid = _randomize()
                gen = 0
                _render()
            elif ch == chr(10):
                grid = _step(grid)
                gen += 1
                _render()
            elif ch in ('r', 'R'):
                grid = _randomize()
                gen = 0
                _render()
            elif ch in ('p', 'P'):
                paused = not paused
                _render()

        if not paused and time.ticks_diff(now, last_step) >= speed:
            last_step = now
            grid = _step(grid)
            gen += 1
            _render()
