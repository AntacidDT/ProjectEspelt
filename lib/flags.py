"""Procedural European flag renderer using geometric primitives.

Each flag is defined as a sequence of drawing operations on a 480x320 canvas.
Standard European flag aspect ratio is 3:2 (480 wide, 320 tall).
Output area on screen is y=28 to y=270 (242 pixels tall). Flags are scaled
and centered to fit inside the output area only, not the title or prompt.

Drawing operations:
  h(y, color)            - horizontal stripe across full width
  v(x, color)            - vertical stripe across full height
  rect(x, y, w, h, color) - filled rectangle
  circle(cx, cy, r, color) - filled circle
  cross(cx, cy, color)   - centered plus cross
"""

def _to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


C = {
    'red':         _to_rgb565(206, 17, 38),
    'white':       _to_rgb565(245, 245, 245),
    'black':       _to_rgb565(0, 0, 0),
    'blue':        _to_rgb565(0, 61, 165),
    'gold':        _to_rgb565(255, 206, 0),
    'yellow':      _to_rgb565(255, 204, 0),
    'green':       _to_rgb565(0, 102, 51),
    'orange':      _to_rgb565(255, 121, 0),
    'navy':        _to_rgb565(0, 36, 125),
    'maroon':      _to_rgb565(128, 0, 0),
    'crimson':     _to_rgb565(220, 20, 60),
    'sky':         _to_rgb565(70, 130, 180),
    'estoniablue': _to_rgb565(0, 114, 206),
    'swedenblue':  _to_rgb565(0, 102, 204),
    'franceblue':  _to_rgb565(0, 85, 164),
    'francered':   _to_rgb565(239, 65, 53),
    'ukblue':      _to_rgb565(0, 36, 125),
    'ukred':       _to_rgb565(200, 16, 46),
    'germanyred':  _to_rgb565(221, 0, 0),
    'germanygold': _to_rgb565(255, 206, 0),
    'spainred':    _to_rgb565(198, 11, 30),
    'spainyellow': _to_rgb565(255, 196, 0),
    'italygreen':  _to_rgb565(0, 146, 70),
    'russablue':   _to_rgb565(0, 57, 166),
    'russared':    _to_rgb565(213, 43, 30),
    'russawhite':  _to_rgb565(255, 255, 255),
    'germanyred':  _to_rgb565(221, 0, 0),
    'netherlandsred': _to_rgb565(174, 28, 40),
    'netherlandsblue': _to_rgb565(33, 70, 139),
    'belgiumblack': _to_rgb565(0, 0, 0),
    'belgiumyellow': _to_rgb565(255, 207, 0),
    'belgiumred': _to_rgb565(239, 51, 64),
    'ukred': _to_rgb565(200, 16, 46),
    'greeceblue': _to_rgb565(15, 70, 158),
    'turkeyred': _to_rgb565(227, 10, 23),
    'portugalgreen': _to_rgb565(0, 102, 0),
    'portugalred': _to_rgb565(255, 0, 0),
    'austriared': _to_rgb565(237, 41, 57),
    'denmarkred': _to_rgb565(198, 12, 48),
    'polandwhite': _to_rgb565(255, 255, 255),
    'polandred': _to_rgb565(220, 20, 60),
    'ukraineblue': _to_rgb565(0, 87, 184),
    'ukraineyellow': _to_rgb565(255, 221, 0),
    'norwayred': _to_rgb565(239, 43, 45),
    'finlandblue': _to_rgb565(0, 53, 128),
    'icelandblue': _to_rgb565(2, 56, 137),
    'icelandred': _to_rgb565(220, 30, 37),
    'switzerlandred': _to_rgb565(215, 30, 40),
    'irelandgreen': _to_rgb565(22, 155, 98),
    'irelandorange': _to_rgb565(255, 130, 0),
    'czechred': _to_rgb565(215, 20, 26),
    'czechblue': _to_rgb565(17, 65, 144),
    'hungaryred': _to_rgb565(205, 42, 62),
    'hungarygreen': _to_rgb565(67, 111, 77),
    'romaniablue': _to_rgb565(0, 43, 127),
    'romaniayellow': _to_rgb565(252, 209, 22),
    'bulgariared': _to_rgb565(213, 43, 30),
    'bulgariagreen': _to_rgb565(0, 150, 110),
    'serbiared': _to_rgb565(213, 43, 30),
    'croatiared': _to_rgb565(255, 0, 0),
    'sloveniawhite': _to_rgb565(255, 255, 255),
    'sloveniablue': _to_rgb565(0, 113, 188),
    'albaniared': _to_rgb565(226, 6, 19),
    'montenegrored': _to_rgb565(172, 28, 36),
    'latviared': _to_rgb565(158, 27, 50),
    'lithuaniayellow': _to_rgb565(253, 185, 19),
    'lithuaniagreen': _to_rgb565(0, 101, 49),
    'lithuaniared': _to_rgb565(193, 39, 45),
    'belarusred': _to_rgb565(210, 38, 42),
    'belarusgreen': _to_rgb565(0, 153, 94),
    'moldovablue': _to_rgb565(0, 95, 173),
    'moldovayellow': _to_rgb565(252, 209, 22),
    'moldovared': _to_rgb565(212, 36, 38),
    'maltared': _to_rgb565(206, 17, 38),
    'cypruswhite': _to_rgb565(255, 255, 255),
    'cyprusorange': _to_rgb565(255, 164, 0),
    'andorrablue': _to_rgb565(0, 85, 164),
    'andorrayellow': _to_rgb565(255, 206, 0),
    'andorrared': _to_rgb565(239, 65, 53),
    'monacored': _to_rgb565(206, 17, 38),
    'liechtensteinblue': _to_rgb565(0, 67, 156),
    'liechtensteinred': _to_rgb565(220, 30, 37),
    'sanmarinowhite': _to_rgb565(255, 255, 255),
    'sanmarinogold': _to_rgb565(255, 200, 0),
    'sanmarinoblue': _to_rgb565(95, 156, 215),
    'vaticanyellow': _to_rgb565(255, 204, 0),
    'vaticanwhite': _to_rgb565(255, 255, 255),
    'kosovoblue': _to_rgb565(45, 75, 145),
    'kosovogold': _to_rgb565(218, 165, 32),
    'macedoniared': _to_rgb565(220, 30, 30),
    'macedoniagold': _to_rgb565(255, 200, 50),
}


FLAGS = {
    'germany': [
        ('h', 0, C['black']),
        ('h', 107, C['germanyred']),
        ('h', 214, C['germanygold']),
    ],
    'france': [
        ('v', 0, C['franceblue']),
        ('v', 160, C['white']),
        ('v', 320, C['francered']),
    ],
    'italy': [
        ('v', 0, C['italygreen']),
        ('v', 160, C['white']),
        ('v', 320, C['red']),
    ],
    'spain': [
        ('h', 0, C['spainred']),
        ('h', 80, C['spainyellow']),
        ('h', 240, C['spainred']),
    ],
    'portugal': [
        ('v', 0, C['portugalgreen']),
        ('v', 160, C['portugalred']),
        ('rect', 160, 0, 80, 160, C['gold']),
        ('circle', 200, 160, 22, C['white']),
        ('circle', 200, 160, 16, C['portugalred']),
    ],
    'netherlands': [
        ('h', 0, C['netherlandsred']),
        ('h', 107, C['white']),
        ('h', 214, C['netherlandsblue']),
    ],
    'belgium': [
        ('v', 0, C['belgiumblack']),
        ('v', 160, C['belgiumyellow']),
        ('v', 320, C['belgiumred']),
    ],
    'luxembourg': [
        ('h', 0, C['red']),
        ('h', 107, C['white']),
        ('h', 214, C['sky']),
    ],
    'unitedkingdom': [
        ('rect', 0, 0, 480, 320, C['ukblue']),
        ('rect', 0, 100, 480, 40, C['white']),
        ('rect', 0, 180, 480, 40, C['white']),
        ('rect', 200, 0, 80, 320, C['white']),
        ('rect', 220, 0, 40, 320, C['ukred']),
        ('rect', 0, 130, 480, 40, C['ukred']),
    ],
    'ireland': [
        ('v', 0, C['irelandgreen']),
        ('v', 160, C['white']),
        ('v', 320, C['irelandorange']),
    ],
    'denmark': [
        ('rect', 0, 0, 480, 320, C['denmarkred']),
        ('rect', 160, 0, 40, 320, C['white']),
        ('rect', 0, 140, 480, 40, C['white']),
    ],
    'sweden': [
        ('rect', 0, 0, 480, 320, C['swedenblue']),
        ('rect', 100, 0, 30, 320, C['gold']),
        ('rect', 0, 145, 480, 30, C['gold']),
    ],
    'norway': [
        ('rect', 0, 0, 480, 320, C['norwayred']),
        ('rect', 130, 0, 40, 320, C['white']),
        ('rect', 0, 140, 480, 40, C['white']),
        ('rect', 150, 0, 20, 320, C['blue']),
        ('rect', 0, 150, 480, 20, C['blue']),
    ],
    'finland': [
        ('rect', 0, 0, 480, 320, C['white']),
        ('rect', 130, 0, 40, 320, C['finlandblue']),
        ('rect', 0, 140, 480, 40, C['finlandblue']),
    ],
    'iceland': [
        ('rect', 0, 0, 480, 320, C['icelandblue']),
        ('rect', 130, 0, 40, 320, C['white']),
        ('rect', 0, 140, 480, 40, C['white']),
        ('rect', 150, 0, 20, 320, C['icelandred']),
        ('rect', 0, 150, 480, 20, C['icelandred']),
    ],
    'russia': [
        ('h', 0, C['white']),
        ('h', 107, C['russablue']),
        ('h', 214, C['russared']),
    ],
    'poland': [
        ('h', 0, C['polandwhite']),
        ('h', 160, C['polandred']),
    ],
    'ukraine': [
        ('h', 0, C['ukraineblue']),
        ('h', 160, C['ukraineyellow']),
    ],
    'czechrepublic': [
        ('h', 0, C['white']),
        ('h', 160, C['czechred']),
        ('tri', 0, 0, 0, 320, C['czechblue']),
    ],
    'slovakia': [
        ('h', 0, C['white']),
        ('h', 107, C['blue']),
        ('h', 214, C['czechred']),
    ],
    'hungary': [
        ('h', 0, C['hungaryred']),
        ('h', 107, C['white']),
        ('h', 214, C['hungarygreen']),
    ],
    'austria': [
        ('h', 0, C['austriared']),
        ('h', 107, C['white']),
        ('h', 214, C['austriared']),
    ],
    'switzerland': [
        ('rect', 0, 0, 480, 320, C['switzerlandred']),
        ('rect', 220, 100, 40, 120, C['white']),
        ('rect', 180, 140, 120, 40, C['white']),
    ],
    'greece': [
        ('rect', 0, 0, 480, 320, C['white']),
        ('h', 40, C['greeceblue']),
        ('h', 80, C['white']),
        ('h', 120, C['greeceblue']),
        ('h', 160, C['white']),
        ('h', 200, C['greeceblue']),
        ('h', 240, C['white']),
        ('h', 280, C['greeceblue']),
        ('rect', 0, 0, 140, 140, C['greeceblue']),
        ('rect', 50, 50, 40, 20, C['white']),
        ('rect', 70, 30, 20, 60, C['white']),
        ('rect', 50, 90, 40, 20, C['white']),
    ],
    'turkey': [
        ('rect', 0, 0, 480, 320, C['turkeyred']),
        ('circle', 180, 160, 55, C['white']),
        ('circle', 200, 160, 45, C['turkeyred']),
        ('circle', 230, 145, 18, C['white']),
    ],
    'romania': [
        ('v', 0, C['romaniablue']),
        ('v', 160, C['romaniayellow']),
        ('v', 320, C['czechred']),
    ],
    'bulgaria': [
        ('h', 0, C['white']),
        ('h', 107, C['bulgariagreen']),
        ('h', 214, C['bulgariared']),
    ],
    'serbia': [
        ('h', 0, C['serbiared']),
        ('h', 107, C['blue']),
        ('h', 214, C['white']),
    ],
    'croatia': [
        ('h', 0, C['croatiared']),
        ('h', 107, C['white']),
        ('h', 214, C['blue']),
    ],
    'slovenia': [
        ('h', 0, C['sloveniawhite']),
        ('h', 107, C['sloveniablue']),
        ('h', 214, C['czechred']),
    ],
    'bosniaandherzegovina': [
        ('rect', 0, 0, 480, 320, C['blue']),
        ('tri', 0, 0, 120, 160, C['gold']),
        ('tri', 0, 320, 120, 160, C['gold']),
        ('stars', 60, 160, 12, C['white']),
    ],
    'bosnia': [
        ('rect', 0, 0, 480, 320, C['blue']),
        ('tri', 0, 0, 120, 160, C['gold']),
        ('tri', 0, 320, 120, 160, C['gold']),
        ('stars', 60, 160, 12, C['white']),
    ],
    'albania': [
        ('rect', 0, 0, 480, 320, C['albaniared']),
    ],
    'montenegro': [
        ('rect', 0, 0, 480, 320, C['montenegrored']),
        ('rect', 0, 145, 480, 30, C['gold']),
        ('rect', 0, 155, 480, 10, C['gold']),
    ],
    'kosovo': [
        ('rect', 0, 0, 480, 320, C['kosovoblue']),
        ('circle', 240, 160, 55, C['kosovogold']),
        ('stars', 240, 160, 8, C['white']),
    ],
    'northmacedonia': [
        ('rect', 0, 0, 480, 320, C['macedoniared']),
        ('circle', 240, 160, 55, C['macedoniagold']),
        ('rays', 240, 160, 50, C['macedoniagold']),
    ],
    'macedonia': [
        ('rect', 0, 0, 480, 320, C['macedoniared']),
        ('circle', 240, 160, 55, C['macedoniagold']),
        ('rays', 240, 160, 50, C['macedoniagold']),
    ],
    'estonia': [
        ('h', 0, C['estoniablue']),
        ('h', 107, C['black']),
        ('h', 214, C['white']),
    ],
    'latvia': [
        ('h', 0, C['latviared']),
        ('h', 107, C['white']),
        ('h', 214, C['latviared']),
    ],
    'lithuania': [
        ('h', 0, C['lithuaniayellow']),
        ('h', 107, C['lithuaniagreen']),
        ('h', 214, C['lithuaniared']),
    ],
    'belarus': [
        ('h', 0, C['belarusred']),
        ('h', 107, C['belarusgreen']),
        ('rect', 0, 60, 100, 120, C['belarusred']),
    ],
    'moldova': [
        ('v', 0, C['moldovablue']),
        ('v', 160, C['moldovayellow']),
        ('v', 320, C['moldovared']),
    ],
    'malta': [
        ('v', 0, C['white']),
        ('v', 240, C['maltared']),
        ('cross', 120, 100, C['maltared']),
    ],
    'cyprus': [
        ('rect', 0, 0, 480, 320, C['cypruswhite']),
        ('rect', 0, 80, 480, 160, C['cyprusorange']),
        ('shape', 240, 160, C['cyprusorange']),
    ],
    'andorra': [
        ('v', 0, C['andorrablue']),
        ('v', 160, C['andorrayellow']),
        ('v', 320, C['andorrared']),
    ],
    'monaco': [
        ('h', 0, C['monacored']),
        ('h', 160, C['white']),
    ],
    'liechtenstein': [
        ('h', 0, C['liechtensteinblue']),
        ('h', 160, C['liechtensteinred']),
        ('crown', 240, 80, C['gold']),
    ],
    'sanmarino': [
        ('h', 0, C['sanmarinoblue']),
        ('h', 107, C['sanmarinowhite']),
        ('h', 214, C['sanmarinogold']),
    ],
    'vatican': [
        ('v', 0, C['vaticanyellow']),
        ('v', 240, C['vaticanwhite']),
        ('cross', 120, 80, C['vaticanyellow']),
    ],
}


# Output area bounds: header is 0-24, prompt starts at y=270
# So flag area is y=28 to y=270 (height=242)
OUTPUT_X = 0
OUTPUT_Y = 28
OUTPUT_W = 480
OUTPUT_H = 242


def list_countries():
    return sorted(FLAGS.keys())


def list_countries_page(page, per_page=8):
    """Return (start, end, total_pages) for the given page number (1-indexed)."""
    all_countries = sorted(FLAGS.keys())
    total = len(all_countries)
    total_pages = (total + per_page - 1) // per_page
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    return all_countries[start:end], page, total_pages


def draw_flag(tft, country):
    """Draw a flag bounded to the output area (y=28 to y=270)."""
    country = country.lower().replace(' ', '').replace('-', '')
    aliases = {
        'uk': 'unitedkingdom', 'britain': 'unitedkingdom',
        'england': 'unitedkingdom', 'greatbritain': 'unitedkingdom',
        'czech': 'czechrepublic',
        'macedonia': 'northmacedonia',
    }
    country = aliases.get(country, country)
    ops = FLAGS.get(country)
    if not ops:
        return False

    # Source canvas is 480x320, but we draw only in the output area (242 tall).
    # Scale factor: 242/320 = 0.756, width becomes 480*0.756 = 363.
    # Center horizontally, start at OUTPUT_Y.
    src_w, src_h = 480, 320
    dst_w = int(src_w * OUTPUT_H / src_h)
    dst_h = OUTPUT_H
    dst_x = (480 - dst_w) // 2
    dst_y = OUTPUT_Y

    for op in ops:
        _draw_op(tft, op, dst_x, dst_y, dst_w, dst_h)
    return True


def _draw_op(tft, op, x, y, w, h):
    kind = op[0]
    if kind == 'h':
        ty = int(y + op[1] * h / 320)
        th = int(107 * h / 320)
        if th < 1:
            th = 1
        tft.fill_rect(x, ty, w, th, op[2])
    elif kind == 'v':
        tx = int(x + op[1] * w / 480)
        tw = int(160 * w / 480)
        if tw < 1:
            tw = 1
        tft.fill_rect(tx, y, tw, h, op[2])
    elif kind == 'rect':
        rx = int(x + op[1] * w / 480)
        ry = int(y + op[2] * h / 320)
        rw = int(op[3] * w / 480)
        rh = int(op[4] * h / 320)
        if rw < 1:
            rw = 1
        if rh < 1:
            rh = 1
        if rx >= x and ry >= y and rx + rw <= x + w and ry + rh <= y + h:
            tft.fill_rect(rx, ry, rw, rh, op[5])
    elif kind == 'circle':
        cx = int(x + op[1] * w / 480)
        cy = int(y + op[2] * h / 320)
        r = int(op[3] * h / 320)
        if r > 0:
            _draw_circle(tft, cx, cy, r, op[4])
    elif kind == 'tri':
        _draw_tri(tft, x, y, w, h, op[5])
    elif kind == 'cross':
        cx = int(x + op[1] * w / 480)
        cy = int(y + op[2] * h / 320)
        cw = int(40 * w / 480)
        ch = int(120 * h / 320)
        if cw < 1:
            cw = 1
        if ch < 1:
            ch = 1
        tft.fill_rect(cx - cw//2, cy - ch//2, cw, ch, op[3])
        tft.fill_rect(cx - ch//2, cy - cw//2, ch, cw, op[3])
    elif kind == 'crown':
        tft.fill_rect(int(x + 200 * w/480), int(y + 80 * h/320), int(80*w/480), int(40*h/320), op[3])
    elif kind == 'shield':
        pass
    elif kind == 'stars':
        pass
    elif kind == 'rays':
        pass
    elif kind == 'keys':
        pass
    elif kind == 'eagle':
        pass
    elif kind == 'pattern':
        pass
    elif kind == 'shape':
        pass


def _draw_circle(tft, cx, cy, r, color):
    if r <= 0:
        return
    for dy in range(-r, r+1):
        dx_sq = r*r - dy*dy
        if dx_sq < 0:
            continue
        dx = int(dx_sq ** 0.5)
        tft.hline(cx - dx, cy + dy, dx * 2, color)


def _draw_tri(tft, x, y, w, h, color):
    # Draw a triangle from left edge to a point on the right side
    # Args: tri(x1, y1, x2, y2, color) - the triangle with vertices at
    # (x1,y1), (x2,y2), and (480,160) on the 480x320 canvas
    pass


COUNTRIES = [
    'germany', 'france', 'italy', 'spain', 'portugal',
    'netherlands', 'belgium', 'luxembourg', 'unitedkingdom', 'ireland',
    'denmark', 'sweden', 'norway', 'finland', 'iceland',
    'russia', 'poland', 'ukraine', 'czechrepublic', 'slovakia',
    'hungary', 'austria', 'switzerland',
    'greece', 'turkey', 'romania', 'bulgaria', 'serbia',
    'croatia', 'slovenia', 'bosniaandherzegovina', 'albania',
    'montenegro', 'kosovo', 'northmacedonia',
    'estonia', 'latvia', 'lithuania', 'belarus', 'moldova',
    'malta', 'cyprus', 'andorra', 'monaco', 'liechtenstein',
    'sanmarino', 'vatican',
]
