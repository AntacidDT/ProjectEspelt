from time import sleep_ms
from machine import Pin, SPI

_WIDTH = const(480)
_HEIGHT = const(320)


def color565(r, g, b):
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


def _rgb666(color):
    r5 = (color >> 11) & 0x1F
    g6 = (color >> 5) & 0x3F
    b5 = color & 0x1F
    return bytes([
        ((r5 << 1) | (r5 >> 4)) & 0xFC,
        g6 & 0xFC,
        ((b5 << 1) | (b5 >> 4)) & 0xFC
    ])


class ILI9488:
    def __init__(self, spi, cs, dc, rst=None,
                 width=_WIDTH, height=_HEIGHT, rotation=0):
        self._spi = spi
        self._cs = cs
        self._dc = dc
        self._rst = rst
        self.width = width
        self.height = height

        self._cs.init(Pin.OUT, value=1)
        self._dc.init(Pin.OUT, value=0)
        if self._rst:
            self._rst.init(Pin.OUT, value=1)

        self._init_display(rotation)

    def _write_cmd(self, cmd):
        self._dc(0)
        self._cs(0)
        self._spi.write(bytes([cmd]))
        self._cs(1)

    def _write_cmd_data(self, cmd, data):
        self._dc(0)
        self._cs(0)
        self._spi.write(bytes([cmd]))
        self._cs(1)
        self._dc(1)
        self._cs(0)
        self._spi.write(data)
        self._cs(1)

    def _write_data(self, data):
        self._dc(1)
        self._cs(0)
        self._spi.write(data)
        self._cs(1)

    def _init_display(self, rotation):
        if self._rst:
            self._rst(0)
            sleep_ms(50)
            self._rst(1)
            sleep_ms(50)

        self._write_cmd(0x01)
        sleep_ms(100)

        self._write_cmd(0x11)
        sleep_ms(120)

        self._write_cmd_data(0xE0, bytes([
            0x00, 0x03, 0x09, 0x08, 0x16, 0x0A, 0x3F, 0x78,
            0x4C, 0x09, 0x0A, 0x08, 0x16, 0x1A, 0x0F]))

        self._write_cmd_data(0xE1, bytes([
            0x00, 0x16, 0x19, 0x03, 0x0F, 0x05, 0x32, 0x45,
            0x46, 0x04, 0x0E, 0x0D, 0x35, 0x37, 0x0F]))

        self._write_cmd_data(0xC0, bytes([0x17, 0x15]))
        self._write_cmd_data(0xC1, bytes([0x41]))
        self._write_cmd_data(0xC2, bytes([0x44]))
        self._write_cmd_data(0xC5, bytes([0x00, 0x12, 0x80]))

        madctl = 0x28
        if rotation == 1:
            madctl = 0x68
        elif rotation == 2:
            madctl = 0xC8
        elif rotation == 3:
            madctl = 0xA8
        self._write_cmd_data(0x36, bytes([madctl]))

        self._write_cmd_data(0x3A, bytes([0x66]))

        self._write_cmd_data(0xB0, bytes([0x00]))
        self._write_cmd_data(0xB1, bytes([0xA0]))
        self._write_cmd_data(0xB4, bytes([0x02]))
        self._write_cmd_data(0xB6, bytes([0x02, 0x02]))

        self._write_cmd_data(0xE9, bytes([0x00]))
        self._write_cmd_data(0x53, bytes([0x2C]))
        self._write_cmd_data(0x51, bytes([0xFF]))
        self._write_cmd_data(0xF7, bytes([0xA9, 0x51, 0x2C, 0x02]))

        self._write_cmd(0x29)
        sleep_ms(50)

    def _set_window(self, x0, y0, x1, y1):
        self._write_cmd_data(0x2A, int.to_bytes(x0, 2, 'big') + int.to_bytes(x1, 2, 'big'))
        self._write_cmd_data(0x2B, int.to_bytes(y0, 2, 'big') + int.to_bytes(y1, 2, 'big'))
        self._write_cmd(0x2C)

    def fill(self, color):
        self._set_window(0, 0, self.width - 1, self.height - 1)
        r5 = (color >> 11) & 0x1F
        g6 = (color >> 5) & 0x3F
        b5 = color & 0x1F
        r6 = ((r5 << 1) | (r5 >> 4)) & 0xFC
        g6b = g6 & 0xFC
        b6 = ((b5 << 1) | (b5 >> 4)) & 0xFC
        pixel = bytes([r6, g6b, b6])
        self._dc(1)
        self._cs(0)
        n = self.width * self.height
        chunk = pixel * 20
        reps, rem = divmod(n, 20)
        spi_write = self._spi.write
        for _ in range(reps):
            spi_write(chunk)
        for _ in range(rem):
            spi_write(pixel)
        self._cs(1)

    def fill_rect(self, x, y, w, h, color):
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            return
        self._set_window(x, y, x + w - 1, y + h - 1)
        r5 = (color >> 11) & 0x1F
        g6 = (color >> 5) & 0x3F
        b5 = color & 0x1F
        pixel = bytes([
            ((r5 << 1) | (r5 >> 4)) & 0xFC,
            g6 & 0xFC,
            ((b5 << 1) | (b5 >> 4)) & 0xFC
        ])
        self._dc(1)
        self._cs(0)
        n = w * h
        chunk = pixel * 20
        reps, rem = divmod(n, 20)
        spi_write = self._spi.write
        for _ in range(reps):
            spi_write(chunk)
        for _ in range(rem):
            spi_write(pixel)
        self._cs(1)

    def pixel(self, x, y, color):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self._set_window(x, y, x, y)
        self._write_data(_rgb666(color))

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def text(self, s, x, y, color=0xFFFF, bg=0x0000, scale=1):
        ox = x
        c666 = _rgb666(color)
        b666 = _rgb666(bg)
        for ch in s:
            if ch == '\n':
                x = ox
                y += 8 * scale
                continue
            code = ord(ch)
            if code < 32 or code > 126:
                code = ord('?')
            idx = (code - 32) * 8
            for row in range(8):
                bits = FONT_DATA[idx + row]
                ry = y + row * scale
                line_buf = bytearray()
                for col in range(8):
                    px = c666 if (bits & (0x80 >> col)) else b666
                    for _ in range(scale):
                        line_buf.extend(px)
                line_bytes = bytes(line_buf)
                for sy in range(scale):
                    self._set_window(x, ry + sy, x + 8 * scale - 1, ry + sy)
                    self._write_data(line_bytes)
            x += 8 * scale

    def text15(self, s, x, y, color=0xFFFF, bg=0x0000):
        ox = x
        c5r = (color >> 11) & 0x1F
        c6g = (color >> 5) & 0x3F
        c5b = color & 0x1F
        b5r = (bg >> 11) & 0x1F
        b6g = (bg >> 5) & 0x3F
        b5b = bg & 0x1F
        fr = ((c5r << 1) | (c5r >> 4)) & 0xFC
        fg = c6g & 0xFC
        fb = ((c5b << 1) | (c5b >> 4)) & 0xFC
        bgr = ((b5r << 1) | (b5r >> 4)) & 0xFC
        bgg = b6g & 0xFC
        bgb = ((b5b << 1) | (b5b >> 4)) & 0xFC
        cw = 12
        ch_ = 14
        for c in s:
            if c == '\n':
                x = ox
                y += 16
                continue
            code = ord(c)
            if code in _EXTENDED:
                ebits = _EXTENDED[code]
                buf = bytearray(cw * ch_ * 3)
                for dy in range(ch_):
                    sy = min(dy * 8 // ch_, 7)
                    bits = ebits[sy]
                    for dx in range(cw):
                        sx = min(dx * 8 // cw, 7)
                        off = (dy * cw + dx) * 3
                        if bits & (0x80 >> sx):
                            buf[off] = fr
                            buf[off + 1] = fg
                            buf[off + 2] = fb
                        else:
                            buf[off] = bgr
                            buf[off + 1] = bgg
                            buf[off + 2] = bgb
                self._set_window(x, y, x + cw - 1, y + ch_ - 1)
                self._dc(1)
                self._cs(0)
                self._spi.write(buf)
                self._cs(1)
                x += cw
                continue
            if code < 32 or code > 126:
                code = ord('?')
            idx = (code - 32) * 8
            buf = bytearray(cw * ch_ * 3)
            for dy in range(ch_):
                sy = min(dy * 8 // ch_, 7)
                bits = FONT_DATA[idx + sy]
                for dx in range(cw):
                    sx = min(dx * 8 // cw, 7)
                    off = (dy * cw + dx) * 3
                    if bits & (0x80 >> sx):
                        buf[off] = fr
                        buf[off + 1] = fg
                        buf[off + 2] = fb
                    else:
                        buf[off] = bgr
                        buf[off + 1] = bgg
                        buf[off + 2] = bgb
            self._set_window(x, y, x + cw - 1, y + ch_ - 1)
            self._dc(1)
            self._cs(0)
            self._spi.write(buf)
            self._cs(1)
            x += cw
        return x

    def text8(self, s, x, y, color=0xFFFF, bg=0x0000):
        ox = x
        c5r = (color >> 11) & 0x1F
        c6g = (color >> 5) & 0x3F
        c5b = color & 0x1F
        b5r = (bg >> 11) & 0x1F
        b6g = (bg >> 5) & 0x3F
        b5b = bg & 0x1F
        fr = ((c5r << 1) | (c5r >> 4)) & 0xFC
        fg = c6g & 0xFC
        fb = ((c5b << 1) | (c5b >> 4)) & 0xFC
        bgr = ((b5r << 1) | (b5r >> 4)) & 0xFC
        bgg = b6g & 0xFC
        bgb = ((b5b << 1) | (b5b >> 4)) & 0xFC
        cw = 8
        ch_ = 10
        for c in s:
            if c == '\n':
                x = ox
                y += 10
                continue
            code = ord(c)
            if code in _EXTENDED:
                ebits = _EXTENDED[code]
                buf = bytearray(cw * ch_ * 3)
                for dy in range(ch_):
                    sy = min(dy * 8 // ch_, 7)
                    bits = ebits[sy]
                    for dx in range(cw):
                        sx = min(dx * 8 // cw, 7)
                        off = (dy * cw + dx) * 3
                        if bits & (0x80 >> sx):
                            buf[off] = fr
                            buf[off + 1] = fg
                            buf[off + 2] = fb
                        else:
                            buf[off] = bgr
                            buf[off + 1] = bgg
                            buf[off + 2] = bgb
                self._set_window(x, y, x + cw - 1, y + ch_ - 1)
                self._dc(1)
                self._cs(0)
                self._spi.write(buf)
                self._cs(1)
                x += cw
                continue
            if code < 32 or code > 126:
                code = ord('?')
            idx = (code - 32) * 8
            buf = bytearray(cw * ch_ * 3)
            for dy in range(ch_):
                sy = min(dy * 8 // ch_, 7)
                bits = FONT_DATA[idx + sy]
                for dx in range(cw):
                    sx = min(dx * 8 // cw, 7)
                    off = (dy * cw + dx) * 3
                    if bits & (0x80 >> sx):
                        buf[off] = fr
                        buf[off + 1] = fg
                        buf[off + 2] = fb
                    else:
                        buf[off] = bgr
                        buf[off + 1] = bgg
                        buf[off + 2] = bgb
            self._set_window(x, y, x + cw - 1, y + ch_ - 1)
            self._dc(1)
            self._cs(0)
            self._spi.write(buf)
            self._cs(1)
            x += cw
        return x

    def blit_bitmap(self, buf, x, y, w, h):
        self._set_window(x, y, x + w - 1, y + h - 1)
        self._dc(1)
        self._cs(0)
        self._spi.write(buf)
        self._cs(1)


FONT_DATA = (
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x7E\x18\x18\x18\x18\x18\x18\x7E'
    b'\x7C\xFE\xC6\xFE\xFE\xC6\xC6\x00'
    b'\x00\xFE\xC6\xFE\xC6\xC6\xFE\x00'
    b'\x7C\xFE\xC0\xC0\xC0\xC0\xFE\x7C'
    b'\x00\xFC\xC6\xC6\xC6\xC6\xFE\x7C'
    b'\x00\xFE\xC0\xFE\xC0\xC0\xFE\x00'
    b'\x00\xFE\xC0\xFE\xC0\xC0\xC0\x00'
    b'\x7C\xFE\xC0\xCE\xC6\xC6\xFE\x7C'
    b'\x00\xC6\xC6\xFE\xC6\xC6\xC6\x00'
    b'\x00\x7E\x18\x18\x18\x18\x18\x7E'
    b'\x00\x06\x06\x06\x06\xC6\xFE\x7C'
    b'\x00\xC6\xCC\xF8\xF8\xCC\xC6\x00'
    b'\x00\xC0\xC0\xC0\xC0\xC0\xFE\x00'
    b'\x00\xC6\xEE\xFE\xD6\xC6\xC6\x00'
    b'\x00\xC6\xE6\xF6\xDE\xCE\xC6\x00'
    b'\x7C\xFE\xC6\xC6\xC6\xC6\xFE\x7C'
    b'\x00\xFC\xC6\xC6\xFC\xC0\xC0\x00'
    b'\x7C\xFE\xC6\xC6\xD6\xDE\xFE\x7C'
    b'\x00\xFC\xC6\xC6\xFC\xCC\xC6\x00'
    b'\x7C\xFE\xC0\x7C\x06\xC6\xFE\x7C'
    b'\x00\xFE\x18\x18\x18\x18\x18\x18'
    b'\x00\xC6\xC6\xC6\xC6\xC6\xFE\x7C'
    b'\x00\xC6\xC6\xC6\xC6\x7C\x38\x10'
    b'\x00\xC6\xC6\xC6\xD6\xFE\x6C\x00'
    b'\x00\xC6\x6C\x38\x38\x6C\xC6\x00'
    b'\x00\xC6\xC6\x7C\x38\x18\x18\x00'
    b'\x00\xFE\x0C\x18\x30\x60\xFE\x00'
    b'\x3C\x30\x30\x30\x30\x30\x30\x3C'
    b'\x00\x00\x04\x0C\x18\x30\x60\x00'
    b'\x3C\x0C\x0C\x0C\x0C\x0C\x0C\x3C'
    b'\x10\x38\x6C\xC6\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\xFF'
    b'\x30\x18\x0C\x00\x00\x00\x00\x00'
    b'\x00\x00\x7C\x06\x7E\xC6\x7E\x00'
    b'\xC0\xC0\xFC\xC6\xC6\xC6\xFC\x00'
    b'\x00\x00\x7C\xC6\xC0\xC0\x7C\x00'
    b'\x06\x06\x7E\xC6\xC6\xC6\x7E\x00'
    b'\x00\x00\x7C\xC6\xFE\xC0\x7C\x00'
    b'\x1C\x36\x30\x7C\x30\x30\x30\x00'
    b'\x00\x00\x7E\xC6\xC6\x7E\x06\x7C'
    b'\xC0\xC0\xFC\xC6\xC6\xC6\xC6\x00'
    b'\x18\x00\x38\x18\x18\x18\x3C\x00'
    b'\x06\x00\x0E\x06\x06\x06\xC6\x7C'
    b'\xC0\xC0\xC6\xCC\xF8\xCC\xC6\x00'
    b'\x38\x18\x18\x18\x18\x18\x3C\x00'
    b'\x00\x00\xEC\xFE\xD6\xD6\xD6\x00'
    b'\x00\x00\xFC\xC6\xC6\xC6\xC6\x00'
    b'\x00\x00\x7C\xC6\xC6\xC6\x7C\x00'
    b'\x00\x00\xFC\xC6\xC6\xFC\xC0\xC0'
    b'\x00\x00\x7E\xC6\xC6\x7E\x06\x06'
    b'\x00\x00\xDC\xE6\xC0\xC0\xC0\x00'
    b'\x00\x00\x7E\xC0\x7C\x06\xFC\x00'
    b'\x30\x30\xFC\x30\x30\x30\x1C\x00'
    b'\x00\x00\xC6\xC6\xC6\xC6\x7E\x00'
    b'\x00\x00\xC6\xC6\xC6\x7C\x38\x00'
    b'\x00\x00\xC6\xD6\xD6\x7C\x38\x00'
    b'\x00\x00\xC6\x6C\x38\x6C\xC6\x00'
    b'\x00\x00\xC6\xC6\xC6\x7E\x06\x7C'
    b'\x00\x00\xFE\x0C\x38\x60\xFE\x00'
    b'\x0E\x18\x18\x70\x18\x18\x0E\x00'
    b'\x18\x18\x18\x18\x18\x18\x18\x18'
    b'\x70\x18\x18\x0E\x18\x18\x70\x00'
    b'\x00\x00\x70\xDA\x0C\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
)

_EXTENDED = {
    937: b'\x00\xFE\xC0\xC0\xC0\xC0\xC0\x00',   # Ω Ohm
    956: b'\x00\x00\xEC\xD6\xD6\xD6\x60\x00',   # μ micro
    8734: b'\x00\x00\x00\x76\xDC\xDC\x76\x00',  # ∞ infinity
    960: b'\x00\x00\x00\x6C\xFE\x6C\x6C\x00',   # π pi
    8730: b'\x00\x00\x00\x7E\x60\x60\x60\x00',  # √ square root
    8364: b'\x1C\x36\x20\x7C\x20\x36\x1C\x00',  # € euro
}

FONT_DATA = bytearray().join([
    b'\x00\x00\x00\x00\x00\x00\x00\x00',  # space
    b'\x18\x18\x18\x18\x00\x00\x18\x00',  # !
    b'\x6C\x6C\x6C\x00\x00\x00\x00\x00',  # "
    b'\x6C\xFE\x6C\x6C\xFE\x6C\x00\x00',  # #
    b'\x18\x3E\x60\x3C\x06\x7C\x18\x00',  # $
    b'\x62\x66\x0C\x18\x30\x66\x46\x00',  # %
    b'\x3C\x66\x3C\x38\x67\x66\x3F\x00',  # &
    b'\x18\x18\x18\x00\x00\x00\x00\x00',  # '
    b'\x0C\x18\x30\x30\x30\x18\x0C\x00',  # (
    b'\x30\x18\x0C\x0C\x0C\x18\x30\x00',  # )
    b'\x00\x66\x3C\xFF\x3C\x66\x00\x00',  # *
    b'\x00\x18\x18\x7E\x18\x18\x00\x00',  # +
    b'\x00\x00\x00\x00\x00\x18\x18\x30',  # ,
    b'\x00\x00\x00\x7E\x00\x00\x00\x00',  # -
    b'\x00\x00\x00\x00\x00\x18\x18\x00',  # .
    b'\x00\x03\x06\x0C\x18\x30\x60\x00',  # /
    b'\x3C\x66\x6E\x76\x66\x66\x3C\x00',  # 0
    b'\x18\x18\x38\x18\x18\x18\x7E\x00',  # 1
    b'\x3C\x66\x06\x0C\x30\x60\x7E\x00',  # 2
    b'\x3C\x66\x06\x1C\x06\x66\x3C\x00',  # 3
    b'\x06\x0E\x1E\x66\x7F\x06\x06\x00',  # 4
    b'\x7E\x60\x7C\x06\x06\x66\x3C\x00',  # 5
    b'\x3C\x66\x60\x7C\x66\x66\x3C\x00',  # 6
    b'\x7E\x66\x0C\x18\x18\x18\x18\x00',  # 7
    b'\x3C\x66\x66\x3C\x66\x66\x3C\x00',  # 8
    b'\x3C\x66\x66\x3E\x06\x66\x3C\x00',  # 9
    b'\x00\x00\x18\x00\x00\x18\x00\x00',  # :
    b'\x00\x00\x18\x00\x00\x18\x18\x30',  # ;
    b'\x0E\x18\x30\x60\x30\x18\x0E\x00',  # <
    b'\x00\x00\x7E\x00\x7E\x00\x00\x00',  # =
    b'\x70\x18\x06\x06\x06\x18\x70\x00',  # >
    b'\x3C\x66\x06\x0C\x18\x00\x18\x00',  # ?
    b'\x3C\x66\x6E\x6E\x60\x62\x3C\x00',  # @
    b'\x18\x3C\x66\x66\x7E\x66\x66\x00',  # A
    b'\x7C\x66\x66\x7C\x66\x66\x7C\x00',  # B
    b'\x3C\x66\x60\x60\x60\x66\x3C\x00',  # C
    b'\x78\x6C\x66\x66\x66\x6C\x78\x00',  # D
    b'\x7E\x60\x60\x78\x60\x60\x7E\x00',  # E
    b'\x7E\x60\x60\x78\x60\x60\x60\x00',  # F
    b'\x3C\x66\x60\x6E\x66\x66\x3C\x00',  # G
    b'\x66\x66\x66\x7E\x66\x66\x66\x00',  # H
    b'\x3C\x18\x18\x18\x18\x18\x3C\x00',  # I
    b'\x1E\x0C\x0C\x0C\x0C\xCC\x78\x00',  # J
    b'\x66\x6C\x78\x70\x78\x6C\x66\x00',  # K
    b'\x60\x60\x60\x60\x60\x60\x7E\x00',  # L
    b'\x63\x77\x7F\x6B\x63\x63\x63\x00',  # M
    b'\x66\x76\x7E\x7E\x6E\x66\x66\x00',  # N
    b'\x3C\x66\x66\x66\x66\x66\x3C\x00',  # O
    b'\x7C\x66\x66\x7C\x60\x60\x60\x00',  # P
    b'\x3C\x66\x66\x66\x66\x3C\x0E\x00',  # Q
    b'\x7C\x66\x66\x7C\x78\x6C\x66\x00',  # R
    b'\x3C\x66\x60\x3C\x06\x66\x3C\x00',  # S
    b'\x7E\x18\x18\x18\x18\x18\x18\x00',  # T
    b'\x66\x66\x66\x66\x66\x66\x3C\x00',  # U
    b'\x66\x66\x66\x66\x66\x3C\x18\x00',  # V
    b'\x63\x63\x63\x6B\x7F\x77\x63\x00',  # W
    b'\x66\x66\x3C\x18\x3C\x66\x66\x00',  # X
    b'\x66\x66\x66\x3C\x18\x18\x18\x00',  # Y
    b'\x7E\x06\x0C\x18\x30\x60\x7E\x00',  # Z
    b'\x3C\x30\x30\x30\x30\x30\x3C\x00',  # [
    b'\x00\x60\x30\x18\x0C\x06\x03\x00',  # backslash
    b'\x3C\x0C\x0C\x0C\x0C\x0C\x3C\x00',  # ]
    b'\x18\x3C\x66\x00\x00\x00\x00\x00',  # ^
    b'\x00\x00\x00\x00\x00\x00\x00\xFF',  # _
    b'\x30\x18\x0C\x00\x00\x00\x00\x00',  # `
    b'\x00\x00\x3C\x06\x3E\x66\x3E\x00',  # a
    b'\x60\x60\x7C\x66\x66\x66\x7C\x00',  # b
    b'\x00\x00\x3C\x66\x60\x66\x3C\x00',  # c
    b'\x06\x06\x3E\x66\x66\x66\x3E\x00',  # d
    b'\x00\x00\x3C\x66\x7E\x60\x3C\x00',  # e
    b'\x1C\x36\x30\x7C\x30\x30\x30\x00',  # f
    b'\x00\x00\x3E\x66\x66\x3E\x06\x3C',  # g
    b'\x60\x60\x7C\x66\x66\x66\x66\x00',  # h
    b'\x18\x00\x38\x18\x18\x18\x3C\x00',  # i
    b'\x06\x00\x0E\x06\x06\x06\x66\x3C',  # j
    b'\x60\x60\x66\x6C\x78\x6C\x66\x00',  # k
    b'\x38\x18\x18\x18\x18\x18\x3C\x00',  # l
    b'\x00\x00\x6C\x7F\x7F\x6B\x63\x00',  # m
    b'\x00\x00\x7C\x66\x66\x66\x66\x00',  # n
    b'\x00\x00\x3C\x66\x66\x66\x3C\x00',  # o
    b'\x00\x00\x7C\x66\x66\x7C\x60\x60',  # p
    b'\x00\x00\x3E\x66\x66\x3E\x06\x06',  # q
    b'\x00\x00\x7C\x66\x60\x60\x60\x00',  # r
    b'\x00\x00\x3E\x60\x3C\x06\x7C\x00',  # s
    b'\x30\x30\x7C\x30\x30\x36\x1C\x00',  # t
    b'\x00\x00\x66\x66\x66\x66\x3E\x00',  # u
    b'\x00\x00\x66\x66\x66\x3C\x18\x00',  # v
    b'\x00\x00\x63\x6B\x7F\x7F\x36\x00',  # w
    b'\x00\x00\x66\x3C\x18\x3C\x66\x00',  # x
    b'\x00\x00\x66\x66\x66\x3E\x06\x3C',  # y
    b'\x00\x00\x7E\x0C\x18\x30\x7E\x00',  # z
    b'\x0E\x18\x18\x70\x18\x18\x0E\x00',  # {
    b'\x18\x18\x18\x18\x18\x18\x18\x18',  # |
    b'\x70\x18\x18\x0E\x18\x18\x70\x00',  # }
    b'\x00\x00\x72\xFE\x4C\x00\x00\x00',  # ~
    b'\x00\x00\x00\x00\x00\x00\x00\x00',  # DEL
])
