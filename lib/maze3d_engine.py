"""Maze3D — first-person maze with raycasting.
Arrow keys to move/turn. Q to quit. Mini-map with Tab.
"""
import time
import math

MAP_W, MAP_H = 8, 8
CELL_PX = 32
VIEW_W, VIEW_H = 480, 280

MAZE = [
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1],
    [1,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,1],
    [1,1,1,1,1,1,1,1],
]

def _cast_ray(px, py, angle):
    dx = math.cos(angle)
    dy = math.sin(angle)
    dist = 0
    step = 0.02
    while dist < 10:
        x = px + dx * dist
        y = py + dy * dist
        mx, my = int(x), int(y)
        if 0 <= mx < MAP_W and 0 <= my < MAP_H:
            if MAZE[my][mx] == 1:
                return dist
        else:
            return 10
        dist += step
    return 10

def maze3d_loop(tft, read_key):
    px, py = 1.5, 1.5
    angle = 0.0
    show_map = False
    speed = 0.08
    turn = 0.12
    fps_time = time.ticks_ms()
    fps = 0

    def _render():
        nonlocal fps
        now = time.ticks_ms()
        dt = time.ticks_diff(now, fps_time) if time.ticks_diff(now, fps_time) > 0 else 1
        fps = 1000 // dt if dt > 0 else 0
        fps_time_ref = now

        tft.fill(0x0000)
        tft.fill_rect(0, 0, 480, 24, 0x1082)
        tft.text15('MAZE 3D', 4, 4, 0x07FF, 0x1082)
        tft.hline(0, 24, 480, 0x07FF)

        if show_map:
            ox, oy = 10, 30
            cs = 12
            for my in range(MAP_H):
                for mx in range(MAP_W):
                    c = 0x8410 if MAZE[my][mx] else 0x0000
                    tft.fill_rect(ox + mx*cs, oy + my*cs, cs-1, cs-1, c)
            px_s = int(ox + px * cs)
            py_s = int(oy + py * cs)
            tft.fill_rect(px_s-1, py_s-1, 3, 3, 0x07FF)
        else:
            for col in range(VIEW_W):
                ray_angle = angle - 0.5 + (col / VIEW_W)
                dist = _cast_ray(px, py, ray_angle)
                h = min(VIEW_H, int(VIEW_H / (dist + 0.001)))
                shade = max(0, min(255, int(255 * (1 - dist / 8))))
                color = (shade >> 3) << 11 | (shade >> 2) << 5 | (shade >> 3)
                y_off = 24 + (VIEW_H - h) // 2
                tft.vline(col, y_off, h, color)

        tft.text15(f'{fps} FPS  {px:.1f},{py:.1f}', 4, 310, 0x8410, 0x0000)

    _render()

    while True:
        ch = read_key()
        if ch is not None:
            if ch in ('q', 'Q', chr(24)):
                return
            if ch in ('\t', chr(9)):
                show_map = not show_map
                _render()
                continue

            moved = False
            if ch == '\x80':
                nx = px - math.sin(angle) * speed
                ny = py + math.cos(angle) * speed
                if MAZE[int(ny)][int(nx)] == 0:
                    px, py = nx, ny
                    moved = True
            elif ch == '\x81':
                nx = px + math.sin(angle) * speed
                ny = py - math.cos(angle) * speed
                if MAZE[int(ny)][int(nx)] == 0:
                    px, py = nx, ny
                    moved = True
            elif ch == '\x84':
                angle -= turn
                moved = True
            elif ch == '\x85':
                angle += turn
                moved = True

            if moved:
                _render()
