import time
import random
import gc
import os

_boot_time = time.ticks_ms()


def cmd_todo(args, tft=None):
    parts = args.strip().split(None, 1) if args.strip() else []
    todo_file = 'todo.txt'

    if not parts:
        def _todo_loop(tft, read_key):
            import time
            from commands.dispatch import THEME_COLORS
            scroll = 0
            confirm_delete = -1

            if THEME_COLORS:
                _bg = THEME_COLORS['bg']
                _fg = THEME_COLORS['white']
                _accent = THEME_COLORS['accent']
                _green = THEME_COLORS['green']
                _yellow = THEME_COLORS['yellow']
                _red = THEME_COLORS['red']
                _header = THEME_COLORS['header']
            else:
                _bg = 0x0000
                _fg = 0xFFFF
                _accent = 0x07FF
                _green = 0x07E0
                _yellow = 0xFFE0
                _red = 0xF800
                _header = 0x1082

            def _load():
                try:
                    with open(todo_file, 'r') as f:
                        return [l.rstrip('\n') for l in f.readlines() if l.strip()]
                except OSError:
                    return []

            def _save(tasks):
                with open(todo_file, 'w') as f:
                    f.write('\n'.join(tasks) + '\n')

            def _render(tasks, sel, scroll):
                tft.fill(_bg)
                tft.text15('=== TODO LIST ===', 4, 2, _accent, _bg)
                visible = 14
                total = len(tasks)
                max_scroll = max(0, total - visible)
                if scroll > max_scroll:
                    scroll = max_scroll
                for i in range(visible):
                    idx = i + scroll
                    y = 20 + i * 16
                    if idx >= total:
                        break
                    t = tasks[idx]
                    if t.startswith('[x]'):
                        sym = chr(0x97) + ' '
                        color = _green
                        text = t[4:]
                    else:
                        sym = chr(0x96) + ' '
                        color = _fg
                        text = t[4:]
                    if idx == sel:
                        tft.fill_rect(0, y, 480, 16, _accent)
                        color = _fg
                    tft.text15(sym + text[:42], 4, y, color, _bg if idx != sel else _accent)
                if total == 0:
                    tft.text15('  No tasks! Press A to add.', 4, 36, _green, _bg)
                help_y = 306
                tft.text15('A:Add  SPC:Toggle  D:Del  C:Clear  ESC:Exit', 4, help_y, _accent, _bg)
                tft.text15(f'{sel + 1}/{total}', 440, help_y, _green, _bg)

            tasks = _load()
            sel = 0
            scroll = 0
            adding = False
            add_buf = ''

            _render(tasks, sel, scroll)

            while True:
                ch = read_key()

                if adding:
                    if ch == '\x1b':
                        adding = False
                        add_buf = ''
                    elif ch == '\n':
                        if add_buf.strip():
                            tasks.append('[ ] ' + add_buf.strip())
                            _save(tasks)
                            sel = len(tasks) - 1
                        adding = False
                        add_buf = ''
                    elif ch == '\b':
                        add_buf = add_buf[:-1] if add_buf else ''
                    elif len(ch) == 1 and 32 <= ord(ch) <= 126:
                        add_buf += ch
                    if adding:
                        tft.fill_rect(0, 306, 480, 16, _bg)
                        tft.text15('> ' + add_buf[:44], 4, 306, _yellow, _bg)
                    else:
                        _render(tasks, sel, scroll)
                    continue

                if ch == '\x1b':
                    _save(tasks)
                    tft.fill(_bg)
                    tft.text15('Saved! Exiting todo...', 4, 150, _green, _bg)
                    time.sleep_ms(300)
                    return

                if ch == ' ' or ch == '\n':
                    if tasks:
                        idx = sel
                        t = tasks[idx]
                        if t.startswith('[ ]'):
                            tasks[idx] = '[x]' + t[3:]
                        else:
                            tasks[idx] = '[ ]' + t[3:]
                        _save(tasks)
                        _render(tasks, sel, scroll)

                elif ch == 'a' or ch == 'A':
                    adding = True
                    add_buf = ''

                elif ch == 'd' or ch == 'D':
                    if tasks and confirm_delete == sel:
                        tasks.pop(sel)
                        _save(tasks)
                        confirm_delete = -1
                        if sel >= len(tasks):
                            sel = max(0, len(tasks) - 1)
                        _render(tasks, sel, scroll)
                    elif tasks:
                        confirm_delete = sel
                        _render(tasks, sel, scroll)
                        tft.fill_rect(0, 306, 480, 16, _bg)
                        tft.text15('Press D again to confirm delete', 4, 306, _red, _bg)
                    else:
                        confirm_delete = -1

                elif ch == 'c' or ch == 'C':
                    tasks = [t for t in tasks if t.startswith('[ ]')]
                    _save(tasks)
                    sel = min(sel, max(0, len(tasks) - 1))
                    confirm_delete = -1
                    _render(tasks, sel, scroll)

                elif ch == '\x80':
                    if sel > 0:
                        sel -= 1
                        if sel < scroll:
                            scroll = sel
                    confirm_delete = -1
                    _render(tasks, sel, scroll)

                elif ch == '\x81':
                    if sel < len(tasks) - 1:
                        sel += 1
                        if sel >= scroll + 14:
                            scroll = sel - 13
                    confirm_delete = -1
                    _render(tasks, sel, scroll)

                else:
                    confirm_delete = -1

        return ('game', _todo_loop)

    action = parts[0].lower()

    try:
        with open(todo_file, 'r') as f:
            tasks = [l.rstrip('\n') for l in f.readlines() if l.strip()]
    except OSError:
        tasks = []

    if action == 'add':
        if len(parts) < 2:
            return ('print', 'todo: what do you want to add?')
        tasks.append('[ ] ' + parts[1])
        with open(todo_file, 'w') as f:
            f.write('\n'.join(tasks) + '\n')
        return ('print', f'  Added: {parts[1]}')

    elif action == 'list':
        if not tasks:
            return ('print', '  No tasks!')
        lines = ['=== TODO List ===']
        for i, t in enumerate(tasks):
            lines.append(f'  {i + 1}. {t}')
        return ('print_lines', lines)

    elif action == 'done':
        if len(parts) < 2:
            return ('print', 'todo: which task?')
        search = parts[1].lower()
        matches = [(i, t) for i, t in enumerate(tasks) if search in t.lower()]
        if not matches:
            return ('print', f'todo: no task matching "{parts[1]}"')
        if len(matches) > 1:
            lines = ['Multiple matches:']
            for i, t in matches:
                lines.append(f'  {i + 1}. {t}')
            return ('print_lines', lines)
        idx, task = matches[0]
        if task.startswith('[ ]'):
            tasks[idx] = '[x]' + task[3:]
        else:
            tasks[idx] = '[ ]' + task[3:]
        with open(todo_file, 'w') as f:
            f.write('\n'.join(tasks) + '\n')
        return ('print', f'  {tasks[idx]}')

    elif action == 'rm':
        if len(parts) < 2:
            return ('print', 'todo: which task?')
        search = parts[1].lower()
        matches = [(i, t) for i, t in enumerate(tasks) if search in t.lower()]
        if not matches:
            return ('print', f'todo: no task matching "{parts[1]}"')
        if len(matches) > 1:
            lines = ['Multiple matches:']
            for i, t in matches:
                lines.append(f'  {i + 1}. {t}')
            return ('print_lines', lines)
        idx, task = matches[0]
        removed = tasks.pop(idx)
        with open(todo_file, 'w') as f:
            f.write('\n'.join(tasks) + '\n')
        return ('print', f'  Removed: {removed[4:]}')

    elif action == 'clear':
        tasks = [t for t in tasks if t.startswith('[ ]')]
        with open(todo_file, 'w') as f:
            f.write('\n'.join(tasks) + '\n')
        return ('print', f'  Cleared done tasks. {len(tasks)} remaining.')

    return ('print', f'todo: unknown action "{action}"')


def cmd_notes(args):
    parts = args.strip().split(None, 1) if args.strip() else []
    notes_dir = '/.data/notes'

    if not parts:
        return ('print_lines', [
            'notes: usage:',
            '  notes list           List all notes',
            '  notes new [name]     Create note (opens nano)',
            '  notes read [name]    Read a note',
            '  notes rm [name]      Delete a note',
            '  todo add [task]     Add a task',
            '  todo list           List all tasks',
            '  todo done [num]     Mark task done',
            '  todo rm [num]       Remove a task',
            '  todo clear          Clear completed tasks',
        ])

    action = parts[0].lower()

    try:
        os.stat(notes_dir)
    except OSError:
        try:
            os.mkdir(notes_dir)
        except:
            pass

    if action == 'list':
        try:
            files = os.listdir(notes_dir)
            if not files:
                return ('print', '  No notes yet!')
            lines = ['=== Notes ===']
            for f in sorted(files):
                lines.append(f'  {f}')
            return ('print_lines', lines)
        except:
            return ('print', '  Error reading notes')

    elif action == 'new':
        if len(parts) < 2:
            return ('print', 'notes: what name?')
        name = parts[1]
        if not name.endswith('.txt'):
            name += '.txt'
        path = notes_dir + '/' + name
        return ('edit', path, '')

    elif action == 'read':
        if len(parts) < 2:
            return ('print', 'notes: which note?')
        name = parts[1]
        if not name.endswith('.txt'):
            name += '.txt'
        path = notes_dir + '/' + name
        try:
            with open(path, 'r') as f:
                content = f.read()
            lines = content.split('\n')
            return ('print_lines', [f'=== {name} ({len(lines)} lines) ==='] + lines[:25])
        except OSError:
            return ('print', f'  Note "{name}" not found')

    elif action == 'rm':
        if len(parts) < 2:
            return ('print', 'notes: which note?')
        name = parts[1]
        if not name.endswith('.txt'):
            name += '.txt'
        path = notes_dir + '/' + name
        try:
            os.remove(path)
            return ('print', f'  Deleted: {name}')
        except OSError:
            return ('print', f'  Note "{name}" not found')

    return ('print', f'notes: unknown action "{action}"')


def cmd_convert(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 3:
        return ('print_lines', [
            'convert: usage: convert [value] [from] [to]',
            '',
            '  Temperature: c, f, k',
            '  Length: km, mi, m, ft, in, cm',
            '  Weight: kg, lb, oz, g',
            '  Volume: l, gal, ml',
            '',
            '  Example: convert 100 km mi',
            '  Example: convert 30 c f',
        ])

    try:
        val = float(parts[0])
    except ValueError:
        return ('print', 'convert: invalid number')

    src = parts[1].lower()
    dst = parts[2].lower()

    conversions = {
        ('c', 'f'): lambda v: v * 9 / 5 + 32,
        ('f', 'c'): lambda v: (v - 32) * 5 / 9,
        ('c', 'k'): lambda v: v + 273.15,
        ('k', 'c'): lambda v: v - 273.15,
        ('f', 'k'): lambda v: (v - 32) * 5 / 9 + 273.15,
        ('k', 'f'): lambda v: (v - 273.15) * 9 / 5 + 32,
        ('km', 'mi'): lambda v: v * 0.621371,
        ('mi', 'km'): lambda v: v * 1.60934,
        ('m', 'ft'): lambda v: v * 3.28084,
        ('ft', 'm'): lambda v: v * 0.3048,
        ('in', 'cm'): lambda v: v * 2.54,
        ('cm', 'in'): lambda v: v * 0.393701,
        ('kg', 'lb'): lambda v: v * 2.20462,
        ('lb', 'kg'): lambda v: v * 0.453592,
        ('oz', 'g'): lambda v: v * 28.3495,
        ('g', 'oz'): lambda v: v * 0.035274,
        ('l', 'gal'): lambda v: v * 0.264172,
        ('gal', 'l'): lambda v: v * 3.78541,
        ('l', 'ml'): lambda v: v * 1000,
        ('ml', 'l'): lambda v: v / 1000,
    }

    key = (src, dst)
    if key in conversions:
        result = conversions[key](val)
        return ('print', f'  {val} {src} = {result:.4g} {dst}')
    return ('print', f'convert: cannot convert {src} to {dst}')


def cmd_base(args):
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            'base: usage:',
            '  base [number]       Show in all bases',
            '  base [number] [to]  Convert to base',
            '',
            '  Bases: bin, oct, dec, hex',
        ])

    num_str = parts[0]

    try:
        if num_str.startswith('0x') or num_str.startswith('0X'):
            n = int(num_str, 16)
        elif num_str.startswith('0b') or num_str.startswith('0B'):
            n = int(num_str, 2)
        elif num_str.startswith('0o') or num_str.startswith('0O'):
            n = int(num_str, 8)
        else:
            n = int(num_str)
    except ValueError:
        return ('print', 'base: invalid number')

    if len(parts) > 1:
        target = parts[1].lower()
        if target == 'bin':
            return ('print', f'  {bin(n)}')
        elif target == 'oct':
            return ('print', f'  {oct(n)}')
        elif target == 'dec':
            return ('print', f'  {n}')
        elif target == 'hex':
            return ('print', f'  {hex(n)}')
        return ('print', f'base: unknown base "{target}"')

    return ('print_lines', [
        f'=== {n} ===',
        f'  BIN: {bin(n)}',
        f'  OCT: {oct(n)}',
        f'  DEC: {n}',
        f'  HEX: {hex(n)}',
    ])


def cmd_passwd(args):
    parts = args.strip().split() if args.strip() else []
    length = 16
    if parts:
        try:
            length = int(parts[0])
            length = max(4, min(64, length))
        except ValueError:
            pass

    charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    pw = ''.join(random.choice(charset) for _ in range(length))
    return ('print', f'  {pw}')


def cmd_weather(args):
    try:
        from commands.apicmd import _https_get
        import ujson
        city = args.strip() if args.strip() else 'Amsterdam'
        path = '/{}?format=j1'.format(city.replace(' ', '+'))
        body = _https_get('wttr.in', path, timeout=10)
        j = ujson.loads(body)
        current = j.get('current_condition', [{}])[0]
        temp = current.get('temp_C', '?')
        feels = current.get('FeelsLikeC', '?')
        desc = current.get('weatherDesc', [{}])[0].get('text', '?')
        humidity = current.get('humidity', '?')
        wind = current.get('windspeedKmph', '?')
        lines = [
            f'=== Weather: {city} ===',
            f'  Temp:     {temp}C (feels {feels}C)',
            f'  Condition: {desc}',
            f'  Humidity: {humidity}%',
            f'  Wind:     {wind} km/h',
        ]
        forecast = j.get('weather', [])
        if forecast:
            lines.append('')
            lines.append('  --- Forecast ---')
            for day in forecast[:3]:
                date = day.get('date', '?')
                hi = day.get('maxtempC', '?')
                lo = day.get('mintempC', '?')
                avg = day.get('hourly', [{}])
                desc_day = avg[4].get('weatherDesc', [{}])[0].get('text', '?') if len(avg) > 4 else '?'
                lines.append(f'  {date}: {hi}/{lo}C  {desc_day}')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'weather: {e}')


def cmd_freq(args):
    from machine import freq
    parts = args.strip().split() if args.strip() else []
    current = freq()
    if not parts:
        return ('print_lines', [
            f'  Current: {current // 1000000}MHz',
            '',
            '  freq [mhz]  Set CPU frequency',
            '  Valid: 20, 40, 80, 160, 240',
        ])
    try:
        target = int(parts[0]) * 1000000
        valid = [20000000, 40000000, 80000000, 160000000, 240000000]
        if target not in valid:
            return ('print', f'freq: must be one of:\n  {", ".join(str(v // 1000000) for v in valid)}')
        freq(target)
        return ('print', f'  CPU: {current // 1000000}MHz -> {target // 1000000}MHz')
    except ValueError:
        return ('print', 'freq: invalid number')


def cmd_mem(args):
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    pct = int(alloc * 100 / total) if total > 0 else 0
    lines = [
        '=== Memory ===',
        f'  Total:     {total} bytes ({total // 1024}KB)',
        f'  Allocated: {alloc} bytes ({alloc // 1024}KB)',
        f'  Free:      {free} bytes ({free // 1024}KB)',
        f'  Usage:     {pct}%',
    ]
    return ('print_lines', lines)


def cmd_uptime(args):
    elapsed = time.ticks_diff(time.ticks_ms(), _boot_time)
    secs = elapsed // 1000
    mins = secs // 60
    hours = mins // 60
    days = hours // 24
    return ('print_lines', [
        '=== Uptime ===',
        f'  {days}d {hours % 24}h {mins % 60}m {secs % 60}s',
    ])


def cmd_ping(args):
    host = args.strip()
    if not host:
        return ('print', 'ping: usage: ping [host]')
    try:
        import usocket
        import ssl
        sock = usocket.socket()
        sock.settimeout(5)
        start = time.ticks_ms()
        addr = usocket.getaddrinfo(host, 443)[0][-1]
        ssock = ssl.wrap_socket(sock, server_hostname=host)
        ssock.connect(addr)
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        ssock.close()
        return ('print', f'  {host}: {elapsed}ms')
    except Exception as e:
        try:
            import usocket
            sock = usocket.socket()
            sock.settimeout(5)
            start = time.ticks_ms()
            addr = usocket.getaddrinfo(host, 80)[0][-1]
            sock.connect(addr)
            elapsed = time.ticks_diff(time.ticks_ms(), start)
            sock.close()
            return ('print', f'  {host}: {elapsed}ms')
        except Exception as e2:
            return ('print', f'ping: {e2}')


def cmd_color(args):
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            'color: usage:',
            '  color [hex]           hex to RGB',
            '  color [r] [g] [b]    RGB to hex',
            '',
            '  Example: color 0xFF5733',
            '  Example: color 255 87 51',
        ])

    if len(parts) == 1:
        try:
            hex_str = parts[0].replace('#', '').replace('0x', '')
            n = int(hex_str, 16)
            r = (n >> 16) & 0xFF
            g = (n >> 8) & 0xFF
            b = n & 0xFF
            return ('print_lines', [
                f'  Hex: 0x{hex_str.upper()}',
                f'  RGB: ({r}, {g}, {b})',
                f'  R565: 0x{(r >> 3) << 11 | (g >> 2) << 5 | b >> 3:04X}',
            ])
        except ValueError:
            return ('print', 'color: invalid hex value')

    elif len(parts) == 3:
        try:
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            hex_val = (r << 16) | (g << 8) | b
            r565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            return ('print_lines', [
                f'  Hex: 0x{hex_val:06X}',
                f'  RGB: ({r}, {g}, {b})',
                f'  R565: 0x{r565:04X}',
            ])
        except ValueError:
            return ('print', 'color: invalid RGB values')

    return ('print', 'color: provide hex or R G B')


def cmd_uuid(args):
    u = '{:08x}-{:04x}-{:04x}-{:04x}-{:012x}'.format(
        random.getrandbits(32),
        random.getrandbits(16),
        random.getrandbits(16),
        random.getrandbits(16),
        random.getrandbits(48)
    )
    return ('print', f'  {u}')


_cmd_history = []


def cmd_history(args):
    if not _cmd_history:
        return ('print', '  No history yet')
    lines = ['=== Command History ===']
    for i, cmd in enumerate(_cmd_history[-20:]):
        lines.append(f'  {len(_cmd_history) - 20 + i + 1 if len(_cmd_history) > 20 else i + 1}  {cmd}')
    return ('print_lines', lines)


def cmd_grep(args):
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 2:
        return ('print', 'grep: usage: grep [pattern] [file]')
    pattern = parts[0]
    filename = parts[1]
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        matches = []
        for i, line in enumerate(lines):
            if pattern in line:
                matches.append(f'  {i + 1}: {line.rstrip()[:50]}')
        if not matches:
            return ('print', f'  No matches for "{pattern}"')
        return ('print_lines', [f'=== {len(matches)} matches ==='] + matches[:20])
    except OSError:
        return ('print', f'grep: {filename} not found')


def cmd_head(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 1:
        return ('print', 'head: usage: head [file] [lines]')
    filename = parts[0]
    n = 10
    if len(parts) > 1:
        try:
            n = int(parts[1])
        except:
            pass
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        return ('print_lines', [l.rstrip()[:50] for l in lines[:n]])
    except OSError:
        return ('print', f'head: {filename} not found')


def cmd_tail(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 1:
        return ('print', 'tail: usage: tail [file] [lines]')
    filename = parts[0]
    n = 10
    if len(parts) > 1:
        try:
            n = int(parts[1])
        except:
            pass
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        return ('print_lines', [l.rstrip()[:50] for l in lines[-n:]])
    except OSError:
        return ('print', f'tail: {filename} not found')


def cmd_wc(args):
    filename = args.strip()
    if not filename:
        return ('print', 'wc: usage: wc [file]')
    try:
        with open(filename, 'r') as f:
            content = f.read()
        lines = content.count('\n')
        words = len(content.split())
        chars = len(content)
        return ('print', f'  {lines} lines  {words} words  {chars} chars')
    except OSError:
        return ('print', f'wc: {filename} not found')


def cmd_diff(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 2:
        return ('print', 'diff: usage: diff [file1] [file2]')
    try:
        with open(parts[0], 'r') as f:
            lines1 = f.readlines()
        with open(parts[1], 'r') as f:
            lines2 = f.readlines()
        diffs = []
        max_lines = max(len(lines1), len(lines2))
        for i in range(max_lines):
            l1 = lines1[i].rstrip() if i < len(lines1) else '<EOF>'
            l2 = lines2[i].rstrip() if i < len(lines2) else '<EOF>'
            if l1 != l2:
                diffs.append(f'  L{i + 1}: - {l1[:40]}')
                diffs.append(f'  L{i + 1}: + {l2[:40]}')
        if not diffs:
            return ('print', '  Files are identical')
        return ('print_lines', [f'=== {len(diffs) // 2} differences ==='] + diffs[:20])
    except OSError as e:
        return ('print', f'diff: {e}')


def cmd_quote(args):
    quotes = [
        'The best way to predict the future is to create it.',
        'Code is like humor. When you have to explain it, it is bad.',
        'First, solve the problem. Then, write the code.',
        'Simplicity is the soul of efficiency.',
        'Talk is cheap. Show me the code. - Linus Torvalds',
        'Any fool can write code that a computer can understand.',
        'Programs must be written for people to read.',
        'The only way to learn a new programming language is by writing programs.',
        'Debugging is twice as hard as writing the code.',
        'Make it work, make it right, make it fast.',
        'Weeks of coding can save you hours of planning.',
        'Code never lies, comments sometimes do.',
        'Optimism is an occupational hazard of programming.',
        'Programming is not about typing, it is about thinking.',
        'The computer was born to solve problems that did not exist before.',
    ]
    return ('print', f'  "{random.choice(quotes)}"')


def cmd_joke(args):
    jokes = [
        ('Why do programmers prefer dark mode?', 'Because light attracts bugs!'),
        ('Why do Java developers wear glasses?', 'Because they cannot C#!'),
        ('What is a programmer favorite hangout place?', 'Foo Bar!'),
        ('Why do programmers hate nature?', 'It has too many bugs!'),
        ('How many programmers does it take to change a light bulb?', 'None, that is a hardware problem!'),
        ('Why did the programmer quit?', 'Because they did not get arrays!'),
        ('What is a programmer fav opening?', 'IE... just kidding!'),
        ('Why do Python programmers have low self-esteem?', 'They are constantly comparing themselves to others!'),
        ('What do you call a group of 8 hobbits?', 'A hobbyte!'),
        ('Why was the JavaScript developer sad?', 'Because he did not Node how to Express himself!'),
        ('A SQL query walks into a bar, sees two tables...', 'and asks: Can I join you?'),
        ('Why do hackers prefer the gym?', 'Because they love breaking firewalls!'),
    ]
    q, a = random.choice(jokes)
    return ('print_lines', [f'  Q: {q}', f'  A: {a}'])


def cmd_cowsay(args):
    text = args.strip() if args.strip() else 'Moo!'
    max_w = 30
    words = text.split()
    lines = []
    line = ''
    for w in words:
        if len(line) + len(w) + 1 > max_w:
            lines.append(line)
            line = w
        else:
            line = line + ' ' + w if line else w
    if line:
        lines.append(line)
    width = max(len(l) for l in lines) if lines else len(text)
    border = '-' * (width + 2)
    result = [f' {border}']
    for l in lines:
        result.append(f'| {l:<{width}} |')
    result.append(f' {border}')
    result.append('        \\   ^__^')
    result.append('         \\  (oo)\\_______')
    result.append('            (__)\\       )\\/\\')
    result.append('                ||----w |')
    result.append('                ||     ||')
    return ('print_lines', result)


def cmd_df(args):
    try:
        st = os.statvfs('/')
        total = st[0] * st[2]
        free = st[0] * st[3]
        used = total - free
        pct = int(used * 100 / total) if total > 0 else 0
        return ('print_lines', [
            '=== Disk Space ===',
            f'  Total:  {total // 1024}KB',
            f'  Used:   {used // 1024}KB ({pct}%)',
            f'  Free:   {free // 1024}KB',
        ])
    except:
        return ('print', 'df: error reading disk')


def cmd_find(args):
    pattern = args.strip() if args.strip() else '*'
    try:
        entries = os.listdir('.')
        matches = []
        for e in entries:
            if pattern == '*' or pattern in e:
                matches.append(f'  {e}')
        if not matches:
            return ('print', f'  No matches for "{pattern}"')
        return ('print_lines', [f'=== Found {len(matches)} ==='] + matches[:20])
    except OSError as e:
        return ('print', f'find: {e}')


def cmd_dice(args):
    import random
    spec = args.strip() if args.strip() else '1d6'
    spec = spec.lower().replace(' ', '')
    if 'd' not in spec:
        return ('print', 'dice: usage: dice [NdN] (e.g. dice 2d6)')
    try:
        parts = spec.split('d')
        n = int(parts[0]) if parts[0] else 1
        faces = int(parts[1])
    except (ValueError, IndexError):
        return ('print', 'dice: usage: dice [NdN] (e.g. dice 2d6)')
    if n < 1 or n > 100 or faces < 1 or faces > 1000:
        return ('print', 'dice: N must be 1-100, faces 1-1000')
    rolls = [random.randint(1, faces) for _ in range(n)]
    total = sum(rolls)
    if n == 1:
        return ('print', f'  dice: {total}')
    details = ', '.join(str(r) for r in rolls)
    return ('print', f'  dice: {details}\n  Total: {total}')


def cmd_flip(args):
    import random
    result = random.choice(['Heads', 'Tails'])
    return ('print', f'  {result}')


def cmd_ip(args):
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            netmask = wlan.ifconfig()[1]
            gw = wlan.ifconfig()[2]
            dns = wlan.ifconfig()[3] if len(wlan.ifconfig()) > 3 else '?'
            ssid = wlan.config('essid')
            mac_hex = wlan.config('mac').hex(':')
            rssi = wlan.status('rssi')
            lines = [
                '=== Network Info ===',
                '  IP:       ' + str(ip),
                '  Netmask:  ' + str(netmask),
                '  Gateway:  ' + str(gw),
                '  DNS:      ' + str(dns),
                '  SSID:     ' + str(ssid),
                '  MAC:      ' + mac_hex,
                '  Signal:   ' + str(rssi) + ' dBm',
            ]
            return ('print_lines', lines)
        return ('print', 'ip: not connected (use wlan)')
    except:
        return ('print', 'ip: network not available')






def cmd_conv(args):
    """Unit conversion. Usage: conv <value> <from> <to>"""
    parts = args.strip().split()
    if len(parts) < 3:
        return ('print_lines', [
            '=== UNIT CONVERSION ===',
            '',
            '  Usage: conv <value> <from_unit> <to_unit>',
            '',
            '-- Examples --',
            '  conv 100 km mi     (kilometer to mile)',
            '  conv 72 F C        (Fahrenheit to Celsius)',
            '  conv 1 GB MB      (gigabyte to megabyte)',
            '  conv 5 kg lb      (kilogram to pound)',
        ])

    try:
        value = float(parts[0])
    except:
        return ('print', f'conv: bad value "{parts[0]}"')

    src = parts[1].lower()
    dst = parts[2].lower()

    # Conversion factors to base unit
    LENGTH = {'m':1, 'km':1000, 'cm':0.01, 'mm':0.001, 'mi':1609.344,
              'ft':0.3048, 'in':0.0254, 'yd':0.9144}
    WEIGHT = {'kg':1, 'g':0.001, 'mg':0.000001, 'lb':0.453592,
              'oz':0.0283495}
    DATA = {'B':1, 'KB':1024, 'MB':1048576, 'GB':1073741824, 'TB':1099511627776}
    TIME = {'s':1, 'min':60, 'h':3600, 'day':86400, 'ms':0.001}

    if src in LENGTH and dst in LENGTH:
        result = value * LENGTH[src] / LENGTH[dst]
        return ('print', f'  {value} {src} = {result:.4g} {dst}')
    if src in WEIGHT and dst in WEIGHT:
        result = value * WEIGHT[src] / WEIGHT[dst]
        return ('print', f'  {value} {src} = {result:.4g} {dst}')
    if src in DATA and dst in DATA:
        result = value * DATA[src] / DATA[dst]
        return ('print', f'  {value} {src} = {result:.4g} {dst}')
    if src in TIME and dst in TIME:
        result = value * TIME[src] / TIME[dst]
        return ('print', f'  {value} {src} = {result:.4g} {dst}')

    # Temperature special case
    if src == 'c' and dst == 'f':
        result = value * 9/5 + 32
        return ('print', f'  {value} C = {result:.2f} F')
    if src == 'f' and dst == 'c':
        result = (value - 32) * 5/9
        return ('print', f'  {value} F = {result:.2f} C')
    if src == 'c' and dst == 'k':
        return ('print', f'  {value} C = {value + 273.15:.2f} K')
    if src == 'k' and dst == 'c':
        return ('print', f'  {value} K = {value - 273.15:.2f} C')
    if src == 'f' and dst == 'k':
        return ('print', f'  {value} F = {(value - 32) * 5/9 + 273.15:.2f} K')
    if src == 'k' and dst == 'f':
        return ('print', f'  {value} K = {(value - 273.15) * 9/5 + 32:.2f} F')

    return ('print', f'  conv: unknown units "{src}" or "{dst}"')


def cmd_tree(args):
    """Directory tree view. Usage: tree [path]"""
    path = args.strip() if args.strip() else '.'
    try:
        entries = os.listdir(path)
    except:
        return ('print', f'tree: {path}: not found')
    lines = [f'  {path}/']
    
    def _walk(p, prefix, depth=0, max_depth=3):
        if depth >= max_depth:
            return
        try:
            items = os.listdir(p)
        except:
            return
        items.sort()
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = '└── ' if is_last else '├── '
            full = p.rstrip('/') + '/' + item
            try:
                st = os.stat(full)
                is_dir = (st[0] & 0x4000) != 0
            except:
                is_dir = False
            if is_dir:
                lines.append(f'{prefix}{connector}{item}/')
                next_prefix = prefix + ('    ' if is_last else '│   ')
                _walk(full, next_prefix, depth + 1, max_depth)
            else:
                lines.append(f'{prefix}{connector}{item}')
    
    _walk(path, '  ', 0, 3)
    return ('print_lines', lines[:30])


def cmd_du_top(args):
    """Show top N largest files. Usage: du --top [N] [path]"""
    parts = args.strip().split() if args.strip() else []
    top_n = 5
    path = '.'
    if '--top' in parts:
        idx = parts.index('--top')
        if idx + 1 < len(parts):
            try:
                top_n = int(parts[idx + 1])
            except:
                pass
        if idx + 2 < len(parts):
            path = parts[idx + 2]
    elif parts:
        path = parts[0]
    
    try:
        entries = os.listdir(path)
    except:
        return ('print', f'du: {path}: not found')
    
    files = []
    for e in entries:
        full = path.rstrip('/') + '/' + e
        try:
            st = os.stat(full)
            files.append((st[6], e))
        except:
            pass
    files.sort(reverse=True)
    
    lines = [f'=== Top {min(top_n, len(files))} in {path}/ ===']
    for size, name in files[:top_n]:
        if size > 1024 * 1024:
            sz = f'{size // (1024*1024)}MB'
        elif size > 1024:
            sz = f'{size // 1024}KB'
        else:
            sz = f'{size}B'
        lines.append(f'  {sz:>8}  {name}')
    return ('print_lines', lines)


def cmd_du(args):
    path = args.strip() if args.strip() else '.'
    try:
        entries = os.listdir(path)
    except:
        return ('print', f'du: {path}: not found')
    total = 0
    file_count = 0
    dir_count = 0
    largest_name = ''
    largest_size = 0
    for e in entries:
        full = path.rstrip('/') + '/' + e
        try:
            st = os.stat(full)
            size = st[6]
            total += size
            file_count += 1
            if size > largest_size:
                largest_size = size
                largest_name = e
        except:
            dir_count += 1
    lines = [
        f'=== {path} ===',
        f'  Files:    {file_count}',
        f'  Dirs:     {dir_count}',
        f'  Total:    {total} bytes ({total // 1024}KB)',
    ]
    if largest_name:
        lines.append(f'  Largest:  {largest_name} ({largest_size}B)')
    return ('print_lines', lines)


def cmd_base64(args):
    import ubinascii
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 2:
        return ('print_lines', [
            'base64: usage:',
            '  base64 enc [text]   Encode to base64',
            '  base64 dec [data]   Decode from base64',
        ])
    action = parts[0].lower()
    data = parts[1]
    if action == 'enc':
        encoded = ubinascii.b2a_base64(data.encode()).decode().strip()
        return ('print', f'  {encoded}')
    elif action == 'dec':
        try:
            decoded = ubinascii.a2b_base64(data).decode()
            return ('print', f'  {decoded}')
        except:
            return ('print', 'base64: invalid base64 data')
    return ('print', 'base64: use enc or dec')


def cmd_ascii(args, tft=None):
    text = args.strip().upper() if args.strip() else 'HI'
    if not tft:
        return ('print', 'ascii: display not available')
    FONT = {
        'A': ['  ##  ', ' #  # ', '######', '#    #', '#    #'],
        'B': ['##### ', '#    #', '##### ', '#    #', '##### '],
        'C': [' #####', '#     ', '#     ', '#     ', ' #####'],
        'D': ['##### ', '#    #', '#    #', '#    #', '##### '],
        'E': ['######', '#     ', '##### ', '#     ', '######'],
        'F': ['######', '#     ', '##### ', '#     ', '#     '],
        'G': [' #####', '#     ', '#  ###', '#    #', ' #####'],
        'H': ['#    #', '#    #', '######', '#    #', '#    #'],
        'I': ['######', '  ##  ', '  ##  ', '  ##  ', '######'],
        'J': ['######', '    # ', '    # ', '#   # ', ' ###  '],
        'K': ['#    #', '#   # ', '###   ', '#   # ', '#    #'],
        'L': ['#     ', '#     ', '#     ', '#     ', '######'],
        'M': ['#    #', '##  ##', '# ## #', '#    #', '#    #'],
        'N': ['#    #', '##   #', '# #  #', '#  # #', '#   ##'],
        'O': [' ###  ', '#   # ', '#   # ', '#   # ', ' ###  '],
        'P': ['##### ', '#    #', '##### ', '#     ', '#     '],
        'Q': [' ###  ', '#   # ', '# # # ', '#  #  ', ' ## # '],
        'R': ['##### ', '#    #', '##### ', '#   # ', '#    #'],
        'S': [' #####', '#     ', ' ###  ', '    # ', '##### '],
        'T': ['######', '  ##  ', '  ##  ', '  ##  ', '  ##  '],
        'U': ['#    #', '#    #', '#    #', '#    #', ' #### '],
        'V': ['#    #', '#    #', '#    #', ' #  # ', '  ##  '],
        'W': ['#    #', '#    #', '# ## #', '##  ##', '#    #'],
        'X': ['#    #', ' #  # ', '  ##  ', ' #  # ', '#    #'],
        'Y': ['#    #', ' #  # ', '  ##  ', '  ##  ', '  ##  '],
        'Z': ['######', '    # ', '  ##  ', ' #    ', '######'],
        '0': [' ###  ', '#   # ', '#   # ', '#   # ', ' ###  '],
        '1': ['  ##  ', ' ###  ', '  ##  ', '  ##  ', '######'],
        '2': [' ###  ', '#   # ', '  ##  ', ' #    ', '######'],
        '3': ['######', '    # ', ' ###  ', '    # ', '######'],
        '4': ['#    #', '#    #', '######', '    # ', '    # '],
        '5': ['######', '#     ', '##### ', '    # ', '##### '],
        '6': [' ###  ', '#     ', '##### ', '#    #', ' ###  '],
        '7': ['######', '    # ', '   #  ', '  #   ', '  #   '],
        '8': [' ###  ', '#   # ', ' ###  ', '#   # ', ' ###  '],
        '9': [' ###  ', '#   # ', ' #### ', '    # ', ' ###  '],
        ' ': ['      ', '      ', '      ', '      ', '      '],
        '.': ['      ', '      ', '      ', '      ', '  ##  '],
        '!': ['  ##  ', '  ##  ', '  ##  ', '      ', '  ##  '],
        '?': [' ###  ', '#   # ', '  ##  ', '      ', '  ##  '],
        '-': ['      ', '      ', '######', '      ', '      '],
        '+': ['      ', '  ##  ', '######', '  ##  ', '      '],
        '=': ['      ', '######', '      ', '######', '      '],
        ':': ['      ', '  ##  ', '      ', '  ##  ', '      '],
        '/': ['    # ', '   #  ', '  ##  ', ' #    ', '#     '],
        '(': ['   #  ', '  #   ', '  #   ', '  #   ', '   #  '],
        ')': ['  #   ', '   #  ', '   #  ', '   #  ', '  #   '],
    }
    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 24, 0x1082)
    tft.text15('ASCII Art', 4, 4, 0x07FF, 0x1082)
    tft.hline(0, 24, 480, 0x07FF)
    chars = text[:12]
    x = 4
    for ch in chars:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(5):
            for col in range(6):
                if glyph[row][col] == '#':
                    tft.fill_rect(x + col * 4, 34 + row * 16, 4, 14, 0xFFFF)
        x += 28
    return ('print', f'  rendered "{text}" on TFT')


def cmd_cp(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 2:
        return ('print', 'cp: usage: cp [source] [dest]')
    src, dst = parts[0], parts[1]
    try:
        with open(src, 'r') as f:
            data = f.read()
    except OSError:
        return ('print', f'cp: {src}: not found')
    try:
        with open(dst, 'w') as f:
            f.write(data)
    except OSError as e:
        return ('print', f'cp: {e}')
    return ('print', f'  {src} -> {dst}')


def cmd_mv(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 2:
        return ('print', 'mv: usage: mv [source] [dest]')
    src, dst = parts[0], parts[1]
    try:
        with open(src, 'r') as f:
            data = f.read()
    except OSError:
        return ('print', f'mv: {src}: not found')
    try:
        with open(dst, 'w') as f:
            f.write(data)
    except OSError as e:
        return ('print', f'mv: {e}')
    try:
        os.remove(src)
    except:
        pass
    return ('print', f'  {src} -> {dst}')


def cmd_search(args):
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 1:
        return ('print_lines', [
            'search: usage:',
            '  search [pattern] [dir]   Recursive grep',
            '',
            '  Searches all text files in dir',
            '  for lines containing pattern.',
            '  Default dir: current dir',
        ])
    pattern = parts[0]
    search_dir = parts[1] if len(parts) > 1 else '.'
    skip_dirs = {'.git', '__pycache__', '.DS_Store', 'node_modules'}
    results = []
    file_count = 0
    try:
        entries = os.listdir(search_dir)
    except OSError:
        return ('print', f'search: {search_dir}: not found')
    stack = [search_dir]
    while stack and len(results) < 30:
        current = stack.pop()
        try:
            items = os.listdir(current)
        except:
            continue
        for item in items:
            if item in skip_dirs:
                continue
            path = current.rstrip('/') + '/' + item
            try:
                st = os.stat(path)
                if st[0] & 0x4000:
                    stack.append(path)
                else:
                    if item.endswith(('.py', '.txt', '.md', '.json', '.cfg', '.csv', '.html', '.js', '.c', '.h')):
                        file_count += 1
                        try:
                            with open(path, 'r') as f:
                                for i, line in enumerate(f):
                                    if pattern in line:
                                        results.append(f'  {path}:{i + 1}: {line.rstrip()[:50]}')
                                        if len(results) >= 30:
                                            break
                        except:
                            pass
            except:
                pass
    if not results:
        return ('print', f'  No matches for "{pattern}"\n  in {file_count} files')
    return ('print_lines', [f'=== {len(results)} matches in {file_count} files ==='] + results)


def cmd_dns(args):
    host = args.strip()
    if not host:
        return ('print', 'dns: usage: dns [hostname]')
    try:
        import usocket
        addrs = usocket.getaddrinfo(host, 80)
        seen = set()
        lines = [f'=== DNS: {host} ===']
        for addr in addrs:
            ip = addr[-1][0]
            if ip not in seen:
                seen.add(ip)
                lines.append(f'  {ip}')
        if len(lines) == 1:
            lines.append('  (no addresses found)')
        return ('print_lines', lines)
    except Exception as e:
        return ('print', f'dns: {e}')


def cmd_curl(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 1:
        return ('print_lines', [
            'curl: usage:',
            '  curl [host] [path]        HTTP GET (HTTPS)',
            '  curl http://host/path     HTTP GET (plain)',
            '',
            '  Example: curl example.com',
            '  Example: curl http://example.com/api',
        ])
    url = parts[0]
    if url.startswith('http://'):
        import usocket
        host_path = url[7:]
        slash = host_path.find('/')
        if slash >= 0:
            host = host_path[:slash]
            path = host_path[slash:]
        else:
            host = host_path
            path = '/'
        try:
            sock = usocket.socket()
            sock.settimeout(10)
            addr = usocket.getaddrinfo(host, 80)[0][-1]
            sock.connect(addr)
            sock.sendall(f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
            data = b''
            while True:
                chunk = sock.read(1024)
                if not chunk:
                    break
                data += chunk
            sock.close()
            raw = data.decode()
            idx = raw.find('\r\n\r\n')
            if idx >= 0:
                body = raw[idx:].lstrip('\r\n')
                headers = raw[:idx]
            else:
                body = raw
                headers = ''
            status = headers.split('\n')[0].strip() if headers else '200 OK'
            return ('print_lines', [
                f'=== {status} ===',
                body[:500],
            ])
        except Exception as e:
            return ('print', f'curl: {e}')
    else:
        if url.startswith('https://'):
            host_path = url[8:]
        else:
            host_path = url
        slash = host_path.find('/')
        if slash >= 0:
            host = host_path[:slash]
            path = host_path[slash:]
        else:
            host = host_path
            path = '/'
        try:
            import usocket
            import ssl
            sock = usocket.socket()
            sock.settimeout(10)
            addr = usocket.getaddrinfo(host, 443)[0][-1]
            sock.connect(addr)
            ssock = ssl.wrap_socket(sock, server_hostname=host)
            ssock.sendall(f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
            data = b''
            while True:
                chunk = ssock.read(1024)
                if not chunk:
                    break
                data += chunk
            ssock.close()
            raw = data.decode()
            idx = raw.find('\r\n\r\n')
            if idx >= 0:
                body = raw[idx:].lstrip('\r\n')
                headers = raw[:idx]
            else:
                body = raw
                headers = ''
            status = headers.split('\n')[0].strip() if headers else '200 OK'
            return ('print_lines', [
                f'=== {status} ===',
                body[:500],
            ])
        except Exception as e:
            return ('print', f'curl: {e}')


def cmd_backup(args):
    backup_dir = '/sd/backup'
    try:
        os.mkdir(backup_dir)
    except:
        pass
    important = [
        'todo.txt', 'notes', '.data',
        'calc_history.txt', 'calc_memory.txt',
        'theme.cfg', 'aliases.txt',
    ]
    copied = 0
    for name in important:
        src = name
        if not name.startswith('/'):
            src = name
        try:
            st = os.stat(src)
            if st[0] & 0x4000:
                continue
        except:
            continue
        try:
            with open(src, 'r') as f:
                data = f.read()
            dst = backup_dir + '/' + name.replace('/', '_')
            with open(dst, 'w') as f:
                f.write(data)
            copied += 1
        except:
            pass
    return ('print', f'  Backed up {copied} files to {backup_dir}/')


def cmd_restore(args):
    backup_dir = '/sd/backup'
    try:
        files = os.listdir(backup_dir)
    except:
        return ('print', 'restore: no backup found (run backup first)')
    if not files:
        return ('print', 'restore: backup directory is empty')
    restored = 0
    for name in files:
        src = backup_dir + '/' + name
        original = name.replace('_', '/')
        try:
            with open(src, 'r') as f:
                data = f.read()
            with open(original, 'w') as f:
                f.write(data)
            restored += 1
        except:
            pass
    return ('print', f'  Restored {restored} files from {backup_dir}/')


def cmd_speedtest(args):
    try:
        import usocket
        import ssl
        import time as _time

        host = 'speed.cloudflare.com'

        # 1. Ping test
        ping_start = _time.ticks_ms()
        sock = usocket.socket()
        sock.settimeout(10)
        addr = usocket.getaddrinfo(host, 443)[0][-1]
        sock.connect(addr)
        ssock = ssl.wrap_socket(sock, server_hostname=host)
        ssock.sendall(f'GET /cdn-cgi/trace HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
        data = b''
        while True:
            chunk = ssock.read(1024)
            if not chunk:
                break
            data += chunk
        ssock.close()
        ping_ms = _time.ticks_diff(_time.ticks_ms(), ping_start)

        # 2. Download test
        dl_start = _time.ticks_ms()
        sock2 = usocket.socket()
        sock2.settimeout(15)
        addr2 = usocket.getaddrinfo(host, 443)[0][-1]
        sock2.connect(addr2)
        ssock2 = ssl.wrap_socket(sock2, server_hostname=host)
        ssock2.sendall(f'GET /cdn-cgi/trace HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
        dl_data = b''
        while True:
            chunk = ssock2.read(4096)
            if not chunk:
                break
            dl_data += chunk
        dl_ms = _time.ticks_diff(_time.ticks_ms(), dl_start)
        ssock2.close()
        dl_kb = len(dl_data) / 1024
        dl_speed = dl_kb / (dl_ms / 1000) if dl_ms > 0 else 0

        # 3. Upload test (POST small data)
        up_start = _time.ticks_ms()
        sock3 = usocket.socket()
        sock3.settimeout(10)
        addr3 = usocket.getaddrinfo(host, 443)[0][-1]
        sock3.connect(addr3)
        ssock3 = ssl.wrap_socket(sock3, server_hostname=host)
        payload = b'x' * 1024
        req = f'POST /cdn-cgi/trace HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n'.encode() + payload
        ssock3.sendall(req)
        up_data = b''
        while True:
            chunk = ssock3.read(1024)
            if not chunk:
                break
            up_data += chunk
        up_ms = _time.ticks_diff(_time.ticks_ms(), up_start)
        ssock3.close()
        up_kb = len(payload) / 1024
        up_speed = up_kb / (up_ms / 1000) if up_ms > 0 else 0

        return ('print_lines', [
            '=== Speed Test ===',
            f'  Ping:    {ping_ms}ms',
            f'  Download:{dl_speed:.1f} KB/s ({dl_kb:.1f}KB in {dl_ms}ms)',
            f'  Upload:  {up_speed:.1f} KB/s ({up_kb:.1f}KB in {up_ms}ms)',
        ])
    except Exception as e:
        return ('print', f'speedtest: {e}')


STARTUP_FILE = 'boot.rc'


def _read_startup():
    """Read startup commands from boot.rc, skipping blanks and comments."""
    lines = []
    try:
        with open(STARTUP_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    lines.append(line)
    except OSError:
        pass
    return lines


def _write_startup(cmds):
    """Write startup commands to boot.rc."""
    with open(STARTUP_FILE, 'w') as f:
        f.write('# boot.rc - startup commands\n')
        f.write('# lines starting with # are comments\n')
        for cmd in cmds:
            f.write(cmd + '\n')


def cmd_startup(args):
    """Manage startup commands that run on boot.
    Usage:
      startup                 - list all startup commands
      startup <command>       - add a command to startup
      startup <command> -d    - remove a command from startup
      startup -c              - clear all startup commands
    """
    raw = args.strip()
    if not raw:
        # List all startup commands
        cmds = _read_startup()
        if not cmds:
            return ('print_lines', [
                '=== Startup Commands ===',
                '',
                '  (none defined)',
                '',
                '  Use: startup <command> to add',
                '       startup <command> -d to remove',
            ])
        lines = ['=== Startup Commands ===', '']
        for i, c in enumerate(cmds, 1):
            lines.append(f'  {i}. {c}')
        lines.append('')
        lines.append('  These run on every boot.')
        return ('print_lines', lines)

    # Check for clear flag
    if raw == '-c' or raw == '--clear':
        _write_startup([])
        return ('print', 'startup: cleared all commands')

    # Check for delete flag
    delete_mode = False
    if raw.endswith(' -d') or raw.endswith(' --delete'):
        delete_mode = True
        cmd = raw[:-2].strip() if raw.endswith(' -d') else raw[:-8].strip()
    else:
        cmd = raw

    if not cmd:
        return ('print', 'startup: usage: startup <command> [-d]')

    cmds = _read_startup()

    if delete_mode:
        # Remove the command
        if cmd in cmds:
            cmds.remove(cmd)
            _write_startup(cmds)
            return ('print', f'startup: removed "{cmd}"')
        else:
            return ('print', f'startup: "{cmd}" not in startup')
    else:
        # Add the command (avoid duplicates)
        if cmd in cmds:
            return ('print', f'startup: "{cmd}" already in startup')
        cmds.append(cmd)
        _write_startup(cmds)
        return ('print', f'startup: added "{cmd}"\n  Will run on next boot')


def cmd_stamp(args):
    import time
    t = time.localtime()
    parts = args.strip().split() if args.strip() else []
    fmt = parts[0] if parts else 'all'
    lines = []
    if fmt in ('all', 'time'):
        lines.append(f'  Time: {t[3]:02d}:{t[4]:02d}:{t[5]:02d}')
    if fmt in ('all', 'date'):
        lines.append(f'  Date: {t[0]:04d}-{t[1]:02d}-{t[2]:02d}')
    if fmt in ('all', 'unix'):
        lines.append(f'  Unix: {int(time.time())}')
    if fmt in ('all', 'iso'):
        lines.append(f'  ISO:  {t[0]:04d}-{t[1]:02d}-{t[2]:02d}T{t[3]:02d}:{t[4]:02d}:{t[5]:02d}')
    if fmt in ('all', 'day'):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        lines.append(f'  Day:  {days[t[6]]}')
    if fmt in ('all', 'week'):
        import math
        jan1 = time.mktime((t[0], 1, 1, 0, 0, 0, 0, 0, 0))
        now = time.time()
        week = int((now - jan1) / 604800) + 1
        lines.append(f'  Week: {week}')
    if not lines:
        lines.append(f'  Time: {t[3]:02d}:{t[4]:02d}:{t[5]:02d}')
        lines.append(f'  Date: {t[0]:04d}-{t[1]:02d}-{t[2]:02d}')
    return ('print_lines', ['=== Timestamp ==='] + lines)


def cmd_hash(args):
    text = args.strip()
    if not text:
        return ('print', 'hash: usage: hash [text]')
    h = 5381
    for c in text:
        h = ((h << 5) + h + ord(c)) & 0xFFFFFFFF
    hex_str = ''.join('0123456789abcdef'[(h >> (i * 4)) & 0xF] for i in range(7, -1, -1))
    return ('print_lines', [
        f'=== Hash ===',
        f'  Text:  {text}',
        f'  djb2:  {hex_str}',
        f'  Dec:   {h}',
    ])


def cmd_leap(args):
    year_str = args.strip()
    if not year_str:
        return ('print', 'leap: usage: leap [year]')
    try:
        year = int(year_str)
    except ValueError:
        return ('print', 'leap: invalid year')
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    days = 366 if is_leap else 365
    feb = 29 if is_leap else 28
    return ('print_lines', [
        f'=== {year} ===',
        f'  Leap year: {"Yes" if is_leap else "No"}',
        f'  Days: {days}',
        f'  February: {feb} days',
    ])


def cmd_age(args):
    import time
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 3:
        return ('print', 'age: usage: age [year] [month] [day]')
    try:
        by = int(parts[0])
        bm = int(parts[1])
        bd = int(parts[2])
    except ValueError:
        return ('print', 'age: invalid date')
    t = time.localtime()
    age_y = t[0] - by
    age_m = t[1] - bm
    age_d = t[2] - bd
    if age_d < 0:
        age_m -= 1
        age_d += 30
    if age_m < 0:
        age_y -= 1
        age_m += 12
    return ('print_lines', [
        f'=== Age ===',
        f'  Born: {by:04d}-{bm:02d}-{bd:02d}',
        f'  Age:  {age_y} years, {age_m} months, {age_d} days',
    ])


def cmd_pct(args):
    parts = args.strip().split() if args.strip() else []
    if len(parts) < 2:
        return ('print', 'pct: usage: pct [value] [total]')
    try:
        val = float(parts[0])
        total = float(parts[1])
    except ValueError:
        return ('print', 'pct: invalid numbers')
    if total == 0:
        return ('print', 'pct: total cannot be zero')
    result = val / total * 100
    return ('print_lines', [
        f'=== Percentage ===',
        f'  {val} / {total} = {result:.2f}%',
    ])


def cmd_rev(args):
    text = args.strip()
    if not text:
        return ('print', 'rev: usage: rev [text]')
    return ('print_lines', [
        f'=== Reverse ===',
        f'  Original: {text}',
        f'  Reversed: {text[::-1]}',
    ])


def cmd_chars(args):
    start = 32
    parts = args.strip().split() if args.strip() else []
    if parts:
        try:
            start = int(parts[0])
        except ValueError:
            pass
    lines = [f'=== ASCII {start}-{start+63} ===']
    for i in range(start, start + 64, 16):
        row = ''
        for j in range(16):
            code = i + j
            if 32 <= code < 127:
                row += f' {code:3d}={chr(code)}'
            else:
                row += f' {code:3d}=.'
        lines.append(row)
    return ('print_lines', lines)
