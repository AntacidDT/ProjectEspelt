import gc
import time
import os
import _thread
from machine import Pin, SPI, PWM
from lib.ili9488 import ILI9488
from lib.oled_ctrl import OLEDController
from lib.keyboard import hid_to_char
from lib.buzzer import Buzzer
from commands.dispatch import dispatch, COMMANDS
import commands.dispatch as _dispatch_mod
from commands.utilcmd import _cmd_history
import usb_host

TFT_CS = Pin(26, Pin.OUT)
TFT_DC = Pin(27, Pin.OUT)
TFT_RST = Pin(4, Pin.OUT)
spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(23), mosi=Pin(6))
tft = ILI9488(spi, cs=TFT_CS, dc=TFT_DC, rst=TFT_RST)

buzzer = Buzzer(20)
_dispatch_mod._buzzer = buzzer
backlight = PWM(Pin(5), freq=1000, duty_u16=65535)
_dispatch_mod._backlight = backlight

COLORS = {
    'default': {'bg': 0x0000, 'header': 0x1082, 'accent': 0x07FF, 'green': 0x07E0, 'yellow': 0xFFE0, 'red': 0xF800, 'white': 0xFFFF},
    'warm':    {'bg': 0x0000, 'header': 0x4208, 'accent': 0xFD20, 'green': 0x07E0, 'yellow': 0xFFE0, 'red': 0xF800, 'white': 0xFFFF},
    'cyber':   {'bg': 0x0000, 'header': 0x001F, 'accent': 0x07FF, 'green': 0x07E0, 'yellow': 0x07FF, 'red': 0xF800, 'white': 0xFFFF},
    'forest':  {'bg': 0x0000, 'header': 0x03E0, 'accent': 0x07E0, 'green': 0x07E0, 'yellow': 0xFFE0, 'red': 0xF800, 'white': 0xFFFF},
}
_theme = 'default'
_dispatch_mod.THEME_COLORS = COLORS[_theme]
def _c(key):
    return COLORS[_theme][key]

def read_key(timeout_ms=0):
    """Read one key from the USB keyboard.
    timeout_ms=0  -> non-blocking, returns None if no key waiting
    timeout_ms>0  -> blocks up to timeout_ms milliseconds
    Returns the decoded character (or None on timeout / no key).
    NOTE: when timeout_ms > 0 we yield with a SINGLE sleep_ms instead of
    a tight poll loop. Splitting the wait into 5 ms chunks starves the
    OLED thread of GIL time and freezes its animation. Original main loop
    used a single sleep_ms(50) for the same reason.
    """
    report = usb_host.read()
    if report is not None:
        return hid_to_char(report)
    if timeout_ms > 0:
        time.sleep_ms(timeout_ms)
    report = usb_host.read()
    if report is None:
        return None
    return hid_to_char(report)

PROMPT = 'espelt> '
MAX_LINE_LEN = 120
LINES_ON_SCREEN = 15
LINE_H = 16
HEADER_H = 24
TEXT_Y0 = 26
screen_lines = []
cursor_line = ''
edit_mode = False
edit_filename = ''
edit_lines = []
edit_cursor_row = 0
edit_cursor_col = 0
edit_scroll = 0
fm_mode = False
fm_path = '/'
fm_cursor = 0
fm_scroll = 0
_screensaver_active = False
_last_input_time = time.ticks_ms()
_startup_done = False
_ctrl_prefix = False
_hist_idx = -1
_stealth = False
_backlight_on = True
_oled_on = True
_oled_mode_select = False
_THEMES = ('default', 'warm', 'cyber', 'forest')
_prev_screen = []       # last drawn content lines (for dirty tracking)
_content_dirty = True   # force full redraw on first draw

def _tab_complete(line):
    parts = line.split()
    if not parts:
        return line
    prefix = parts[-1]
    matches = [c for c in COMMANDS if c.startswith(prefix)]
    if len(matches) == 1:
        parts[-1] = matches[0]
        return ' '.join(parts)
    if len(matches) > 1:
        screen_lines.append('  ' + ' '.join(matches))
        tft_redraw()
    return line

def _do_screensaver():
    global _screensaver_active, _last_input_time
    if _screensaver_active:
        return
    _screensaver_active = True
    oled.set_mode('dvd')

def _exit_screensaver():
    global _screensaver_active, _last_input_time
    if not _screensaver_active:
        return
    _screensaver_active = False
    _last_input_time = time.ticks_ms()
    oled.set_mode('status')

_THEMES_LIST = ['default', 'warm', 'cyber', 'forest']

def _history_prev():
    global _hist_idx, cursor_line
    if not _cmd_history:
        return
    if _hist_idx < len(_cmd_history) - 1:
        _hist_idx += 1
        cursor_line = _cmd_history[-(1 + _hist_idx)]
        _draw_prompt()

def _history_next():
    global _hist_idx, cursor_line
    if _hist_idx <= -1:
        return
    _hist_idx -= 1
    if _hist_idx == -1:
        cursor_line = ''
    else:
        cursor_line = _cmd_history[-(1 + _hist_idx)]
    _draw_prompt()

def _toggle_stealth():
    global _stealth
    _stealth = not _stealth
    if _stealth:
        tft_clear()
        backlight.duty_u16(0)
        oled.screen_off()
    else:
        backlight.duty_u16(65535 if _backlight_on else 0)
        if _oled_on:
            oled.screen_on()
            oled.set_mode('status')
        tft_redraw()

def _toggle_backlight():
    global _backlight_on
    _backlight_on = not _backlight_on
    backlight.duty_u16(65535 if _backlight_on else 0)

def _toggle_oled():
    global _oled_on
    _oled_on = not _oled_on
    if _oled_on:
        oled.screen_on()
        oled.set_mode('auto')
    else:
        oled.screen_off()

def _oled_pick_mode(ch):
    pass

def _cycle_theme():
    global _theme
    idx = _THEMES_LIST.index(_theme) if _theme in _THEMES_LIST else 0
    _theme = _THEMES_LIST[(idx + 1) % len(_THEMES_LIST)]
    _dispatch_mod.THEME_COLORS = COLORS[_theme]
    try:
        oled.set_theme(COLORS[_theme])
    except:
        pass
    screen_lines.append(f'  theme: {_theme}')
    tft_redraw()

def _show_free_ram():
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    screen_lines.append('  RAM: ' + str(free // 1024) + 'KB free / ' +
                        str(total // 1024) + 'KB total')
    _draw_lines()
    _draw_prompt()

def _clear_screen():
    screen_lines.clear()
    tft_clear()
    tft_print_header()
    if _oled_on:
        oled.set_mode('status')

def _handle_shortcut(char):
    """Handle Ctrl+ shortcuts and navigation. Returns True if consumed."""
    global cursor_line
    code = ord(char)

    # Navigation (arrows + PgUp/PgDn + Ctrl+1/2)
    if char == '\x80' or char == '\x82':  # Up / PgUp / Ctrl+1
        _history_prev()
        return True
    if char == '\x81' or char == '\x83':  # Down / PgDn / Ctrl+2
        _history_next()
        return True
    if char == '\x92':  # Ctrl+3: stealth
        _toggle_stealth()
        return True

    # Ctrl+letter
    if code == 1:   # Ctrl+A: clear input
        cursor_line = ''
        _draw_prompt()
        return True
    if code == 2:   # Ctrl+B: toggle backlight
        _toggle_backlight()
        return True
    if code == 3:   # Ctrl+C: clear input
        cursor_line = ''
        _draw_prompt()
        return True
    if code == 6:   # Ctrl+F: show free RAM
        _show_free_ram()
        return True
    if code == 12:  # Ctrl+L: clear screen
        _clear_screen()
        return True
    if code == 15:  # Ctrl+O: toggle OLED
        _toggle_oled()
        return True
    if code == 18:  # Ctrl+R: reboot
        import machine
        machine.reset()
        return True
    if code == 20:  # Ctrl+T: cycle theme
        _cycle_theme()
        return True
    if code == 21:  # Ctrl+U: clear input
        cursor_line = ''
        _draw_prompt()
        return True
    return False

def _run_startup():
    global _startup_done
    _startup_done = True
    try:
        with open('boot.rc', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    dispatch(line, tft, oled)
    except OSError:
        pass

def tft_clear():
    tft.fill(_c('bg'))

def tft_print_header():
    tft.fill_rect(0, 0, 480, HEADER_H, _c('header'))
    tft.text15('Project Espelt', 120, 4, _c('accent'), _c('header'))
    tft.hline(0, HEADER_H, 480, _c('accent'))

def _line_color(line):
    """Return the TFT color constant for a screen line."""
    if line.startswith('>>>') or line.startswith('espelt>'):
        return _c('green')
    if line.startswith('---'):
        return _c('accent')
    if line.startswith('  '):
        return _c('yellow')
    if 'Error' in line or 'error' in line or 'Unknown' in line:
        return _c('red')
    return _c('white')

def _draw_lines():
    """Incremental content redraw.

    Compares the current visible window of screen_lines to the last one
    we drew (_prev_screen).  If the window itself shifted (new lines
    pushed old ones off-screen) we must do a full redraw because every
    y-position now holds different content.  If the window is the same
    we only clear+redraw the individual lines that actually changed —
    saving ~90 % of the SPI traffic on a normal keystroke.
    """
    global _prev_screen, _content_dirty

    visible = screen_lines[-LINES_ON_SCREEN:] if len(screen_lines) > LINES_ON_SCREEN else screen_lines
    bg = _c('bg')

    # Detect scroll: did the visible window change?
    scrolled = (len(visible) != len(_prev_screen) or
                visible[0] != _prev_screen[0] if visible and _prev_screen else True)

    if scrolled or _content_dirty:
        # Full clear + redraw (unavoidable on scroll or first draw)
        tft.fill_rect(0, TEXT_Y0, 480, LINES_ON_SCREEN * LINE_H, bg)
        y = TEXT_Y0
        for line in visible:
            tft.text15(line[:MAX_LINE_LEN], 4, y, _line_color(line), bg)
            y += LINE_H
    else:
        # Window is the same — only redraw lines whose content changed
        for i, line in enumerate(visible):
            if i >= len(_prev_screen) or line != _prev_screen[i]:
                y = TEXT_Y0 + i * LINE_H
                tft.fill_rect(0, y, 480, LINE_H, bg)
                tft.text15(line[:MAX_LINE_LEN], 4, y, _line_color(line), bg)

    _prev_screen = list(visible)
    _content_dirty = False

def _draw_prompt():
    prompt_y = TEXT_Y0 + LINES_ON_SCREEN * LINE_H
    tft.fill_rect(0, prompt_y, 480, LINE_H + 2, _c('bg'))
    visible_w = 58
    full = PROMPT + cursor_line
    if len(full) > visible_w:
        display = full[len(full) - visible_w:]
    else:
        display = full
    tft.text15(display, 4, prompt_y, _c('green'), _c('bg'))

def tft_redraw():
    global _prev_screen, _content_dirty
    _prev_screen = []
    _content_dirty = True
    tft_clear()
    tft_print_header()
    _draw_lines()
    _draw_prompt()

def _draw_edit():
    global edit_scroll
    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, HEADER_H, _c('header'))
    tft.text15('Edit: ' + edit_filename, 4, 4, _c('accent'), _c('header'))
    y = TEXT_Y0
    for i in range(LINES_ON_SCREEN):
        idx = edit_scroll + i
        if idx >= len(edit_lines):
            break
        color = _c('green') if idx == edit_cursor_row else _c('white')
        tft.text15(edit_lines[idx][:MAX_LINE_LEN], 4, y, color, _c('bg'))
        y += LINE_H

def _draw_fm():
    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, HEADER_H, _c('header'))
    tft.text15('File Manager', 4, 4, _c('accent'), _c('header'))

usb_host.read()
oled = OLEDController()
import commands.dispatch as _dispatch_mod
_dispatch_mod.OLED_REF = oled
def oled_loop():
    oled.run()
_thread.start_new_thread(oled_loop, ())

# Initialize I2S audio (ES8311 codec + speaker + mic)
try:
    from lib.audio import AudioPlayer
    _audio = AudioPlayer()
    if _audio.available:
        _audio.enable_pa()
        screen_lines.append('Audio: I2S speaker ready')
except:
    _audio = None

tft_clear()
tft_print_header()
screen_lines.append('Project Espelt v1.0')
screen_lines.append('Type help for commands')
screen_lines.append('')
tft_redraw()
_run_startup()

while True:
    try:
        char = read_key(timeout_ms=50)
        if char is None:
            continue

        if edit_mode:
            if char == chr(27):
                with open(edit_filename, 'w') as f:
                    f.write(chr(10).join(edit_lines))
                edit_mode = False
                screen_lines.clear()
                screen_lines.append('Saved')
                tft_redraw()
            elif char == chr(24):
                edit_mode = False
                screen_lines.clear()
                screen_lines.append('Quit')
                tft_redraw()
            elif char == chr(10):
                pos = edit_cursor_col
                line = edit_lines[edit_cursor_row]
                edit_lines[edit_cursor_row] = line[:pos]
                edit_cursor_row += 1
                edit_lines.insert(edit_cursor_row, line[pos:])
                edit_cursor_col = 0
                _draw_edit()
            elif char == chr(8):
                if edit_cursor_col > 0:
                    edit_lines[edit_cursor_row] = edit_lines[edit_cursor_row][:edit_cursor_col-1] + edit_lines[edit_cursor_row][edit_cursor_col:]
                    edit_cursor_col -= 1
                    _draw_edit()
            elif len(char) == 1 and 32 <= ord(char) <= 126:
                row = edit_cursor_row
                col = edit_cursor_col
                line = edit_lines[row]
                edit_lines[row] = line[:col] + char + line[col:]
                edit_cursor_col += 1
                _draw_edit()
            continue

        if char == chr(10):
            screen_lines.clear()
            screen_lines.append(PROMPT + cursor_line)
            try:
                result = dispatch(cursor_line, tft, oled)
            except Exception as e:
                err = str(e)
                if len(err) > 30:
                    err = err[:27] + '...'
                screen_lines.append('Err: ' + err)
                result = None
            if cursor_line.strip():
                _cmd_history.append(cursor_line.strip())
                oled.set_last_command(cursor_line.strip().split()[0])
                # Track recent commands for help recent
                try:
                    rec = []
                    try:
                        with open('/sd/recent_commands.txt', 'r') as f:
                            rec = [l.strip() for l in f.readlines() if l.strip()]
                    except:
                        pass
                    cmd = cursor_line.strip().split()[0]
                    if cmd in rec:
                        rec.remove(cmd)
                    rec.append(cmd)
                    if len(rec) > 16:
                        rec = rec[-16:]
                    with open('/sd/recent_commands.txt', 'w') as f:
                        for r in rec:
                            f.write(r + '\n')
                except:
                    pass
            if result is None:
                cursor_line = ''
            elif result[0] == 'clear':
                screen_lines.clear()
                tft_clear()
                tft_print_header()
            elif result[0] == 'print':
                for line in result[1].split(chr(10)):
                    screen_lines.append(line)
            elif result[0] == 'print_lines':
                for line in result[1]:
                    screen_lines.append(line)
            elif result[0] == 'game':
                try:
                    result[1](tft, read_key)
                except Exception as e:
                    err = str(e)
                    if len(err) > 30:
                        err = err[:27] + '...'
                    screen_lines.append('Err: ' + err)
                tft_redraw()
            elif result[0] == 'edit':
                edit_mode = True
                edit_filename = result[1]
                edit_lines = result[2].split(chr(10)) if result[2] else ['']
                edit_cursor_row = 0
                edit_cursor_col = 0
                edit_scroll = 0
                _draw_edit()
            elif result[0] == 'fm':
                fm_mode = True
                fm_path = result[1] if len(result) > 1 else '/'
                fm_cursor = 0
                fm_scroll = 0
                _draw_fm()
            cursor_line = ''
            _hist_idx = -1
            _draw_lines()
            _draw_prompt()
        elif char == chr(8):
            if cursor_line:
                cursor_line = cursor_line[:-1]
                _draw_prompt()
        elif char == chr(27):
            cursor_line = ''
            _draw_prompt()
        elif char == chr(9):
            cursor_line = _tab_complete(cursor_line)
            _draw_prompt()
        elif _handle_shortcut(char):
            pass
        elif len(char) == 1 and 32 <= ord(char) <= 126:
            if len(cursor_line) < MAX_LINE_LEN - len(PROMPT):
                cursor_line += char
                _draw_prompt()
    except Exception as e:
        try:
            screen_lines.append('REPL error: ' + str(e)[:30])
            _draw_lines()
            _draw_prompt()
        except:
            pass
        time.sleep_ms(100)
