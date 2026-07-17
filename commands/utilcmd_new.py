import time


def cmd_draw(args, tft=None):
    def _draw_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS

        CW = 480
        CH = 280
        Y0 = 25

        PALETTE = [
            0xFFFF, 0xF800, 0x07E0, 0x001F,
            0xFFE0, 0x07FF, 0xFC1F, 0x8410,
            0x0000, 0x4208, 0x8400, 0x0200,
            0x0010, 0x0210, 0x0400, 0x8000,
        ]
        ci = 0
        color = PALETTE[ci]

        BRUSH_SIZES = [1, 2, 4, 8]
        bi = 0
        brush = BRUSH_SIZES[bi]

        tool = 'pen'
        cx, cy = CW // 2, CH // 2
        line_start = None
        rect_start = None

        undo_stack = []
        MAX_UNDO = 20

        canvas = [[0x0000] * CW for _ in range(CH)]

        def _get_theme():
            try:
                from commands.dispatch import THEME_COLORS as tc
                return tc
            except:
                return None

        def _header():
            tc = _get_theme()
            ac = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.text15('Paint', 4, 4, ac, bg)
            tft.text15(f'{tool} B:{brush} C:{ci}', 100, 4, 0xFFFF, bg)
            tft.text15(f'{cx},{cy}', 340, 4, 0x8410, bg)
            tft.hline(0, 24, 480, ac)

        def _draw_toolbar():
            tc = _get_theme()
            bg = tc.get('header', 0x1082) if tc else 0x1082
            ty = Y0 + CH
            tft.fill_rect(0, ty, 480, 20, bg)
            for i, c in enumerate(PALETTE):
                row = i // 8
                col = i % 8
                x = 4 + col * 28
                y = ty + 2 + row * 9
                tft.fill_rect(x, y, 8, 8, c)
                if i == ci:
                    tft.rect(x - 1, y - 1, 10, 10, 0xFFE0)
            tft.text15('D:pen E:eraser F:fill L:line R:rect B:size C:col U:undo', 230, ty + 3, 0x8410, bg)
            tft.text15('S:save X:load Z:clear Q:quit', 230, ty + 11, 0x8410, bg)

        def _draw_cursor():
            half = 12
            for dx in range(-half, half + 1):
                if dx != 0:
                    px = cx + dx
                    if 0 <= px < CW:
                        tft.pixel(px, Y0 + cy, 0xFFE0)
            for dy in range(-half, half + 1):
                if dy != 0:
                    py = cy + dy
                    if 0 <= py < CH:
                        tft.pixel(cx, Y0 + py, 0xFFE0)
            tft.pixel(cx, Y0 + cy, 0xFFFF)

        def _erase_cursor():
            half = 12
            for dx in range(-half, half + 1):
                if dx != 0:
                    px = cx + dx
                    if 0 <= px < CW:
                        tft.pixel(px, Y0 + cy, canvas[cy][px])
            for dy in range(-half, half + 1):
                if dy != 0:
                    py = cy + dy
                    if 0 <= py < CH:
                        tft.pixel(cx, Y0 + py, canvas[py][cx])

        def _push_undo(x, y):
            undo_stack.append((x, y, canvas[y][x]))
            if len(undo_stack) > MAX_UNDO:
                undo_stack.pop(0)

        def _draw_pixel(x, y, c):
            half = brush // 2
            for dy in range(-half, half + (1 if brush % 2 else 0)):
                for dx in range(-half, half + (1 if brush % 2 else 0)):
                    px, py = x + dx, y + dy
                    if 0 <= px < CW and 0 <= py < CH:
                        _push_undo(px, py)
                        canvas[py][px] = c
                        tft.fill_rect(px, Y0 + py, 1, 1, c)

        def _flood_fill(x, y, new_color):
            if not (0 <= x < CW and 0 <= y < CH):
                return
            target = canvas[y][x]
            if target == new_color:
                return
            stack = [(x, y)]
            while stack:
                fx, fy = stack.pop()
                if 0 <= fx < CW and 0 <= fy < CH and canvas[fy][fx] == target:
                    _push_undo(fx, fy)
                    canvas[fy][fx] = new_color
                    tft.fill_rect(fx, Y0 + fy, 1, 1, new_color)
                    stack.append((fx + 1, fy))
                    stack.append((fx - 1, fy))
                    stack.append((fx, fy + 1))
                    stack.append((fx, fy - 1))

        def _bresenham_line(x0, y0, x1, y1, c):
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy
            while True:
                _draw_pixel(x0, y0, c)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy

        def _draw_rect_outline(x0, y0, x1, y1, c):
            rx0, rx1 = min(x0, x1), max(x0, x1)
            ry0, ry1 = min(y0, y1), max(y0, y1)
            for x in range(rx0, rx1 + 1):
                _draw_pixel(x, ry0, c)
                if ry0 != ry1:
                    _draw_pixel(x, ry1, c)
            for y in range(ry0 + 1, ry1):
                _draw_pixel(rx0, y, c)
                if rx0 != rx1:
                    _draw_pixel(rx1, y, c)

        def _undo():
            if not undo_stack:
                return
            action = []
            while undo_stack:
                entry = undo_stack[-1]
                undo_stack.pop()
                action.append(entry)
                if len(action) >= brush * brush and brush > 1:
                    break
                if len(action) >= 1 and brush == 1:
                    break
            for x, y, old_c in action:
                canvas[y][x] = old_c
                tft.fill_rect(x, Y0 + y, 1, 1, old_c)

        def _clear():
            for y in range(CH):
                for x in range(CW):
                    canvas[y][x] = 0x0000
            tft.fill_rect(0, Y0, CW, CH, 0x0000)

        def _save():
            try:
                with open('/sd/paint.bin', 'wb') as f:
                    for y in range(CH):
                        for x in range(CW):
                            c = canvas[y][x]
                            f.write(bytes([c >> 8, c & 0xFF]))
                return True
            except:
                return False

        def _load():
            try:
                with open('/sd/paint.bin', 'rb') as f:
                    for y in range(CH):
                        for x in range(CW):
                            d = f.read(2)
                            if len(d) < 2:
                                return False
                            canvas[y][x] = (d[0] << 8) | d[1]
                tft.fill_rect(0, Y0, CW, CH, 0x0000)
                for y in range(CH):
                    for x in range(CW):
                        c = canvas[y][x]
                        if c != 0x0000:
                            tft.fill_rect(x, Y0 + y, 1, 1, c)
                return True
            except:
                return False

        _header()
        tft.fill_rect(0, Y0, CW, CH, 0x0000)
        _draw_toolbar()
        _draw_cursor()

        while True:
            ch = read_key()
            if ch is None:
                continue

            if ch == 'q' or ch == 'Q':
                return

            handled = True
            if ch == 'd':
                tool = 'pen'
            elif ch == 'e':
                tool = 'eraser'
            elif ch == 'f':
                tool = 'fill'
            elif ch == 'l':
                if tool == 'line' and line_start is not None:
                    _bresenham_line(line_start[0], line_start[1], cx, cy, color)
                    line_start = None
                    tool = 'pen'
                else:
                    tool = 'line'
                    line_start = (cx, cy)
            elif ch == 'r':
                if tool == 'rect' and rect_start is not None:
                    _draw_rect_outline(rect_start[0], rect_start[1], cx, cy, color)
                    rect_start = None
                    tool = 'pen'
                else:
                    tool = 'rect'
                    rect_start = (cx, cy)
            elif ch == 'b':
                bi = (bi + 1) % len(BRUSH_SIZES)
                brush = BRUSH_SIZES[bi]
            elif ch == 'c':
                ci = (ci + 1) % len(PALETTE)
                color = PALETTE[ci]
            elif ch == 'u':
                _undo()
            elif ch == 's':
                _save()
            elif ch == 'x':
                _load()
            elif ch == 'z':
                _clear()
            elif ch == '\x85':
                cx = max(0, cx - 1)
            elif ch == '\x84':
                cx = min(CW - 1, cx + 1)
            elif ch == '\x80':
                cy = max(0, cy - 1)
            elif ch == '\x81':
                cy = min(CH - 1, cy + 1)
            else:
                handled = False

            if handled:
                if tool == 'pen':
                    _draw_pixel(cx, cy, color)
                elif tool == 'eraser':
                    _draw_pixel(cx, cy, 0x0000)
                elif tool == 'fill':
                    _flood_fill(cx, cy, color)

                _erase_cursor()
                _draw_cursor()
                _header()
                _draw_toolbar()

    return ('game', _draw_loop)


def cmd_calendar(args, tft=None):
    def _cal_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS
        import time as _time
        t = _time.localtime()
        year = t[0]
        month = t[1]
        cur_day = t[2]
        MONTHS = ['','January','February','March','April','May','June',
                  'July','August','September','October','November','December']
        DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

        def days_in_month(y, m):
            if m in (1,3,5,7,8,10,12): return 31
            if m in (4,6,9,11): return 30
            if m == 2:
                return 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
            return 30

        def day_of_week(y, m, d):
            if m < 3:
                m += 12
                y -= 1
            k = d
            j = y // 100
            h = (k + (13 * (m + 1)) // 5 + y + y // 4 - j // 4 + j * 5) % 7
            return (h + 6) % 7

        def _header():
            try:
                from commands.dispatch import THEME_COLORS as tc
            except:
                tc = None
            c = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.text15(f'{MONTHS[month]} {year}', 160, 4, c, bg)
            tft.hline(0, 24, 480, c)

        def _draw_cal():
            tft.fill_rect(0, 25, 480, 295, 0x0000)
            cell_w = 60
            cell_h = 38
            ox = 30
            oy = 35
            for i, d in enumerate(DAYS):
                x = ox + i * cell_w
                tft.text15(d, x + 16, oy, 0x07FF, 0x0000)
            oy += 20
            first_dow = day_of_week(year, month, 1)
            total = days_in_month(year, month)
            day = 1
            for row in range(6):
                if day > total:
                    break
                for col in range(7):
                    x = ox + col * cell_w
                    y = oy + row * cell_h
                    if row == 0 and col < first_dow:
                        continue
                    if day > total:
                        break
                    if day == cur_day:
                        tft.fill_rect(x + 2, y + 2, cell_w - 4, cell_h - 4, 0x07FF)
                        tft.text15(f'{day:2d}', x + 20, y + 10, 0x0000, 0x07FF)
                    else:
                        tft.rect(x + 2, y + 2, cell_w - 4, cell_h - 4, 0x4208)
                        tft.text15(f'{day:2d}', x + 20, y + 10, 0xFFFF, 0x0000)
                    day += 1
            tft.text('Left/Right=month Q=quit', 4, 308, 0x07E0, 0x0000)

        _header()
        _draw_cal()

        while True:
            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q':
                return
            elif ch == '\x85':
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
                _header()
                _draw_cal()
            elif ch == '\x84':
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                _header()
                _draw_cal()

    return ('game', _cal_loop)


def cmd_alarm(args, tft=None):
    def _alarm_loop(tft, read_key):
        from lib.buzzer import Buzzer
        import time as _time
        buzzer = Buzzer(20)
        alarms = []
        selected = 0
        input_buf = ''
        input_mode = 'time'
        a_h = 0
        a_m = 0
        t = _time.localtime()
        now_h = t[3]
        now_m = t[4]

        def _header():
            try:
                from commands.dispatch import THEME_COLORS as tc
            except:
                tc = None
            c = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.text15('Alarm Clock', 170, 4, c, bg)
            tft.hline(0, 24, 480, c)

        def _draw():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            t = _time.localtime()
            now_h = t[3]
            now_m = t[4]
            tft.text15(f'Now: {now_h:02d}:{now_m:02d}', 4, 32, 0xFFE0, 0x0000)
            tft.hline(0, 50, 480, 0x4208)
            if input_mode == 'time':
                tft.text15('New alarm (HH:MM):', 4, 58, 0xFFFF, 0x0000)
                tft.text15(f'{a_h:02d}:{a_m:02d} {input_buf}', 4, 78, 0x07E0, 0x0000)
                tft.text('1-9=set hour 0=set min Enter=save', 4, 290, 0x8410, 0x0000)
            else:
                tft.text15('Alarms:', 4, 58, 0xFFFF, 0x0000)
                y = 78
                for i, (ah, am) in enumerate(alarms):
                    marker = '> ' if i == selected else '  '
                    color = 0x07E0 if i == selected else 0xFFFF
                    tft.text15(f'{marker}{ah:02d}:{am:02d}', 4, y, color, 0x0000)
                    y += 18
                tft.text('A=add D=delete N=new Q=quit', 4, 290, 0x8410, 0x0000)

        _header()
        _draw()

        while True:
            ch = read_key()
            if ch is None:
                continue
            t = _time.localtime()
            now_h = t[3]
            now_m = t[4]
            for ah, am in alarms:
                if now_h == ah and now_m == am and now_m % 60 == 0:
                    buzzer.alarm()
            if ch == 'q' or ch == 'Q':
                return
            elif ch == 'n':
                input_mode = 'time'
                a_h = 0
                a_m = 0
                input_buf = ''
                _draw()
            elif input_mode == 'time':
                if ch in '0123456789':
                    input_buf += ch
                    if len(input_buf) == 2:
                        a_h = int(input_buf[:2])
                        input_buf = ''
                    elif len(input_buf) >= 4:
                        a_m = int(input_buf[:2])
                        input_buf = ''
                elif ch == '\n':
                    if 0 <= a_h <= 23 and 0 <= a_m <= 59:
                        alarms.append((a_h, a_m))
                        alarms.sort()
                    input_mode = 'list'
                elif ch == '\x1b':
                    input_mode = 'list'
            else:
                if ch == '\x80' and selected > 0:
                    selected -= 1
                elif ch == '\x81' and selected < len(alarms) - 1:
                    selected += 1
                elif ch == 'd' and alarms:
                    alarms.pop(selected)
                    selected = min(selected, max(0, len(alarms) - 1))
            _draw()

    return ('game', _alarm_loop)


def cmd_notes(args, tft=None):
    def _notes_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS
        notes_dir = '/sd/notes'
        try:
            os.mkdir(notes_dir)
        except:
            pass
        files = []
        sel = 0
        mode = 'list'
        buf = ''
        edit_lines = []
        edit_idx = 0
        edit_name = ''
        scroll_off = 0
        EDIT_VIS = 15

        def _header():
            try:
                from commands.dispatch import THEME_COLORS as tc
            except:
                tc = None
            c = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            title = 'Notes' if mode == 'list' else f'Editing: {edit_name}'
            tft.text15(title, max(0, (480 - len(title) * 12) // 2), 4, c, bg)
            tft.hline(0, 24, 480, c)

        def _refresh_files():
            nonlocal files
            try:
                entries = os.listdir(notes_dir)
                files = [e for e in entries if e.endswith('.txt')]
            except:
                files = []

        def _draw_list():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            tft.text15('Notes:', 4, 32, 0xFFFF, 0x0000)
            y = 52
            for i, f in enumerate(files):
                marker = '> ' if i == sel else '  '
                color = 0x07E0 if i == sel else 0xFFFF
                tft.text15(f'{marker}{f}', 4, y, color, 0x0000)
                y += 16
            if not files:
                tft.text15('  (no notes)', 4, 52, 0x8410, 0x0000)
            tft.text('N=new O=open D=delete Q=quit', 4, 308, 0x8410, 0x0000)

        def _draw_editor():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            vis = edit_lines[scroll_off:scroll_off + EDIT_VIS]
            y = 30
            for i, l in enumerate(vis):
                line_num = scroll_off + i + 1
                is_cur = (scroll_off + i) == edit_idx
                color = 0x07E0 if is_cur else 0xFFFF
                tft.text15(f'{line_num:3d}', 4, y, 0x8410, 0x0000)
                tft.text15(l[:34], 44, y, color, 0x0000)
                y += 16
            tft.text('Enter=new line Ctrl+S=save Esc=exit', 4, 308, 0x8410, 0x0000)

        _refresh_files()
        _header()
        _draw_list()

        while True:
            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q':
                return
            if mode == 'list':
                if ch == 'n':
                    name = f'note{len(files)+1}.txt'
                    try:
                        with open(f'{notes_dir}/{name}', 'w') as f:
                            f.write('')
                        _refresh_files()
                        sel = len(files) - 1
                    except:
                        pass
                elif ch == 'o' and files:
                    edit_name = files[sel]
                    try:
                        with open(f'{notes_dir}/{edit_name}', 'r') as f:
                            edit_lines = f.read().split('\n')
                    except:
                        edit_lines = ['']
                    edit_idx = 0
                    scroll_off = 0
                    mode = 'edit'
                elif ch == 'd' and files:
                    try:
                        os.remove(f'{notes_dir}/{files[sel]}')
                        _refresh_files()
                        sel = min(sel, max(0, len(files) - 1))
                    except:
                        pass
                elif ch == '\x80':
                    sel = max(0, sel - 1)
                elif ch == '\x81':
                    sel = min(len(files) - 1, sel + 1)
            elif mode == 'edit':
                if ch == '\x1b':
                    mode = 'list'
                    _refresh_files()
                elif ch == '\x03':
                    if edit_name:
                        try:
                            with open(f'{notes_dir}/{edit_name}', 'w') as f:
                                f.write('\n'.join(edit_lines))
                        except:
                            pass
                    mode = 'list'
                    _refresh_files()
                elif ch == '\n':
                    edit_lines.insert(edit_idx + 1, buf)
                    edit_idx += 1
                    buf = ''
                    if edit_idx >= scroll_off + EDIT_VIS:
                        scroll_off = edit_idx - EDIT_VIS + 1
                elif ch == '\x80':
                    if edit_idx > 0:
                        edit_idx -= 1
                    if edit_idx < scroll_off:
                        scroll_off = edit_idx
                elif ch == '\x81':
                    if edit_idx < len(edit_lines) - 1:
                        edit_idx += 1
                    if edit_idx >= scroll_off + EDIT_VIS:
                        scroll_off = edit_idx - EDIT_VIS + 1
                elif ch == '\b' or ch == '\x7f':
                    if buf:
                        buf = buf[:-1]
                    elif edit_idx > 0:
                        prev = edit_lines[edit_idx - 1]
                        cur = edit_lines[edit_idx]
                        edit_lines[edit_idx - 1] = prev + cur
                        edit_lines.pop(edit_idx)
                        edit_idx -= 1
                        buf = edit_lines[edit_idx]
                elif len(ch) == 1 and ord(ch) >= 32 and ord(ch) <= 126:
                    buf += ch
            _header()
            if mode == 'list':
                _draw_list()
            else:
                _draw_editor()
                tft.fill_rect(0, 290, 480, 16, 0x1082)
                tft.text15('> ' + buf[:36], 4, 290, 0x07E0, 0x1082)

    return ('game', _notes_loop)


def cmd_reminders(args, tft=None):
    def _remind_loop(tft, read_key):
        import time
        from lib.buzzer import Buzzer
        from commands.dispatch import THEME_COLORS
        buzzer = Buzzer(20)
        reminders = []
        sel = 0
        mode = 'list'
        buf = ''
        input_field = 'time'
        r_min = 0
        r_text = ''

        def _header():
            try:
                from commands.dispatch import THEME_COLORS as tc
            except:
                tc = None
            c = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.text15('Reminders', 180, 4, c, bg)
            tft.hline(0, 24, 480, c)

        def _draw_list():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            t = time.localtime()
            now = t[3] * 60 + t[4]
            tft.text15(f'Now: {t[3]:02d}:{t[4]:02d}', 4, 32, 0xFFE0, 0x0000)
            tft.hline(0, 50, 480, 0x4208)
            y = 56
            for i, (mins, text) in enumerate(reminders):
                marker = '> ' if i == sel else '  '
                remaining = mins - now
                if remaining < 0:
                    remaining += 1440
                color = 0x07E0 if remaining > 0 else 0xF800
                rh = remaining // 60
                rm = remaining % 60
                tft.text15(f'{marker}{rh:02d}:{rm:02d} {text[:20]}', 4, y, color, 0x0000)
                y += 16
            if not reminders:
                tft.text15('  (no reminders)', 4, 56, 0x8410, 0x0000)
            tft.text('N=new D=delete Q=quit', 4, 308, 0x8410, 0x0000)

        def _draw_input():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            if input_field == 'time':
                tft.text15('Minutes from now:', 4, 32, 0xFFFF, 0x0000)
                tft.text15(f'{buf}_ min', 4, 52, 0x07E0, 0x0000)
                tft.text('Enter numbers then Enter', 4, 308, 0x8410, 0x0000)
            else:
                tft.text15('Reminder text:', 4, 32, 0xFFFF, 0x0000)
                tft.text15(f'{buf}_', 4, 52, 0x07E0, 0x0000)
                tft.text('Type text then Enter', 4, 308, 0x8410, 0x0000)

        _header()
        _draw_list()

        while True:
            t = time.localtime()
            now = t[3] * 60 + t[4]
            for mins, text in reminders:
                if now == mins:
                    buzzer.alarm()
            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q':
                return
            if mode == 'list':
                if ch == 'n':
                    mode = 'input'
                    input_field = 'time'
                    buf = ''
                    r_min = 0
                    r_text = ''
                elif ch == 'd' and reminders:
                    reminders.pop(sel)
                    sel = min(sel, max(0, len(reminders) - 1))
                elif ch == '\x80':
                    sel = max(0, sel - 1)
                elif ch == '\x81':
                    sel = min(len(reminders) - 1, sel + 1)
            elif mode == 'input':
                if ch == '\x1b':
                    mode = 'list'
                elif ch == '\n':
                    if input_field == 'time':
                        try:
                            r_min = int(buf) if buf else 5
                        except:
                            r_min = 5
                        r_min = (now + r_min) % 1440
                        input_field = 'text'
                        buf = ''
                    else:
                        r_text = buf if buf else 'Reminder'
                        reminders.append((r_min, r_text))
                        reminders.sort(key=lambda x: x[0])
                        mode = 'list'
                        buf = ''
                elif ch == '\b' or ch == '\x7f':
                    buf = buf[:-1]
                elif len(ch) == 1 and ord(ch) >= 32 and ord(ch) <= 126:
                    buf += ch
            _header()
            if mode == 'list':
                _draw_list()
            else:
                _draw_input()

    return ('game', _remind_loop)


def cmd_contacts(args, tft=None):
    def _contacts_loop(tft, read_key):
        import time
        from commands.dispatch import THEME_COLORS
        CONTACTS_FILE = '/sd/contacts.txt'
        contacts = []
        sel = 0
        mode = 'list'
        buf = ''
        input_field = 'name'
        c_name = ''
        c_phone = ''
        c_email = ''

        def _load():
            nonlocal contacts
            try:
                with open(CONTACTS_FILE, 'r') as f:
                    contacts = []
                    for line in f.readlines():
                        parts = line.strip().split('|')
                        if len(parts) >= 3:
                            contacts.append((parts[0], parts[1], parts[2]))
            except:
                contacts = []

        def _save():
            try:
                with open(CONTACTS_FILE, 'w') as f:
                    for name, phone, email in contacts:
                        f.write(f'{name}|{phone}|{email}\n')
            except:
                pass

        def _header():
            try:
                from commands.dispatch import THEME_COLORS as tc
            except:
                tc = None
            c = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.text15('Contacts', 190, 4, c, bg)
            tft.hline(0, 24, 480, c)

        def _draw_list():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            tft.text15(f'{len(contacts)} contacts', 4, 32, 0x8410, 0x0000)
            y = 50
            for i, (name, phone, email) in enumerate(contacts):
                marker = '> ' if i == sel else '  '
                color = 0x07E0 if i == sel else 0xFFFF
                tft.text15(f'{marker}{name}', 4, y, color, 0x0000)
                if phone:
                    tft.text15(f'  {phone}', 4, y + 14, 0x8410, 0x0000)
                y += 30
            if not contacts:
                tft.text15('  (no contacts)', 4, 50, 0x8410, 0x0000)
            tft.text('N=new D=delete Q=quit', 4, 308, 0x8410, 0x0000)

        def _draw_input():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            labels = {'name': 'Name:', 'phone': 'Phone:', 'email': 'Email:'}
            tft.text15(f'{labels[input_field]}', 4, 32, 0xFFFF, 0x0000)
            tft.text15(f'{buf}_', 4, 52, 0x07E0, 0x0000)
            tft.text('Enter to confirm, Esc to cancel', 4, 308, 0x8410, 0x0000)

        _load()
        _header()
        _draw_list()

        while True:
            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q':
                _save()
                return
            if mode == 'list':
                if ch == 'n':
                    mode = 'input'
                    input_field = 'name'
                    buf = ''
                    c_name = ''
                    c_phone = ''
                    c_email = ''
                elif ch == 'd' and contacts:
                    contacts.pop(sel)
                    sel = min(sel, max(0, len(contacts) - 1))
                    _save()
                elif ch == '\x80':
                    sel = max(0, sel - 1)
                elif ch == '\x81':
                    sel = min(len(contacts) - 1, sel + 1)
            elif mode == 'input':
                if ch == '\x1b':
                    mode = 'list'
                elif ch == '\n':
                    if input_field == 'name':
                        c_name = buf if buf else 'Unnamed'
                        input_field = 'phone'
                        buf = ''
                    elif input_field == 'phone':
                        c_phone = buf
                        input_field = 'email'
                        buf = ''
                    else:
                        c_email = buf
                        contacts.append((c_name, c_phone, c_email))
                        contacts.sort(key=lambda x: x[0].lower())
                        _save()
                        mode = 'list'
                        buf = ''
                elif ch == '\b' or ch == '\x7f':
                    buf = buf[:-1]
                elif len(ch) == 1 and ord(ch) >= 32 and ord(ch) <= 126:
                    buf += ch
            _header()
            if mode == 'list':
                _draw_list()
            else:
                _draw_input()

    return ('game', _contacts_loop)


def cmd_hexdump(args):
    filename = args.strip()
    if not filename:
        return ('print', 'hexdump: usage: hexdump [file]')
    try:
        with open(filename, 'rb') as f:
            data = f.read(256)
        lines = [f'=== hexdump: {filename} ({len(data)} bytes) ===']
        for i in range(0, len(data), 16):
            chunk = data[i:i + 16]
            hex_str = ' '.join(f'{b:02X}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f'  {i:04X}  {hex_str:<48s} {ascii_str}')
        if len(data) >= 256:
            lines.append(f'  ... ({len(data)} bytes shown)')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'hexdump: {e}')


def cmd_timer(args, tft=None):
    def _timer_loop(tft, read_key):
        import time
        from lib.buzzer import Buzzer
        from commands.dispatch import THEME_COLORS
        buzzer = Buzzer(20)
        mode = 'menu'
        timer_running = False
        timer_end = 0
        timer_type = ''
        timer_label = ''
        timer_secs = 0
        pomodoro_work = 25
        pomodoro_break = 5
        pomodoro_rounds = 4
        pomodoro_current = 0
        pomodoro_is_break = False

        def _header():
            try:
                from commands.dispatch import THEME_COLORS as tc
            except:
                tc = None
            c = tc.get('accent', 0x07FF) if tc else 0x07FF
            bg = tc.get('header', 0x1082) if tc else 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.text15('Timer', 200, 4, c, bg)
            tft.hline(0, 24, 480, c)

        def _draw_menu():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            tft.text15('Timer Mode:', 4, 32, 0xFFFF, 0x0000)
            tft.text15('  1 - Countdown', 4, 60, 0x07E0, 0x0000)
            tft.text15('  2 - Pomodoro', 4, 80, 0xFFE0, 0x0000)
            tft.text15('  3 - Stopwatch', 4, 100, 0x07FF, 0x0000)
            tft.text('Q=quit', 4, 308, 0x8410, 0x0000)

        def _draw_countdown():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            remaining = max(0, timer_end - time.time())
            mins = int(remaining) // 60
            secs = int(remaining) % 60
            tft.text15(timer_label, 4, 32, 0xFFFF, 0x0000)
            tft.text15(f'{mins:02d}:{secs:02d}', 140, 80, 0x07E0, 0x0000)
            pct = int(remaining * 100 / timer_secs) if timer_secs > 0 else 0
            bar_w = int(400 * pct / 100)
            tft.rect(40, 140, 400, 20, 0x4208)
            tft.fill_rect(40, 140, bar_w, 20, 0x07E0)
            tft.text15(f'{pct}%', 220, 165, 0xFFFF, 0x0000)

        def _draw_pomodoro():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            phase = 'BREAK' if pomodoro_is_break else 'WORK'
            tft.text15(f'Pomodoro - {phase}', 4, 32, 0xFFFF, 0x0000)
            tft.text15(f'Round {pomodoro_current + 1}/{pomodoro_rounds}', 4, 52, 0x8410, 0x0000)
            remaining = max(0, timer_end - time.time())
            mins = int(remaining) // 60
            secs = int(remaining) % 60
            tft.text15(f'{mins:02d}:{secs:02d}', 140, 80, 0x07E0 if not pomodoro_is_break else 0x07FF, 0x0000)
            for i in range(pomodoro_rounds):
                x = 100 + i * 70
                color = 0x07E0 if i < pomodoro_current else (0x07FF if i == pomodoro_current and not pomodoro_is_break else 0x4208)
                tft.fill_rect(x, 130, 50, 20, color)

        def _draw_stopwatch():
            tft.fill_rect(0, 25, 480, 271, 0x0000)
            elapsed = time.time() - timer_end
            mins = int(elapsed) // 60
            secs = int(elapsed) % 60
            cs = int((elapsed * 100) % 100)
            tft.text15('Stopwatch', 4, 32, 0xFFFF, 0x0000)
            tft.text15(f'{mins:02d}:{secs:02d}.{cs:02d}', 100, 80, 0x07FF, 0x0000)

        _header()
        _draw_menu()

        while True:
            if timer_running:
                if timer_type == 'countdown' or timer_type == 'pomodoro':
                    if time.time() >= timer_end:
                        buzzer.alarm()
                        if timer_type == 'pomodoro':
                            pomodoro_current += 1
                            if pomodoro_current >= pomodoro_rounds:
                                timer_running = False
                                timer_type = ''
                            else:
                                pomodoro_is_break = not pomodoro_is_break
                                dur = pomodoro_break * 60 if pomodoro_is_break else pomodoro_work * 60
                                timer_end = time.time() + dur
                                timer_secs = dur
                if timer_type == 'countdown':
                    _draw_countdown()
                elif timer_type == 'pomodoro':
                    _draw_pomodoro()
                elif timer_type == 'stopwatch':
                    _draw_stopwatch()

            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q':
                buzzer.off()
                return
            if mode == 'menu':
                if ch == '1':
                    timer_type = 'countdown'
                    timer_label = 'Countdown'
                    timer_secs = 600
                    timer_end = time.time() + timer_secs
                    timer_running = True
                    mode = 'running'
                elif ch == '2':
                    timer_type = 'pomodoro'
                    pomodoro_current = 0
                    pomodoro_is_break = False
                    timer_secs = pomodoro_work * 60
                    timer_end = time.time() + timer_secs
                    timer_running = True
                    mode = 'running'
                elif ch == '3':
                    timer_type = 'stopwatch'
                    timer_end = time.time()
                    timer_running = True
                    mode = 'running'
            elif mode == 'running':
                if ch == ' ':
                    timer_running = not timer_running
                    if timer_running and timer_type == 'stopwatch':
                        timer_end = time.time() - (timer_secs if hasattr(timer_secs, '__float__') else 0)
                elif ch == '\x84':
                    if timer_type == 'countdown':
                        timer_secs = min(3600, timer_secs + 60)
                        timer_end = time.time() + timer_secs
                elif ch == '\x85':
                    if timer_type == 'countdown':
                        timer_secs = max(60, timer_secs - 60)
                        timer_end = time.time() + timer_secs

    return ('game', _timer_loop)
