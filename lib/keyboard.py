import usb_host

KEY_MAP = {
    0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e', 0x09: 'f',
    0x0a: 'g', 0x0b: 'h', 0x0c: 'i', 0x0d: 'j', 0x0e: 'k', 0x0f: 'l',
    0x10: 'm', 0x11: 'n', 0x12: 'o', 0x13: 'p', 0x14: 'q', 0x15: 'r',
    0x16: 's', 0x17: 't', 0x18: 'u', 0x19: 'v', 0x1a: 'w', 0x1b: 'x',
    0x1c: 'y', 0x1d: 'z',
    0x1e: '1', 0x1f: '2', 0x20: '3', 0x21: '4', 0x22: '5',
    0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9', 0x27: '0',
    0x28: '\n', 0x29: '\x1b', 0x2a: '\b', 0x2b: '\t',
    0x2c: ' ', 0x2d: '-', 0x2e: '=', 0x2f: '[', 0x30: ']',
    0x31: '\\', 0x33: ';', 0x34: "'", 0x36: ',', 0x37: '.', 0x38: '/',
    0x52: '\x80',  # Up Arrow
    0x51: '\x81',  # Down Arrow
    0x4B: '\x82',  # Page Up
    0x4E: '\x83',  # Page Down
    0x4F: '\x84',  # Right Arrow
    0x50: '\x85',  # Left Arrow
    0x58: '\n',    # Keypad Enter
    0x0D: '\n',    # CR (some keyboards)
    0xE9: '\x86',  # Volume Up
    0xEA: '\x87',  # Volume Down
    0xE2: '\x88',  # Mute
}

KEY_MAP_SHIFT = {
    0x04: 'A', 0x05: 'B', 0x06: 'C', 0x07: 'D', 0x08: 'E', 0x09: 'F',
    0x0a: 'G', 0x0b: 'H', 0x0c: 'I', 0x0d: 'J', 0x0e: 'K', 0x0f: 'L',
    0x10: 'M', 0x11: 'N', 0x12: 'O', 0x13: 'P', 0x14: 'Q', 0x15: 'R',
    0x16: 'S', 0x17: 'T', 0x18: 'U', 0x19: 'V', 0x1a: 'W', 0x1b: 'X',
    0x1c: 'Y', 0x1d: 'Z',
    0x1e: '!', 0x1f: '@', 0x20: '#', 0x21: '$', 0x22: '%',
    0x23: '^', 0x24: '&', 0x25: '*', 0x26: '(', 0x27: ')',
    0x2d: '_', 0x2e: '+', 0x2f: '{', 0x30: '}',
    0x31: '|', 0x33: ':', 0x34: '"', 0x36: '<', 0x37: '>', 0x38: '?',
}

MOD_LSHIFT = 0x02
MOD_LCTRL = 0x01
MOD_LALT = 0x04
MOD_RSHIFT = 0x20
MOD_RCTRL = 0x10
MOD_RALT = 0x40

_last_keycode = 0
_pending = ''


def hid_to_char(report):
    global _last_keycode, _pending
    if _pending:
        c = _pending[0]
        _pending = _pending[1:]
        return c
    modifier = report[0]
    keycode = report[2]
    if keycode == 0:
        _last_keycode = 0
        return None
    if keycode == _last_keycode:
        return None
    _last_keycode = keycode
    ctrl = modifier & (MOD_LCTRL | MOD_RCTRL)
    alt = modifier & (MOD_LALT | MOD_RALT)
    shift = modifier & (MOD_LSHIFT | MOD_RSHIFT)
    if alt:
        ch = KEY_MAP_SHIFT.get(keycode, None) if shift else KEY_MAP.get(keycode, None)
        if ch and len(ch) == 1:
            _pending = ch.lower()
            return '\x1f'
        return None
    if ctrl:
        if keycode == 0x0c:
            return '\x1e'
        if keycode >= 0x04 and keycode <= 0x1d:
            return chr(keycode - 0x04 + 1)
        # Ctrl+1 / Ctrl+2 are navigation aliases for Up/Down.
        # Ctrl+3 toggles stealth mode. Return single sentinels so the
        # main loop can handle them in one pass instead of chasing
        # _pending state.
        if keycode == 0x1e:
            return '\x80'
        if keycode == 0x1f:
            return '\x81'
        if keycode == 0x20:
            return '\x92'
        return None
    if shift:
        return KEY_MAP_SHIFT.get(keycode, None)
    return KEY_MAP.get(keycode, None)
