# code_engine.py — Coding/Engineering engine for Espelt32
# Number bases, ASCII, data structures, algorithms, string tools,
# regex reference, Python/MicroPython cheatsheet, code editor.
# All display functions return list[str], max ~38 chars per line.


# ────────────────────────────────────────────────────────────────
# 1. NUMBER BASE CONVERSIONS
# ────────────────────────────────────────────────────────────────

_BASES = {'bin': 2, 'oct': 8, 'dec': 10, 'hex': 16}


def _parse_int(s):
    s = s.strip()
    if s.startswith(('0x', '0X')):
        return int(s, 16)
    if s.startswith(('0b', '0B')):
        return int(s, 2)
    if s.startswith(('0o', '0O')):
        return int(s, 8)
    return int(s)


def _to_base(n, base):
    if n == 0:
        return '0'
    digits = []
    neg = n < 0
    n = abs(n)
    while n:
        d = n % base
        digits.append('0123456789ABCDEF'[d])
        n //= base
    if neg:
        digits.append('-')
    return ''.join(reversed(digits))


def _signed8(n):
    v = n & 0xFF
    return v - 256 if v > 127 else v


def _signed16(n):
    v = n & 0xFFFF
    return v - 65536 if v > 32767 else v


def base_convert(value_str, target=None):
    """Convert a number string to base representations."""
    try:
        n = _parse_int(value_str)
    except ValueError:
        return ['Error: invalid number']

    if target:
        t = target.lower()
        if t == 'bin':
            return [f'  {bin(n)}']
        if t == 'oct':
            return [f'  {oct(n)}']
        if t == 'dec':
            return [f'  {str(n)}']
        if t == 'hex':
            return [f'  {hex(n)}']
        return [f'Unknown base: {target}']

    u8 = n & 0xFF
    s8 = _signed8(n)
    u16 = n & 0xFFFF
    s16 = _signed16(n)
    return [
        f'=== {n} ===',
        f'  BIN: {bin(n)}',
        f'  OCT: {oct(n)}',
        f'  DEC: {n}',
        f'  HEX: {hex(n)}',
        f'  U8:  {u8}',
        f'  S8:  {s8}',
        f'  U16: {u16}',
        f'  S16: {s16}',
    ]


def base_between(value_str, from_base_str, to_base_str):
    """Convert from one named base to another."""
    try:
        fb = _BASES.get(from_base_str.lower()) if from_base_str else 10
        tb = _BASES.get(to_base_str.lower()) if to_base_str else 10
        if fb is None:
            fb = int(from_base_str)
        if tb is None:
            tb = int(to_base_str)
        n = int(value_str.strip(), fb)
    except ValueError:
        return ['Error: invalid input or base']
    if tb == 2:
        return [f'  {bin(n)}']
    if tb == 8:
        return [f'  {oct(n)}']
    if tb == 10:
        return [f'  {n}']
    if tb == 16:
        return [f'  {hex(n)}']
    if 2 <= tb <= 16:
        return [f'  {_to_base(n, tb)}']
    return ['Error: base must be 2..16']


# ────────────────────────────────────────────────────────────────
# 2. ASCII TABLE
# ────────────────────────────────────────────────────────────────

_CTRL = {
    0: 'NUL', 1: 'SOH', 2: 'STX', 3: 'ETX', 4: 'EOT',
    5: 'ENQ', 6: 'ACK', 7: 'BEL', 8: 'BS',  9: 'TAB',
    10: 'LF',  11: 'VT',  12: 'FF',  13: 'CR',  14: 'SO',
    15: 'SI',  16: 'DLE', 17: 'DC1', 18: 'DC2', 19: 'DC3',
    20: 'DC4', 21: 'NAK', 22: 'SYN', 23: 'ETB', 24: 'CAN',
    25: 'EM',  26: 'SUB', 27: 'ESC', 28: 'FS',  29: 'GS',
    30: 'RS',  31: 'US',  127: 'DEL',
}


def ascii_lookup_char(ch):
    """Look up a character's ASCII code."""
    if not ch:
        return ['Error: provide a character']
    code = ord(ch[0])
    if code in _CTRL:
        return [f'  {ch[0]} = {code} ({_CTRL[code]})']
    return [f'  {ch[0]} = {code} (0x{code:02X})']


def ascii_lookup_code(code_str):
    """Look up a code value's character."""
    try:
        code = int(code_str)
    except ValueError:
        return ['Error: invalid code']
    if code < 0 or code > 127:
        return ['Error: code must be 0-127']
    if code in _CTRL:
        return [f'  {code} = {_CTRL[code]}']
    if code == 32:
        return ['  32 = SPACE']
    return [f'  {code} = {chr(code)} (0x{code:02X})']


def _ascii_table(start=32, end=126):
    """Return printable ASCII table in lines."""
    lines = [f'=== ASCII {start}-{end} ===']
    for i in range(start, min(end + 1, 127)):
        ch = chr(i)
        line = f'  {i:3d} 0x{i:02X}  {ch}'
        lines.append(line)
    return lines


def ascii_table_range(start_str=None, end_str=None):
    """Printable ASCII table, optional start/end range."""
    s = 32
    e = 126
    if start_str:
        try:
            s = int(start_str)
        except ValueError:
            try:
                s = ord(start_str[0])
            except (IndexError, ValueError):
                pass
    if end_str:
        try:
            e = int(end_str)
        except ValueError:
            try:
                e = ord(end_str[0])
            except (IndexError, ValueError):
                pass
    s = max(0, min(s, 126))
    e = max(s, min(e, 126))
    return _ascii_table(s, e)


# ────────────────────────────────────────────────────────────────
# 3. DATA STRUCTURES REFERENCE
# ────────────────────────────────────────────────────────────────

_DATA_STRUCTURES = [
    ('Array', 'Indexed contiguous memory block',
     ('O(1)', 'O(n)', 'O(n)', 'O(n)', 'O(n)')),
    ('Singly Linked List', 'Nodes with next pointers',
     ('O(n)', 'O(n)', 'O(1)*', 'O(1)*', 'O(n)')),
    ('Doubly Linked List', 'Nodes with prev+next ptrs',
     ('O(n)', 'O(n)', 'O(1)*', 'O(1)*', 'O(n)')),
    ('Stack', 'LIFO -- push/pop from top',
     ('O(n)', 'O(n)', 'O(1)', 'O(1)', 'O(n)')),
    ('Queue', 'FIFO -- enqueue/dequeue ends',
     ('O(n)', 'O(n)', 'O(1)*', 'O(1)*', 'O(n)')),
    ('Hash Table', 'Key-value with hash index',
     ('O(1)*', 'O(1)*', 'O(1)*', 'O(1)*', 'O(n)')),
    ('BST', 'Binary Search Tree (sorted)',
     ('O(h)', 'O(h)', 'O(h)', 'O(h)', 'O(n)')),
    ('Graph', 'Vertices + weighted edges',
     ('O(1)', 'O(V+E)', 'O(1)', 'O(1)', 'O(V+E)')),
]


def data_structures_list():
    """Return data structures as display lines."""
    lines = ['=== Data Structures ===', '',
             '  A=Access Se=Search']
    lines.append('  In=Insert De=Delete Tr=Traverse')
    for name, desc, ops in _DATA_STRUCTURES:
        lines.append(f'')
        lines.append(f'  {name}')
        lines.append(f'    {desc}')
        lines.append(f'    A:{ops[0]} Se:{ops[1]} '
                     f'In:{ops[2]} De:{ops[3]}')
    return lines


def data_structure_detail(name_str):
    """Return detail for a single data structure."""
    target = name_str.strip().lower()
    for name, desc, ops in _DATA_STRUCTURES:
        if target in name.lower():
            return [
                f'=== {name} ===',
                f'  {desc}',
                '',
                '  Time Complexity:',
                f'    Access:    {ops[0]}',
                f'    Search:    {ops[1]}',
                f'    Insert:    {ops[2]}',
                f'    Delete:    {ops[3]}',
                f'    Traverse:  {ops[4]}',
                '',
                '  Space: O(n)',
            ]
    return [f'Unknown: {name_str}']


# ────────────────────────────────────────────────────────────────
# 4. ALGORITHM COMPLEXITY REFERENCE
# ────────────────────────────────────────────────────────────────

_ALGORITHMS = [
    ('Bubble Sort',    'O(n)',   'O(n^2)', 'O(n^2)',  'O(1)'),
    ('Selection Sort', 'O(n^2)', 'O(n^2)', 'O(n^2)',  'O(1)'),
    ('Insertion Sort', 'O(n)',   'O(n^2)', 'O(n^2)',  'O(1)'),
    ('Merge Sort',     'O(n lg n)', 'O(n lg n)', 'O(n lg n)', 'O(n)'),
    ('Quick Sort',     'O(n lg n)', 'O(n lg n)', 'O(n^2)', 'O(lg n)'),
    ('Heap Sort',      'O(n lg n)', 'O(n lg n)', 'O(n lg n)', 'O(1)'),
    ('Counting Sort',  'O(n+k)', 'O(n+k)', 'O(n+k)', 'O(k)'),
    ('Radix Sort',     'O(nk)',  'O(nk)',  'O(nk)',  'O(n+k)'),
    ('Linear Search',  'O(1)',   'O(n)',   'O(n)',   'O(1)'),
    ('Binary Search',  'O(1)',   'O(lg n)','O(lg n)','O(1)'),
    ('Hash Lookup',    'O(1)*',  'O(1)*',  'O(n)',   'O(n)'),
]


def algorithms_list():
    """Return algorithm complexity as display lines."""
    lines = ['=== Algorithm Complexity ===', '']
    for name, best, avg, worst, space in _ALGORITHMS:
        lines.append(f'  {name}')
        lines.append(f'   Best:{best}')
        lines.append(f'   Avg:{avg} Worst:{worst}')
        lines.append(f'   Space:{space}')
    return lines


def algorithm_detail(name_str):
    """Return detail for a single algorithm."""
    target = name_str.strip().lower()
    for name, best, avg, worst, space in _ALGORITHMS:
        if target in name.lower():
            return [
                f'=== {name} ===',
                '',
                f'  Best case:     {best}',
                f'  Average case:  {avg}',
                f'  Worst case:    {worst}',
                f'  Space:         {space}',
                '',
                '  * = amortized',
            ]
    return [f'Unknown algorithm: {name_str}']


# ────────────────────────────────────────────────────────────────
# 5. STRING TOOLS
# ────────────────────────────────────────────────────────────────

def rot13(text):
    """ROT13 cipher."""
    result = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            result.append(chr((o - 65 + 13) % 26 + 65))
        elif 97 <= o <= 122:
            result.append(chr((o - 97 + 13) % 26 + 97))
        else:
            result.append(ch)
    encoded = ''.join(result)
    return [f'  Input:  {text[:30]}', f'  ROT13:  {encoded[:30]}']


def caesar_cipher(text, shift):
    """Caesar cipher with arbitrary shift."""
    shift = int(shift) % 26
    result = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            result.append(chr((o - 65 + shift) % 26 + 65))
        elif 97 <= o <= 122:
            result.append(chr((o - 97 + shift) % 26 + 97))
        else:
            result.append(ch)
    encoded = ''.join(result)
    return [
        f'  Input:   {text[:30]}',
        f'  Shift:   {shift}',
        f'  Encoded: {encoded[:30]}',
    ]


def vigenere_cipher(text, key, decrypt=False):
    """Vigenere cipher encrypt/decrypt."""
    key = key.upper()
    ki = 0
    result = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            k = ord(key[ki % len(key)]) - 65
            if decrypt:
                k = -k
            result.append(chr((o - 65 + k) % 26 + 65))
            ki += 1
        elif 97 <= o <= 122:
            k = ord(key[ki % len(key)]) - 65
            if decrypt:
                k = -k
            result.append(chr((o - 97 + k) % 26 + 97))
            ki += 1
        else:
            result.append(ch)
    encoded = ''.join(result)
    action = 'Decrypted' if decrypt else 'Encrypted'
    return [
        f'  Input:  {text[:30]}',
        f'  Key:    {key}',
        f'  {action}: {encoded[:30]}',
    ]


def text_to_binary(text):
    """Convert text to binary representation."""
    parts = []
    for ch in text:
        n = ord(ch)
        bits = ''
        for i in range(8):
            bits = str(n % 2) + bits
            n >>= 1
        parts.append(bits)
    binary = ' '.join(parts)
    return [
        f'  Text:   {text[:24]}',
        f'  Binary: {binary[:34]}',
        f'  Length: {len(text) * 8} bits',
    ]


def binary_to_text(binary_str):
    """Convert binary string to text."""
    parts = binary_str.strip().split()
    result = []
    for p in parts:
        try:
            result.append(chr(int(p, 2)))
        except ValueError:
            result.append('?')
    text = ''.join(result)
    return [
        f'  Binary: {binary_str[:34]}',
        f'  Text:   {text[:24]}',
    ]


def text_to_hex(text):
    """Convert text to hex representation."""
    hex_chars = '0123456789ABCDEF'
    parts = []
    for ch in text:
        n = ord(ch)
        hi = hex_chars[n // 16]
        lo = hex_chars[n % 16]
        parts.append(hi + lo)
    hex_str = ' '.join(parts)
    return [
        f'  Text: {text[:28]}',
        f'  Hex:  {hex_str[:34]}',
    ]


def hex_to_text(hex_str):
    """Convert hex string to text."""
    parts = hex_str.strip().split()
    result = []
    for p in parts:
        try:
            result.append(chr(int(p, 16)))
        except ValueError:
            result.append('?')
    text = ''.join(result)
    return [
        f'  Hex:  {hex_str[:34]}',
        f'  Text: {text[:28]}',
    ]


def binary_and(a, b):
    """Bitwise AND."""
    r = a & b
    return [f'  {a} AND {b} = {r}', f'  BIN: {bin(r)}']


def binary_or(a, b):
    """Bitwise OR."""
    r = a | b
    return [f'  {a} OR {b} = {r}', f'  BIN: {bin(r)}']


def binary_xor(a, b):
    """Bitwise XOR."""
    r = a ^ b
    return [f'  {a} XOR {b} = {r}', f'  BIN: {bin(r)}']


def binary_not(a):
    """Bitwise NOT."""
    r = ~a & 0xFFFFFFFF
    return [f'  NOT {a} = {r}', f'  BIN: {bin(r)}']


def binary_lshift(a, n):
    """Left shift."""
    r = a << n
    return [f'  {a} << {n} = {r}', f'  BIN: {bin(r)}']


def binary_rshift(a, n):
    """Right shift."""
    r = a >> n
    return [f'  {a} >> {n} = {r}', f'  BIN: {bin(r)}']


def count_bits(n):
    """Count set bits in a number."""
    orig = int(n)
    n = abs(orig)
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return [f'  Value: {orig}', f'  Set bits: {count}', f'  BIN: {bin(orig)}']


# ── Number Theory ────────────────────────────────────

def is_prime(n):
    """Check if a number is prime."""
    n = int(n)
    if n < 2:
        return [f'  {n} is not prime']
    if n < 4:
        return [f'  {n} is prime']
    if n % 2 == 0 or n % 3 == 0:
        return [f'  {n} is not prime']
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return [f'  {n} is not prime']
        i += 6
    return [f'  {n} is prime']


def prime_factors(n):
    """Find prime factors of a number."""
    n = int(n)
    if n < 2:
        return [f'  No prime factors for {n}']
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    factor_str = ' × '.join(str(f) for f in factors)
    return [f'  {int(n * (factors[0] if factors else 1))} = {factor_str}' if factors else f'  {n}']


def all_factors(n):
    """Find all factors of a number."""
    n = abs(int(n))
    factors = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    factors.sort()
    return [f'  Factors of {n}: {", ".join(str(f) for f in factors)}']


def gcd_list(numbers):
    """GCD of a list of numbers."""
    def _gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    result = int(numbers[0])
    for n in numbers[1:]:
        result = _gcd(result, int(n))
    return [f'  GCD: {result}']


def lcm_list(numbers):
    """LCM of a list of numbers."""
    def _gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    def _lcm(a, b):
        return abs(a * b) // _gcd(a, b) if a and b else 0
    result = int(numbers[0])
    for n in numbers[1:]:
        result = _lcm(result, int(n))
    return [f'  LCM: {result}']


# ── Roman Numerals ───────────────────────────────────

_ROMAN_VALS = [
    (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
    (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
]


def int_to_roman(n):
    """Convert integer to Roman numeral."""
    n = int(n)
    if n < 1 or n > 3999:
        return ['Error: range 1-3999']
    result = []
    for val, sym in _ROMAN_VALS:
        while n >= val:
            result.append(sym)
            n -= val
    return [f'  {int(n)} = {"".join(result)}']


def roman_to_int(s):
    """Convert Roman numeral to integer."""
    s = s.upper()
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev = 0
    for ch in reversed(s):
        val = roman_map.get(ch, 0)
        if val < prev:
            result -= val
        else:
            result += val
        prev = val
    return [f'  {s} = {result}']


# ── Hash Functions ───────────────────────────────────

def hash_md5(text):
    """MD5 hash of text (pure Python implementation)."""
    try:
        import uhashlib
        h = uhashlib.md5(text.encode())
        digest = ''.join('{:02x}'.format(b) for b in h.digest())
        return [f'  MD5({text[:20]}):', f'  {digest}']
    except ImportError:
        pass
    try:
        import hashlib
        digest = hashlib.md5(text.encode()).hexdigest()
        return [f'  MD5({text[:20]}):', f'  {digest}']
    except ImportError:
        return ['Error: no hash library available']


def hash_sha256(text):
    """SHA-256 hash of text."""
    try:
        import uhashlib
        h = uhashlib.sha256(text.encode())
        digest = ''.join('{:02x}'.format(b) for b in h.digest())
        return [f'  SHA256({text[:20]}):', f'  {digest}']
    except ImportError:
        pass
    try:
        import hashlib
        digest = hashlib.sha256(text.encode()).hexdigest()
        return [f'  SHA256({text[:20]}):', f'  {digest}']
    except ImportError:
        return ['Error: no hash library available']


def hash_sha1(text):
    """SHA-1 hash of text."""
    try:
        import uhashlib
        h = uhashlib.sha1(text.encode())
        digest = ''.join('{:02x}'.format(b) for b in h.digest())
        return [f'  SHA1({text[:20]}):', f'  {digest}']
    except ImportError:
        pass
    try:
        import hashlib
        digest = hashlib.sha1(text.encode()).hexdigest()
        return [f'  SHA1({text[:20]}):', f'  {digest}']
    except ImportError:
        return ['Error: no hash library available']


# ────────────────────────────────────────────────────────────────
# 6. MORSE CODE
# ────────────────────────────────────────────────────────────────

_MORSE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    ' ': '/',
}
_MORSE_REV = {v: k for k, v in _MORSE.items() if k != ' '}


def morse_encode(text):
    """Encode text to Morse code."""
    parts = []
    for ch in text.upper():
        code = _MORSE.get(ch)
        if code:
            parts.append(code)
        else:
            parts.append('?')
    result = ' '.join(parts)
    return [f'  Input: {text[:20]}', f'  Morse: {result[:30]}']


def morse_decode(code):
    """Decode Morse code to text."""
    parts = code.strip().split(' ')
    result = []
    for p in parts:
        if p == '/':
            result.append(' ')
        elif p in _MORSE_REV:
            result.append(_MORSE_REV[p])
        else:
            result.append('?')
    decoded = ''.join(result)
    return [f'  Morse: {code[:30]}', f'  Text:  {decoded[:30]}']


def morse_reference():
    """Return Morse code reference table."""
    lines = ['=== Morse Code ===', '', '  Letters:']
    row = '  '
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        entry = f'{ch}={_MORSE[ch]}'
        if len(row) + len(entry) + 1 > 36:
            lines.append(row)
            row = '  '
        row += entry + ' '
    if row.strip():
        lines.append(row)
    lines.append('')
    lines.append('  Numbers:')
    row = '  '
    for ch in '0123456789':
        entry = f'{ch}={_MORSE[ch]}'
        if len(row) + len(entry) + 1 > 36:
            lines.append(row)
            row = '  '
        row += entry + ' '
    if row.strip():
        lines.append(row)
    return lines


# ────────────────────────────────────────────────────────────────
# 7. BASE64
# ────────────────────────────────────────────────────────────────

def base64_encode(text):
    """Base64 encode text."""
    try:
        import ubinascii
        encoded = ubinascii.b2a_base64(text.encode()).decode().strip()
        return [f'  Input:   {text[:28]}', f'  Base64:  {encoded[:28]}']
    except ImportError:
        return ['Error: ubinascii not available']


def base64_decode(data):
    """Base64 decode data."""
    try:
        import ubinascii
        decoded = ubinascii.a2b_base64(data).decode()
        return [f'  Base64: {data[:28]}', f'  Text:   {decoded[:28]}']
    except Exception:
        return ['Error: invalid base64 data']


# ────────────────────────────────────────────────────────────────
# 8. REGEX REFERENCE
# ────────────────────────────────────────────────────────────────

_REGEX_PATTERNS = [
    ('Email',    r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'),
    ('Phone US', r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
    ('URL',      r'https?://[^\s]+'),
    ('IPv4',     r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
    ('Hex Color',r'#[0-9a-fA-F]{6}'),
    ('Date',     r'\d{4}-\d{2}-\d{2}'),
    ('Time 24h', r'\d{2}:\d{2}(:\d{2})?'),
    ('ZIP/Post', r'\d{5}(-\d{4})?'),
    ('UUID',     r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
]

_REGEX_META = [
    ('.',   'Any char except newline'),
    ('*',   'Zero or more'),
    ('+',   'One or more'),
    ('?',   'Zero or one (optional)'),
    ('[]',  'Character class'),
    ('()',  'Capture group'),
    ('{}',  'Repeat count: {n} or {n,m}'),
    ('^',   'Start of string/line'),
    ('$',   'End of string/line'),
    ('|',   'OR alternation'),
    ('\\',  'Escape special char'),
    ('\\d', 'Digit [0-9]'),
    ('\\w', 'Word char [a-zA-Z0-9_]'),
    ('\\s', 'Whitespace space/tab'),
    ('\\b', 'Word boundary'),
    ('[^x]','Negated class'),
]


def regex_patterns_list():
    """Return regex pattern reference."""
    lines = ['=== Regex Patterns ===', '']
    for name, pattern in _REGEX_PATTERNS:
        if len(pattern) > 30:
            lines.append(f'  {name}:')
            lines.append(f'   {pattern[:34]}')
        else:
            lines.append(f'  {name}: {pattern}')
    return lines


def regex_metachars():
    """Return regex metacharacter reference."""
    lines = ['=== Regex Metachars ===', '']
    for char, desc in _REGEX_META:
        lines.append(f'  {char:<6s} {desc}')
    return lines


# ────────────────────────────────────────────────────────────────
# 9. PYTHON / MICROPYTHON CHEATSHEET
# ────────────────────────────────────────────────────────────────

_PYTHON_SYNTAX = [
    ('Control Flow', [
        'if x > 0:',
        '    pass',
        'elif x == 0:',
        '    pass',
        'else:',
        '    pass',
    ]),
    ('For Loop', [
        'for i in range(10):',
        '    pass',
        'for i, v in enumerate(lst):',
        '    pass',
        'for k, v in d.items():',
        '    pass',
    ]),
    ('While Loop', [
        'while cond:',
        '    break',
        '    continue',
    ]),
    ('Functions', [
        'def func(a, b=0):',
        '    return a + b',
        'lambda x: x * 2',
    ]),
    ('Classes', [
        'class Foo:',
        '    def __init__(self):',
        '        self.x = 0',
        '    def method(self):',
        '        pass',
    ]),
    ('Try/Except', [
        'try:',
        '    x = 1 / 0',
        'except ValueError:',
        '    pass',
        'except Exception as e:',
        '    print(e)',
        'finally:',
        '    cleanup()',
    ]),
    ('List Comprehension', [
        'squares = [x*x for x in r]',
        'evens = [x for x in r if x%2==0]',
    ]),
    ('Dict Comprehension', [
        'd = {k: v for k, v in pairs}',
    ]),
    ('Slicing', [
        'lst[1:3]   # index 1,2',
        'lst[::2]   # every 2nd',
        'lst[::-1]  # reversed',
    ]),
]

_PYTHON_BUILTINS = [
    ('len(x)',     'Length'),
    ('range(n)',   'Int seq 0..n-1'),
    ('int(x)',     'To integer'),
    ('str(x)',     'To string'),
    ('float(x)',   'To float'),
    ('bool(x)',    'To boolean'),
    ('list(x)',    'To list'),
    ('dict(x)',    'To dict'),
    ('tuple(x)',   'To tuple'),
    ('set(x)',     'To set'),
    ('print(x)',   'Print stdout'),
    ('input()',    'Read stdin'),
    ('abs(x)',     'Absolute val'),
    ('min(x)',     'Minimum'),
    ('max(x)',     'Maximum'),
    ('sum(x)',     'Sum'),
    ('sorted(x)',  'Sorted list'),
    ('reversed(x)', 'Reversed'),
    ('enumerate(x)', '(i,item) pairs'),
    ('zip(a,b)',   'Pair iterables'),
    ('map(fn,x)',  'Apply fn'),
    ('filter(fn,x)', 'Filter'),
    ('isinstance(x,T)', 'Type check'),
    ('hasattr(x,n)', 'Attr exists?'),
    ('getattr(x,n)', 'Get attr'),
    ('id(x)',      'Identity'),
    ('type(x)',    'Type'),
    ('repr(x)',    'Repr'),
    ('hex(x)',     'Hex str'),
    ('oct(x)',     'Oct str'),
    ('bin(x)',     'Bin str'),
    ('chr(i)',     'Int->char'),
    ('ord(c)',     'Char->int'),
]

_MICROPYTHON_IMPORTS = [
    ('machine',  'Pin, PWM, ADC, I2C'),
    ('time',     'sleep, ticks_ms'),
    ('os',       'listdir, stat, mkdir'),
    ('random',   'randint, choice'),
    ('math',     'pi, sqrt, sin, cos'),
    ('json',     'dumps, loads'),
    ('sys',      'platform, exit'),
    ('gc',       'mem_free, collect'),
    ('network',  'WLAN, STA_IF'),
    ('socket',   'socket, getaddrinfo'),
    ('_thread',  'start_new_thread'),
    ('ubinascii', 'hexlify, base64'),
    ('uctypes',  'sizeof, addressof'),
    ('micropython', 'opt_level, const'),
    ('struct',   'pack, unpack'),
]


def python_syntax_list():
    """Return Python syntax cheat sheet."""
    lines = ['=== Python Syntax ===', '']
    for section, examples in _PYTHON_SYNTAX:
        lines.append(f'  -- {section} --')
        for ex in examples:
            lines.append(f'    {ex}')
        lines.append('')
    return lines


def python_builtins_list():
    """Return Python builtins cheat sheet."""
    lines = ['=== Python Builtins ===', '']
    for func, desc in _PYTHON_BUILTINS:
        lines.append(f'  {func}  {desc}')
    return lines


def micropython_imports_list():
    """Return MicroPython imports cheat sheet."""
    lines = ['=== MicroPython Imports ===', '']
    for module, items in _MICROPYTHON_IMPORTS:
        lines.append(f'  {module}  {items}')
    return lines


# ────────────────────────────────────────────────────────────────
# 10. CODE EXAMPLES
# ────────────────────────────────────────────────────────────────

_CODE_EXAMPLES = {
    'fibonacci': [
        'def fib(n):',
        '    a, b = 0, 1',
        '    for _ in range(n):',
        '        a, b = b, a+b',
        '    return a',
        '',
        'print(fib(10))  # 55',
    ],
    'factorial': [
        'def factorial(n):',
        '    r = 1',
        '    for i in range(2, n+1):',
        '        r *= i',
        '    return r',
        '',
        'print(factorial(5))  # 120',
    ],
    'fizzbuzz': [
        'for i in range(1, 101):',
        '    if i % 15 == 0:',
        '        print("FizzBuzz")',
        '    elif i % 3 == 0:',
        '        print("Fizz")',
        '    elif i % 5 == 0:',
        '        print("Buzz")',
        '    else:',
        '        print(i)',
    ],
    'palindrome': [
        'def is_palindrome(s):',
        '    s = s.lower()',
        '    return s == s[::-1]',
        '',
        'print(is_palindrome("racecar"))',
        'print(is_palindrome("hello"))',
    ],
    'sort': [
        'def bubble_sort(lst):',
        '    n = len(lst)',
        '    for i in range(n):',
        '        for j in range(n-i-1):',
        '            if lst[j] > lst[j+1]:',
        '                lst[j], lst[j+1]',
        '                = lst[j+1], lst[j]',
        '    return lst',
    ],
    'binary_search': [
        'def bsearch(lst, val):',
        '    lo, hi = 0, len(lst)-1',
        '    while lo <= hi:',
        '        mid = (lo+hi)//2',
        '        if lst[mid] == val:',
        '            return mid',
        '        elif lst[mid] < val:',
        '            lo = mid+1',
        '        else:',
        '            hi = mid-1',
        '    return -1',
    ],
    'quicksort': [
        'def quicksort(lst):',
        '    if len(lst) <= 1:',
        '        return lst',
        '    pivot = lst[len(lst)//2]',
        '    left = [x for x in lst if x < pivot]',
        '    mid = [x for x in lst if x == pivot]',
        '    right = [x for x in lst if x > pivot]',
        '    return quicksort(left) + mid + quicksort(right)',
    ],
    'mergesort': [
        'def mergesort(lst):',
        '    if len(lst) <= 1:',
        '        return lst',
        '    mid = len(lst) // 2',
        '    left = mergesort(lst[:mid])',
        '    right = mergesort(lst[mid:])',
        '    return merge(left, right)',
        '',
        'def merge(l, r):',
        '    result = []',
        '    i = j = 0',
        '    while i < len(l) and j < len(r):',
        '        if l[i] <= r[j]:',
        '            result.append(l[i]); i += 1',
        '        else:',
        '            result.append(r[j]); j += 1',
        '    return result + l[i:] + r[j:]',
    ],
    'linked_list': [
        'class Node:',
        '    def __init__(self, data):',
        '        self.data = data',
        '        self.next = None',
        '',
        'class LinkedList:',
        '    def __init__(self):',
        '        self.head = None',
        '    def append(self, data):',
        '        n = Node(data)',
        '        if not self.head:',
        '            self.head = n',
        '            return',
        '        cur = self.head',
        '        while cur.next:',
        '            cur = cur.next',
        '        cur.next = n',
    ],
    'hash_table': [
        'class HashTable:',
        '    def __init__(self, size=64):',
        '        self.size = size',
        '        self.table = [[] for _ in range(size)]',
        '',
        '    def _hash(self, key):',
        '        return hash(key) % self.size',
        '',
        '    def set(self, key, val):',
        '        h = self._hash(key)',
        '        for i, (k, v) in enumerate(self.table[h]):',
        '            if k == key:',
        '                self.table[h][i] = (key, val)',
        '                return',
        '        self.table[h].append((key, val))',
        '',
        '    def get(self, key):',
        '        h = self._hash(key)',
        '        for k, v in self.table[h]:',
        '            if k == key:',
        '                return v',
        '        raise KeyError(key)',
    ],
    'bfs': [
        'from collections import deque',
        '',
        'def bfs(graph, start):',
        '    visited = set([start])',
        '    queue = deque([start])',
        '    order = []',
        '    while queue:',
        '        node = queue.popleft()',
        '        order.append(node)',
        '        for neighbor in graph[node]:',
        '            if neighbor not in visited:',
        '                visited.add(neighbor)',
        '                queue.append(neighbor)',
        '    return order',
    ],
    'dfs': [
        'def dfs(graph, start, visited=None):',
        '    if visited is None:',
        '        visited = set()',
        '    visited.add(start)',
        '    order = [start]',
        '    for neighbor in graph[start]:',
        '        if neighbor not in visited:',
        '            order.extend(dfs(graph, neighbor, visited))',
        '    return order',
    ],
    'dijkstra': [
        'import heapq',
        '',
        'def dijkstra(graph, start):',
        '    dist = {v: float("inf") for v in graph}',
        '    dist[start] = 0',
        '    pq = [(0, start)]',
        '    while pq:',
        '        d, u = heapq.heappop(pq)',
        '        if d > dist[u]:',
        '            continue',
        '        for v, w in graph[u].items():',
        '            if dist[u] + w < dist[v]:',
        '                dist[v] = dist[u] + w',
        '                heapq.heappush(pq, (dist[v], v))',
        '    return dist',
    ],
    'tree': [
        'class TreeNode:',
        '    def __init__(self, val):',
        '        self.val = val',
        '        self.left = None',
        '        self.right = None',
        '',
        'def inorder(node):',
        '    if node:',
        '        yield from inorder(node.left)',
        '        yield node.val',
        '        yield from inorder(node.right)',
    ],
    'graph_basics': [
        'graph = {}',
        '',
        'def add_edge(g, u, v):',
        '    g.setdefault(u, []).append(v)',
        '    g.setdefault(v, []).append(u)',
        '',
        'add_edge(graph, "A", "B")',
        'add_edge(graph, "A", "C")',
        'add_edge(graph, "B", "D")',
        '',
        'for node, edges in graph.items():',
        '    print(f"{node}: {edges}")',
    ],
    'bit_manipulation': [
        '# Check if power of 2',
        'def is_pow2(n):',
        '    return n > 0 and (n & (n-1)) == 0',
        '',
        '# Count set bits',
        'def popcount(n):',
        '    c = 0',
        '    while n:',
        '        c += n & 1',
        '        n >>= 1',
        '    return c',
        '',
        '# Swap without temp',
        'a, b = 5, 3',
        'a ^= b; b ^= a; a ^= b',
    ],
    'string_algorithms': [
        '# KMP pattern matching',
        'def kmp_search(text, pat):',
        '    n, m = len(text), len(pat)',
        '    lps = [0] * m',
        '    j = 0',
        '    for i in range(1, m):',
        '        while j and pat[i] != pat[j]:',
        '            j = lps[j-1]',
        '        if pat[i] == pat[j]:',
        '            j += 1',
        '        lps[i] = j',
        '    results = []',
        '    j = 0',
        '    for i in range(n):',
        '        while j and text[i] != pat[j]:',
        '            j = lps[j-1]',
        '        if text[i] == pat[j]:',
        '            j += 1',
        '        if j == m:',
        '            results.append(i - m + 1)',
        '            j = lps[j-1]',
        '    return results',
    ],
}


def examples_list():
    """Return list of available code examples."""
    lines = ['=== Code Examples ===', '']
    for name in _CODE_EXAMPLES:
        lines.append(f'  {name}')
    return lines


def example_detail(name):
    """Return a code example by name."""
    key = name.strip().lower()
    if key in _CODE_EXAMPLES:
        lines = [f'=== {key} ===', '']
        for line in _CODE_EXAMPLES[key]:
            lines.append(f'  {line}')
        return lines
    return [f'Unknown example: {name}']


# ────────────────────────────────────────────────────────────────
# 11. MICROPYTHON HARDWARE QUICK REFERENCE
# ────────────────────────────────────────────────────────────────

_MP_REF = [
    ('Pin', [
        'from machine import Pin',
        'led = Pin(2, Pin.OUT)',
        'led.value(1)',
        'btn = Pin(0, Pin.IN, Pin.PULL_UP)',
        'val = btn.value()',
    ]),
    ('PWM', [
        'from machine import Pin, PWM',
        'pwm = PWM(Pin(2), freq=1000)',
        'pwm.duty(512)  # 0-1023',
        'pwm.deinit()',
    ]),
    ('ADC', [
        'from machine import Pin, ADC',
        'adc = ADC(Pin(34))',
        'adc.atten(ADC.ATTN_11DB)',
        'val = adc.read()  # 0-4095',
    ]),
    ('I2C', [
        'from machine import I2C, Pin',
        'i2c = I2C(0, sda=Pin(21),',
        '          scl=Pin(22), freq=400000)',
        'devices = i2c.scan()',
        'i2c.writeto(addr, b"\\x00")',
        'data = i2c.readfrom(addr, 2)',
    ]),
    ('SPI', [
        'from machine import SPI, Pin',
        'spi = SPI(1, baudrate=1000000)',
        'cs = Pin(5, Pin.OUT)',
        'cs.value(0)',
        'spi.write(b"\\x01\\x02")',
        'cs.value(1)',
    ]),
    ('UART', [
        'from machine import UART',
        'uart = UART(1, 9600)',
        'uart.write("Hello")',
        'data = uart.read(10)',
    ]),
    ('Sleep', [
        'import time',
        'time.sleep(1)      # seconds',
        'time.sleep_ms(500) # millis',
        'time.sleep_us(100) # micros',
        'time.ticks_ms()    # tick ms',
    ]),
    ('Deepsleep', [
        'import machine',
        'machine.deepsleep(10000)',
        '  # sleep 10s, reset on wake',
        'machine.reset()',
        'machine.freq()  # CPU freq',
    ]),
    ('Memory', [
        'import gc',
        'gc.mem_free()  # free bytes',
        'gc.mem_alloc() # used bytes',
        'gc.collect()   # run GC',
        'import micropython',
        'micropython.mem_info()',
    ]),
    ('IRQ', [
        'from machine import Pin',
        'def handler(pin):',
        '    print("IRQ")',
        'pin = Pin(0, Pin.IN)',
        'pin.irq(handler)',
        '',
        'import machine',
        'machine.disable_irq()',
        'machine.enable_irq()',
    ]),
]


def mp_reference_list():
    """Return MicroPython hardware reference index."""
    lines = ['=== MicroPython Ref ===', '']
    for name, _ in _MP_REF:
        lines.append(f'  {name}')
    return lines


def mp_reference_detail(name):
    """Return detail for a MicroPython hardware topic."""
    target = name.strip().lower()
    for name_key, examples in _MP_REF:
        if target in name_key.lower():
            lines = [f'=== {name_key} ===', '']
            for ex in examples:
                lines.append(f'  {ex}')
            return lines
    return [f'Unknown topic: {name}']


# ────────────────────────────────────────────────────────────────
# 12. CODE EDITOR STATE MANAGEMENT
# ────────────────────────────────────────────────────────────────

_SCRIPTS_DIR = '/sd/scripts'


def _ensure_scripts_dir():
    """Create scripts directory if it doesn't exist.
    Returns True if directory is ready, False otherwise."""
    try:
        import os
        try:
            os.stat(_SCRIPTS_DIR)
            return True
        except OSError:
            # Try building path from root
            try:
                os.stat('/sd')
            except OSError:
                return False
            os.mkdir(_SCRIPTS_DIR)
            return True
    except ImportError:
        return False


def code_new(name):
    """Create a new script editor state.
    Returns the state dict."""
    return {
        'name': name.strip(),
        'lines': [],
        'modified': False,
    }


def code_add_line(state, line):
    """Add a line to the current script.
    Returns updated state dict."""
    state['lines'].append(line)
    state['modified'] = True
    return state


def code_get_lines(state):
    """Get current script lines from state."""
    return list(state['lines'])


def code_save(state):
    """Save script to /sd/scripts/<name>.py.
    Returns display lines."""
    if not _ensure_scripts_dir():
        return ['Error: /sd not available']
    name = state['name']
    path = f'{_SCRIPTS_DIR}/{name}.py'
    try:
        f = open(path, 'w')
        for line in state['lines']:
            f.write(line + '\n')
        f.close()
        state['modified'] = False
        n = len(state['lines'])
        return [
            f'  Saved: {name}.py',
            f'  Lines: {n}',
        ]
    except OSError as e:
        return [f'Error: {e}']


def code_load(name):
    """Load script from /sd/scripts/<name>.py.
    Returns (state, display_lines) or (None, error_lines)."""
    if not _ensure_scripts_dir():
        return None, ['Error: /sd not available']
    name = name.strip()
    path = f'{_SCRIPTS_DIR}/{name}.py'
    try:
        f = open(path, 'r')
        lines = []
        for line in f:
            lines.append(line.rstrip('\n'))
        f.close()
        state = {
            'name': name,
            'lines': lines,
            'modified': False,
        }
        n = len(lines)
        display = [
            f'  Loaded: {name}.py',
            f'  Lines: {n}',
        ]
        return state, display
    except OSError:
        return None, [f'Error: {name}.py not found']


def code_list():
    """List all scripts in /sd/scripts/.
    Returns display lines."""
    if not _ensure_scripts_dir():
        return ['  (sd card not available)']
    try:
        import os
        files = os.listdir(_SCRIPTS_DIR)
        py_files = [f for f in files if f.endswith('.py')]
        if not py_files:
            return ['  (no scripts saved)']
        lines = [f'=== Scripts ({len(py_files)}) ===', '']
        for f in sorted(py_files):
            lines.append(f'  {f}')
        return lines
    except (ImportError, OSError):
        return ['  (unable to list scripts)']


def code_delete(name):
    """Delete a script from /sd/scripts/.
    Returns display lines."""
    if not _ensure_scripts_dir():
        return ['Error: /sd not available']
    name = name.strip()
    path = f'{_SCRIPTS_DIR}/{name}.py'
    try:
        import os
        os.remove(path)
        return [f'  Deleted: {name}.py']
    except OSError:
        return [f'Error: {name}.py not found']


def code_run(name):
    """Execute a script from /sd/scripts/<name>.py.
    Returns display lines with result."""
    if not _ensure_scripts_dir():
        return ['Error: /sd not available']
    name = name.strip()
    path = f'{_SCRIPTS_DIR}/{name}.py'
    try:
        f = open(path, 'r')
        source = f.read()
        f.close()
    except OSError:
        return [f'Error: {name}.py not found']

    try:
        code = compile(source, name, 'exec')
        exec(code)
        return ['OK']
    except Exception as e:
        err = str(e)
        lines = []
        lines.append(f'Error: {type(e).__name__}')
        for i in range(0, len(err), 40):
            lines.append(err[i:i+40])
        return lines


def code_clear():
    """Clear current editor state.
    Returns fresh state dict."""
    return {
        'name': '',
        'lines': [],
        'modified': False,
    }


# ────────────────────────────────────────────────────────────────
# 13. MENU / TOP-LEVEL DISPATCH
# ────────────────────────────────────────────────────────────────

def code_menu():
    """Return the top-level menu for the coding engine."""
    return [
        '=== Code Engine ===', '',
        '  code base <num> [base]',
        '  code bases <num> <from> <to>',
        '  code ascii <char|code>',
        '  code asciitable [s] [e]',
        '  code ds [name]',
        '  code algo [name]',
        '  code rot13 <text>',
        '  code caesar <text> <n>',
        '  code vigenere <text> <key>',
        '  code vdec <text> <key>',
        '  code morse enc|dec <text>',
        '  code morse ref',
        '  code b64 enc|dec <text>',
        '  --- Text Conversions ---',
        '  code tobinary <text>',
        '  code frombinary <bits>',
        '  code tohex <text>',
        '  code fromhex <hex>',
        '  --- Binary Operations ---',
        '  code and <a> <b>',
        '  code or <a> <b>',
        '  code xor <a> <b>',
        '  code not <a>',
        '  code lshift <a> <n>',
        '  code rshift <a> <n>',
        '  code bits <n>',
        '  --- Number Theory ---',
        '  code prime <n>',
        '  code factors <n>',
        '  code allfactors <n>',
        '  code gcd <a> <b>',
        '  code lcm <a> <b>',
        '  --- Roman Numerals ---',
        '  code roman <n|numeral>',
        '  --- Hash ---',
        '  code md5 <text>',
        '  code sha1 <text>',
        '  code sha256 <text>',
        '  --- Regex ---',
        '  code regex patterns',
        '  code regex metachars',
        '  --- Python Ref ---',
        '  code syntax',
        '  code functions',
        '  code libraries',
        '  code examples [name]',
        '  code mp [topic]',
        '  --- Code Editor ---',
        '  code edit new <name>',
        '  code edit add <line>',
        '  code edit lines',
        '  code edit save',
        '  code edit load <name>',
        '  code edit list',
        '  code edit delete <name>',
        '  code edit run <name>',
        '  code edit clear',
    ]


def code_dispatch(args):
    """Top-level dispatcher for code commands.
    Returns list of display lines."""
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return code_menu()

    cmd = parts[0].lower()
    rest = parts[1:]

    # --- Base conversions ---
    if cmd == 'base' or cmd == 'convert':
        if not rest:
            return ['Usage: code base <num> [bin|oct|dec|hex]']
        target = rest[1] if len(rest) > 1 else None
        return base_convert(rest[0], target)

    if cmd == 'bases' or cmd == 'between':
        if len(rest) < 3:
            return ['Usage: code bases <num> <from> <to>']
        return base_between(rest[0], rest[1], rest[2])

    # --- ASCII ---
    if cmd == 'ascii':
        if not rest:
            return ['Usage: code ascii <char|code>']
        val = rest[0]
        if val.isdigit():
            return ascii_lookup_code(val)
        return ascii_lookup_char(val)

    if cmd == 'asciitable':
        s = rest[0] if rest else None
        e = rest[1] if len(rest) > 1 else None
        return ascii_table_range(s, e)

    # --- Data structures ---
    if cmd in ('ds', 'struct', 'datastruct'):
        if not rest:
            return data_structures_list()
        return data_structure_detail(rest[0])

    # --- Algorithms ---
    if cmd in ('algo', 'algorithm'):
        if not rest:
            return algorithms_list()
        return algorithm_detail(rest[0])

    # --- String tools ---
    if cmd == 'rot13':
        text = ' '.join(rest) if rest else ''
        return rot13(text)

    if cmd == 'caesar':
        if len(rest) < 2:
            return ['Usage: code caesar <text> <shift>']
        shift = rest[-1]
        text = ' '.join(rest[:-1])
        try:
            return caesar_cipher(text, int(shift))
        except ValueError:
            return ['Error: shift must be a number']

    if cmd == 'vigenere':
        if len(rest) < 2:
            return ['Usage: code vigenere <text> <key>']
        key = rest[-1]
        text = ' '.join(rest[:-1])
        return vigenere_cipher(text, key)

    if cmd == 'vdec':
        if len(rest) < 2:
            return ['Usage: code vdec <text> <key>']
        key = rest[-1]
        text = ' '.join(rest[:-1])
        return vigenere_cipher(text, key, decrypt=True)

    if cmd == 'morse':
        if not rest:
            return morse_reference()
        action = rest[0].lower()
        text = ' '.join(rest[1:]) if len(rest) > 1 else ''
        if action in ('enc', 'encode'):
            return morse_encode(text)
        if action in ('dec', 'decode'):
            return morse_decode(text)
        if action in ('ref', 'reference'):
            return morse_reference()
        return morse_encode(' '.join(rest))

    if cmd in ('b64', 'base64'):
        if len(rest) < 2:
            return [
                'Usage: code b64 enc <text>',
                '       code b64 dec <data>',
            ]
        action = rest[0].lower()
        data = ' '.join(rest[1:])
        if action in ('enc', 'encode'):
            return base64_encode(data)
        if action in ('dec', 'decode'):
            return base64_decode(data)
        return ['Usage: code b64 enc|dec <text>']

    # --- Text Conversions ---
    if cmd == 'tobinary':
        text = ' '.join(rest) if rest else ''
        return text_to_binary(text)

    if cmd == 'frombinary':
        return binary_to_text(' '.join(rest) if rest else '')

    if cmd == 'tohex':
        text = ' '.join(rest) if rest else ''
        return text_to_hex(text)

    if cmd == 'fromhex':
        return hex_to_text(' '.join(rest) if rest else '')

    # --- Binary Operations ---
    if cmd == 'and' and len(rest) >= 2:
        try:
            return binary_and(int(rest[0]), int(rest[1]))
        except ValueError:
            return ['Error: need two numbers']

    if cmd == 'or' and len(rest) >= 2:
        try:
            return binary_or(int(rest[0]), int(rest[1]))
        except ValueError:
            return ['Error: need two numbers']

    if cmd == 'xor' and len(rest) >= 2:
        try:
            return binary_xor(int(rest[0]), int(rest[1]))
        except ValueError:
            return ['Error: need two numbers']

    if cmd == 'not' and len(rest) >= 1:
        try:
            return binary_not(int(rest[0]))
        except ValueError:
            return ['Error: need a number']

    if cmd == 'lshift' and len(rest) >= 2:
        try:
            return binary_lshift(int(rest[0]), int(rest[1]))
        except ValueError:
            return ['Error: need two numbers']

    if cmd == 'rshift' and len(rest) >= 2:
        try:
            return binary_rshift(int(rest[0]), int(rest[1]))
        except ValueError:
            return ['Error: need two numbers']

    if cmd == 'bits' and len(rest) >= 1:
        try:
            return count_bits(int(rest[0]))
        except ValueError:
            return ['Error: need a number']

    # --- Number Theory ---
    if cmd == 'prime' and len(rest) >= 1:
        try:
            return is_prime(rest[0])
        except ValueError:
            return ['Error: need a number']

    if cmd == 'factors' and len(rest) >= 1:
        try:
            return prime_factors(rest[0])
        except ValueError:
            return ['Error: need a number']

    if cmd == 'allfactors' and len(rest) >= 1:
        try:
            return all_factors(rest[0])
        except ValueError:
            return ['Error: need a number']

    if cmd == 'gcd' and len(rest) >= 2:
        try:
            return gcd_list([rest[0], rest[1]])
        except ValueError:
            return ['Error: need two numbers']

    if cmd == 'lcm' and len(rest) >= 2:
        try:
            return lcm_list([rest[0], rest[1]])
        except ValueError:
            return ['Error: need two numbers']

    # --- Roman Numerals ---
    if cmd == 'roman' and len(rest) >= 1:
        val = rest[0]
        if val.isdigit():
            return int_to_roman(val)
        return roman_to_int(val)

    # --- Hash ---
    if cmd == 'md5':
        text = ' '.join(rest) if rest else ''
        return hash_md5(text)

    if cmd == 'sha1':
        text = ' '.join(rest) if rest else ''
        return hash_sha1(text)

    if cmd == 'sha256':
        text = ' '.join(rest) if rest else ''
        return hash_sha256(text)

    # --- Regex ---
    if cmd == 'regex':
        sub = rest[0].lower() if rest else ''
        if sub in ('pat', 'patterns', 'pattern'):
            return regex_patterns_list()
        if sub in ('meta', 'metachars', 'ref'):
            return regex_metachars()
        return regex_patterns_list() + [''] + regex_metachars()

    # --- Python reference shortcuts ---
    if cmd in ('syntax', 'syn'):
        return python_syntax_list()

    if cmd in ('functions', 'builtins', 'built'):
        return python_builtins_list()

    if cmd in ('libraries', 'imports', 'import'):
        return micropython_imports_list()

    if cmd == 'examples':
        if rest:
            return example_detail(rest[0])
        return examples_list()

    if cmd == 'mp':
        if rest:
            return mp_reference_detail(rest[0])
        return mp_reference_list()

    # --- Python legacy sub-commands ---
    if cmd in ('python', 'py'):
        sub = rest[0].lower() if rest else ''
        if sub in ('syn', 'syntax'):
            return python_syntax_list()
        if sub in ('built', 'builtins'):
            return python_builtins_list()
        if sub in ('import', 'imports'):
            return micropython_imports_list()
        return python_syntax_list() + [''] + \
               python_builtins_list() + [''] + \
               micropython_imports_list()

    # --- Code editor ---
    if cmd == 'edit':
        if not rest:
            return ['Usage: code edit <subcommand>']
        sub = rest[0].lower()
        subrest = rest[1:]

        if sub == 'new':
            if not subrest:
                return ['Usage: code edit new <name>']
            name = subrest[0]
            state = code_new(name)
            return [f'  New script: {name}', '  Use "code edit add"']

        if sub == 'add':
            if not subrest:
                return ['Usage: code edit add <line>']
            line = ' '.join(subrest)
            return ['  (use editor mode)',
                    '  "code edit add <line>"']

        if sub == 'lines':
            return ['  (editor state held',
                    '   in code REPL session)']

        if sub == 'save':
            return ['  (editor state held',
                    '   in code REPL session)']

        if sub == 'load':
            if not subrest:
                return ['Usage: code edit load <name>']
            _, display = code_load(subrest[0])
            return display

        if sub == 'list':
            return code_list()

        if sub == 'delete':
            if not subrest:
                return ['Usage: code edit delete <name>']
            return code_delete(subrest[0])

        if sub == 'run':
            if not subrest:
                return ['Usage: code edit run <name>']
            return code_run(subrest[0])

        if sub == 'clear':
            return ['  Editor cleared']

        return [f'Unknown edit cmd: {sub}']

    return [f'Unknown: {cmd}', 'Type "code" for menu']
