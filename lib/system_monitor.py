import gc
import time
from machine import Pin, I2C
from lib.ssd1306 import SSD1306


class SystemMonitor:
    def __init__(self):
        self._oled = None
        self._last_update = 0
        self._init_oled()

    def _init_oled(self):
        try:
            i2c = I2C(0, scl=Pin(8), sda=Pin(7), freq=400000)
            self._oled = SSD1306(128, 64, i2c, addr=0x3C)
        except:
            pass

    def update(self):
        now = time.ticks_ms()
        if not self._oled or time.ticks_diff(now, self._last_update) < 1000:
            return
        self._last_update = now

        oled = self._oled
        oled.fill(0)

        oled.text('ESP32-P4', 0, 0)
        oled.text('Espelt', 0, 10)

        free = gc.mem_free()
        alloc = gc.mem_alloc()
        total = free + alloc
        used_pct = int(alloc * 100 / total) if total > 0 else 0

        oled.text(f'RAM: {used_pct}%', 0, 24)
        bar_w = 100
        bar_x = 14
        oled.rect(bar_x, 34, bar_w, 6, 1)
        fill_w = int(bar_w * used_pct / 100)
        if fill_w > 0:
            oled.fill_rect(bar_x, 34, fill_w, 6, 1)

        oled.text(f'{free//1024}KB free', 0, 44)

        try:
            import os
            st = os.statvfs('/')
            total_flash = st[0] * st[2]
            free_flash = st[0] * st[3]
            flash_pct = int((total_flash - free_flash) * 100 / total_flash) if total_flash > 0 else 0
            oled.text(f'Flash: {flash_pct}%', 0, 54)
        except:
            oled.text('Flash: N/A', 0, 54)

        oled.show()
