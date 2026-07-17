import math
import time


def graph_on_oled(oled, expr):
    if not oled:
        return
    if not expr or not expr.strip():
        return

    W = 128
    H = 64
    MARGIN_LEFT = 14
    MARGIN_RIGHT = 4
    MARGIN_TOP = 6
    MARGIN_BOTTOM = 10
    PLOT_W = W - MARGIN_LEFT - MARGIN_RIGHT
    PLOT_H = H - MARGIN_TOP - MARGIN_BOTTOM

    x_min, x_max = -6.28, 6.28
    y_min, y_max = -3.0, 3.0

    samples = PLOT_W
    points = []
    for i in range(samples):
        x_val = x_min + (x_max - x_min) * i / (samples - 1)
        try:
            y_val = _eval_graph_expr(expr, x_val)
            if y_val is not None and not (y_val != y_val) and abs(y_val) < 1e6:
                points.append((i, y_val))
            else:
                points.append((i, None))
        except:
            points.append((i, None))

    y_vals = [p[1] for p in points if p[1] is not None]
    if not y_vals:
        oled.fill(0)
        oled.text('No data to plot', 10, 24)
        oled.show()
        return

    if len(y_vals) > 2:
        y_vals_sorted = sorted(y_vals)
        p10 = y_vals_sorted[len(y_vals_sorted) // 10]
        p90 = y_vals_sorted[-len(y_vals_sorted) // 10 - 1]
        y_range = p90 - p10
        if y_range < 0.01:
            y_range = 2.0
        y_mid = (p90 + p10) / 2
        y_min = y_mid - y_range * 0.6
        y_max = y_mid + y_range * 0.6

    oled.fill(0)

    _draw_axes(oled, MARGIN_LEFT, MARGIN_TOP, PLOT_W, PLOT_H, x_min, x_max, y_min, y_max)

    prev_py = None
    for i, (px, y_val) in enumerate(points):
        if y_val is None:
            prev_py = None
            continue
        py = MARGIN_TOP + PLOT_H - int((y_val - y_min) / (y_max - y_min) * PLOT_H)
        py = max(MARGIN_TOP, min(MARGIN_TOP + PLOT_H - 1, py))
        screen_x = MARGIN_LEFT + px
        if prev_py is not None and abs(py - prev_py) < 8:
            _draw_line(oled, screen_x - 1, prev_py, screen_x, py, 1)
        else:
            oled.pixel(screen_x, py, 1)
        prev_py = py

    _draw_label(oled, expr[:16], 0, 0)
    oled.show()


def _draw_axes(oled, ox, oy, pw, ph, xmin, xmax, ymin, ymax):
    oled.hline(ox, oy + ph, pw, 1)
    oled.vline(ox, oy, ph, 1)

    if ymin < 0 < ymax:
        y_zero = oy + ph - int((0 - ymin) / (ymax - ymin) * ph)
        oled.hline(ox, y_zero, pw, 1)

    if xmin < 0 < xmax:
        x_zero = ox + int((0 - xmin) / (xmax - xmin) * pw)
        oled.vline(x_zero, oy, ph, 1)

    oled.text('x', ox + pw - 6, oy + ph + 1, 1)
    oled.text('y', 1, oy, 1)


def _draw_line(oled, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < 128 and 0 <= y0 < 64:
            oled.pixel(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def _draw_label(oled, text, x, y):
    oled.fill_rect(x, y, len(text) * 6, 8, 0)
    oled.text(text, x, y, 1)


def _eval_graph_expr(expr, x):
    import math as _math
    expr = expr.strip()
    expr = expr.replace('^', '**')
    expr = expr.replace('pi', str(_math.pi))
    for fn_name in ('exp', 'ceil', 'cos', 'sin', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'sqrt', 'log', 'ln', 'abs', 'floor'):
        expr = expr.replace(fn_name, fn_name.replace('e', '_E_E_'))
    expr = expr.replace('e', str(_math.e))
    for fn_name in ('exp', 'ceil', 'cos', 'sin', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'sqrt', 'log', 'ln', 'abs', 'floor'):
        expr = expr.replace(fn_name.replace('e', '_E_E_'), fn_name)

    namespace = {
        'x': x,
        'sin': _math.sin,
        'cos': _math.cos,
        'tan': _math.tan,
        'asin': _math.asin,
        'acos': _math.acos,
        'atan': _math.atan,
        'sinh': _math.sinh,
        'cosh': _math.cosh,
        'tanh': _math.tanh,
        'log': _math.log10,
        'ln': _math.log,
        'sqrt': _math.sqrt,
        'abs': abs,
        'pi': _math.pi,
        'e': _math.e,
        'exp': _math.exp,
        'floor': _math.floor,
        'ceil': _math.ceil,
    }

    result = eval(expr, namespace)
    return float(result)
