_KEY_COLOR = const(0x0000)


def color565(r, g, b):
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


def _rgb666_bytes(color):
    r5 = (color >> 11) & 0x1F
    g6 = (color >> 5) & 0x3F
    b5 = color & 0x1F
    return bytes([
        ((r5 << 1) | (r5 >> 4)) & 0xFC,
        g6 & 0xFC,
        ((b5 << 1) | (b5 >> 4)) & 0xFC
    ])


def render_sprite(width, height, draw_fn):
    buf = bytearray(width * height * 3)
    draw_fn(buf, width, height)
    return buf


def blit_sprite(tft, buf, x, y, w, h, key_color=None):
    if key_color is None:
        tft.blit_bitmap(buf, x, y, w, h)
        return
    px = _rgb666_bytes(key_color)
    for row in range(h):
        ry = y + row
        if ry < 0 or ry >= tft.height:
            continue
        segments = []
        seg_start = -1
        for col in range(w):
            off = (row * w + col) * 3
            if buf[off] == px[0] and buf[off + 1] == px[1] and buf[off + 2] == px[2]:
                if seg_start >= 0:
                    segments.append((seg_start, col))
                    seg_start = -1
            else:
                if seg_start < 0:
                    seg_start = col
        if seg_start >= 0:
            segments.append((seg_start, w))
        for sx, ex in segments:
            sw = ex - sx
            row_buf = bytearray(sw * 3)
            src_off = (row * w + sx) * 3
            row_buf[:] = buf[src_off:src_off + sw * 3]
            tft.blit_bitmap(row_buf, x + sx, ry, sw, 1)


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life')

    def __init__(self, x, y, vx, vy, color, life=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life


class ParticleSystem:
    def __init__(self, max_particles=60):
        self.particles = []
        self.max = max_particles

    def emit(self, x, y, count=10, speed=3, colors=None, life=30):
        import random
        if not colors:
            colors = [0xFFE0, 0xF800, 0x07FF, 0xFFFF]
        for _ in range(count):
            if len(self.particles) >= self.max:
                break
            vx = random.randint(-speed * 10, speed * 10) / 10
            vy = random.randint(-speed * 10, speed * 10) / 10
            c = colors[random.randint(0, len(colors) - 1)]
            l = life + random.randint(-5, 5)
            self.particles.append(Particle(x, y, vx, vy, c, l))

    def update(self, tft, gravity=0.1):
        dead = []
        for i, p in enumerate(self.particles):
            if p.life <= 0:
                dead.append(i)
                continue
            ox = int(p.x)
            oy = int(p.y)
            p.x += p.vx
            p.y += p.vy
            p.vy += gravity
            p.life -= 1
            nx = int(p.x)
            ny = int(p.y)
            if 0 <= ox < tft.width and 0 <= oy < tft.height:
                tft.fill_rect(ox, oy, 2, 2, 0x0000)
            if 0 <= nx < tft.width and 0 <= ny < tft.height:
                fade = p.life / p.max_life
                if fade > 0.3:
                    tft.fill_rect(nx, ny, 2, 2, p.color)
        for i in reversed(dead):
            self.particles.pop(i)

    def clear(self, tft):
        for p in self.particles:
            ox = int(p.x)
            oy = int(p.y)
            if 0 <= ox < tft.width and 0 <= oy < tft.height:
                tft.fill_rect(ox, oy, 2, 2, 0x0000)
        self.particles.clear()


def gradient_rect(tft, x, y, w, h, color_top, color_bot):
    for row in range(h):
        ratio = row / max(h - 1, 1)
        r = int(((color_top >> 11) & 0x1F) * (1 - ratio) + ((color_bot >> 11) & 0x1F) * ratio)
        g = int(((color_top >> 5) & 0x3F) * (1 - ratio) + ((color_bot >> 5) & 0x3F) * ratio)
        b = int((color_top & 0x1F) * (1 - ratio) + (color_bot & 0x1F) * ratio)
        c = (r << 11) | (g << 5) | b
        tft.fill_rect(x, y + row, w, 1, c)


def draw_3d_rect(tft, x, y, w, h, base_color, light_color=None, dark_color=None):
    if light_color is None:
        r = (base_color >> 11) & 0x1F
        g = (base_color >> 5) & 0x3F
        b = base_color & 0x1F
        light_color = (min(r + 6, 31) << 11) | (min(g + 12, 63) << 5) | min(b + 6, 31)
        dark_color = (max(r - 6, 0) << 11) | (max(g - 12, 0) << 5) | max(b - 6, 0)
    tft.fill_rect(x, y, w, h, base_color)
    tft.fill_rect(x, y, w, 2, light_color)
    tft.fill_rect(x, y, 2, h, light_color)
    tft.fill_rect(x, y + h - 2, w, 2, dark_color)
    tft.fill_rect(x + w - 2, y, 2, h, dark_color)
