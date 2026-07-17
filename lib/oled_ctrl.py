import gc
import time
import math
import os
import random
from machine import Pin, I2C
from lib.ssd1306 import SSD1306

MATRIX_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*!?'


class OLEDController:
    def __init__(self):
        self._oled = None
        self._mode = 'status'
        self._running = True
        self._timer_end = 0
        self._timer_secs = 0
        self._timer_done = False
        self._timer_flash_t = 0
        self._info_page = 'status'
        self._text = ''
        self._dvd_x = 10
        self._dvd_y = 10
        self._dvd_dx = 3
        self._dvd_dy = 2
        self._wave_col = 0
        self._wave_prev = 32
        self._matrix_cols = []
        self._star_field = []
        self._bounce_x = 64
        self._bounce_y = 32
        self._bounce_dx = 2
        self._bounce_dy = 1
        self._rain_drops = []
        self._fw_particles = []
        self._fw_x = 64
        self._fw_y = 32
        self._eq_bars = [0] * 16
        self._pong_ly = 24
        self._pong_ry = 24
        self._pong_bx = 64
        self._pong_by = 32
        self._pong_bdx = 2
        self._pong_bdy = 1
        self._pong_lscore = 0
        self._pong_rscore = 0
        self._dna_phase = 0
        self._lava_blobs = []
        self._sparkle_stars = []
        self._pulse_r = 0
        self._cube_angle = 0
        self._scroll_text = 'ESPELT CYBERDECK - ESP32-P4 - POWERED BY MICROPYTHON'
        self._scroll_x = 128
        self._msnake = [(5, 3), (4, 3), (3, 3)]
        self._msnake_food = (10, 5)
        self._msnake_dx = 1
        self._msnake_dy = 0
        self._msnake_score = 0
        self._invader_frame = 0
        self._spiral_phase = 0
        self._boot_lines = []
        self._boot_done = False
        self._disco_seed = 0
        self._eye_px = 64
        self._eye_py = 32
        self._eye_tx = 64
        self._eye_ty = 32
        self._checker_phase = 0
        self._lightning_bolt = []
        self._lightning_timer = 0
        self._dance_pose = 0
        self._dance_timer = 0
        self._doom_scale = 1
        self._doom_timer = 0
        self._cat_ear = 0
        self._random_last = ''
        self._chicken_x = 0
        self._chicken_frame = 0
        self._chicken_dir = 1
        self._esp_angle = 0
        self._pac_x = 0
        self._pac_mouth = 0
        self._pac_dots = []
        self._tunnel_phase = 0
        self._tw_text = 'Espelt OS'
        self._tw_pos = 0
        self._tw_clearing = False
        self._tw_clear_pos = 0
        self._radar_angle = 0
        self._radar_blips = []
        self._tf_blocks = []
        self._tf_score = 0
        self._ff_dots = []
        self._spec_bars = [0] * 16
        self._spec_peaks = [0] * 16
        self._osnake = [(5, 3), (4, 3), (3, 3)]
        self._osnake_food = (10, 5)
        self._osnake_dx = 1
        self._osnake_dy = 0
        self._osnake_score = 0
        self._game_hud_score = 0
        self._game_hud_lives = 0
        self._game_hud_level = 1
        self._game_hud_name = ''
        self._notify_text = ''
        self._notify_end = 0
        self._prev_mode = 'status'
        self._last_cmd = ''
        self._theme = None
        self._engine_name = ''
        self._engine_lines = ['', '', '', '', '']
        self._init_oled()

    def set_last_command(self, cmd):
        if cmd:
            self._last_cmd = cmd[:20]

    def set_engine_status(self, engine, **kwargs):
        self._engine_name = engine[:10]
        for i in range(5):
            key = 'line' + str(i)
            self._engine_lines[i] = kwargs.get(key, '')[:20]
        if self._mode not in ('game_hud', 'notify'):
            self._prev_mode = self._mode
            self._mode = 'engine_status'

    def _init_oled(self):
        try:
            i2c = I2C(0, scl=Pin(8), sda=Pin(7), freq=400000)
            self._oled = SSD1306(128, 64, i2c, addr=0x3C)
        except:
            pass

    def screen_off(self):
        if self._oled:
            self._oled.display_off()

    def screen_on(self):
        if self._oled:
            self._oled.display_on()

    def set_mode(self, mode, **kwargs):
        self._info_page = kwargs.get('page', 'status')
        self._text = kwargs.get('text', '')
        if mode == 'timer':
            self._timer_secs = kwargs.get('seconds', 60)
            self._timer_end = time.ticks_add(time.ticks_ms(), self._timer_secs * 1000)
            self._timer_done = False
            self._timer_flash_t = 0
        if mode == 'dvd':
            self._dvd_x, self._dvd_y = 10, 10
            self._dvd_dx, self._dvd_dy = 3, 2
        if mode == 'wave':
            self._wave_col = 0
            self._wave_prev = 32
        if mode == 'matrix':
            cols = []
            x = 0
            while x < 128:
                cols.append({'x': x, 'y': random.randint(-20, 0), 'speed': random.randint(1, 3),
                             'chars': [random.randint(0, len(MATRIX_CHARS) - 1) for _ in range(8)]})
                x += 10
            self._matrix_cols = cols
        if mode == 'starfield':
            self._star_field = []
            for _ in range(20):
                self._star_field.append({'x': random.randint(0, 127),
                                         'y': random.randint(0, 63),
                                         'speed': random.randint(1, 3)})
        if mode == 'bounce':
            self._bounce_x = 64
            self._bounce_y = 32
            self._bounce_dx = 2
            self._bounce_dy = 1
        if mode == 'rain':
            self._rain_drops = []
            for _ in range(15):
                self._rain_drops.append({'x': random.randint(0, 127), 'y': random.randint(-64, 0), 'speed': random.randint(2, 5)})
        if mode == 'fireworks':
            self._fw_particles = []
            self._fw_x = 64
            self._fw_y = 32
        if mode == 'equalizer':
            self._eq_bars = [random.randint(5, 55) for _ in range(16)]
        if mode == 'pong':
            self._pong_ly = 24
            self._pong_ry = 24
            self._pong_bx = 64
            self._pong_by = 32
            self._pong_bdx = 2
            self._pong_bdy = 1
            self._pong_lscore = 0
            self._pong_rscore = 0
        if mode == 'plasma':
            pass
        if mode == 'dna':
            self._dna_phase = 0
        if mode == 'lava':
            self._lava_blobs = []
            for _ in range(5):
                self._lava_blobs.append({'x': random.randint(10, 118), 'y': random.randint(20, 55),
                                         'r': random.randint(5, 10), 'dy': -random.random() * 0.5 - 0.2})
        if mode == 'sparkle':
            self._sparkle_stars = []
            for _ in range(20):
                self._sparkle_stars.append({'x': random.randint(0, 127), 'y': random.randint(0, 63),
                                            'phase': random.random() * 6.28, 'speed': random.random() * 0.3 + 0.1})
        if mode == 'pulse':
            self._pulse_r = 0
        if mode == 'cube':
            self._cube_angle = 0
        if mode == 'textscroll':
            self._scroll_x = 128
        if mode == 'minisnake':
            self._msnake = [(5, 3), (4, 3), (3, 3)]
            self._msnake_food = self._msnake_food_pos()
            self._msnake_dx = 1
            self._msnake_dy = 0
            self._msnake_score = 0
        if mode == 'invader':
            self._invader_frame = 0
        if mode == 'spiral':
            self._spiral_phase = 0
        if mode == 'boot':
            self._boot_lines = []
            self._boot_done = False
        if mode == 'disco':
            self._disco_seed = 0
        if mode == 'eye':
            self._eye_px = 64
            self._eye_py = 32
            self._eye_tx = 64
            self._eye_ty = 32
        if mode == 'checker':
            self._checker_phase = 0
        if mode == 'lightning':
            self._lightning_bolt = []
            self._lightning_timer = 0
        if mode == 'dance':
            self._dance_pose = 0
            self._dance_timer = 0
        if mode == 'doom':
            self._doom_scale = 1
            self._doom_timer = 0
        if mode == 'cat':
            self._cat_ear = 0
        if mode == 'stopwatch':
            self._sw_running = True
            self._sw_start = time.ticks_ms()
            self._sw_elapsed = 0
        if mode == 'chicken':
            self._chicken_x = 0
            self._chicken_frame = 0
            self._chicken_dir = 1
        if mode == 'esp32':
            self._esp_angle = 0
        if mode == 'pacman':
            self._pac_x = 0
            self._pac_mouth = 0
            self._pac_dots = [1] * 32
        if mode == 'tunnel':
            self._tunnel_phase = 0
        if mode == 'typewriter':
            self._tw_pos = 0
            self._tw_clearing = False
            self._tw_clear_pos = 0
        if mode == 'radar':
            self._radar_angle = 0
            self._radar_blips = []
            for _ in range(5):
                self._radar_blips.append({'x': random.randint(10, 118), 'y': random.randint(10, 54), 'life': random.randint(0, 60)})
        if mode == 'tetrisfall':
            self._tf_blocks = []
            self._tf_score = 0
        if mode == 'firefly':
            self._ff_dots = []
            for _ in range(8):
                self._ff_dots.append({'x': random.randint(0, 127), 'y': random.randint(0, 63),
                                      'brightness': random.randint(0, 10), 'dx': random.choice([-1, 0, 1]),
                                      'dy': random.choice([-1, 0, 1])})
        if mode == 'spectrum':
            self._spec_bars = [0] * 16
            self._spec_peaks = [0] * 16
        if mode == 'osnake':
            self._osnake = [(5, 3), (4, 3), (3, 3)]
            self._osnake_food = self._osnake_food_pos()
            self._osnake_dx = 1
            self._osnake_dy = 0
            self._osnake_score = 0
        if mode == 'game_hud':
            self._game_hud_score = kwargs.get('score', 0)
            self._game_hud_lives = kwargs.get('lives', 0)
            self._game_hud_level = kwargs.get('level', 1)
            self._game_hud_name = kwargs.get('game_name', 'GAME')
            self._prev_mode = self._mode
        if mode == 'wlan':
            self._prev_mode = self._mode
        if mode == 'auto':
            self._prev_mode = self._mode
        if mode == 'engine_status':
            self._prev_mode = self._mode
        self._mode = mode
        if self._oled:
            self._oled.fill(0)
            self._oled.show()

    def get_mode(self):
        return self._mode

    _ANIMATIONS = ['dvd', 'wave', 'clock', 'matrix', 'fire', 'starfield', 'bounce',
                   'plasma', 'rain', 'fireworks', 'dna', 'equalizer', 'pong',
                   'lava', 'sparkle', 'pulse', 'cube', 'textscroll', 'minisnake',
                   'heart', 'invader', 'spiral', 'boot', 'glitch', 'disco',
                   'binary', 'eye', 'checker', 'lightning', 'helplogo', 'skull',
                   'cat', 'dance', 'doom', 'potato',
                   'chicken', 'esp32', 'pacman', 'tunnel', 'typewriter',
                   'radar', 'tetrisfall', 'firefly', 'spectrum', 'osnake']

    def run(self):
        while self._running:
            if not self._oled:
                time.sleep_ms(100)
                continue
            m = self._mode
            if m == 'random':
                choices = [a for a in self._ANIMATIONS if a != self._random_last]
                pick = random.choice(choices)
                self._random_last = pick
                self.set_mode(pick)
                m = pick
            try:
                if m == 'status':
                    self._draw_info()
                elif m == 'timer':
                    done = self._draw_timer()
                    if done:
                        self._mode = 'status'
                elif m == 'text':
                    self._draw_text()
                elif m == 'dvd':
                    self._draw_dvd()
                elif m == 'wave':
                    self._draw_wave()
                elif m == 'clock':
                    self._draw_clock()
                elif m == 'matrix':
                    self._draw_matrix()
                elif m == 'fire':
                    self._draw_fire()
                elif m == 'starfield':
                    self._draw_starfield()
                elif m == 'bounce':
                    self._draw_bounce()
                elif m == 'plasma':
                    self._draw_plasma()
                elif m == 'rain':
                    self._draw_rain()
                elif m == 'fireworks':
                    self._draw_fireworks()
                elif m == 'dna':
                    self._draw_dna()
                elif m == 'equalizer':
                    self._draw_equalizer()
                elif m == 'pong':
                    self._draw_pong()
                elif m == 'lava':
                    self._draw_lava()
                elif m == 'sparkle':
                    self._draw_sparkle()
                elif m == 'pulse':
                    self._draw_pulse()
                elif m == 'cube':
                    self._draw_cube()
                elif m == 'textscroll':
                    self._draw_textscroll()
                elif m == 'minisnake':
                    self._draw_minisnake()
                elif m == 'heart':
                    self._draw_heart()
                elif m == 'invader':
                    self._draw_invader()
                elif m == 'spiral':
                    self._draw_spiral()
                elif m == 'boot':
                    self._draw_boot()
                elif m == 'glitch':
                    self._draw_glitch()
                elif m == 'disco':
                    self._draw_disco()
                elif m == 'binary':
                    self._draw_binary()
                elif m == 'eye':
                    self._draw_eye()
                elif m == 'checker':
                    self._draw_checker()
                elif m == 'lightning':
                    self._draw_lightning()
                elif m == 'helplogo':
                    self._draw_helplogo()
                elif m == 'skull':
                    self._draw_skull()
                elif m == 'cat':
                    self._draw_cat()
                elif m == 'dance':
                    self._draw_dance()
                elif m == 'doom':
                    self._draw_doom()
                elif m == 'potato':
                    self._draw_potato()
                elif m == 'stopwatch':
                    self._draw_stopwatch()
                elif m == 'chicken':
                    self._draw_chicken()
                elif m == 'esp32':
                    self._draw_esp32()
                elif m == 'pacman':
                    self._draw_pacman()
                elif m == 'tunnel':
                    self._draw_tunnel()
                elif m == 'typewriter':
                    self._draw_typewriter()
                elif m == 'radar':
                    self._draw_radar()
                elif m == 'tetrisfall':
                    self._draw_tetrisfall()
                elif m == 'firefly':
                    self._draw_firefly()
                elif m == 'spectrum':
                    self._draw_spectrum()
                elif m == 'osnake':
                    self._draw_osnake()
                elif m == 'game_hud':
                    self._draw_game_hud()
                elif m == 'wlan':
                    self._draw_wlan()
                elif m == 'auto':
                    self._draw_auto()
                elif m == 'engine_status':
                    self._draw_engine_status()
                elif m == 'notify':
                    self._draw_notify()
            except Exception as e:
                self._oled.fill(0)
                self._oled.text('ERR', 0, 0)
                self._oled.text(str(e)[:16], 0, 12)
                self._oled.show()
            time.sleep_ms(50)

    def _draw_info(self):
        o = self._oled
        o.fill(0)
        page = self._info_page

        if page == 'status':
            o.text('ESP32-P4', 0, 0)
            o.text('Espelt v1.0', 0, 10)
            free = gc.mem_free()
            alloc = gc.mem_alloc()
            total = free + alloc
            pct = int(alloc * 100 / total) if total > 0 else 0
            o.text(f'RAM: {pct}%', 0, 24)
            o.rect(14, 34, 100, 6, 1)
            fw = int(100 * pct / 100)
            if fw > 0:
                o.fill_rect(14, 34, fw, 6, 1)
            o.text(f'{free//1024}KB free', 0, 44)

        elif page == 'ram':
            o.text('--- RAM ---', 0, 0)
            free = gc.mem_free()
            alloc = gc.mem_alloc()
            total = free + alloc
            o.text(f'Total: {total//1024}KB', 0, 12)
            o.text(f'Used:  {alloc//1024}KB', 0, 22)
            o.text(f'Free:  {free//1024}KB', 0, 32)
            pct = int(alloc * 100 / total) if total > 0 else 0
            o.text(f'Usage: {pct}%', 0, 42)

        elif page == 'flash':
            o.text('--- Flash ---', 0, 0)
            try:
                st = os.statvfs('/')
                total = st[0] * st[2]
                free = st[0] * st[3]
                used = total - free
                o.text(f'Total: {total//1024}KB', 0, 12)
                o.text(f'Used:  {used//1024}KB', 0, 22)
                o.text(f'Free:  {free//1024}KB', 0, 32)
                pct = int(used * 100 / total) if total > 0 else 0
                o.text(f'Usage: {pct}%', 0, 42)
            except:
                o.text('Error reading flash', 0, 12)

        elif page == 'info':
            o.text('--- System ---', 0, 0)
            try:
                from machine import freq
                f = freq()
                o.text(f'CPU: {f//1000000}MHz', 0, 12)
            except:
                o.text('CPU: ???', 0, 12)
            try:
                import network
                wlan = network.WLAN(network.STA_IF)
                if wlan.isconnected():
                    ip = wlan.ifconfig()[0]
                    o.text(f'WiFi: {ip}', 0, 22)
                else:
                    o.text('WiFi: off', 0, 22)
            except:
                o.text('WiFi: N/A', 0, 22)
            o.text('ESP32-P4 Nano', 0, 32)
            o.text('Waveshare', 0, 42)

        o.show()

    def _draw_text(self):
        o = self._oled
        o.fill(0)
        text = self._text
        y = 0
        while text and y < 64:
            line, text = text[:16], text[16:]
            o.text(line, 0, y)
            y += 10
        o.show()

    def _draw_dvd(self):
        o = self._oled
        x, y = self._dvd_x, self._dvd_y
        dx, dy = self._dvd_dx, self._dvd_dy
        x += dx
        y += dy
        if x <= 0 or x >= 110:
            dx = -dx
        if y <= 0 or y >= 50:
            dy = -dy
        x = max(0, min(110, x))
        y = max(0, min(50, y))
        self._dvd_x, self._dvd_y = x, y
        self._dvd_dx, self._dvd_dy = dx, dy
        o.fill(0)
        o.text('DVD', x, y)
        o.show()

    def _draw_wave(self):
        o = self._oled
        if not hasattr(self, '_wave_frame'):
            self._wave_frame = 0
        o.fill(0)
        f = self._wave_frame
        prev_y1 = int(32 + 18 * math.sin(f * 0.08))
        for x in range(1, 128):
            y1 = int(32 + 18 * math.sin((x + f) * 0.08))
            if prev_y1 < y1:
                for py in range(prev_y1, y1 + 1):
                    if 0 <= py < 64:
                        o.pixel(x - 1, py, 1)
            elif prev_y1 > y1:
                for py in range(y1, prev_y1 + 1):
                    if 0 <= py < 64:
                        o.pixel(x - 1, py, 1)
            if 0 <= y1 < 64:
                o.pixel(x, y1, 1)
            prev_y1 = y1
        for x in range(0, 128, 2):
            y2 = int(32 + 12 * math.sin((x + f) * 0.05 + 2.1))
            if 0 <= y2 < 64:
                o.pixel(x, y2, 1)
                if y2 + 1 < 64:
                    o.pixel(x, y2 + 1, 1)
        self._wave_frame += 3
        o.show()

    def _draw_clock(self):
        o = self._oled
        o.fill(0)
        try:
            from machine import RTC
            dt = RTC().datetime()
            h, m, s = dt[4], dt[5], dt[6]
        except:
            t = time.time()
            h = (t // 3600) % 24
            m = (t // 60) % 60
            s = t % 60
        o.text('Clock', 40, 0)
        o.text('{:02d}:{:02d}:{:02d}'.format(h, m, s), 16, 24)
        o.show()

    def _draw_matrix(self):
        o = self._oled
        o.fill(0)
        for col in self._matrix_cols:
            y = col['y']
            cx = col['x']
            speed = col['speed']
            chars = col['chars']
            for i in range(7, -1, -1):
                py = y + i * 8
                if -7 <= py < 64:
                    ci = chars[i]
                    if i == 7:
                        o.fill_rect(cx, py, 6, 7, 1)
                    elif i >= 5:
                        o.text(MATRIX_CHARS[ci], cx, py)
                    elif i >= 3 and ci % 2 == 0:
                        o.pixel(cx + 1, py + 2, 1)
                        o.pixel(cx + 4, py + 5, 1)
            col['y'] += speed
            if col['y'] > 72:
                col['y'] = random.randint(-40, -8)
                col['speed'] = random.randint(1, 4)
                col['chars'] = [random.randint(0, len(MATRIX_CHARS) - 1) for _ in range(8)]
        o.show()

    def _draw_fire(self):
        o = self._oled
        if not hasattr(self, '_fire_heat'):
            self._fire_heat = [0] * 128
        heat = self._fire_heat
        new_heat = [0] * 128
        for x in range(128):
            h = heat[x]
            if x > 0:
                h = (h + heat[x - 1]) // 2
            if x < 127:
                h = (h + heat[x + 1]) // 2
            new_heat[x] = max(0, h - random.randint(1, 4))
        for x in range(128):
            if random.randint(0, 2) == 0:
                new_heat[x] = min(60, new_heat[x] + random.randint(10, 30))
        self._fire_heat = new_heat
        o.fill(0)
        for x in range(0, 128, 2):
            h = new_heat[x]
            if h > 0:
                flicker = random.randint(-4, 4)
                h = max(1, min(63, h + flicker))
                top = 64 - h
                o.fill_rect(x, top, 2, h, 1)
                if h > 15 and random.randint(0, 4) == 0:
                    gap_y = top + random.randint(2, h // 3)
                    gap_h = random.randint(1, 3)
                    o.fill_rect(x, gap_y, 2, gap_h, 0)
        o.show()

    def _draw_starfield(self):
        o = self._oled
        for star in self._star_field:
            if 'z' not in star:
                star['z'] = random.randint(1, 5)
        o.fill(0)
        for star in self._star_field:
            z = star['z']
            star['x'] -= star['speed'] * z
            if star['x'] < 0:
                star['x'] = 127
                star['y'] = random.randint(0, 63)
                star['z'] = random.randint(1, 5)
            px = int(star['x'])
            py = int(star['y'])
            if 0 <= px < 128 and 0 <= py < 64:
                if z <= 1:
                    o.fill_rect(px, py, 2, 2, 1)
                elif z <= 2:
                    streak = min(3, int(star['speed'] * z))
                    for sx in range(px, min(128, px + streak)):
                        o.pixel(sx, py, 1)
                else:
                    o.pixel(px, py, 1)
        o.show()

    def _draw_bounce(self):
        o = self._oled
        if not hasattr(self, '_bounce_trails'):
            self._bounce_trails = []
            self._bounce_flash = 0
        x, y = self._bounce_x, self._bounce_y
        dx, dy = self._bounce_dx, self._bounce_dy
        x += dx
        y += dy
        hit_x = False
        hit_y = False
        if x <= 0 or x >= 122:
            dx = -dx
            hit_x = True
        if y <= 0 or y >= 58:
            dy = -dy
            hit_y = True
        if hit_x and hit_y:
            self._bounce_flash = 3
        x = max(0, min(122, x))
        y = max(0, min(58, y))
        self._bounce_trails.append((x, y))
        if len(self._bounce_trails) > 4:
            self._bounce_trails.pop(0)
        self._bounce_x, self._bounce_y = x, y
        self._bounce_dx, self._bounce_dy = dx, dy
        if self._bounce_flash > 0:
            o.fill(1)
            self._bounce_flash -= 1
            o.show()
            return
        o.fill(0)
        speed = abs(dx) + abs(dy)
        if speed > 2:
            for s in range(1, min(speed, 4) + 1):
                sx = x - dx * s
                sy = y - dy * s
                sz = max(2, 6 - s * 2)
                if 0 <= sx < 128 and 0 <= sy < 64:
                    o.fill_rect(sx, sy, sz, sz, 1)
        trail_sizes = [4, 3, 2]
        for i in range(len(self._bounce_trails) - 1):
            tx, ty = self._bounce_trails[i]
            sz = trail_sizes[min(i, 2)]
            if 0 <= tx < 128 and 0 <= ty < 64:
                o.fill_rect(tx, ty, sz, sz, 1)
        o.fill_rect(x, y, 6, 6, 1)
        o.pixel(x, y, 0)
        o.pixel(x + 5, y, 0)
        o.pixel(x, y + 5, 0)
        o.pixel(x + 5, y + 5, 0)
        o.show()

    def _draw_plasma(self):
        o = self._oled
        t = time.ticks_ms() // 60
        o.fill(0)
        for x in range(0, 128, 2):
            for y in range(0, 64, 2):
                v1 = math.sin(x * 0.1 + t * 0.12)
                v2 = math.sin(y * 0.15 + t * 0.08)
                v3 = math.sin((x + y) * 0.07 + t * 0.05)
                v = (v1 + v2 + v3) / 3.0
                if v > 0.1:
                    o.fill_rect(x, y, 2, 2, 1)
        o.show()

    def _draw_rain(self):
        o = self._oled
        if not hasattr(self, '_rain_splashes'):
            self._rain_splashes = []
        o.fill(0)
        wind = math.sin(time.ticks_ms() * 0.001) * 0.5
        alive = []
        for splash in self._rain_splashes:
            t = splash['t']
            r = splash['r']
            if t <= r:
                cx = splash['x']
                cy = splash['y']
                o.hline(cx - t, cy, t * 2 + 1, 1)
                splash['t'] = t + 1
                alive.append(splash)
        self._rain_splashes = alive
        for drop in self._rain_drops:
            y = drop['y']
            x = drop['x']
            for i in range(3):
                if 0 <= y - i < 64:
                    o.pixel(int(x), y - i, 1)
            drop['y'] += drop['speed']
            drop['x'] += wind
            if drop['y'] >= 63:
                self._rain_splashes.append({'x': int(x), 'y': 63, 't': 0, 'r': 4})
                drop['y'] = random.randint(-30, -5)
                drop['x'] = random.randint(0, 127)
                drop['speed'] = random.randint(2, 5)
            if drop['x'] < 0:
                drop['x'] = 127
            elif drop['x'] >= 128:
                drop['x'] = 0
        o.show()

    def _draw_fireworks(self):
        o = self._oled
        if not self._fw_particles:
            self._fw_x = random.randint(20, 108)
            self._fw_y = random.randint(15, 50)
            for _ in range(15):
                angle = random.random() * 6.28
                speed = random.random() * 2 + 0.5
                self._fw_particles.append({
                    'x': float(self._fw_x),
                    'y': float(self._fw_y),
                    'dx': math.cos(angle) * speed,
                    'dy': math.sin(angle) * speed,
                    'life': random.randint(8, 16)
                })
        o.fill(0)
        alive = False
        for p in self._fw_particles:
            if p['life'] > 0:
                alive = True
                px = int(p['x'])
                py = int(p['y'])
                if 0 <= px < 128 and 0 <= py < 64:
                    o.pixel(px, py, 1)
                p['x'] += p['dx']
                p['y'] += p['dy']
                p['dy'] += 0.08
                p['life'] -= 1
        if not alive:
            self._fw_particles = []
        o.show()

    def _draw_dna(self):
        o = self._oled
        o.fill(0)
        self._dna_phase += 0.12
        for x in range(0, 128, 3):
            y1 = int(32 + 22 * math.sin(x * 0.06 + self._dna_phase))
            y2 = int(32 + 22 * math.sin(x * 0.06 + self._dna_phase + 3.14159))
            if 0 <= y1 < 63:
                o.pixel(x, y1, 1)
                o.pixel(x + 1, y1, 1)
                o.pixel(x, y1 - 1, 1)
                o.pixel(x + 1, y1 + 1, 1)
            if 0 <= y2 < 63:
                o.pixel(x, y2, 1)
                o.pixel(x + 1, y2, 1)
                o.pixel(x, y2 - 1, 1)
                o.pixel(x + 1, y2 + 1, 1)
            if x % 10 == 0 and abs(y1 - y2) > 4:
                for dy in range(min(y1, y2) + 1, max(y1, y2)):
                    if 0 <= dy < 64:
                        o.pixel(x, dy, 1)
                o.fill_rect(x - 1, y1 - 1, 3, 3, 1)
                o.fill_rect(x - 1, y2 - 1, 3, 3, 1)
                o.pixel(x, y1, 0)
                o.pixel(x, y2, 0)
        o.show()

    def _draw_equalizer(self):
        o = self._oled
        o.fill(0)
        bar_w = 8
        for i in range(16):
            h = self._eq_bars[i]
            h += random.randint(-3, 3)
            h = max(3, min(58, h))
            self._eq_bars[i] = h
            x = i * bar_w
            for row in range(0, h, 3):
                y = 62 - row
                o.fill_rect(x + 1, y, bar_w - 2, 2, 1)
        o.show()

    def _draw_pong(self):
        o = self._oled
        if not hasattr(self, '_pong_trail'):
            self._pong_trail = []
            self._pong_hit = 0
        bx, by = self._pong_bx, self._pong_by
        bdx, bdy = self._pong_bdx, self._pong_bdy
        ly, ry = self._pong_ly, self._pong_ry
        bx += bdx
        by += bdy
        hit = False
        if by <= 0 or by >= 61:
            bdy = -bdy
        if bx <= 4 and ly <= by <= ly + 12:
            bdx = -bdx
            hit = True
        elif bx <= 0:
            self._pong_rscore += 1
            bx, by = 64, 32
            bdx = abs(bdx)
        if bx >= 123 and ry <= by <= ry + 12:
            bdx = -bdx
            hit = True
        elif bx >= 127:
            self._pong_lscore += 1
            bx, by = 64, 32
            bdx = -abs(bdx)
        if hit:
            self._pong_hit = 3
        self._pong_trail.append((int(bx), int(by)))
        if len(self._pong_trail) > 5:
            self._pong_trail.pop(0)
        if by < ly + 6:
            ly -= 1
        elif by > ly + 6:
            ly += 1
        if by < ry + 6:
            ry -= 1
        elif by > ry + 6:
            ry += 1
        ly = max(0, min(52, ly))
        ry = max(0, min(52, ry))
        self._pong_bx, self._pong_by = bx, by
        self._pong_bdx, self._pong_bdy = bdx, bdy
        self._pong_ly, self._pong_ry = ly, ry
        o.fill(0)
        for y in range(0, 64, 4):
            o.pixel(63, y, 1)
            o.pixel(64, y, 1)
        for i in range(len(self._pong_trail) - 1):
            tx, ty = self._pong_trail[i]
            if 0 <= tx < 128 and 0 <= ty < 64:
                o.pixel(tx, ty, 1)
        pw = 4
        ph = 12
        if self._pong_hit > 0:
            o.fill_rect(0, ly - 1, pw, ph + 2, 1)
            o.fill_rect(124, ry - 1, pw, ph + 2, 1)
            self._pong_hit -= 1
        else:
            o.fill_rect(0, ly, pw, ph, 1)
            o.fill_rect(124, ry, pw, ph, 1)
        o.fill_rect(int(bx), int(by), 3, 3, 1)
        o.text(f'{self._pong_lscore}', 30, 0)
        o.text(f'{self._pong_rscore}', 90, 0)
        o.show()

    def _draw_lava(self):
        o = self._oled
        t = time.ticks_ms() // 80
        o.fill(0)
        heat = [0] * 64
        for blob in self._lava_blobs:
            blob['y'] += blob['dy']
            if blob['y'] < -blob['r']:
                blob['y'] = 64 + blob['r']
                blob['x'] = random.randint(10, 118)
                blob['r'] = random.randint(5, 10)
            blob['dy'] -= 0.01
            if blob['dy'] < -0.8:
                blob['dy'] = -0.2
            cx = int(blob['x'])
            cy = int(blob['y'])
            r = blob['r']
            for dy in range(-r, r + 1):
                py = cy + dy
                if 0 <= py < 64:
                    dx = int(math.sqrt(max(0, r * r - dy * dy)))
                    strength = int((1.0 - abs(dy) / max(r, 1)) * 8)
                    for px in range(max(0, cx - dx), min(128, cx + dx)):
                        heat[py] = max(heat[py], strength)
        for x in range(128):
            col_idx = x % 64
            h = heat[col_idx]
            if h > 0:
                wobble = int(math.sin(x * 0.2 + t * 0.15) * 2)
                base_y = 60 + wobble
                fill_h = min(h * 3, 58)
                if fill_h > 0:
                    y_start = max(0, base_y - fill_h)
                    o.fill_rect(x, y_start, 1, base_y - y_start + 2, 1)
        o.show()

    def _draw_sparkle(self):
        o = self._oled
        o.fill(0)
        for star in self._sparkle_stars:
            star['phase'] += star['speed']
            brightness = (math.sin(star['phase']) + 1) * 0.5
            sx, sy = int(star['x']), int(star['y'])
            if brightness > 0.7:
                o.pixel(sx, sy, 1)
                o.pixel(sx - 1, sy, 1)
                o.pixel(sx + 1, sy, 1)
                o.pixel(sx, sy - 1, 1)
                o.pixel(sx, sy + 1, 1)
            elif brightness > 0.3:
                o.pixel(sx, sy, 1)
            if random.randint(0, 50) == 0:
                star['phase'] = star['phase'] + 3.14
        if random.randint(0, 30) == 0:
            sx = random.randint(0, 100)
            sy = random.randint(0, 50)
            for i in range(8):
                px = sx + i * 3
                py = sy + i
                if 0 <= px < 128 and 0 <= py < 64:
                    o.pixel(px, py, 1)
        o.show()

    def _draw_pulse(self):
        o = self._oled
        o.fill(0)
        self._pulse_r = (self._pulse_r + 1) % 50
        cx, cy = 64, 32
        for ring in range(3):
            r = (self._pulse_r + ring * 17) % 50
            if r > 0:
                for angle in range(0, 360, 4):
                    rad = angle * 3.14159 / 180
                    px = int(cx + r * math.cos(rad))
                    py = int(cy + r * math.sin(rad) * 0.6)
                    if 0 <= px < 128 and 0 <= py < 64:
                        o.pixel(px, py, 1)
                    if r > 5:
                        px2 = int(cx + (r - 1) * math.cos(rad))
                        py2 = int(cy + (r - 1) * math.sin(rad) * 0.6)
                        if 0 <= px2 < 128 and 0 <= py2 < 64:
                            o.pixel(px2, py2, 1)
        o.fill_rect(cx - 1, cy - 1, 3, 3, 1)
        o.show()

    def _draw_cube(self):
        o = self._oled
        o.fill(0)
        self._cube_angle += 0.06
        a = self._cube_angle
        b = a * 0.7
        verts = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                 (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        proj = []
        for vx, vy, vz in verts:
            rx = vx * math.cos(a) - vz * math.sin(a)
            rz = vx * math.sin(a) + vz * math.cos(a)
            ry = vy * math.cos(b) - rz * math.sin(b)
            rz2 = vy * math.sin(b) + rz * math.cos(b)
            scale = 20 / (4 + rz2)
            px = int(64 + rx * scale * 8)
            py = int(32 + ry * scale * 8)
            proj.append((px, py))
        for i, j in edges:
            x1, y1 = proj[i]
            x2, y2 = proj[j]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x2 > x1 else -1
            sy = 1 if y2 > y1 else -1
            err = dx - dy
            cx, cy = x1, y1
            while True:
                if 0 <= cx < 128 and 0 <= cy < 64:
                    o.pixel(cx, cy, 1)
                if cx == x2 and cy == y2:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    cx += sx
                if e2 < dx:
                    err += dx
                    cy += sy
        for px, py in proj:
            if 0 <= px < 128 and 0 <= py < 64:
                o.fill_rect(px - 1, py - 1, 3, 3, 1)
        o.show()

    def _draw_textscroll(self):
        o = self._oled
        o.fill(0)
        x = self._scroll_x
        o.text(self._scroll_text, x, 24)
        self._scroll_x -= 2
        tw = len(self._scroll_text) * 8
        if self._scroll_x < -tw:
            self._scroll_x = 128
        o.show()

    def _msnake_food_pos(self):
        while True:
            fx = random.randint(0, 15)
            fy = random.randint(0, 7)
            if (fx, fy) not in self._msnake:
                return (fx, fy)

    def _draw_minisnake(self):
        o = self._oled
        hx, hy = self._msnake[0]
        nx = (hx + self._msnake_dx) % 16
        ny = (hy + self._msnake_dy) % 8
        head = (nx, ny)
        if head in self._msnake:
            self._msnake = [(5, 3), (4, 3), (3, 3)]
            self._msnake_dx = 1
            self._msnake_dy = 0
            self._msnake_score = 0
            self._msnake_food = self._msnake_food_pos()
            o.fill(0)
            o.text('GAME OVER', 24, 24)
            o.show()
            time.sleep_ms(800)
            return
        self._msnake.insert(0, head)
        if head == self._msnake_food:
            self._msnake_score += 1
            self._msnake_food = self._msnake_food_pos()
        else:
            self._msnake.pop()
        o.fill(0)
        for sx, sy in self._msnake:
            o.fill_rect(sx * 8, sy * 8, 7, 7, 1)
        fx, fy = self._msnake_food
        o.fill_rect(fx * 8, fy * 8, 7, 7, 1)
        o.text(str(self._msnake_score), 0, 0)
        o.show()
        time.sleep_ms(200)

    def _draw_heart(self):
        o = self._oled
        t = time.ticks_ms() // 200
        scale = abs(math.sin(t * 0.5)) * 2 + 0.5
        o.fill(0)
        cx, cy = 64, 32
        for angle in range(0, 360, 3):
            rad = angle * 3.14159 / 180
            hx = 16 * math.sin(rad) ** 3
            hy = -(13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
            px = int(cx + hx * scale)
            py = int(cy + hy * scale)
            if 0 <= px < 128 and 0 <= py < 64:
                o.pixel(px, py, 1)
        o.show()

    def _draw_invader(self):
        o = self._oled
        self._invader_frame += 1
        frame = (self._invader_frame // 10) % 2
        o.fill(0)
        patterns = [
            [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x5A, 0x81, 0x42],
            [0x18, 0x3C, 0x7E, 0xDB, 0xFF, 0x24, 0x5A, 0xA5],
        ]
        pat = patterns[frame]
        ox, oy = 44, 12
        for row in range(8):
            bits = pat[row]
            for col in range(8):
                if bits & (0x80 >> col):
                    o.fill_rect(ox + col * 4, oy + row * 4, 4, 4, 1)
        o.show()

    def _draw_spiral(self):
        o = self._oled
        o.fill(0)
        self._spiral_phase += 0.1
        for i in range(200):
            t = i * 0.15
            r = t * 0.6
            x = int(64 + r * math.cos(t + self._spiral_phase))
            y = int(32 + r * math.sin(t + self._spiral_phase))
            if 0 <= x < 128 and 0 <= y < 64:
                o.pixel(x, y, 1)
        o.show()

    def _draw_boot(self):
        o = self._oled
        if not self._boot_done:
            msgs = ['Espelt OS v1.0', 'ESP32-P4 @ 360MHz', 'RAM: 320KB', 'USB: OK', 'OLED: OK', 'WiFi: scan...', 'Ready.']
            t = time.ticks_ms() // 600
            idx = t % (len(msgs) + 2)
            while len(self._boot_lines) < idx and len(self._boot_lines) < len(msgs):
                self._boot_lines.append(msgs[len(self._boot_lines)])
            if len(self._boot_lines) >= len(msgs):
                self._boot_done = True
        o.fill(0)
        visible = self._boot_lines[-8:]
        for i, line in enumerate(visible):
            o.text('> ' + line[:14], 0, i * 8)
        o.show()

    def _draw_glitch(self):
        o = self._oled
        for _ in range(8):
            y = random.randint(0, 63)
            w = random.randint(10, 60)
            x = random.randint(0, 127 - w)
            o.fill_rect(x, y, w, random.randint(1, 3), random.randint(0, 1))
        o.show()

    def _draw_disco(self):
        o = self._oled
        if not hasattr(self, '_disco_pattern'):
            self._disco_pattern = 0
            self._disco_frames = 0
        self._disco_frames += 1
        if self._disco_frames % 10 == 0:
            o.fill(1)
            o.show()
            return
        if self._disco_frames % 3 == 0:
            self._disco_pattern = (self._disco_pattern + 1) % 6
        o.fill(0)
        p = self._disco_pattern
        if p == 0:
            for row in range(0, 64, 8):
                for col in range(0, 128, 8):
                    if ((row // 8) + (col // 8)) % 2 == 0:
                        o.fill_rect(col, row, 8, 8, 1)
        elif p == 1:
            for _ in range(80):
                o.pixel(random.randint(0, 127), random.randint(0, 63), 1)
        elif p == 2:
            for y in range(0, 64, 4):
                o.hline(0, y, 128, 1)
        elif p == 3:
            for x in range(0, 128, 4):
                o.vline(x, 0, 64, 1)
        elif p == 4:
            off = (self._disco_frames * 3) % 16
            for x in range(0, 128, 8):
                for i in range(8):
                    y = (x + off + i * 2) % 64
                    o.pixel(x, y, 1)
        elif p == 5:
            cx, cy = 64, 32
            for r in range(4, 30, 6):
                rr = (r + self._disco_frames * 2) % 30
                for angle in range(0, 360, 30):
                    rad = angle * 3.14159 / 180
                    px = int(cx + rr * math.cos(rad))
                    py = int(cy + rr * math.sin(rad))
                    if 0 <= px < 128 and 0 <= py < 64:
                        o.pixel(px, py, 1)
        o.show()

    def _draw_binary(self):
        o = self._oled
        if not hasattr(self, '_binary_cols'):
            self._binary_cols = []
            for i in range(16):
                self._binary_cols.append({
                    'x': i * 8, 'y': random.randint(-40, 0),
                    'speed': random.randint(1, 3),
                    'chars': [random.randint(0, 1) for _ in range(9)]
                })
        o.fill(0)
        for col in self._binary_cols:
            cx = col['x']
            cy = col['y']
            chars = col['chars']
            for i, ch in enumerate(chars):
                py = cy + i * 8
                if -8 < py < 64:
                    if i == len(chars) - 1:
                        o.fill_rect(cx - 1, py - 1, 10, 10, 1)
                        o.text(str(ch), cx, py, 0)
                    else:
                        o.text(str(ch), cx, py, 1)
            if random.randint(0, 8) == 0:
                idx = random.randint(0, len(chars) - 1)
                col['chars'][idx] = 1 - col['chars'][idx]
            col['y'] += col['speed']
            if col['y'] > 72:
                col['y'] = random.randint(-30, -5)
                col['speed'] = random.randint(1, 3)
                col['chars'] = [random.randint(0, 1) for _ in range(9)]
        o.show()

    def _draw_eye(self):
        o = self._oled
        o.fill(0)
        cx, cy = 64, 32
        if random.randint(0, 25) == 0:
            self._eye_tx = random.randint(35, 93)
            self._eye_ty = random.randint(18, 46)
        if random.randint(0, 80) == 0:
            self._eye_tx = cx + random.randint(-40, 40)
            self._eye_ty = cy + random.randint(-20, 20)
        dx = self._eye_tx - self._eye_px
        dy = self._eye_ty - self._eye_py
        dist = math.sqrt(dx * dx + dy * dy)
        speed = 0.15 if dist > 10 else 0.08
        self._eye_px += int(dx * speed)
        self._eye_py += int(dy * speed)
        for angle in range(0, 360, 2):
            rad = angle * 3.14159 / 180
            ex = int(cx + 38 * math.cos(rad))
            ey = int(cy + 18 * math.sin(rad))
            if 0 <= ex < 128 and 0 <= ey < 64:
                o.pixel(ex, ey, 1)
        px, py = int(self._eye_px), int(self._eye_py)
        for angle in range(0, 360, 3):
            rad = angle * 3.14159 / 180
            ix = int(px + 10 * math.cos(rad))
            iy = int(py + 10 * math.sin(rad))
            if 0 <= ix < 128 and 0 <= iy < 64:
                o.pixel(ix, iy, 1)
        o.fill_rect(px - 4, py - 4, 8, 8, 1)
        o.fill_rect(px - 2, py - 2, 4, 4, 0)
        o.pixel(px - 1, py - 2, 1)
        o.show()

    def _draw_checker(self):
        o = self._oled
        self._checker_phase = (self._checker_phase + 1) % 100
        invert = self._checker_phase > 50
        for row in range(0, 64, 8):
            for col in range(0, 128, 8):
                on = ((row // 8) + (col // 8)) % 2 == 0
                if invert:
                    on = not on
                if on:
                    o.fill_rect(col, row, 8, 8, 1)
        o.show()

    def _draw_lightning(self):
        o = self._oled
        if not hasattr(self, '_lightning_fade'):
            self._lightning_fade = 0
            self._lightning_wait = 0
        now = time.ticks_ms()
        if self._lightning_wait > 0:
            self._lightning_wait -= 1
            o.fill(0)
            o.show()
            return
        if not self._lightning_bolt or time.ticks_diff(now, self._lightning_timer) > 600:
            main_bolt = []
            x = random.randint(40, 88)
            y = 0
            while y < 64:
                nx = x + random.randint(-5, 5)
                nx = max(10, min(118, nx))
                ny = y + random.randint(3, 8)
                main_bolt.append((x, y, nx, min(ny, 63)))
                x = nx
                y = ny
            branches = []
            for si in range(1, len(main_bolt) - 1):
                if random.randint(0, 3) == 0:
                    bx, by = main_bolt[si][2], main_bolt[si][3]
                    bd = random.choice([-1, 1])
                    for _ in range(random.randint(2, 4)):
                        bnx = bx + bd * random.randint(2, 4)
                        bny = by + random.randint(2, 5)
                        branches.append((bx, by, bnx, min(bny, 63)))
                        bx, by = bnx, bny
            self._lightning_bolt = main_bolt + branches
            self._lightning_timer = now
            self._lightning_fade = 4
            o.fill(1)
            o.show()
            return
        if self._lightning_fade > 0:
            o.fill(0)
            for x1, y1, x2, y2 in self._lightning_bolt:
                steps = max(abs(x2 - x1), abs(y2 - y1), 1)
                for s in range(steps + 1):
                    t = s / steps
                    px = int(x1 + (x2 - x1) * t)
                    py = int(y1 + (y2 - y1) * t)
                    if 0 <= px < 128 and 0 <= py < 64:
                        if self._lightning_fade >= 3:
                            o.pixel(px, py, 1)
                        elif self._lightning_fade == 2:
                            if (px + py) % 2 == 0:
                                o.pixel(px, py, 1)
                        else:
                            if (px + py) % 3 == 0:
                                o.pixel(px, py, 1)
            self._lightning_fade -= 1
            if self._lightning_fade == 0:
                self._lightning_wait = random.randint(3, 8)
            o.show()

    def _draw_helplogo(self):
        o = self._oled
        if not hasattr(self, '_hl_x'):
            self._hl_x, self._hl_y = 40, 20
            self._hl_dx, self._hl_dy = 2, 1
        self._hl_x += self._hl_dx
        self._hl_y += self._hl_dy
        if self._hl_x <= 0 or self._hl_x >= 96:
            self._hl_dx = -self._hl_dx
        if self._hl_y <= 0 or self._hl_y >= 50:
            self._hl_dy = -self._hl_dy
        o.fill(0)
        o.text('HELP', self._hl_x, self._hl_y)
        o.show()

    def _draw_skull(self):
        o = self._oled
        blink = (time.ticks_ms() // 1000) % 4 == 0
        o.fill(0)
        o.text('  .-"""-.  ', 8, 4)
        o.text(' /        \\', 8, 12)
        if blink:
            o.text(' |  -  - |', 8, 20)
        else:
            o.text(' |  o  o |', 8, 20)
        o.text(' |   __   |', 8, 28)
        o.text(' \\  \\/  /', 8, 36)
        o.text('  '-...-'  ', 8, 44)
        o.show()

    def _draw_cat(self):
        o = self._oled
        self._cat_ear = (self._cat_ear + 1) % 20
        ear_offset = 1 if self._cat_ear < 10 else 0
        o.fill(0)
        o.text(' /\\_/\\', 24, 4 + ear_offset)
        o.text('( o.o )', 24, 14)
        o.text(' > ^ <', 24, 24)
        o.text('/|   |\\', 24, 34)
        o.text('(_|   |_)', 20, 44)
        o.show()

    def _draw_dance(self):
        o = self._oled
        self._dance_timer += 1
        if self._dance_timer > 5:
            self._dance_timer = 0
            self._dance_pose = (self._dance_pose + 1) % 3
        o.fill(0)
        poses = [
            ('  O  ', ' /|\\ ', ' / \\ '),
            ('  O  ', ' /|\\/', ' / \\ '),
            (' \\O/ ', '  |  ', ' / \\ '),
        ]
        head, body, legs = poses[self._dance_pose]
        o.text(head, 48, 16)
        o.text(body, 48, 26)
        o.text(legs, 48, 36)
        o.text('DANCE', 40, 52)
        o.show()

    def _draw_doom(self):
        o = self._oled
        self._doom_timer += 1
        if self._doom_timer > 5:
            self._doom_timer = 0
            self._doom_scale += 1
            if self._doom_scale > 5:
                self._doom_scale = 1
        o.fill(0)
        s = self._doom_scale
        w = 6 * s
        h = 8 * s
        ox = 64 - w // 2
        oy = 32 - h // 2
        if w > 0 and h > 0 and ox >= 0 and oy >= 0:
            o.fill_rect(ox, oy, w, h, 1)
            o.fill_rect(ox + 2, oy + 2, max(1, w - 4), max(1, h - 4), 0)
        o.show()

    def _draw_potato(self):
        o = self._oled
        o.fill(0)
        t = time.ticks_ms() // 3000
        msgs = ['potato', '  potato', '   potato', 'potato.']
        msg = msgs[t % len(msgs)]
        o.text('    .-""""-.    ', 4, 8)
        o.text('   /        \\   ', 4, 16)
        o.text('  |  ()  ()  |  ', 4, 24)
        o.text('  |    __    |  ', 4, 32)
        o.text('   \\  \\__/  /   ', 4, 40)
        o.text('    `-....-\'    ', 4, 48)
        o.text(msg, 32, 58)
        o.show()

    def _draw_timer(self):
        o = self._oled
        now = time.ticks_ms()
        remaining = time.ticks_diff(self._timer_end, now)
        if remaining <= 0:
            if not self._timer_done:
                self._timer_done = True
                self._timer_flash_t = now
            elapsed = time.ticks_diff(now, self._timer_flash_t)
            o.fill(0)
            if (elapsed // 200) & 1:
                o.text('TIME UP!', 32, 20)
                o.rect(16, 16, 96, 20, 1)
            o.show()
            return elapsed > 3000
        secs = remaining // 1000
        total = self._timer_secs
        mins = secs // 60
        s = secs % 60
        o.fill(0)
        o.text('TIMER', 44, 0)
        o.hline(0, 10, 128, 1)
        o.text('{:02d}:{:02d}'.format(mins, s), 32, 20)
        bar_w = int(120 * secs / total) if total > 0 else 0
        o.rect(4, 40, 120, 8, 1)
        o.fill_rect(4, 40, bar_w, 8, 1)
        pct = int(100 * secs / total) if total > 0 else 0
        o.text(str(pct) + '%', 52, 52)
        o.show()
        return False

    def _draw_stopwatch(self):
        o = self._oled
        now = time.ticks_ms()
        if self._sw_running:
            self._sw_elapsed = time.ticks_diff(now, self._sw_start)
        ms = self._sw_elapsed
        mins = ms // 60000
        secs = (ms % 60000) // 1000
        centis = (ms % 1000) // 10
        o.fill(0)
        o.text('STOPWATCH', 24, 0)
        o.hline(0, 10, 128, 1)
        o.text('{:02d}:{:02d}.{:02d}'.format(mins, secs, centis), 16, 20)
        status = 'RUNNING' if self._sw_running else 'PAUSED'
        o.text(status, 40, 40)
        if self._sw_running and (ms // 500) & 1:
            o.fill_rect(60, 52, 8, 8, 1)
        o.show()
        return False

    def _draw_chicken(self):
        o = self._oled
        self._chicken_frame = (self._chicken_frame + 1) % 4
        x = self._chicken_x
        d = self._chicken_dir
        f = self._chicken_frame
        o.fill(0)
        cy = 24
        # Body (always same position relative to x)
        o.fill_rect(x + 6, cy, 14, 10, 1)
        # Head
        if d > 0:
            o.fill_rect(x + 18, cy - 4, 7, 7, 1)
            o.pixel(x + 22, cy - 2, 0)  # eye
            o.fill_rect(x + 25, cy - 1, 3, 2, 1)  # beak
            o.fill_rect(x + 20, cy - 7, 2, 3, 1)  # comb
        else:
            o.fill_rect(x, cy - 4, 7, 7, 1)
            o.pixel(x + 2, cy - 2, 0)  # eye
            o.fill_rect(x - 3, cy - 1, 3, 2, 1)  # beak
            o.fill_rect(x + 4, cy - 7, 2, 3, 1)  # comb
        # Tail
        if d > 0:
            o.fill_rect(x + 1, cy - 3, 5, 5, 1)
        else:
            o.fill_rect(x + 14, cy - 3, 5, 5, 1)
        # Legs
        if f < 2:
            o.fill_rect(x + 8, cy + 10, 2, 6, 1)
            o.fill_rect(x + 16, cy + 10, 2, 4, 1)
        else:
            o.fill_rect(x + 8, cy + 10, 2, 4, 1)
            o.fill_rect(x + 16, cy + 10, 2, 6, 1)
        x += d * 2
        if x > 88 or x < 2:
            d = -d
            self._chicken_dir = d
        self._chicken_x = x
        o.text('chicken', 32, 56)
        o.show()

    def _draw_esp32(self):
        o = self._oled
        cx, cy = 64, 32
        r = 20
        a = self._esp_angle
        x = int(cx + r * math.cos(a))
        y = int(cy + r * math.sin(a))
        o.fill(0)
        o.text('ESP32', x - 12, y - 4)
        o.hline(0, 56, 128, 1)
        o.vline(64, 0, 64, 1)
        o.fill_rect(cx - 1, cy - 1, 3, 3, 1)
        self._esp_angle += 0.15
        if self._esp_angle > 6.28:
            self._esp_angle -= 6.28
        o.show()

    def _draw_pacman(self):
        o = self._oled
        px = self._pac_x
        mouth = self._pac_mouth
        o.fill(0)
        cy = 28
        import math
        mouth_angle = abs(math.sin(mouth * 0.5)) * 5
        o.fill_rect(px + 2, cy, 10, 12, 1)
        if mouth_angle > 2:
            o.fill_rect(px + 12, cy + 3, int(mouth_angle), 2, 0)
            o.fill_rect(px + 12, cy + 7, int(mouth_angle), 2, 0)
        o.pixel(px + 8, cy + 2, 0)
        self._pac_mouth = (self._pac_mouth + 1) % 12
        dot_y = cy + 5
        for i in range(32):
            dx = i * 4
            if self._pac_dots[i] and dx > px + 14:
                o.fill_rect(dx, dot_y, 2, 2, 1)
        for i in range(32):
            dx = i * 4
            if self._pac_dots[i] and dx <= px + 12:
                self._pac_dots[i] = 0
        self._pac_x += 2
        if self._pac_x > 130:
            self._pac_x = -15
            self._pac_dots = [1] * 32
        o.text('PAC-MAN', 36, 0)
        o.show()

    def _draw_tunnel(self):
        o = self._oled
        cx, cy = 64, 32
        phase = self._tunnel_phase
        o.fill(0)
        for i in range(8):
            depth = (phase + i * 4) % 32
            w = 32 - depth
            h = int(w * 0.6)
            if w > 0:
                x1 = cx - w
                y1 = cy - h
                o.rect(x1, y1, w * 2, h * 2, 1)
                if i % 2 == 0 and w > 8:
                    o.hline(cx - w + 4, cy - h + 4, w * 2 - 8, 1)
                    o.hline(cx - w + 4, cy + h - 4, w * 2 - 8, 1)
        self._tunnel_phase += 1
        if self._tunnel_phase >= 32:
            self._tunnel_phase = 0
        o.show()

    def _draw_typewriter(self):
        o = self._oled
        text = self._tw_text
        o.fill(0)
        o.text('>', 0, 0)
        if not self._tw_clearing:
            pos = self._tw_pos
            if pos <= len(text):
                shown = text[:pos]
                o.text(shown, 8, 0)
                if pos < len(text):
                    if pos % 2 == 0:
                        o.fill_rect(8 + pos * 6, 0, 5, 7, 1)
                else:
                    o.fill_rect(8 + pos * 6, 0, 5, 7, 1)
            self._tw_pos += 1
            if self._tw_pos > len(text) + 10:
                self._tw_clearing = True
                self._tw_clear_pos = len(text)
        else:
            cp = self._tw_clear_pos
            if cp >= 0:
                o.text(text[:cp], 8, 0)
                o.fill_rect(8 + cp * 6, 0, 5, 7, 1)
            self._tw_clear_pos -= 1
            if self._tw_clear_pos < -5:
                self._tw_clearing = False
                self._tw_pos = 0
        o.show()

    def _draw_radar(self):
        o = self._oled
        cx, cy = 64, 32
        r = 28
        o.fill(0)
        for ring_r in (r, r * 2 // 3, r // 3):
            for deg in range(0, 360, 3):
                rad = deg * 3.14159 / 180
                px = int(cx + ring_r * math.cos(rad))
                py = int(cy + ring_r * math.sin(rad))
                if 0 <= px < 128 and 0 <= py < 64:
                    o.pixel(px, py, 1)
        o.hline(cx - r, cy, r * 2, 1)
        o.vline(cx, cy - r, r * 2, 1)
        angle = self._radar_angle
        ex = int(cx + r * math.cos(angle))
        ey = int(cy + r * math.sin(angle))
        dx = abs(ex - cx)
        dy = abs(ey - cy)
        sx = 1 if ex > cx else -1
        sy = 1 if ey > cy else -1
        err = dx - dy
        lx, ly = cx, cy
        while True:
            if 0 <= lx < 128 and 0 <= ly < 64:
                o.pixel(lx, ly, 1)
            if lx == ex and ly == ey:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                lx += sx
            if e2 < dx:
                err += dx
                ly += sy
        for t in range(1, 6):
            ta = angle - t * 0.1
            tr = r * (6 - t) // 6
            if tr > 2:
                for step in range(0, tr, 4):
                    tx = int(cx + step * math.cos(ta))
                    ty = int(cy + step * math.sin(ta))
                    if 0 <= tx < 128 and 0 <= ty < 64:
                        o.pixel(tx, ty, 1)
        for blip in self._radar_blips:
            bx, by = blip['x'], blip['y']
            dx_b = bx - cx
            dy_b = by - cy
            if dx_b * dx_b + dy_b * dy_b <= r * r:
                blip['life'] -= 1
                if blip['life'] > 0:
                    o.fill_rect(bx - 1, by - 1, 3, 3, 1)
                else:
                    blip['x'] = random.randint(cx - r + 5, cx + r - 5)
                    blip['y'] = random.randint(cy - r + 5, cy + r - 5)
                    blip['life'] = random.randint(20, 50)
        o.fill_rect(cx - 1, cy - 1, 3, 3, 1)
        self._radar_angle += 0.1
        if self._radar_angle > 6.28:
            self._radar_angle -= 6.28
        o.text('RADAR', 44, 0)
        o.show()

    def _draw_tetrisfall(self):
        o = self._oled
        o.fill(0)
        blocks = self._tf_blocks
        shapes = [
            [(0,0),(1,0),(2,0),(3,0)],
            [(0,0),(1,0),(0,1),(1,1)],
            [(0,0),(1,0),(2,0),(1,1)],
            [(0,0),(0,1),(1,1),(2,1)],
            [(1,0),(2,0),(0,1),(1,1)],
        ]
        if random.randint(0, 3) == 0 and len(blocks) < 30:
            shape = shapes[random.randint(0, 4)]
            bx = random.randint(0, 28)
            blocks.append({'cells': [(bx + cx, cy) for cx, cy in shape], 'speed': random.randint(1, 2)})
        i = 0
        while i < len(blocks):
            b = blocks[i]
            if random.randint(0, 10 - b['speed']) == 0:
                new_cells = [(x, y + 1) for x, y in b['cells']]
                if any(y >= 15 for _, y in new_cells):
                    for x, y in b['cells']:
                        o.fill_rect(x * 4, (y + 1) * 4, 3, 3, 1)
                    self._tf_score += 1
                    blocks.pop(i)
                    continue
                else:
                    b['cells'] = new_cells
            for x, y in b['cells']:
                o.fill_rect(x * 4, y * 4, 3, 3, 1)
            i += 1
        o.hline(0, 63, 128, 1)
        o.text(str(self._tf_score), 0, 0)
        o.show()

    def _draw_firefly(self):
        o = self._oled
        o.fill(0)
        for dot in self._ff_dots:
            x, y = int(dot['x']), int(dot['y'])
            b = dot['brightness']
            import math
            glow = int((math.sin(b * 0.6) + 1) * 5)
            if glow > 6:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 <= x + dx < 128 and 0 <= y + dy < 64:
                            o.pixel(x + dx, y + dy, 1)
            elif glow > 3:
                o.pixel(x, y, 1)
            dot['brightness'] += 0.4
            if dot['brightness'] > 6.28:
                dot['brightness'] = 0
            dot['x'] += dot['dx'] * 0.3
            dot['y'] += dot['dy'] * 0.3
            if dot['x'] <= 2 or dot['x'] >= 125:
                dot['dx'] = -dot['dx']
            if dot['y'] <= 2 or dot['y'] >= 61:
                dot['dy'] = -dot['dy']
            if random.randint(0, 40) == 0:
                dot['dx'] = random.choice([-1, 0, 1])
                dot['dy'] = random.choice([-1, 0, 1])
        o.text('FIREFLY', 36, 0)
        o.show()

    def _draw_spectrum(self):
        o = self._oled
        o.fill(0)
        for i in range(16):
            target = random.randint(8, 55) if random.randint(0, 3) == 0 else self._spec_bars[i]
            self._spec_bars[i] += (target - self._spec_bars[i]) // 3
            if self._spec_bars[i] > self._spec_peaks[i]:
                self._spec_peaks[i] = self._spec_bars[i]
            else:
                self._spec_peaks[i] = max(0, self._spec_peaks[i] - 1)
            x = i * 8
            h = self._spec_bars[i]
            for row in range(int(h)):
                brightness = 1 if row < h - 4 else (row % 2 == 0)
                o.fill_rect(x, 63 - row, 6, 1, brightness)
            py = 63 - int(self._spec_peaks[i])
            o.fill_rect(x + 1, py, 4, 1, 1)
        o.show()

    def _draw_osnake(self):
        o = self._oled
        o.fill(0)
        head = self._osnake[0]
        nx = head[0] + self._osnake_dx
        ny = head[1] + self._osnake_dy
        if nx < 0 or nx > 15 or ny < 0 or ny > 7:
            self._osnake = [(5, 3), (4, 3), (3, 3)]
            self._osnake_food = self._osnake_food_pos()
            self._osnake_dx = 1
            self._osnake_dy = 0
            self._osnake_score = 0
            o.text('GAME OVER', 24, 24)
            o.show()
            time.sleep_ms(800)
            return
        if (nx, ny) in self._osnake:
            self._osnake = [(5, 3), (4, 3), (3, 3)]
            self._osnake_food = self._osnake_food_pos()
            self._osnake_dx = 1
            self._osnake_dy = 0
            self._osnake_score = 0
            o.text('GAME OVER', 24, 24)
            o.show()
            time.sleep_ms(800)
            return
        self._osnake.insert(0, (nx, ny))
        if (nx, ny) == self._osnake_food:
            self._osnake_score += 1
            self._osnake_food = self._osnake_food_pos()
        else:
            self._osnake.pop()
        for sx, sy in self._osnake:
            o.fill_rect(sx * 8, sy * 8, 6, 6, 1)
        fx, fy = self._osnake_food
        o.fill_rect(fx * 8, fy * 8, 6, 6, 1)
        if random.randint(0, 5) == 0:
            if self._osnake_dx == 0:
                self._osnake_dx = random.choice([-1, 1])
                self._osnake_dy = 0
            else:
                self._osnake_dy = random.choice([-1, 1])
                self._osnake_dx = 0
        o.text(str(self._osnake_score), 0, 0)
        o.show()

    def _draw_game_hud(self):
        o = self._oled
        o.fill(0)
        o.text(self._game_hud_name[:16], 0, 0)
        o.line(0, 10, 127, 10, 1)
        o.text(f'Score: {self._game_hud_score}', 0, 14)
        if self._game_hud_lives > 0:
            o.text(f'Lives: {self._game_hud_lives}', 0, 26)
        if self._game_hud_level > 1:
            o.text(f'Level: {self._game_hud_level}', 0, 38)
        o.show()

    def _draw_wlan(self):
        o = self._oled
        o.fill(0)
        o.text('--- WiFi ---', 0, 0)
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                cfg = wlan.ifconfig()
                ip = cfg[0]
                o.text(f'IP: {ip}', 0, 14)
                essid = wlan.config('essid')
                o.text(f'SSID: {essid[:14]}', 0, 26)
                o.text('Status: ON', 0, 38)
            else:
                o.text('Status: OFF', 0, 14)
                o.text('Not connected', 0, 26)
        except:
            o.text('N/A', 0, 14)
        o.show()

    def _draw_auto(self):
        if self._game_hud_name:
            self._draw_game_hud()
        else:
            self._draw_status_compact()

    def _draw_status_compact(self):
        o = self._oled
        o.fill(0)
        # Line 1: Time + WiFi
        try:
            t = time.localtime()
            ts = '%02d:%02d' % (t[3], t[4])
        except:
            ts = '??:??'
        wifi_sym = '\x07'  # will show as ? but we use text
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            wifi_str = 'WiFi:ON' if wlan.isconnected() else 'WiFi:OFF'
        except:
            wifi_str = 'WiFi:N/A'
        o.text(ts + ' ' + wifi_str, 0, 0)
        # Line 2: RAM + Flash
        free = gc.mem_free()
        alloc = gc.mem_alloc()
        total = free + alloc
        ram_pct = int(alloc * 100 / total) if total > 0 else 0
        o.text('RAM:' + str(100 - ram_pct) + '%', 0, 12)
        try:
            st = os.statvfs('/')
            flash_total = st[0] * st[2]
            flash_free = st[0] * st[3]
            fl_pct = int((1 - flash_free / flash_total) * 100) if flash_total > 0 else 0
            o.text(' Flash:' + str(fl_pct) + '%', 64, 12)
        except:
            pass
        # Line 3: Uptime
        try:
            ut = time.ticks_ms() // 1000
            if ut < 3600:
                ut_str = '%dm%ds' % (ut // 60, ut % 60)
            else:
                ut_str = '%dh%dm' % (ut // 3600, (ut % 3600) // 60)
            o.text('Up:' + ut_str, 0, 24)
        except:
            pass
        # Line 4: IP
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                ip = wlan.ifconfig()[0]
                o.text('IP:' + ip[:16], 0, 36)
            else:
                o.text('IP:none', 0, 36)
        except:
            o.text('IP:N/A', 0, 36)
        # Line 5: Last command
        if self._last_cmd:
            o.text('>' + self._last_cmd[:15], 0, 48)
        o.show()

    def _draw_notify(self):
        o = self._oled
        o.fill(0)
        o.text('--- Alert ---', 0, 0)
        t = self._notify_text
        if len(t) > 16:
            o.text(t[:16], 0, 16)
            o.text(t[16:32], 0, 28)
            if len(t) > 32:
                o.text(t[32:48], 0, 40)
        else:
            o.text(t, 0, 20)
        o.show()
        if time.ticks_ms() >= self._notify_end:
            self._mode = self._prev_mode

    def set_theme(self, theme_colors):
        """Set theme colors from dispatch.THEME_COLORS."""
        if theme_colors:
            self._theme = theme_colors
        else:
            self._theme = None

    def notify(self, text, duration_ms=2000):
        if not self._oled:
            return
        self._prev_mode = self._mode
        self._notify_text = text
        self._notify_end = time.ticks_add(time.ticks_ms(), duration_ms)
        self._mode = 'notify'

    def _draw_engine_status(self):
        o = self._oled
        o.fill(0)
        # Line 0: Engine name
        o.text('[' + self._engine_name + ']', 0, 0)
        # Lines 1-5: Status lines
        for i in range(5):
            if self._engine_lines[i]:
                o.text(self._engine_lines[i], 0, 10 + i * 10)
        o.show()
