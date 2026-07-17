import time
import os


def cmd_clock(tft=None):
    try:
        from machine import RTC
        rtc = RTC()
        dt = rtc.datetime()
        time_str = '{:02d}:{:02d}:{:02d}'.format(dt[4], dt[5], dt[6])
        date_str = '{:02d}/{:02d}/{:02d}'.format(dt[2], dt[1], dt[0] % 100)
        return ('print_lines', [f'  {date_str} {time_str}'])
    except:
        return ('print', 'clock: RTC not available')


def cmd_calc(args, tft=None):
    if not args.strip():
        from commands.utilcmd import _calc_loop
        return ('game', _calc_loop)
    expr = args.strip()
    try:
        from lib.calc_engine import CalcEngine
        engine = CalcEngine()
        result = engine.eval_expr(expr)
        return ('print', f'  = {result}')
    except Exception as e:
        return ('print', f'calc: {e}')


def cmd_nano(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'nano: usage: nano [filename]')
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except OSError:
        content = ''
    return ('edit', filename, content)


def cmd_run(args):
    filename = args.strip()
    if not filename:
        return ('print', 'run: usage: run [filename.py]')
    try:
        with open(filename, 'r') as f:
            code = f.read()
        exec(compile(code, filename, 'exec'))
        return ('print', f'run: {filename} done')
    except OSError:
        return ('print', f'run: {filename} not found')
    except Exception as e:
        return ('print', f'run: {e}')


def cmd_sleep(args, tft=None):
    if tft:
        tft.fill(0x0000)
    try:
        import machine
        machine.lightsleep()
    except:
        pass
    return ('print', 'sleep: woke up')


def cmd_viewjpg(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'view: usage: view [filename.jpg]')
    if not tft:
        return ('print', 'view: no display available')
    try:
        from lib.jpegdec import JPEGDecoder
        decoder = JPEGDecoder()
        out_w, out_h = decoder.decode(filename, tft, max_w=tft.width, max_h=tft.height)
        return ('print', f'view: {filename} ({out_w}x{out_h})')
    except Exception as e:
        return ('print', f'view: {e}')


def cmd_bmpview(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'bmpview: usage: bmpview [filename.bmp]')
    if not tft:
        return ('print', 'bmpview: no display available')
    try:
        with open(filename, 'rb') as f:
            header = f.read(54)
            if header[:2] != b'BM':
                return ('print', 'bmpview: not a BMP file')
            width = int.from_bytes(header[18:22], 'little')
            height = int.from_bytes(header[22:26], 'little')
            planes = int.from_bytes(header[26:28], 'little')
            bits = int.from_bytes(header[28:30], 'little')
            compression = int.from_bytes(header[30:34], 'little')
            if planes != 1 or bits != 24 or compression != 0:
                return ('print', 'bmpview: only 24-bit uncompressed BMP supported')
            data_offset = int.from_bytes(header[10:14], 'little')
            f.seek(data_offset)
            row_size = (width * 3 + 3) & ~3
            max_w = min(width, tft.width)
            max_h = min(height, tft.height)
            scale_x = width / max_w if width > max_w else 1
            scale_y = height / max_h if height > max_h else 1
            buf = bytearray(max_w * 2)
            for y in range(max_h - 1, -1, -1):
                src_y = int(y * scale_y) if scale_y != 1 else y
                f.seek(data_offset + (height - 1 - src_y) * row_size)
                row = f.read(row_size)
                for x in range(max_w):
                    src_x = int(x * scale_x) if scale_x != 1 else x
                    idx = src_x * 3
                    b = row[idx]
                    g = row[idx + 1]
                    r = row[idx + 2]
                    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    buf[x * 2] = (color >> 8) & 0xFF
                    buf[x * 2 + 1] = color & 0xFF
                tft._set_window(0, y, max_w - 1, y)
                tft._dc(1)
                tft._cs(0)
                tft._spi.write(buf)
                tft._cs(1)
        return ('print', f'bmpview: {filename} ({max_w}x{max_h})')
    except Exception as e:
        return ('print', f'bmpview: {e}')


def cmd_wlan(args):
    import os
    import json
    CRED_FILE = '/wlan_creds.json'

    def load_creds():
        try:
            with open(CRED_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_creds(data):
        try:
            with open(CRED_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

    parts = args.strip().split() if args.strip() else []

    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
    except Exception as e:
        return ('print', f'wlan: {e}')

    if not parts:
        try:
            if wlan.isconnected():
                cfg = wlan.ifconfig()
                return ('print_lines', [
                    '=== WiFi Connected ===',
                    f'  SSID: {wlan.config("essid")}',
                    f'  IP:   {cfg[0]}',
                    f'  Mask: {cfg[1]}',
                    f'  GW:   {cfg[2]}',
                    f'  DNS:  {cfg[3]}',
                ])
            else:
                scanned = wlan.scan()
                if scanned:
                    lines = ['=== Available Networks ===']
                    seen = set()
                    for ssid, bssid, channel, rssi, authmode, hidden in scanned:
                        name = ssid.decode()
                        if name not in seen:
                            seen.add(name)
                            lines.append(f'  {name} ({rssi}dBm)')
                    return ('print_lines', lines)
                else:
                    return ('print', 'wlan: no networks found')
        except Exception as e:
            return ('print', f'wlan: {e}')

    if parts[0] == '-l':
        creds = load_creds()
        if creds:
            lines = ['=== Saved Networks ===']
            for name, info in creds.items():
                lines.append(f'  {name} -> {info["ssid"]}')
            return ('print_lines', lines)
        return ('print', 'wlan: no saved networks')

    if parts[0] == '-d':
        if len(parts) < 2:
            return ('print', 'wlan: -d requires a name')
        creds = load_creds()
        if parts[1] in creds:
            del creds[parts[1]]
            save_creds(creds)
            return ('print', f'wlan: deleted {parts[1]}')
        return ('print', f'wlan: {parts[1]} not found')

    if '-s' in parts:
        idx = parts.index('-s')
        if len(parts) < idx + 2:
            return ('print', 'wlan: -s requires a name after it')
        name = parts[idx + 1]
        if len(parts) < 3:
            return ('print', 'wlan: need ssid and password to save')
        ssid = parts[0]
        password = parts[1]
        creds = load_creds()
        creds[name] = {'ssid': ssid, 'password': password}
        save_creds(creds)
        return ('print', f'wlan: saved as "{name}"')

    name = parts[0]
    creds = load_creds()
    if name in creds:
        ssid = creds[name]['ssid']
        password = creds[name]['password']
    elif len(parts) >= 2:
        ssid = parts[0]
        password = parts[1]
    else:
        return ('print', f'wlan: unknown "{name}" (try -l)')

    try:
        wlan.connect(ssid, password)
        for _ in range(30):
            if wlan.isconnected():
                ip = wlan.ifconfig()[0]
                _sync_ntp_time()
                return ('print', f'wlan: connected to {ssid}\n  IP: {ip}')
            time.sleep(0.5)
        return ('print', f'wlan: failed to connect to {ssid}')
    except Exception as e:
        return ('print', f'wlan: {e}')


_is_cest = None

def _sync_ntp_time():
    try:
        import ntptime
        ntptime.host = 'pool.ntp.org'
        ntptime.settime()
        utc = time.time()
        import utime
        t = utime.gmtime(utc)
        year, month, day = t[0], t[1], t[2]
        hour = t[3]
        offset = 2 if _is_cest(year, month, day, hour) else 1
        local = utc + offset * 3600
        lt = utime.gmtime(local)
        from machine import RTC
        rtc = RTC()
        rtc.datetime((lt[0], lt[1], lt[2], lt[6] + 1, lt[3], lt[4], lt[5], 0))
    except:
        pass


def _is_cest(year, month, day, hour):
    if month < 3 or month > 10:
        return False
    if month > 3 and month < 10:
        return True
    if month == 3:
        last_sun = day - (day % 7) + (6 - (day % 7)) % 7
        if last_sun > 31:
            last_sun -= 7
        if day < last_sun:
            return False
        if day == last_sun and hour < 2:
            return False
        return True
    if month == 10:
        last_sun = day - (day % 7) + (6 - (day % 7)) % 7
        if last_sun > 31:
            last_sun -= 7
        if day < last_sun:
            return True
        if day == last_sun and hour < 3:
            return True
        return False
    return False


def cmd_calc(args, tft=None):
    # FIX: Define calculator loop BEFORE calling it
    def _calc_loop(tft, read_key):
        import time
        from lib.calc_fraction import Fraction, format_value
        from lib.calc_engine import CalcEngine
        from lib.calc_history import save_history, load_history, save_memory, load_memory
        
        engine = CalcEngine()
        engine.memory = load_memory()
        history = load_history()
        
        input_buf = ''
        frac_mode = False
        angle_mode = 'DEG'
        oled = None
        try:
            from lib.oled_ctrl import OLEDController
            oled = OLEDController()
        except:
            pass
        
        def draw_header():
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15('Espelt Calc', 120, 4, 0x07FF, 0x1082)
            tft.hline(0, 24, 480, 0x07FF)
        
        def draw_prompt():
            tft.fill_rect(0, 280, 480, 40, 0x0000)
            mode_str = f"Mode: {angle_mode} | Frac: {'ON' if frac_mode else 'OFF'}"
            tft.text15(mode_str, 4, 284, 0x07E0, 0x0000)
            tft.text15(f"> {input_buf}_", 4, 300, 0xFFFF, 0x0000)
        
        def draw_result(result):
            tft.fill_rect(0, 24, 480, 256, 0x0000)
            tft.text15(f"= {format_value(result, frac_mode)}", 4, 28, 0x07E0, 0x0000)
        
        tft_fill = lambda c: tft.fill(c)
        tft_fill(0x0000)
        draw_header()
        
        while True:
            draw_prompt()
            ch = read_key()
            
            if ch == '\x18':  # Ctrl+X - Exit
                save_history(engine.history)
                save_memory(engine.memory)
                tft.text15('Exiting calc...', 120, 140, 0x07E0, 0x0000)
                time.sleep_ms(500)
                return
            
            elif ch == '\x04':  # Ctrl+D - Toggle fraction mode
                frac_mode = not frac_mode
                tft.text15(f"  Frac: {'ON' if frac_mode else 'OFF'}", 4, 284, 0x07E0, 0x0000)
            
            elif ch == '\x07':  # Ctrl+G - Graph
                if oled:
                    tft.text15('Graphing...', 4, 284, 0x07E0, 0x0000)
                    try:
                        graph_on_oled(oled._oled, input_buf)
                        tft.text15('Done!', 4, 284, 0x07E0, 0x0000)
                    except Exception as e:
                        tft.text15(f'Error: {e}', 4, 284, 0xFF00, 0x0000)
                    time.sleep_ms(1000)
            
            elif ch == '\x0c':  # Ctrl+L - Clear screen
                tft_fill(0x0000)
                draw_header()
                input_buf = ''
            
            elif ch == '\x03':  # Ctrl+C - Cancel line
                input_buf = ''
            
            elif ch == '\x13':  # Save (Ctrl+S or PgUp)
                save_history(engine.history)
                tft.text15('  Saved!', 4, 284, 0x07E0, 0x0000)
                time.sleep_ms(500)
            
            elif ch == '\n':  # Enter - Evaluate
                if input_buf.strip():
                    try:
                        result = engine.eval_expr(input_buf)
                        draw_result(result)
                        input_buf = ''
                        tft.text15(f"= {format_value(result, frac_mode)}", 4, 280, 0x07E0, 0x0000)
                    except Exception as e:
                        tft.text15(f"Error: {e}", 4, 280, 0xFF00, 0x0000)
                    time.sleep_ms(500)
            
            elif ch == '\x1b':  # Esc - Clear line
                input_buf = ''
            
            elif ch == '\b':  # Backspace
                input_buf = input_buf[:-1]
            
            elif ch == '\t':  # Tab - Auto-complete functions
                funcs = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'log', 'ln', 'sqrt', 'cbrt', 'fact', 'nPr', 'nCr', 'rand', 'randint', 'mean', 'stddev', 'pol', 'rec']
                for f in funcs:
                    if input_buf.startswith(f):
                        input_buf = f + '('
                        break
            
            elif ch.isalnum() or ch in '+-*/().^%!_ ':
                input_buf += ch
            
            draw_prompt()
            time.sleep_ms(20)
    
    if not args.strip():
        return ('game', _calc_loop)
    expr = args.strip()
    try:
        from lib.calc_engine import CalcEngine
        engine = CalcEngine()
        result = engine.eval_expr(expr)
        return ('print', f'  = {result}')
    except Exception as e:
        return ('print', f'calc: {e}')


def cmd_nano(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'nano: usage: nano [filename]')
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except OSError:
        content = ''
    return ('edit', filename, content)


def cmd_run(args):
    filename = args.strip()
    if not filename:
        return ('print', 'run: usage: run [filename.py]')
    try:
        with open(filename, 'r') as f:
            code = f.read()
        exec(compile(code, filename, 'exec'))
        return ('print', f'run: {filename} done')
    except OSError:
        return ('print', f'run: {filename} not found')
    except Exception as e:
        return ('print', f'run: {e}')


def cmd_sleep(args, tft=None):
    if tft:
        tft.fill(0x0000)
    try:
        import machine
        machine.lightsleep()
    except:
        pass
    return ('print', 'sleep: woke up')


def cmd_viewjpg(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'view: usage: view [filename.jpg]')
    if not tft:
        return ('print', 'view: no display available')
    try:
        from lib.jpegdec import JPEGDecoder
        decoder = JPEGDecoder()
        out_w, out_h = decoder.decode(filename, tft, max_w=tft.width, max_h=tft.height)
        return ('print', f'view: {filename} ({out_w}x{out_h})')
    except Exception as e:
        return ('print', f'view: {e}')


def cmd_bmpview(args, tft=None):
    filename = args.strip()
    if not filename:
        return ('print', 'bmpview: usage: bmpview [filename.bmp]')
    if not tft:
        return ('print', 'bmpview: no display available')
    try:
        with open(filename, 'rb') as f:
            header = f.read(54)
            if header[:2] != b'BM':
                return ('print', 'bmpview: not a BMP file')
            width = int.from_bytes(header[18:22], 'little')
            height = int.from_bytes(header[22:26], 'little')
            planes = int.from_bytes(header[26:28], 'little')
            bits = int.from_bytes(header[28:30], 'little')
            compression = int.from_bytes(header[30:34], 'little')
            if planes != 1 or bits != 24 or compression != 0:
                return ('print', 'bmpview: only 24-bit uncompressed BMP supported')
            data_offset = int.from_bytes(header[10:14], 'little')
            f.seek(data_offset)
            row_size = (width * 3 + 3) & ~3
            max_w = min(width, tft.width)
            max_h = min(height, tft.height)
            scale_x = width / max_w if width > max_w else 1
            scale_y = height / max_h if height > max_h else 1
            buf = bytearray(max_w * 2)
            for y in range(max_h - 1, -1, -1):
                src_y = int(y * scale_y) if scale_y != 1 else y
                f.seek(data_offset + (height - 1 - src_y) * row_size)
                row = f.read(row_size)
                for x in range(max_w):
                    src_x = int(x * scale_x) if scale_x != 1 else x
                    idx = src_x * 3
                    b = row[idx]
                    g = row[idx + 1]
                    r = row[idx + 2]
                    color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    buf[x * 2] = (color >> 8) & 0xFF
                    buf[x * 2 + 1] = color & 0xFF
                tft._set_window(0, y, max_w - 1, y)
                tft._dc(1)
                tft._cs(0)
                tft._spi.write(buf)
                tft._cs(1)
        return ('print', f'bmpview: {filename} ({max_w}x{max_h})')
    except Exception as e:
        return ('print', f'bmpview: {e}')


_is_cest = None

def _sync_ntp_time():
    try:
        import ntptime
        ntptime.host = 'pool.ntp.org'
        ntptime.settime()
        utc = time.time()
        import utime
        t = utime.gmtime(utc)
        year, month, day = t[0], t[1], t[2]
        hour = t[3]
        offset = 2 if _is_cest(year, month, day, hour) else 1
        local = utc + offset * 3600
        lt = utime.gmtime(local)
        from machine import RTC
        rtc = RTC()
        rtc.datetime((lt[0], lt[1], lt[2], lt[6] + 1, lt[3], lt[4], lt[5], 0))
    except:
        pass


def _is_cest(year, month, day, hour):
    if month < 3 or month > 10:
        return False
    if month > 3 and month < 10:
        return True
    if month == 3:
        last_sun = day - (day % 7) + (6 - (day % 7)) % 7
        if last_sun > 31:
            last_sun -= 7
        if day < last_sun:
            return False
        if day == last_sun and hour < 2:
            return False
        return True
    if month == 10:
        last_sun = day - (day % 7) + (6 - (day % 7)) % 7
        if last_sun > 31:
            last_sun -= 7
        if day < last_sun:
            return True
        if day == last_sun and hour < 3:
            return True
        return False
    return False
