_BG = 0x0000
_FG = 0xFFFF
_ACCENT = 0x07FF
_GREEN = 0x07E0
_RED = 0xF800
_YELLOW = 0xFFE0
_GRAY = 0x8410
_DGRAY = 0x4208


def set_theme(theme_colors):
    global _BG, _FG, _ACCENT, _GREEN, _RED, _YELLOW, _GRAY, _DGRAY
    _BG = theme_colors['bg']
    _FG = theme_colors['white']
    _ACCENT = theme_colors['accent']
    _GREEN = theme_colors['green']
    _YELLOW = theme_colors['yellow']
    _RED = theme_colors['red']
    _GRAY = 0x8410
    _DGRAY = 0x4208

HEADER_H = 24
RESULTS_Y = 26
MATH_Y = 242
MATH_H = 36
PROMPT_Y = 280
LINE_H = 16

_INT_PTS = (
    (3, 0), (3, 1), (2, 2), (2, 3), (1, 4), (1, 5), (2, 6), (2, 7),
    (3, 8), (3, 9), (4, 10), (4, 11), (5, 12), (5, 13), (4, 14), (4, 15),
    (3, 16), (3, 17),
)

_SIG_PTS = (
    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0),
    (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6),
    (1, 7),
    (2, 8), (3, 9), (4, 10), (5, 11), (6, 12), (7, 13),
    (0, 14), (1, 14), (2, 14), (3, 14), (4, 14), (5, 14), (6, 14), (7, 14), (8, 14),
)

_ARR_PTS = ((0, 1), (1, 1), (2, 1), (3, 1), (4, 0), (4, 2), (5, 1))


def _fmt_num(v, frac_mode=False):
    if isinstance(v, list):
        return _fmt_matrix(v)
    if not isinstance(v, float):
        return str(v)
    if v != v:
        return 'NaN'
    if v == float('inf'):
        return 'inf'
    if v == float('-inf'):
        return '-inf'
    if frac_mode:
        return _fmt_fraction(v)
    if abs(v) >= 1e10 or (abs(v) < 0.001 and v != 0):
        return '{:.6e}'.format(v)
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return '{:.10g}'.format(v)


def _fmt_fraction(v):
    if v != v or v == float('inf') or v == float('-inf'):
        return str(v)
    if v == 0:
        return '0'
    sign = -1 if v < 0 else 1
    v = abs(v)
    best_num, best_den = int(round(v)), 1
    best_err = abs(v - best_num)
    for den in range(2, 1000):
        num = round(v * den)
        err = abs(v - num / den)
        if err < best_err:
            best_err = err
            best_num, best_den = num, den
        if err < 1e-9:
            break
    if best_den == 1:
        return str(sign * best_num)
    prefix = '-' if sign < 0 else ''
    if best_num >= best_den:
        whole = best_num // best_den
        rem = best_num % best_den
        if rem == 0:
            return '{}{}'.format(prefix, whole)
        return '{}{} {}/{}'.format(prefix, whole, rem, best_den)
    return '{}{}/{}'.format(prefix, best_num, best_den)


def _fmt_matrix(m):
    if not m or not isinstance(m, list):
        return str(m)
    if isinstance(m[0], list):
        rows = m
    else:
        rows = [m]
    lines = []
    for row in rows:
        lines.append('[' + ', '.join(_fmt_num(x) for x in row) + ']')
    if len(lines) == 1:
        return lines[0]
    return '[' + '; '.join(lines) + ']'


def _to_fraction(v, max_den=1000):
    if v != v or v == float('inf') or v == float('-inf'):
        return None, None
    if v == 0:
        return 0, 1
    sign = -1 if v < 0 else 1
    v = abs(v)
    best_num, best_den = int(round(v)), 1
    best_err = abs(v - best_num)
    for den in range(2, max_den + 1):
        num = round(v * den)
        err = abs(v - num / den)
        if err < best_err:
            best_err = err
            best_num, best_den = num, den
        if err < 1e-9:
            break
    return sign * best_num, best_den


def _ew(elems):
    w = 0
    for e in elems:
        if isinstance(e, str):
            w += 12
        elif isinstance(e, list):
            w += _nw(e)
    return w


def _nw(node):
    t = node[0]
    if t == 'F':
        return max(_ew(node[1]), _ew(node[2]), 12) + 8
    if t == 'P':
        return max(_ew(node[1]), 12) + max(_ew(node[2]), 12)
    if t == 'S':
        return 6 + max(_ew(node[1]), 12) + 8
    if t == 'I':
        return 54
    if t == 'M':
        return 54
    if t == 'D':
        return 54 + max(_ew(node[2]), 12)
    if t == 'L':
        return 54 + max(_ew(node[3]), 12)
    if t == 'R':
        return max(_ew(node[1]), 12) + max(_ew(node[2]), 12) + 4
    return 0


def _pts(tft, data, cx, y, color):
    for dx, dy in data:
        tft.pixel(cx + dx, y + dy, color)


def _re(tft, elems, cx, y, buf, color, bg):
    in_list = buf.cl is elems
    for i, e in enumerate(elems):
        if in_list and buf.ci == i:
            tft.text15('_', cx, y, _ACCENT, bg)
            cx += 12
        if isinstance(e, str):
            tft.text15(e, cx, y, color, bg)
            cx += 12
        elif isinstance(e, list):
            cx = _rn(tft, e, cx, y, buf, color, bg)
    if in_list and buf.ci >= len(elems):
        tft.text15('_', cx, y, _ACCENT, bg)
        cx += 12
    return cx


def _rn(tft, node, cx, y, buf, color, bg):
    t = node[0]
    if t == 'F':
        return _rf(tft, node, cx, y, buf, color, bg)
    if t == 'P':
        return _rp(tft, node, cx, y, buf, color, bg)
    if t == 'S':
        return _rs(tft, node, cx, y, buf, color, bg)
    if t == 'I':
        return _ri(tft, node, cx, y, buf, color, bg)
    if t == 'M':
        return _rm(tft, node, cx, y, buf, color, bg)
    if t == 'D':
        return _rd(tft, node, cx, y, buf, color, bg)
    if t == 'L':
        return _rli(tft, node, cx, y, buf, color, bg)
    if t == 'R':
        return _rsub(tft, node, cx, y, buf, color, bg)
    return cx


def _rf(tft, node, cx, y, buf, color, bg):
    nw = _ew(node[1])
    dw = _ew(node[2])
    mw = max(nw, dw, 12)
    nx = cx + (mw - nw) // 2
    _re(tft, node[1], nx, y - 4, buf, color, bg)
    tft.hline(cx, y + 10, mw, color)
    tft.pixel(cx, y + 10, color)
    tft.pixel(cx + mw - 1, y + 10, color)
    dx = cx + (mw - dw) // 2
    _re(tft, node[2], dx, y + 12, buf, color, bg)
    return cx + mw + 4


def _rp(tft, node, cx, y, buf, color, bg):
    bx = _re(tft, node[1], cx, y, buf, color, bg)
    _re(tft, node[2], bx, y - 6, buf, color, bg)
    return bx + _ew(node[2])


def _rs(tft, node, cx, y, buf, color, bg):
    tft.vline(cx, y + 2, 12, color)
    tft.hline(cx, y + 14, 4, color)
    tft.pixel(cx + 1, y + 1, color)
    tft.pixel(cx + 2, y, color)
    ix = cx + 6
    iw = max(_ew(node[1]), 12)
    _re(tft, node[1], ix, y, buf, color, bg)
    tft.hline(ix, y - 1, iw + 4, color)
    return ix + iw + 6


def _ri(tft, node, cx, y, buf, color, bg):
    _pts(tft, _INT_PTS, cx, y, color)
    ul = buf.flatten(node[2])
    if ul:
        tft.text8(ul, cx + 8, y - 2, _YELLOW, bg)
    ll = buf.flatten(node[1])
    if ll:
        tft.text8(ll, cx + 8, y + 19, _YELLOW, bg)
    _re(tft, node[3], cx + 8, y + 5, buf, color, bg)
    return cx + 54


def _rm(tft, node, cx, y, buf, color, bg):
    _pts(tft, _SIG_PTS, cx, y, color)
    ul = buf.flatten(node[3])
    if ul:
        tft.text8(ul, cx + 12, y - 4, _YELLOW, bg)
    ll = buf.flatten(node[2])
    if ll:
        tft.text8(ll, cx + 12, y + 15, _YELLOW, bg)
    _re(tft, node[4], cx + 12, y + 2, buf, color, bg)
    return cx + 54


def _rd(tft, node, cx, y, buf, color, bg):
    tft.text15('d/d' + node[1], cx, y, color, bg)
    _re(tft, node[2], cx + 48, y, buf, color, bg)
    return cx + 48 + _ew(node[2])


def _rli(tft, node, cx, y, buf, color, bg):
    tft.text8('lim', cx, y + 2, color, bg)
    vx = cx
    vy = y + 13
    for ch in node[1]:
        tft.text8(ch, vx, vy, color, bg)
        vx += 8
    _pts(tft, _ARR_PTS, vx, vy - 1, color)
    vx += 7
    for ch in node[2]:
        tft.text8(ch, vx, vy, color, bg)
        vx += 8
    _re(tft, node[3], cx + 48, y + 4, buf, color, bg)
    return cx + 48 + _ew(node[3])


def _rsub(tft, node, cx, y, buf, color, bg):
    bx = _re(tft, node[1], cx, y, buf, color, bg)
    _re(tft, node[2], bx, y + 6, buf, color, bg)
    return bx + _ew(node[2]) + 2


def render_math_input(tft, buf, x, y, color=_FG, bg=_BG):
    tft.fill_rect(x, y, 480 - x, 40, bg)
    _re(tft, buf.top, x, y, buf, color, bg)


def render_header(tft, frac_mode, angle_mode, hist_count=0, cas_mode=False):
    tft.fill_rect(0, 0, 480, HEADER_H, 0x1082)
    tft.text15('Espelt Math', 170, 4, _ACCENT, 0x1082)
    cas_str = 'CAS' if cas_mode else ''
    info = '{} | H:{}{}'.format(angle_mode, hist_count, ' | ' + cas_str if cas_str else '')
    tw = len(info) * 12
    tft.text15(info, 480 - tw - 4, 4, _YELLOW, 0x1082)
    tft.hline(0, HEADER_H, 480, _ACCENT)


def render_prompt(tft, buf, frac_mode, angle_mode, y=PROMPT_Y):
    tft.fill_rect(0, y, 480, 40, _BG)
    mode_str = '{} | {}'.format(angle_mode, 'Frac ON' if frac_mode else 'Frac OFF')
    tft.text15(mode_str, 4, y + 2, _GRAY, _BG)
    render_math_input(tft, buf, 4, y + 18, _FG, _BG)


def render_results_area(tft, results, last_steps=None, scroll_idx=0, y_start=RESULTS_Y, y_end=MATH_Y - 2):
    tft.fill_rect(0, y_start, 480, y_end - y_start, _BG)
    tft.vline(240, y_start, y_end - y_start, _DGRAY)
    visible_h = y_end - y_start
    max_lines = visible_h // LINE_H
    start = max(0, len(results) - max_lines - scroll_idx)
    end = min(len(results), start + max_lines)
    y = y_start
    for i in range(start, end):
        entry = results[i]
        color = _FG
        if isinstance(entry, str):
            if entry.startswith('>'):
                color = _ACCENT
            elif entry.startswith('='):
                color = _GREEN
            elif entry.startswith('Error'):
                color = _RED
            tft.text15(entry[:19], 4, y, color, _BG)
        else:
            tft.text15(str(entry)[:19], 4, y, color, _BG)
        y += LINE_H
    if last_steps:
        y = y_start
        tft.text15('Steps:', 244, y, _YELLOW, _BG)
        y += LINE_H
        step_start = max(0, len(last_steps) - (max_lines - 1))
        for i in range(step_start, len(last_steps)):
            if y >= y_end:
                break
            tft.text15(last_steps[i][:19], 244, y, _GREEN, _BG)
            y += LINE_H


def render_math_display(tft, value=None, frac_mode=False, help_lines=None):
    tft.fill_rect(0, MATH_Y, 480, MATH_H, _BG)
    tft.hline(0, MATH_Y, 480, _DGRAY)
    if help_lines:
        y = MATH_Y + 2
        for line in help_lines[:2]:
            tft.text15(line[:38], 4, y, _YELLOW, _BG)
            y += 14
    elif value is not None:
        render_math_value(tft, value, 8, MATH_Y + 4, frac_mode, _GREEN)


def render_math_value(tft, value, x, y, frac_mode=False, color=_FG):
    if isinstance(value, list):
        tft.text15(_fmt_matrix(value)[:38], x, y, color, _BG)
        return
    if not isinstance(value, float):
        tft.text15(str(value), x, y, color, _BG)
        return
    if frac_mode:
        num, den = _to_fraction(value)
        if num is not None and den != 1:
            prefix = ''
            abs_num = abs(num)
            if num < 0:
                prefix = '-'
            if abs_num >= den:
                whole = abs_num // den
                rem = abs_num % den
                if rem == 0:
                    tft.text15('{}{}'.format(prefix, whole), x, y, color, _BG)
                    return
                whole_str = '{}{}'.format(prefix, whole)
                ww = len(whole_str) * 12
                nw = len(str(rem)) * 12
                dw = len(str(den)) * 12
                fw = max(nw, dw)
                tft.text15(whole_str, x, y, color, _BG)
                fx = x + ww + 4
                tft.text15(str(rem), fx + (fw - nw) // 2, y - 4, color, _BG)
                tft.hline(fx, y + 10, fw, color)
                tft.text15(str(den), fx + (fw - dw) // 2, y + 12, color, _BG)
                return
            nw = len(str(num)) * 12
            dw = len(str(den)) * 12
            mw = max(nw, dw)
            tft.text15('{}{}'.format(prefix, abs_num) if num < 0 else str(num), x + (mw - nw) // 2, y - 4, color, _BG)
            tft.hline(x, y + 10, mw, color)
            tft.text15(str(den), x + (mw - dw) // 2, y + 12, color, _BG)
            return
    tft.text15(_fmt_num(value, False), x, y, color, _BG)


def render_error(tft, msg, y=PROMPT_Y):
    tft.fill_rect(0, y, 480, 16, _BG)
    tft.text15(msg[:38], 4, y, _RED, _BG)


def render_info(tft, msg, y=PROMPT_Y):
    tft.fill_rect(0, y, 480, 16, _BG)
    tft.text15(msg[:38], 4, y, _GREEN, _BG)
