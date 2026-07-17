"""Minimal SVG parser for flag rendering.
Handles simple <path> elements with rectangular shapes.
Also handles stroked paths (lines) for Nordic crosses.
Returns a list of draw operations compatible with our flag renderer.
"""


def _hex_to_rgb565(hexstr):
    h = hexstr.lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def _parse_viewbox(svg):
    """Extract viewBox dimensions. Returns (x, y, w, h) or None.
    Falls back to width/height attributes if no viewBox is present.
    """
    i = svg.find('viewBox="')
    if i < 0:
        i = svg.find("viewBox='")
    if i >= 0:
        start = i + 9
        if svg[i + 8] == "'":
            start = i + 9
        end = svg.find('"', start)
        if end < 0:
            end = svg.find("'", start)
        if end >= 0:
            parts = svg[start:end].split()
            if len(parts) == 4:
                try:
                    return (float(parts[0]), float(parts[1]),
                            float(parts[2]), float(parts[3]))
                except ValueError:
                    pass
    w_i = svg.find('width="')
    h_i = svg.find('height="')
    if w_i >= 0 and h_i >= 0:
        w_end = svg.find('"', w_i + 7)
        h_end = svg.find('"', h_i + 8)
        if w_end >= 0 and h_end >= 0:
            try:
                w = float(svg[w_i+7:w_end])
                h = float(svg[h_i+8:h_end])
                return (0.0, 0.0, w, h)
            except ValueError:
                pass
    return (0.0, 0.0, 100.0, 60.0)


def _extract_attr(tag, name):
    """Extract attribute value from a tag string."""
    q1 = name + '="'
    i = tag.find(q1)
    if i >= 0:
        start = i + len(q1)
        end = tag.find('"', start)
        if end < 0:
            return None
        return tag[start:end]
    q1 = name + "='"
    i = tag.find(q1)
    if i < 0:
        return None
    start = i + len(q1)
    end = tag.find("'", start)
    if end < 0:
        return None
    return tag[start:end]


def _parse_stroke_width(tag):
    val = _extract_attr(tag, 'stroke-width')
    if val is None:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def _extract_stroke_color(tag):
    val = _extract_attr(tag, 'stroke')
    if val is None or val == 'none':
        return None
    try:
        return _hex_to_rgb565(val)
    except Exception:
        return None


def _parse_path_rect(d, vb_x, vb_y, vb_w, vb_h):
    """Parse a simple rectangular filled path.
    Returns (x, y, w, h) in viewBox coords or None.
    Uses bounding box of all points traversed.
    Handles paths with multiple sub-paths (multiple M commands) by
    returning a list of rectangles or None.
    """
    d = d.replace(',', ' ')
    d = d.replace('M', ' M ').replace('H', ' H ').replace('V', ' V ')
    d = d.replace('h', ' h ').replace('v', ' v ').replace('Z', ' Z ').replace('z', ' z ')
    tokens = d.split()
    if not tokens:
        return None
    x, y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    i = 0
    rect_moves = 0
    seen_any_z = False
    rects = []
    cur_min_x = 999999.0
    cur_min_y = 999999.0
    cur_max_x = -999999.0
    cur_max_y = -999999.0
    while i < len(tokens):
        t = tokens[i]
        if t == 'M':
            if rect_moves == 1:
                if cur_min_x != cur_max_x and cur_min_y != cur_max_y:
                    rw = cur_max_x - cur_min_x
                    rh = cur_max_y - cur_min_y
                    if rw >= 0.01 and rh >= 0.01:
                        if seen_any_z or (rw > 0 and rh > 0):
                            rects.append((cur_min_x - vb_x, cur_min_y - vb_y, rw, rh))
            if i + 2 > len(tokens):
                return None
            try:
                x = float(tokens[i+1])
                y = float(tokens[i+2])
            except (ValueError, IndexError):
                return None
            start_x, start_y = x, y
            rect_moves = 1
            cur_min_x = x
            cur_min_y = y
            cur_max_x = x
            cur_max_y = y
            i += 3
        elif t == 'H':
            try:
                x = float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            if x < cur_min_x: cur_min_x = x
            if x > cur_max_x: cur_max_x = x
            i += 2
        elif t == 'V':
            try:
                y = float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            if y < cur_min_y: cur_min_y = y
            if y > cur_max_y: cur_max_y = y
            i += 2
        elif t == 'h':
            try:
                x += float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            if x < cur_min_x: cur_min_x = x
            if x > cur_max_x: cur_max_x = x
            i += 2
        elif t == 'v':
            try:
                y += float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            if y < cur_min_y: cur_min_y = y
            if y > cur_max_y: cur_max_y = y
            i += 2
        elif t == 'Z' or t == 'z':
            seen_any_z = True
            i += 1
        else:
            return None
    if rect_moves == 1:
        if cur_min_x != cur_max_x and cur_min_y != cur_max_y:
            rw = cur_max_x - cur_min_x
            rh = cur_max_y - cur_min_y
            if rw >= 0.01 and rh >= 0.01:
                if seen_any_z or (rw > 0 and rh > 0):
                    rects.append((cur_min_x - vb_x, cur_min_y - vb_y, rw, rh))
    if not rects:
        return None
    if len(rects) == 1:
        return rects[0]
    return rects


def _parse_path_stroke(d, vb_x, vb_y, vb_w, vb_h, stroke_width):
    """Parse a stroke path that may contain multiple sub-paths (lines).
    Returns a list of (x, y, w, h) rectangles or None.
    """
    d = d.replace(',', ' ')
    d = d.replace('M', ' M ').replace('H', ' H ').replace('V', ' V ')
    d = d.replace('h', ' h ').replace('v', ' v ').replace('Z', ' Z ').replace('z', ' z ')
    tokens = d.split()
    if not tokens:
        return None
    rects = []
    x, y = 0.0, 0.0
    i = 0
    cur_start_x = 0.0
    cur_start_y = 0.0
    cur_moves = 0
    half = stroke_width / 2.0
    while i < len(tokens):
        t = tokens[i]
        if t == 'M':
            if cur_moves == 1:
                min_x = min(cur_start_x, x)
                min_y = min(cur_start_y, y)
                max_x = max(cur_start_x, x)
                max_y = max(cur_start_y, y)
                rw = max_x - min_x
                rh = max_y - min_y
                if rw >= 0.01 and rh < 0.01:
                    rects.append((min_x - vb_x, min_y - half - vb_y, rw, stroke_width))
                elif rh >= 0.01 and rw < 0.01:
                    rects.append((min_x - half - vb_x, min_y - vb_y, stroke_width, rh))
            if i + 2 > len(tokens):
                return None
            try:
                x = float(tokens[i+1])
                y = float(tokens[i+2])
            except (ValueError, IndexError):
                return None
            cur_start_x, cur_start_y = x, y
            cur_moves = 1
            i += 3
        elif t == 'H':
            try:
                x = float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            i += 2
        elif t == 'V':
            try:
                y = float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            i += 2
        elif t == 'h':
            try:
                x += float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            i += 2
        elif t == 'v':
            try:
                y += float(tokens[i+1])
            except (ValueError, IndexError):
                return None
            i += 2
        elif t == 'Z' or t == 'z':
            i += 1
        else:
            return None
    if cur_moves == 1:
        min_x = min(cur_start_x, x)
        min_y = min(cur_start_y, y)
        max_x = max(cur_start_x, x)
        max_y = max(cur_start_y, y)
        rw = max_x - min_x
        rh = max_y - min_y
        if rw >= 0.01 and rh < 0.01:
            rects.append((min_x - vb_x, min_y - half - vb_y, rw, stroke_width))
        elif rh >= 0.01 and rw < 0.01:
            rects.append((min_x - half - vb_x, min_y - vb_y, stroke_width, rh))
    if not rects:
        return None
    return rects


def parse_svg(svg):
    """Parse an SVG string. Returns list of ops:
       ('rect', x, y, w, h, color565) in viewBox units.
    Returns None if SVG is too complex to parse.
    """
    vb = _parse_viewbox(svg)
    if vb is None:
        return None
    vb_x, vb_y, vb_w, vb_h = vb

    ops = []
    pos = 0
    while True:
        path_start = svg.find('<path', pos)
        if path_start < 0:
            break
        path_end = svg.find('>', path_start)
        if path_end < 0:
            break
        tag = svg[path_start:path_end+1]

        is_stroke_only = ('fill="none"' in tag or "fill='none'" in tag)
        has_fill_attr = ('fill="' in tag or "fill='" in tag)

        if is_stroke_only:
            stroke_w = _parse_stroke_width(tag)
            if stroke_w is not None:
                d = _extract_attr(tag, 'd')
                if d:
                    color = _extract_stroke_color(tag)
                    if color is not None:
                        rects = _parse_path_stroke(d, vb_x, vb_y, vb_w, vb_h, stroke_w)
                        if rects:
                            for rect in rects:
                                rx, ry, rw, rh = rect
                                ops.append(('rect', rx, ry, rw, rh, color))
            pos = path_end + 1
            continue

        if not has_fill_attr:
            stroke_w = _parse_stroke_width(tag)
            if stroke_w is not None:
                d = _extract_attr(tag, 'd')
                if d:
                    color = _extract_stroke_color(tag)
                    if color is not None:
                        rects = _parse_path_stroke(d, vb_x, vb_y, vb_w, vb_h, stroke_w)
                        if rects:
                            for rect in rects:
                                rx, ry, rw, rh = rect
                                ops.append(('rect', rx, ry, rw, rh, color))
                pos = path_end + 1
                continue
            fill = '#000000'
        else:
            fill = _extract_attr(tag, 'fill')
            if fill is None or fill in ('none', 'currentColor'):
                pos = path_end + 1
                continue

        d = _extract_attr(tag, 'd')
        if d is None:
            pos = path_end + 1
            continue

        rects = _parse_path_rect(d, vb_x, vb_y, vb_w, vb_h)
        if rects is None:
            return None
        try:
            color = _hex_to_rgb565(fill)
        except Exception:
            pos = path_end + 1
            continue
        if isinstance(rects, list):
            for rect in rects:
                rx, ry, rw, rh = rect
                ops.append(('rect', rx, ry, rw, rh, color))
        else:
            rx, ry, rw, rh = rects
            ops.append(('rect', rx, ry, rw, rh, color))
        pos = path_end + 1
    return ops


def is_simple(svg):
    return parse_svg(svg) is not None
