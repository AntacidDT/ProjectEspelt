import time
from micropython import const

_SETCONTRAST = const(0x81)
_DISPLAYALLON = const(0xA5)
_NORMALDISPLAY = const(0xA6)
_DISPLAYOFF = const(0xAE)
_DISPLAYON = const(0xAF)
_SETDISPLAYOFFSET = const(0xD3)
_SETDISPLAYCLOCKDIV = const(0xD5)
_SETPRECHARGE = const(0xD9)
_SETMULTIPLEX = const(0xA8)
_SETLOWCOLUMN = const(0x00)
_SETHIGHCOLUMN = const(0x10)
_SETSTARTLINE = const(0x40)
_CHARGEPUMP = const(0x8D)
_MEMORYMODE = const(0x20)
_COLUMNADDR = const(0x21)
_PAGEADDR = const(0x22)
_COMSCANDEC = const(0xC8)
_SETCOMPINS = const(0xDA)
_SETVCOMDETECT = const(0xDB)
_SETVALUE = const(0x30)
_SETVALUE_MASK = const(0x0F)
_SETVALUE_RESET = const(0x00)
_PAGEADDR_MASK = const(0x07)


class SSD1306:
    def __init__(self, width, height, i2c, addr=0x3C, buf=None):
        self.width = width
        self.height = height
        self._i2c = i2c
        self._addr = addr
        self._buf = buf if buf is not None else bytearray(width * ((height + 7) // 8))
        self._command = bytearray(2)
        self._init_display()

    def _write_cmd(self, cmd):
        self._i2c.writeto_mem(self._addr, 0x00, bytes([cmd]))

    def _init_display(self):
        init_seq = [
            _DISPLAYOFF,
            _SETDISPLAYCLOCKDIV, 0x80,
            _SETMULTIPLEX, self.height - 1,
            _SETDISPLAYOFFSET, 0x00,
            _SETSTARTLINE | 0x00,
            _CHARGEPUMP, 0x14,
            _MEMORYMODE, 0x00,
            _SETCOMPINS, 0x12 if self.height == 64 else 0x02,
            _SETCONTRAST, 0xCF,
            0xA1,
            _COMSCANDEC,
            _SETPRECHARGE, 0xF1,
            _SETVCOMDETECT, 0x40,
            0xA4,
            _NORMALDISPLAY,
            _DISPLAYON,
        ]
        for cmd in init_seq:
            self._write_cmd(cmd)
        time.sleep_ms(100)

    def contrast(self, val):
        self._write_cmd(_SETCONTRAST)
        self._write_cmd(val)

    def invert(self, invert):
        self._write_cmd(0xA6 if not invert else 0xA7)

    def display_off(self):
        self._write_cmd(_DISPLAYOFF)

    def display_on(self):
        self._write_cmd(_DISPLAYON)

    def show(self):
        self._write_cmd(_COLUMNADDR)
        self._write_cmd(0)
        self._write_cmd(self.width - 1)
        self._write_cmd(_PAGEADDR)
        self._write_cmd(0)
        self._write_cmd((self.height // 8) - 1)
        self._i2c.writeto_mem(self._addr, 0x40, self._buf)

    def fill(self, color):
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        self._buf[:] = bytes([fill] * len(self._buf))

    def pixel(self, x, y, color=None):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if color is None:
            color = 1
        offset = y // 8 * self.width + x
        if color:
            self._buf[offset] |= (1 << (y & 7))
        else:
            self._buf[offset] &= ~(1 << (y & 7))

    def text(self, s, x, y, color=1):
        for ch in s:
            self._draw_char(x, y, ch, color)
            x += 8
            if x > self.width - 8:
                x = 0
                y += 8

    def _draw_char(self, x, y, ch, color):
        code = ord(ch)
        if code < 32 or code > 126:
            return
        offset = (code - 32) * 5
        for i in range(5):
            col = FONT5X7[offset + i]
            for j in range(7):
                if col & (1 << j):
                    self.pixel(x + i, y + j, color)

    def hline(self, x, y, w, color=1):
        for i in range(w):
            self.pixel(x + i, y, color)

    def vline(self, x, y, h, color=1):
        for i in range(h):
            self.pixel(x, y + i, color)

    def rect(self, x, y, w, h, color=1):
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        for j in range(h):
            self.hline(x, y + j, w, color)

    def line(self, x0, y0, x1, y1, color=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy


FONT5X7 = (
    b'\x00\x00\x00\x00\x00'  # (space)
    b'\x00\x00\x5F\x00\x00'  # !
    b'\x00\x07\x00\x07\x00'  # "
    b'\x14\x7F\x14\x7F\x14'  # #
    b'\x24\x2A\x7F\x2A\x12'  # $
    b'\x23\x13\x08\x64\x62'  # %
    b'\x36\x49\x55\x22\x50'  # &
    b'\x00\x05\x03\x00\x00'  # '
    b'\x00\x1C\x22\x41\x00'  # (
    b'\x00\x41\x22\x1C\x00'  # )
    b'\x08\x2A\x1C\x2A\x08'  # *
    b'\x08\x08\x3E\x08\x08'  # +
    b'\x00\x50\x30\x00\x00'  # ,
    b'\x08\x08\x08\x08\x08'  # -
    b'\x00\x60\x60\x00\x00'  # .
    b'\x20\x10\x08\x04\x02'  # /
    b'\x3E\x51\x49\x45\x3E'  # 0
    b'\x00\x42\x7F\x40\x00'  # 1
    b'\x42\x61\x51\x49\x46'  # 2
    b'\x21\x41\x45\x4B\x31'  # 3
    b'\x18\x14\x12\x7F\x10'  # 4
    b'\x27\x45\x45\x45\x39'  # 5
    b'\x3C\x4A\x49\x49\x30'  # 6
    b'\x01\x71\x09\x05\x03'  # 7
    b'\x36\x49\x49\x49\x36'  # 8
    b'\x06\x49\x49\x29\x1E'  # 9
    b'\x00\x36\x36\x00\x00'  # :
    b'\x00\x56\x36\x00\x00'  # ;
    b'\x00\x08\x14\x22\x41'  # <
    b'\x14\x14\x14\x14\x14'  # =
    b'\x41\x22\x14\x08\x00'  # >
    b'\x02\x01\x51\x09\x06'  # ?
    b'\x32\x49\x79\x41\x3E'  # @
    b'\x7E\x11\x11\x11\x7E'  # A
    b'\x7F\x49\x49\x49\x36'  # B
    b'\x3E\x41\x41\x41\x22'  # C
    b'\x7F\x41\x41\x22\x1C'  # D
    b'\x7F\x49\x49\x49\x41'  # E
    b'\x7F\x09\x09\x01\x01'  # F
    b'\x3E\x41\x41\x51\x32'  # G
    b'\x7F\x08\x08\x08\x7F'  # H
    b'\x00\x41\x7F\x41\x00'  # I
    b'\x20\x40\x41\x3F\x01'  # J
    b'\x7F\x08\x14\x22\x41'  # K
    b'\x7F\x40\x40\x40\x40'  # L
    b'\x7F\x02\x04\x02\x7F'  # M
    b'\x7F\x04\x08\x10\x7F'  # N
    b'\x3E\x41\x41\x41\x3E'  # O
    b'\x7F\x09\x09\x09\x06'  # P
    b'\x3E\x41\x51\x21\x5E'  # Q
    b'\x7F\x09\x19\x29\x46'  # R
    b'\x46\x49\x49\x49\x31'  # S
    b'\x01\x01\x7F\x01\x01'  # T
    b'\x3F\x40\x40\x40\x3F'  # U
    b'\x1F\x20\x40\x20\x1F'  # V
    b'\x3F\x40\x38\x40\x3F'  # W
    b'\x63\x14\x08\x14\x63'  # X
    b'\x07\x08\x70\x08\x07'  # Y
    b'\x61\x51\x49\x45\x43'  # Z
    b'\x00\x00\x7F\x41\x41'  # [
    b'\x02\x04\x08\x10\x20'  # backslash
    b'\x41\x41\x7F\x00\x00'  # ]
    b'\x04\x02\x01\x02\x04'  # ^
    b'\x40\x40\x40\x40\x40'  # _
    b'\x00\x01\x02\x04\x00'  # `
    b'\x20\x54\x54\x54\x78'  # a
    b'\x7F\x48\x44\x44\x38'  # b
    b'\x38\x44\x44\x44\x20'  # c
    b'\x38\x44\x44\x48\x7F'  # d
    b'\x38\x54\x54\x54\x18'  # e
    b'\x08\x7E\x09\x01\x02'  # f
    b'\x08\x54\x54\x54\x3C'  # g
    b'\x7F\x08\x04\x04\x78'  # h
    b'\x00\x44\x7D\x40\x00'  # i
    b'\x20\x40\x44\x3D\x00'  # j
    b'\x00\x7F\x10\x28\x44'  # k
    b'\x00\x41\x7F\x40\x00'  # l
    b'\x7C\x04\x18\x04\x78'  # m
    b'\x7C\x08\x04\x04\x78'  # n
    b'\x38\x44\x44\x44\x38'  # o
    b'\x7C\x14\x14\x14\x08'  # p
    b'\x08\x14\x14\x18\x7C'  # q
    b'\x7C\x08\x04\x04\x08'  # r
    b'\x48\x54\x54\x54\x20'  # s
    b'\x04\x3F\x44\x40\x20'  # t
    b'\x3C\x40\x40\x20\x7C'  # u
    b'\x1C\x20\x40\x20\x1C'  # v
    b'\x3C\x40\x30\x40\x3C'  # w
    b'\x44\x28\x10\x28\x44'  # x
    b'\x0C\x50\x50\x50\x3C'  # y
    b'\x44\x64\x54\x4C\x44'  # z
    b'\x00\x08\x36\x41\x00'  # {
    b'\x00\x00\x7F\x00\x00'  # |
    b'\x00\x41\x36\x08\x00'  # }
    b'\x08\x08\x2A\x1C\x08'  # ~
)

