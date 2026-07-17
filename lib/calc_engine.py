import math
import random


# ── Complex Number Type ──────────────────────────────

class Cpx:
    __slots__ = ('re', 'im')
    def __init__(self, re=0.0, im=0.0):
        self.re = float(re)
        self.im = float(im)
    def __add__(self, o):
        if isinstance(o, Cpx):
            return Cpx(self.re + o.re, self.im + o.im)
        return Cpx(self.re + float(o), self.im)
    def __radd__(self, o):
        return Cpx(float(o) + self.re, self.im)
    def __sub__(self, o):
        if isinstance(o, Cpx):
            return Cpx(self.re - o.re, self.im - o.im)
        return Cpx(self.re - float(o), self.im)
    def __rsub__(self, o):
        return Cpx(float(o) - self.re, -self.im)
    def __mul__(self, o):
        if isinstance(o, Cpx):
            return Cpx(self.re * o.re - self.im * o.im,
                       self.re * o.im + self.im * o.re)
        return Cpx(self.re * float(o), self.im * float(o))
    def __rmul__(self, o):
        return Cpx(float(o) * self.re, float(o) * self.im)
    def __truediv__(self, o):
        if isinstance(o, Cpx):
            d = o.re * o.re + o.im * o.im
            if d == 0:
                raise ValueError('Error: Division by zero')
            return Cpx((self.re * o.re + self.im * o.im) / d,
                       (self.im * o.re - self.re * o.im) / d)
        f = float(o)
        if f == 0:
            raise ValueError('Error: Division by zero')
        return Cpx(self.re / f, self.im / f)
    def __rtruediv__(self, o):
        d = self.re * self.re + self.im * self.im
        if d == 0:
            raise ValueError('Error: Division by zero')
        f = float(o)
        return Cpx(f * self.re / d, -f * self.im / d)
    def __neg__(self):
        return Cpx(-self.re, -self.im)
    def __pow__(self, o):
        if isinstance(o, Cpx):
            if o.im == 0:
                return self._pow_real(o.re)
            r = abs_cpx(self)
            t = arg_cpx(self)
            n = o.re
            k = o.im
            rn = r ** n
            return Cpx(rn * math.exp(-k * t) * math.cos(n * t + k * math.log(r)),
                       rn * math.exp(-k * t) * math.sin(n * t + k * math.log(r)))
        return self._pow_real(float(o))
    def _pow_real(self, e):
        r = abs_cpx(self)
        if r == 0:
            return Cpx(0, 0)
        t = arg_cpx(self)
        rn = r ** e
        return Cpx(rn * math.cos(e * t), rn * math.sin(e * t))
    def __eq__(self, o):
        if isinstance(o, Cpx):
            return self.re == o.re and self.im == o.im
        return self.re == float(o) and self.im == 0
    def __ne__(self, o):
        return not self.__eq__(o)
    def __abs__(self):
        return math.sqrt(self.re * self.re + self.im * self.im)
    def __repr__(self):
        return cpx_to_str(self)
    def __bool__(self):
        return self.re != 0 or self.im != 0


def cpx_to_str(z):
    if z.im == 0:
        return _fv(z.re)
    if z.re == 0:
        if z.im == 1:
            return 'i'
        if z.im == -1:
            return '-i'
        return _fv(z.im) + 'i'
    sign = '+' if z.im >= 0 else '-'
    aim = abs(z.im)
    if aim == 1:
        ims = 'i'
    else:
        ims = _fv(aim) + 'i'
    return _fv(z.re) + sign + ims


def abs_cpx(z):
    if isinstance(z, Cpx):
        return math.sqrt(z.re * z.re + z.im * z.im)
    return abs(z)


def arg_cpx(z):
    if isinstance(z, Cpx):
        return math.atan2(z.im, z.re)
    return 0 if z >= 0 else math.pi


def conj_cpx(z):
    if isinstance(z, Cpx):
        return Cpx(z.re, -z.im)
    return Cpx(z, 0)


def polar_cpx(z):
    if isinstance(z, Cpx):
        return (abs_cpx(z), arg_cpx(z))
    return (abs(z), 0)


def rect_cpx(r, theta):
    return Cpx(r * math.cos(theta), r * math.sin(theta))


def cis_cpx(theta):
    return Cpx(math.cos(theta), math.sin(theta))


def is_cpx(v):
    return isinstance(v, Cpx)


def _fv(v):
    if is_cpx(v):
        return cpx_to_str(v)
    if isinstance(v, float):
        if v != v:
            return 'NaN'
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return '{:.6g}'.format(v)
    if isinstance(v, list):
        if v and isinstance(v[0], list):
            return _mat_str(v)
        return '[' + ', '.join(_fv(x) for x in v) + ']'
    return str(v)


def _gcd(a, b):
    a, b = abs(int(a)), abs(int(b))
    while b:
        a, b = b, a % b
    return a


def _lcm(a, b):
    a, b = abs(int(a)), abs(int(b))
    if a == 0 or b == 0:
        return 0
    return a * b // _gcd(a, b)


class CalcEngine:
    def __init__(self):
        self.memory = {
            'Ans': 0.0,
            'A': 0.0, 'B': 0.0, 'C': 0.0,
            'D': 0.0, 'E': 0.0, 'F': 0.0,
            'X': 0.0, 'Y': 0.0, 'M': 0.0,
        }
        self.lists = {
            'L1': [], 'L2': [], 'L3': [],
            'L4': [], 'L5': [], 'L6': [],
        }
        self.history = []
        self.steps = []
        self.last_steps = []
        self.angle_mode = 'DEG'
        self.cas_mode = True

    def _to_rad(self, x):
        if self.angle_mode == 'DEG':
            return x * math.pi / 180.0
        elif self.angle_mode == 'GRAD':
            return x * math.pi / 200.0
        return x

    def _from_rad(self, x):
        if self.angle_mode == 'DEG':
            return x * 180.0 / math.pi
        elif self.angle_mode == 'GRAD':
            return x * 200.0 / math.pi
        return x

    def _factorial(self, n):
        if n < 0 or n != int(n):
            raise ValueError('Error: Invalid input for factorial')
        n = int(n)
        if n > 170:
            raise ValueError('Error: Value out of range')
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    def _nPr(self, n, r):
        if n < 0 or r < 0 or n != int(n) or r != int(r):
            raise ValueError('Error: Invalid input for nPr')
        n, r = int(n), int(r)
        if r > n:
            return 0
        return self._factorial(n) // self._factorial(n - r)

    def _nCr(self, n, r):
        if n < 0 or r < 0 or n != int(n) or r != int(r):
            raise ValueError('Error: Invalid input for nCr')
        n, r = int(n), int(r)
        if r > n:
            return 0
        return self._factorial(n) // (self._factorial(r) * self._factorial(n - r))

    def _mean(self, args):
        if not args:
            raise ValueError('Error: mean requires arguments')
        return sum(args) / len(args)

    def _stddev(self, args):
        if len(args) < 2:
            raise ValueError('Error: stddev requires 2+ arguments')
        m = self._mean(args)
        variance = sum((x - m) ** 2 for x in args) / (len(args) - 1)
        return math.sqrt(variance)

    def eval_expr(self, expr):
        expr = expr.strip()
        if not expr:
            raise ValueError('Error: Empty expression')

        if self.cas_mode and self._is_cas_expr(expr):
            return self._eval_cas(expr)

        self._pos = 0
        self._expr = expr
        self._len = len(expr)
        self.steps = []
        result = self._parse_add_sub()
        if self._pos < self._len:
            ch = self._expr[self._pos]
            if ch not in (' ', '\t'):
                raise ValueError(f'Error: Unexpected character "{ch}"')
        self.memory['Ans'] = result
        self.history.append(expr)
        if len(self.history) > 50:
            self.history.pop(0)
        self.last_steps = list(self.steps)
        return result

    def _is_cas_expr(self, expr):
        import re
        if re.match(r'^(diff|int|solve|expand|factor)\s*\(', expr):
            return True
        if '=' in expr:
            eq_pos = -1
            depth = 0
            for i, c in enumerate(expr):
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                elif c == '=' and depth == 0:
                    if i + 1 < len(expr) and expr[i + 1] == '=':
                        continue
                    if i > 0 and expr[i - 1] == '!':
                        continue
                    eq_pos = i
                    break
            if eq_pos >= 0:
                left = expr[:eq_pos].strip()
                if re.match(r'^[a-zA-Z](\^[0-9]+)?(\s*[+\-*/]\s*[a-zA-Z0-9]+)*$', left):
                    return True
                if re.match(r'^[a-zA-Z0-9^+\-*/().\s]+$', expr):
                    import re as _re
                    vs = set(_re.findall(r'[a-z]', expr.lower()))
                    vs -= {'e'}
                    if len(vs) >= 1:
                        return True
        return False

    def _eval_cas(self, expr):
        from lib.cas_engine import cas_eval
        raw, display = cas_eval(expr)
        self.steps = ['CAS: ' + expr, '= ' + display]
        self.last_steps = list(self.steps)
        self.history.append(expr)
        if len(self.history) > 50:
            self.history.pop(0)
        try:
            val = float(raw)
            self.memory['Ans'] = val
            return val
        except:
            return raw

    def _skip_spaces(self):
        while self._pos < self._len and self._expr[self._pos] in (' ', '\t'):
            self._pos += 1

    def _peek(self):
        self._skip_spaces()
        if self._pos < self._len:
            return self._expr[self._pos]
        return None

    def _consume(self, ch=None):
        self._skip_spaces()
        if self._pos >= self._len:
            raise ValueError('Error: Unexpected end of expression')
        if ch and self._expr[self._pos] != ch:
            raise ValueError(f'Error: Expected "{ch}" but got "{self._expr[self._pos]}"')
        self._pos += 1

    def _parse_add_sub(self):
        left = self._parse_mul_div()
        while True:
            ch = self._peek()
            if ch == '+':
                self._consume('+')
                right = self._parse_mul_div()
                if isinstance(left, list) and isinstance(right, list):
                    result = _mat_add(left, right)
                else:
                    result = left + right
                self.steps.append(_fv(left) + ' + ' + _fv(right) + ' = ' + _fv(result))
                left = result
            elif ch == '-':
                self._consume('-')
                right = self._parse_mul_div()
                if isinstance(left, list) and isinstance(right, list):
                    result = _mat_sub(left, right)
                else:
                    result = left - right
                self.steps.append(_fv(left) + ' - ' + _fv(right) + ' = ' + _fv(result))
                left = result
            elif ch == '<':
                self._consume('<')
                if self._peek() == '=':
                    self._consume('=')
                    right = self._parse_mul_div()
                    left = 1.0 if left <= right else 0.0
                else:
                    right = self._parse_mul_div()
                    left = 1.0 if left < right else 0.0
            elif ch == '>':
                self._consume('>')
                if self._peek() == '=':
                    self._consume('=')
                    right = self._parse_mul_div()
                    left = 1.0 if left >= right else 0.0
                else:
                    right = self._parse_mul_div()
                    left = 1.0 if left > right else 0.0
            elif ch == '=' and self._pos + 1 < self._len and self._expr[self._pos + 1] == '=':
                self._consume('=')
                self._consume('=')
                right = self._parse_mul_div()
                left = 1.0 if left == right else 0.0
            elif ch == '!' and self._pos + 1 < self._len and self._expr[self._pos + 1] == '=':
                self._consume('!')
                self._consume('=')
                right = self._parse_mul_div()
                left = 1.0 if left != right else 0.0
            else:
                break
        return left

    def _parse_mul_div(self):
        left = self._parse_power()
        while True:
            ch = self._peek()
            if ch == '*':
                self._consume('*')
                if self._peek() == '*':
                    self._consume('*')
                    right = self._parse_power()
                    self.steps.append(_fv(left) + ' ^ ' + _fv(right) + ' = ' + _fv(left ** right))
                    left = left ** right
                else:
                    right = self._parse_power()
                    if isinstance(left, list) and isinstance(right, list):
                        result = _mat_mul(left, right)
                    elif isinstance(left, list):
                        result = _mat_scale(left, right)
                    elif isinstance(right, list):
                        result = _mat_scale(right, left)
                    else:
                        result = left * right
                    self.steps.append(_fv(left) + ' * ' + _fv(right) + ' = ' + _fv(result))
                    left = result
            elif ch == '/':
                self._consume('/')
                right = self._parse_power()
                if isinstance(right, list):
                    right = _mat_inv(right)
                    result = _mat_mul(left, right) if isinstance(left, list) else _mat_scale(right, left)
                else:
                    if right == 0:
                        raise ValueError('Error: Division by zero')
                    result = left / right
                self.steps.append(_fv(left) + ' / ' + _fv(right) + ' = ' + _fv(result))
                left = result
            else:
                break
        return left

    def _parse_power(self):
        left = self._parse_unary()
        while True:
            ch = self._peek()
            if ch == '^':
                self._consume('^')
                right = self._parse_unary()
                self.steps.append(_fv(left) + ' ^ ' + _fv(right) + ' = ' + _fv(left ** right))
                left = left ** right
            elif ch == '!' and self._pos + 1 < self._len and self._expr[self._pos + 1] == '=':
                break
            elif ch == '!' and (self._pos + 1 >= self._len or self._expr[self._pos + 1] != '='):
                self._consume('!')
                left = self._factorial(left)
                self.steps.append(_fv(left) + '! = ' + _fv(left))
            elif ch == '%':
                self._consume('%')
                left = left / 100.0
                self.steps.append(_fv(left * 100) + '% = ' + _fv(left))
            elif self._is_implicit_mul(ch):
                right = self._parse_unary()
                left = left * right
            else:
                break
        return left

    def _is_implicit_mul(self, ch):
        if ch is None:
            return False
        return ch == '(' or ch.isalpha() or ch == '_'

    def _parse_unary(self):
        ch = self._peek()
        if ch == '+':
            self._consume('+')
            return self._parse_unary()
        elif ch == '-':
            self._consume('-')
            return -self._parse_unary()
        return self._parse_primary()

    def _parse_primary(self):
        ch = self._peek()
        if ch is None:
            raise ValueError('Error: Unexpected end of expression')

        if ch == '(':
            self._consume('(')
            result = self._parse_add_sub()
            self._consume(')')
            return result

        if ch == '[':
            return self._parse_matrix()

        if ch == '{':
            return self._parse_list_literal()

        if ch.isdigit() or ch == '.':
            return self._parse_number()

        if ch.isalpha() or ch == '_':
            return self._parse_name_or_func()

        raise ValueError(f'Error: Unexpected character "{ch}"')

    def _parse_number(self):
        start = self._pos
        has_dot = False
        while self._pos < self._len and (self._expr[self._pos].isdigit() or self._expr[self._pos] == '.'):
            if self._expr[self._pos] == '.':
                if has_dot:
                    raise ValueError('Error: Invalid number (multiple dots)')
                has_dot = True
            self._pos += 1
        if self._pos < self._len and self._expr[self._pos] in ('e', 'E'):
            self._pos += 1
            if self._pos < self._len and self._expr[self._pos] in ('+', '-'):
                self._pos += 1
            exp_start = self._pos
            while self._pos < self._len and self._expr[self._pos].isdigit():
                self._pos += 1
            if self._pos == exp_start:
                raise ValueError('Error: Invalid scientific notation')
        num_str = self._expr[start:self._pos]
        return float(num_str)

    def _parse_name_or_func(self):
        start = self._pos
        while self._pos < self._len and (self._expr[self._pos].isalpha() or self._expr[self._pos].isdigit() or self._expr[self._pos] == '_'):
            self._pos += 1
        name = self._expr[start:self._pos]

        constants = {
            'pi': math.pi,
            'e': math.e,
            'g': 9.80665,
            'c': 299792458.0,
            'phi': (1 + math.sqrt(5)) / 2,
            'i': Cpx(0, 1),
            'j': Cpx(0, 1),
        }
        if name in constants:
            return constants[name]

        if name in self.lists:
            if self._peek() == '=' and self._pos + 1 < self._len and self._expr[self._pos + 1] != '=':
                self._consume('=')
                val = self._parse_add_sub()
                if isinstance(val, list):
                    self.lists[name] = val
                else:
                    self.lists[name] = [val]
                self.steps.append(name + ' = ' + _fv(val))
                return val
            return self.lists[name]

        if name in self.memory:
            if self._peek() == '=' and self._pos + 1 < self._len and self._expr[self._pos + 1] != '=':
                self._consume('=')
                val = self._parse_add_sub()
                self.memory[name] = val
                self.steps.append(name + ' = ' + _fv(val))
                return val
            return self.memory[name]

        if name == 'Ans':
            return self.memory['Ans']

        self._consume('(')
        args = []

        _NUMERIC_FUNCS = {'summate', 'Σ', 'product', 'Π', 'fnInt', 'fnDiff', 'seq', 'solve2', 'piecewise'}
        if name in _NUMERIC_FUNCS:
            raw_parts = []
            depth = 1
            start = self._pos
            while self._pos < self._len and depth > 0:
                c = self._expr[self._pos]
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        break
                elif c == ',' and depth == 1:
                    raw = self._expr[start:self._pos].strip()
                    raw_parts.append(raw)
                    start = self._pos + 1
                self._pos += 1
            last = self._expr[start:self._pos].strip()
            if last:
                raw_parts.append(last)
            self._consume(')')
            if raw_parts:
                args.append(raw_parts[0])
            for rp in raw_parts[1:]:
                args.append(rp)
        else:
            if self._peek() != ')':
                args.append(self._parse_add_sub())
                while self._peek() == ',':
                    self._consume(',')
                    args.append(self._parse_add_sub())
            self._consume(')')

        funcs_single = {
            'sin': lambda x: math.sin(self._to_rad(x)) if not is_cpx(x) else _cpx_sin(x, self),
            'cos': lambda x: math.cos(self._to_rad(x)) if not is_cpx(x) else _cpx_cos(x, self),
            'tan': lambda x: math.tan(self._to_rad(x)) if not is_cpx(x) else _cpx_tan(x, self),
            'asin': lambda x: self._from_rad(math.asin(x)) if not is_cpx(x) else _cpx_asin(x, self),
            'acos': lambda x: self._from_rad(math.acos(x)) if not is_cpx(x) else _cpx_acos(x, self),
            'atan': lambda x: self._from_rad(math.atan(x)) if not is_cpx(x) else _cpx_atan(x, self),
            'sinh': lambda x: math.sinh(x) if not is_cpx(x) else _cpx_sinh(x),
            'cosh': lambda x: math.cosh(x) if not is_cpx(x) else _cpx_cosh(x),
            'tanh': lambda x: math.tanh(x) if not is_cpx(x) else _cpx_tanh(x),
            'asinh': lambda x: math.asinh(x) if not is_cpx(x) else _cpx_asinh(x),
            'acosh': lambda x: math.acosh(x) if not is_cpx(x) else _cpx_acosh(x),
            'atanh': lambda x: math.atanh(x) if not is_cpx(x) else _cpx_atanh(x),
            'ln': lambda x: math.log(x) if not is_cpx(x) else _cpx_ln(x),
            'log10': lambda x: math.log10(x) if not is_cpx(x) else _cpx_log(x, 10),
            'log2': lambda x: math.log2(x) if not is_cpx(x) else _cpx_log(x, 2),
            'sqrt': lambda x: _cpx_sqrt(x) if is_cpx(x) or (isinstance(x, float) and x < 0) else math.sqrt(x),
            'cbrt': lambda x: math.copysign(abs(x) ** (1.0 / 3.0), x) if not is_cpx(x) else x._pow_real(1.0/3.0),
            'abs': lambda x: abs_cpx(x),
            'floor': lambda x: math.floor(x) if not is_cpx(x) else Cpx(math.floor(x.re), math.floor(x.im)),
            'ceil': lambda x: math.ceil(x) if not is_cpx(x) else Cpx(math.ceil(x.re), math.ceil(x.im)),
            'round': lambda x: round(x) if not is_cpx(x) else Cpx(round(x.re), round(x.im)),
            'fact': lambda x: self._factorial(x) if not is_cpx(x) else self._factorial(x.re),
            'deg': lambda x: self._from_rad(x) if not is_cpx(x) else Cpx(self._from_rad(x.re), self._from_rad(x.im)),
            'rad': lambda x: self._to_rad(x) if not is_cpx(x) else Cpx(self._to_rad(x.re), self._to_rad(x.im)),
            'sign': lambda x: (1.0 if x > 0 else (-1.0 if x < 0 else 0.0)) if not is_cpx(x) else _cpx_sign(x),
            'exp': lambda x: math.exp(x) if not is_cpx(x) else _cpx_exp(x),
            're': lambda x: x.re if is_cpx(x) else float(x),
            'im': lambda x: x.im if is_cpx(x) else 0.0,
            'conj': lambda x: conj_cpx(x),
            'arg': lambda x: arg_cpx(x),
            'polar': lambda x: polar_cpx(x),
        }

        if name in funcs_single:
            if len(args) != 1:
                raise ValueError(f'Error: {name} takes 1 argument')
            result = funcs_single[name](args[0])
            self.steps.append(name + '(' + _fv(args[0]) + ') = ' + _fv(result))
            return result

        funcs_multi = {
            'nPr': lambda a: self._nPr(a[0], a[1]),
            'nCr': lambda a: self._nCr(a[0], a[1]),
            'pow': lambda a: a[0] ** a[1],
            'atan2': lambda a: self._from_rad(math.atan2(a[0], a[1])),
            'mean': lambda a: self._mean(a),
            'stddev': lambda a: self._stddev(a),
            'randint': lambda a: random.randint(int(a[0]), int(a[1])),
            'mod': lambda a: a[0] % a[1],
            'min': lambda a: min(a),
            'max': lambda a: max(a),
            'gcd': lambda a: _gcd(a[0], a[1]),
            'lcm': lambda a: _lcm(a[0], a[1]),
            'clamp': lambda a: max(a[1], min(a[0], a[2])) if len(a) == 3 else max(a[1], min(a[0], a[2])),
            'hypot': lambda a: math.hypot(a[0], a[1]),
            'rect': lambda a: rect_cpx(a[0], a[1]),
            'cis': lambda a: cis_cpx(a[0]),
            'complex': lambda a: Cpx(a[0], a[1] if len(a) > 1 else 0),
            'det': lambda a: _mat_det(a[0]),
            'inv': lambda a: _mat_inv(a[0]),
            'tr': lambda a: _mat_trace(a[0]),
            'trace': lambda a: _mat_trace(a[0]),
            'transpose': lambda a: _mat_transpose(a[0]),
            'rref': lambda a: _mat_rref(a[0]),
            'eye': lambda a: _mat_eye(a[0]),
            'zeros': lambda a: _mat_zeros(a[0], a[1]) if len(a) > 1 else _mat_zeros(a[0]),
            'length': lambda a: len(a[0]) if isinstance(a[0], list) else 0,
            'sort': lambda a: sorted(a[0]) if isinstance(a[0], list) else [],
            'sum': lambda a: sum(a[0]) if isinstance(a[0], list) else sum(a),
            'linreg': lambda a: _linreg(a[0], a[1]),
            'quadreg': lambda a: _quadreg(a[0], a[1]),
            'expreg': lambda a: _expreg(a[0], a[1]),
            'logreg': lambda a: _logreg(a[0], a[1]),
            'pwreg': lambda a: _pwreg(a[0], a[1]),
            'MedMed': lambda a: _medmed(a[0], a[1]),
            'corr': lambda a: _corr(a[0], a[1]),
            'Σ': lambda a: _summation(a, self),
            'summate': lambda a: _summation(a, self),
            'Π': lambda a: _product(a, self),
            'product': lambda a: _product(a, self),
            'fnInt': lambda a: _fnint(a, self),
            'fnDiff': lambda a: _fndiff(a, self),
            'seq': lambda a: _seq(a, self),
            'normalpdf': lambda a: _normalpdf(a[0], a[1] if len(a) > 1 else 0, a[2] if len(a) > 2 else 1),
            'normalcdf': lambda a: _normalcdf(a[0], a[1], a[2] if len(a) > 2 else 0, a[3] if len(a) > 3 else 1),
            'invNorm': lambda a: _invnorm(a[0], a[1] if len(a) > 1 else 0, a[2] if len(a) > 2 else 1),
            'binompdf': lambda a: _binompdf(int(a[0]), a[1], int(a[2])),
            'binomcdf': lambda a: _binomcdf(int(a[0]), a[1], int(a[2])),
            'poissonpdf': lambda a: _poissonpdf(a[0], int(a[1])),
            'poissoncdf': lambda a: _poissoncdf(a[0], int(a[1])),
            'χ²cdf': lambda a: _chi2cdf(a[0], a[1], int(a[2])) if len(a) > 2 else _chi2cdf(a[0], a[1], 1),
            'tcdf': lambda a: _tcdf(a[0], a[1], int(a[2])) if len(a) > 2 else _tcdf(a[0], a[1], 999999),
            'fcdf': lambda a: _fcdf(a[0], a[1], int(a[2]), int(a[3])),
            'ztest': lambda a: _ztest(a[0], a[1], a[2], a[3]),
            'ttest': lambda a: _ttest(a[0], a[1], a[2], a[3]),
            'piecewise': lambda a: _piecewise(a, self),
            'when': lambda a: a[1] if a[0] else a[2] if len(a) > 2 else 0,
            'solve2': lambda a: _solve2(a, self),
        }

        if name in funcs_multi:
            result = funcs_multi[name](args)
            arg_str = ', '.join(_fv(a) for a in args)
            self.steps.append(name + '(' + arg_str + ') = ' + _fv(result))
            return result

        if name == 'rand':
            if args:
                return random.random() * args[0]
            return random.random()

        if name == 'sum':
            return sum(args)

        raise ValueError(f'Error: Unknown function "{name}"')

    def _parse_matrix(self):
        self._consume('[')
        rows = []
        row = []
        if self._peek() != ']':
            val = self._parse_add_sub()
            if isinstance(val, list):
                rows.append(val)
            else:
                row.append(val)
            while self._peek() in (',', ';'):
                sep = self._peek()
                self._consume()
                if sep == ';':
                    if row:
                        rows.append(row)
                    row = []
                    if self._peek() != ']':
                        val = self._parse_add_sub()
                        if isinstance(val, list):
                            row.extend(val)
                        else:
                            row.append(val)
                else:
                    val = self._parse_add_sub()
                    if isinstance(val, list):
                        row.extend(val)
                    else:
                        row.append(val)
            if row:
                rows.append(row)
        self._consume(']')
        return rows

    def _parse_list_literal(self):
        self._consume('{')
        items = []
        if self._peek() != '}':
            items.append(self._parse_add_sub())
            while self._peek() == ',':
                self._consume(',')
                items.append(self._parse_add_sub())
        self._consume('}')
        return items


# ── Complex Math Functions ───────────────────────────

def _cpx_sin(z, eng):
    if not is_cpx(z):
        return math.sin(eng._to_rad(z))
    x, y = z.re, z.im
    return Cpx(math.sin(x) * math.cosh(y), math.cos(x) * math.sinh(y))


def _cpx_cos(z, eng):
    if not is_cpx(z):
        return math.cos(eng._to_rad(z))
    x, y = z.re, z.im
    return Cpx(math.cos(x) * math.cosh(y), -math.sin(x) * math.sinh(y))


def _cpx_tan(z, eng):
    if not is_cpx(z):
        return math.tan(eng._to_rad(z))
    s = _cpx_sin(z, eng)
    c = _cpx_cos(z, eng)
    return s / c


def _cpx_asin(z, eng):
    if not is_cpx(z):
        return eng._from_rad(math.asin(z))
    iz = Cpx(0, 1) * z
    inside = Cpx(1, 0) - z * z
    sq = _cpx_sqrt(inside)
    ln_val = _cpx_ln(iz + sq)
    return Cpx(0, -1) * ln_val


def _cpx_acos(z, eng):
    if not is_cpx(z):
        return eng._from_rad(math.acos(z))
    inside = z * z - Cpx(1, 0)
    sq = _cpx_sqrt(inside)
    ln_val = _cpx_ln(z + sq)
    return Cpx(0, -1) * ln_val


def _cpx_atan(z, eng):
    if not is_cpx(z):
        return eng._from_rad(math.atan(z))
    iz = Cpx(0, 1) * z
    one_minus = Cpx(1, 0) - iz
    one_plus = Cpx(1, 0) + iz
    ln_val = _cpx_ln(one_minus / one_plus)
    return Cpx(0, 0.5) * ln_val


def _cpx_sinh(z):
    if not is_cpx(z):
        return math.sinh(z)
    return (z.exp() - (-z).exp()) / Cpx(2, 0)


def _cpx_cosh(z):
    if not is_cpx(z):
        return math.cosh(z)
    return (z.exp() + (-z).exp()) / Cpx(2, 0)


def _cpx_tanh(z):
    if not is_cpx(z):
        return math.tanh(z)
    s = _cpx_sinh(z)
    c = _cpx_cosh(z)
    return s / c


def _cpx_asinh(z):
    if not is_cpx(z):
        return math.asinh(z)
    inside = z * z + Cpx(1, 0)
    sq = _cpx_sqrt(inside)
    return _cpx_ln(z + sq)


def _cpx_acosh(z):
    if not is_cpx(z):
        return math.acosh(z)
    inside = z * z - Cpx(1, 0)
    sq = _cpx_sqrt(inside)
    return _cpx_ln(z + sq)


def _cpx_atanh(z):
    if not is_cpx(z):
        return math.atanh(z)
    one_plus = Cpx(1, 0) + z
    one_minus = Cpx(1, 0) - z
    ln_val = _cpx_ln(one_plus / one_minus)
    return Cpx(0.5, 0) * ln_val


def _cpx_exp(z):
    if not is_cpx(z):
        return math.exp(z)
    er = math.exp(z.re)
    return Cpx(er * math.cos(z.im), er * math.sin(z.im))


def _cpx_ln(z):
    if not is_cpx(z):
        return math.log(z)
    r = abs_cpx(z)
    t = arg_cpx(z)
    return Cpx(math.log(r), t)


def _cpx_log(z, base):
    if not is_cpx(z):
        return math.log(z, base)
    return _cpx_ln(z) / math.log(base)


def _cpx_log10(z):
    if not is_cpx(z):
        return math.log10(z)
    return _cpx_ln(z) / math.log(10)


def _cpx_sqrt(z):
    if not is_cpx(z):
        if z >= 0:
            return math.sqrt(z)
        return Cpx(0, math.sqrt(-z))
    r = abs_cpx(z)
    t = arg_cpx(z)
    sr = math.sqrt(r)
    return Cpx(sr * math.cos(t / 2), sr * math.sin(t / 2))


def _cpx_sign(z):
    if not is_cpx(z):
        return 1.0 if z > 0 else (-1.0 if z < 0 else 0.0)
    r = abs_cpx(z)
    if r == 0:
        return Cpx(0, 0)
    return Cpx(z.re / r, z.im / r)


# ── Matrix Operations ────────────────────────────────

def _mat_rows(A):
    return len(A)


def _mat_cols(A):
    return len(A[0]) if A else 0


def _mat_add(A, B):
    if _mat_rows(A) != _mat_rows(B) or _mat_cols(A) != _mat_cols(B):
        raise ValueError('Error: Matrix dimension mismatch')
    return [[A[i][j] + B[i][j] for j in range(_mat_cols(A))] for i in range(_mat_rows(A))]


def _mat_sub(A, B):
    if _mat_rows(A) != _mat_rows(B) or _mat_cols(A) != _mat_cols(B):
        raise ValueError('Error: Matrix dimension mismatch')
    return [[A[i][j] - B[i][j] for j in range(_mat_cols(A))] for i in range(_mat_rows(A))]


def _mat_mul(A, B):
    if _mat_cols(A) != _mat_rows(B):
        raise ValueError('Error: Incompatible matrix dimensions')
    ra, ca = _mat_rows(A), _mat_cols(A)
    cb = _mat_cols(B)
    result = [[0.0] * cb for _ in range(ra)]
    for i in range(ra):
        for j in range(cb):
            s = 0.0
            for k in range(ca):
                s += A[i][k] * B[k][j]
            result[i][j] = s
    return result


def _mat_scale(A, k):
    return [[A[i][j] * k for j in range(_mat_cols(A))] for i in range(_mat_rows(A))]


def _mat_det(A):
    n = _mat_rows(A)
    if n != _mat_cols(A):
        raise ValueError('Error: Determinant requires square matrix')
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    det = 0.0
    for j in range(n):
        sign = 1.0 if j % 2 == 0 else -1.0
        minor = [[A[i][k] for k in range(n) if k != j] for i in range(1, n)]
        det += sign * A[0][j] * _mat_det(minor)
    return det


def _mat_inv(A):
    n = _mat_rows(A)
    if n != _mat_cols(A):
        raise ValueError('Error: Inverse requires square matrix')
    det = _mat_det(A)
    if abs(det) < 1e-12:
        raise ValueError('Error: Singular matrix (no inverse)')
    if n == 1:
        return [[1.0 / A[0][0]]]
    if n == 2:
        return [[A[1][1] / det, -A[0][1] / det],
                [-A[1][0] / det, A[0][0] / det]]
    adj = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sign = 1.0 if (i + j) % 2 == 0 else -1.0
            minor = [[A[r][c] for c in range(n) if c != j] for r in range(n) if r != i]
            adj[j][i] = sign * _mat_det(minor)
    return _mat_scale(adj, 1.0 / det)


def _mat_transpose(A):
    rows, cols = _mat_rows(A), _mat_cols(A)
    return [[A[i][j] for i in range(rows)] for j in range(cols)]


def _mat_trace(A):
    n = _mat_rows(A)
    if n != _mat_cols(A):
        raise ValueError('Error: Trace requires square matrix')
    return sum(A[i][i] for i in range(n))


def _mat_rref(A):
    M = [[A[i][j] for j in range(_mat_cols(A))] for i in range(_mat_rows(A))]
    rows, cols = _mat_rows(M), _mat_cols(M)
    lead = 0
    for r in range(rows):
        if lead >= cols:
            break
        i = r
        while abs(M[i][lead]) < 1e-10:
            i += 1
            if i == rows:
                i = r
                lead += 1
                if lead == cols:
                    break
        M[i], M[r] = M[r], M[i]
        if abs(M[r][lead]) > 1e-10:
            lv = M[r][lead]
            M[r] = [v / lv for v in M[r]]
            for i in range(rows):
                if i != r:
                    fv = M[i][lead]
                    M[i] = [M[i][j] - fv * M[r][j] for j in range(cols)]
        lead += 1
    return M


def _mat_eye(n):
    n = int(n)
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _mat_zeros(m, n=None):
    m = int(m)
    n = int(n) if n is not None else m
    return [[0.0] * n for _ in range(m)]


def _mat_str(A):
    lines = []
    for row in A:
        lines.append('[' + ', '.join(_fv(v) for v in row) + ']')
    return '[' + '; '.join(lines) + ']'


# ── Regression & List Functions ──────────────────────

def _linreg(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 2:
        raise ValueError('Error: Need 2+ data points')
    sx = sum(x_list[:n])
    sy = sum(y_list[:n])
    sxy = sum(x_list[i] * y_list[i] for i in range(n))
    sx2 = sum(x_list[i] ** 2 for i in range(n))
    denom = n * sx2 - sx * sx
    if abs(denom) < 1e-12:
        raise ValueError('Error: Vertical line (no slope)')
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    y_mean = sy / n
    ss_tot = sum((y_list[i] - y_mean) ** 2 for i in range(n))
    ss_res = sum((y_list[i] - (slope * x_list[i] + intercept)) ** 2 for i in range(n))
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 1
    r = math.sqrt(abs(r2))
    if sxy / n - sx * sy / (n * n) < 0:
        r = -r
    return {'slope': slope, 'intercept': intercept, 'r': r, 'r2': r2,
            'eq': f'y={_fv(slope)}x+{_fv(intercept)}'}


def _quadreg(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 3:
        raise ValueError('Error: Need 3+ data points')
    sx = sum(x_list[:n])
    sx2 = sum(x_list[i] ** 2 for i in range(n))
    sx3 = sum(x_list[i] ** 3 for i in range(n))
    sx4 = sum(x_list[i] ** 4 for i in range(n))
    sy = sum(y_list[:n])
    sxy = sum(x_list[i] * y_list[i] for i in range(n))
    sx2y = sum(x_list[i] ** 2 * y_list[i] for i in range(n))
    det = (n * sx2 * sx4 + 2 * sx * sx2 * sx3
           - sx2 ** 3 - sx ** 2 * sx4 - n * sx3 ** 2)
    if abs(det) < 1e-12:
        raise ValueError('Error: Singular system')
    a = (n * sx2y * sx4 + sx * sx3 * sy + sx2 * sx * sxy
         - sx2 ** 2 * sy - sx * sx2y * sx - n * sx3 * sxy) / det
    b = (n * sx2 * sxy + sx * sx2 * sy + sx3 * sx4 * n * 0
         - sx2 ** 2 * sxy - sx * sx2 * sy * 0 - n * sx2 * sxy) / det
    c = (sy - a * sx2 - b * sx) / n
    return {'a': a, 'b': b, 'c': c,
            'eq': f'y={_fv(a)}x^2+{_fv(b)}x+{_fv(c)}'}


def _expreg(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 2:
        raise ValueError('Error: Need 2+ data points')
    ln_y = [math.log(y) if y > 0 else 0 for y in y_list[:n]]
    sx = sum(x_list[:n])
    sy = sum(ln_y)
    sxy = sum(x_list[i] * ln_y[i] for i in range(n))
    sx2 = sum(x_list[i] ** 2 for i in range(n))
    denom = n * sx2 - sx * sx
    if abs(denom) < 1e-12:
        raise ValueError('Error: Cannot fit')
    b = (n * sxy - sx * sy) / denom
    a = math.exp((sy - b * sx) / n)
    return {'a': a, 'b': b, 'eq': f'y={_fv(a)}*e^({_fv(b)}x)'}


def _logreg(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 2:
        raise ValueError('Error: Need 2+ data points')
    ln_x = [math.log(x) if x > 0 else 0 for x in x_list[:n]]
    sx = sum(ln_x)
    sy = sum(y_list[:n])
    sxy = sum(ln_x[i] * y_list[i][0] if isinstance(y_list[i], list) else ln_x[i] * y_list[i] for i in range(n))
    sx2 = sum(ln_x[i] ** 2 for i in range(n))
    denom = n * sx2 - sx * sx
    if abs(denom) < 1e-12:
        raise ValueError('Error: Cannot fit')
    b = (n * sxy - sx * sy) / denom
    a = (sy - b * sx) / n
    return {'a': a, 'b': b, 'eq': f'y={_fv(a)}+{_fv(b)}*ln(x)'}


def _pwreg(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 2:
        raise ValueError('Error: Need 2+ data points')
    ln_x = [math.log(x) if x > 0 else 1 for x in x_list[:n]]
    ln_y = [math.log(y) if y > 0 else 0 for y in y_list[:n]]
    sx = sum(ln_x)
    sy = sum(ln_y)
    sxy = sum(ln_x[i] * ln_y[i] for i in range(n))
    sx2 = sum(ln_x[i] ** 2 for i in range(n))
    denom = n * sx2 - sx * sx
    if abs(denom) < 1e-12:
        raise ValueError('Error: Cannot fit')
    b = (n * sxy - sx * sy) / denom
    a = math.exp((sy - b * sx) / n)
    return {'a': a, 'b': b, 'eq': f'y={_fv(a)}*x^{_fv(b)}'}


def _medmed(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 3:
        raise ValueError('Error: Need 3+ points')
    sorted_pairs = sorted(zip(x_list[:n], y_list[:n]), key=lambda p: p[0])
    third = n // 3
    g1x = [p[0] for p in sorted_pairs[:third]]
    g1y = [p[1] for p in sorted_pairs[:third]]
    g2x = [p[0] for p in sorted_pairs[third:2*third]]
    g2y = [p[1] for p in sorted_pairs[third:2*third]]
    g3x = [p[0] for p in sorted_pairs[2*third:]]
    g3y = [p[1] for p in sorted_pairs[2*third:]]
    mx1 = sorted(g1x)[len(g1x)//2]
    my1 = sorted(g1y)[len(g1y)//2]
    mx2 = sorted(g2x)[len(g2x)//2]
    my2 = sorted(g2y)[len(g2y)//2]
    mx3 = sorted(g3x)[len(g3x)//2]
    my3 = sorted(g3y)[len(g3y)//2]
    if mx3 == mx1:
        slope = 0
    else:
        slope = (my3 - my1) / (mx3 - mx1)
    intercept = (my1 + my2 + my3 - slope * (mx1 + mx2 + mx3)) / 3
    return {'slope': slope, 'intercept': intercept,
            'eq': f'y={_fv(slope)}x+{_fv(intercept)}'}


def _corr(x_list, y_list):
    n = min(len(x_list), len(y_list))
    if n < 2:
        raise ValueError('Error: Need 2+ data points')
    mx = sum(x_list[:n]) / n
    my = sum(y_list[:n]) / n
    sxy = sum((x_list[i] - mx) * (y_list[i] - my) for i in range(n))
    sx = math.sqrt(sum((x_list[i] - mx) ** 2 for i in range(n)))
    sy = math.sqrt(sum((y_list[i] - my) ** 2 for i in range(n)))
    if sx * sy == 0:
        return 0
    return sxy / (sx * sy)


# ── Numerical Operations (sum, product, int, diff) ───

def _eval_with_var(expr_str, var_name, var_val, eng):
    """Evaluate expr_str with var_name set to var_val."""
    old_val = eng.memory.get(var_name, 0)
    eng.memory[var_name] = var_val
    try:
        result = eng.eval_expr(expr_str)
    finally:
        eng.memory[var_name] = old_val
    return result


def _summation(args, eng):
    """Σ(expr, var, start, end)"""
    if len(args) < 4:
        raise ValueError('Error: sum(expr, var, start, end)')
    expr_str = str(args[0])
    var_name = str(args[1])
    start = int(float(args[2]))
    end = int(float(args[3]))
    total = 0.0
    for i in range(start, end + 1):
        total += _eval_with_var(expr_str, var_name, i, eng)
    return total


def _product(args, eng):
    """Π(expr, var, start, end)"""
    if len(args) < 4:
        raise ValueError('Error: prod(expr, var, start, end)')
    expr_str = str(args[0])
    var_name = str(args[1])
    start = int(float(args[2]))
    end = int(float(args[3]))
    result = 1.0
    for i in range(start, end + 1):
        result *= _eval_with_var(expr_str, var_name, i, eng)
    return result


def _fnint(args, eng):
    """fnInt(expr, var, a, b) — Simpson's rule"""
    if len(args) < 4:
        raise ValueError('Error: fnInt(expr, var, a, b)')
    expr_str = str(args[0])
    var_name = str(args[1])
    a = float(args[2])
    b = float(args[3])
    n = 100
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    fa = _eval_with_var(expr_str, var_name, a, eng)
    fb = _eval_with_var(expr_str, var_name, b, eng)
    total = fa + fb
    for i in range(1, n):
        x = a + i * h
        fx = _eval_with_var(expr_str, var_name, x, eng)
        if i % 2 == 0:
            total += 2 * fx
        else:
            total += 4 * fx
    return total * h / 3


def _fndiff(args, eng):
    """fnDiff(expr, var, x) — central difference"""
    if len(args) < 3:
        raise ValueError('Error: fnDiff(expr, var, x)')
    expr_str = str(args[0])
    var_name = str(args[1])
    x = float(args[2])
    h = 1e-6
    fp = _eval_with_var(expr_str, var_name, x + h, eng)
    fm = _eval_with_var(expr_str, var_name, x - h, eng)
    return (fp - fm) / (2 * h)


def _seq(args, eng):
    """seq(expr, var, start, end) — generate sequence"""
    if len(args) < 4:
        raise ValueError('Error: seq(expr, var, start, end)')
    expr_str = str(args[0])
    var_name = str(args[1])
    start = int(float(args[2]))
    end = int(float(args[3]))
    return [_eval_with_var(expr_str, var_name, i, eng) for i in range(start, end + 1)]


# ── Statistical Distributions ────────────────────────

def _erf(x):
    """Error function approximation (Abramowitz & Stegun)."""
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign * (1.0 - poly * math.exp(-x * x))


def _normalpdf(x, mu=0, sigma=1):
    if sigma <= 0:
        raise ValueError('Error: sigma must be > 0')
    z = (x - mu) / sigma
    return math.exp(-0.5 * z * z) / (sigma * math.sqrt(2 * math.pi))


def _normalcdf(a, b, mu=0, sigma=1):
    if sigma <= 0:
        raise ValueError('Error: sigma must be > 0')
    za = (a - mu) / sigma
    zb = (b - mu) / sigma
    return 0.5 * (_erf(zb / math.sqrt(2)) - _erf(za / math.sqrt(2)))


def _invnorm(p, mu=0, sigma=1):
    if p <= 0 or p >= 1:
        raise ValueError('Error: p must be 0 < p < 1')
    if p < 0.5:
        return mu - sigma * _invnorm(1 - p)
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    z = t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)
    return mu + sigma * z


def _binompdf(n, p, x):
    if p < 0 or p > 1 or n < 0 or x < 0 or x > n:
        return 0
    log_comb = (math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1))
    return math.exp(log_comb + x * math.log(p) + (n - x) * math.log(1 - p))


def _binomcdf(n, p, x):
    total = 0.0
    for k in range(int(x) + 1):
        total += _binompdf(n, p, k)
    return min(total, 1.0)


def _poissonpdf(lam, x):
    if lam <= 0 or x < 0:
        return 0
    return math.exp(-lam + x * math.log(lam) - math.lgamma(x + 1))


def _poissoncdf(lam, x):
    total = 0.0
    for k in range(int(x) + 1):
        total += _poissonpdf(lam, k)
    return min(total, 1.0)


def _chi2cdf(x, a, df):
    if x <= 0:
        return 0
    if df <= 0:
        raise ValueError('Error: df must be > 0')
    k = df / 2.0
    return _gammainc(k, x / 2.0)


def _tcdf(x, a, df):
    if df <= 0:
        raise ValueError('Error: df must be > 0')
    if df >= 1000:
        return _normalcdf(a, x)
    t_val = x
    return 0.5 + t_val * math.sqrt(df + t_val * t_val) / (math.pi * (df + t_val * t_val)) * (
        1 + 1 / (2 * df) + 3 / (8 * df * df)
    ) if abs(t_val) < 10 else (1 if t_val > 0 else 0)


def _fcdf(x, a, df1, df2):
    if x <= 0 or df1 <= 0 or df2 <= 0:
        return 0
    return _betai(df1 / 2.0, df2 / 2.0, df1 * x / (df1 * x + df2))


def _gammainc(a, x):
    """Lower incomplete gamma function approximation."""
    if x < 0:
        return 0
    if x == 0:
        return 0
    if x < a + 1:
        s = 1.0 / a
        term = 1.0 / a
        for n in range(1, 200):
            term *= x / (a + n)
            s += term
            if abs(term) < 1e-10:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    else:
        b = x + 1 - a
        c = 1e30
        d = 1.0 / b
        h = d
        for i in range(1, 200):
            an = -i * (i - a)
            b += 2
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1) < 1e-10:
                break
        return 1.0 - h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _betai(a, b, x):
    """Incomplete beta function approximation."""
    if x < 0 or x > 1:
        return 0
    if x == 0 or x == 1:
        return x
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def _betacf(a, b, x):
    """Continued fraction for incomplete beta."""
    max_iter = 200
    eps = 1e-10
    m, m2 = 1, 1
    aa = 1.0
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        even = m % 2 == 0
        if even:
            t1 = m * (b - m) * x / ((qam + m2) * (a + m2))
        else:
            t1 = -(a + m - 1 + m * (b - m) * x / ((qam + m2) * (a + m2)))
        d = 1.0 + t1 * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + t1 / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        if abs(d * c - 1) < eps:
            break
    return h


def _ztest(mu0, sigma, xbar, n):
    if n <= 0 or sigma <= 0:
        raise ValueError('Error: n and sigma must be > 0')
    z = (xbar - mu0) / (sigma / math.sqrt(n))
    p = 2 * (1 - _normalcdf(0, abs(z)))
    return {'z': z, 'p': p, 'mu0': mu0, 'xbar': xbar, 'n': n}


def _ttest(mu0, s, xbar, n):
    if n <= 1:
        raise ValueError('Error: n must be > 1')
    t = (xbar - mu0) / (s / math.sqrt(n))
    df = n - 1
    return {'t': t, 'df': df, 'mu0': mu0, 'xbar': xbar, 'n': n}


# ── Piecewise & System Solver ────────────────────────

def _piecewise(args, eng):
    """piecewise(expr1, cond1, expr2, cond2, ...)"""
    for i in range(0, len(args) - 1, 2):
        cond = args[i + 1]
        if isinstance(cond, str):
            cond = eng.eval_expr(cond)
        if cond:
            val = args[i]
            if isinstance(val, str):
                val = eng.eval_expr(val)
            return val
    if len(args) % 2 == 1:
        val = args[-1]
        if isinstance(val, str):
            val = eng.eval_expr(val)
        return val
    return 0


def _solve2(args, eng):
    """solve2([eq1_str, eq2_str], [x_init, y_init]) — Newton's method for 2x2 system."""
    if len(args) < 3:
        raise ValueError('Error: solve2([eq1,eq2], [x0,y0])')
    eq1_str = str(args[0])
    eq2_str = str(args[1])
    x0 = float(args[2]) if not isinstance(args[2], str) else 0.0
    y0 = float(args[3]) if len(args) > 3 and not isinstance(args[3], str) else 0.0
    x, y = x0, y0
    h = 1e-6
    for _ in range(50):
        eng.memory['x'] = x
        eng.memory['y'] = y
        f1 = eng.eval_expr(eq1_str)
        f2 = eng.eval_expr(eq2_str)
        if abs(f1) < 1e-10 and abs(f2) < 1e-10:
            break
        eng.memory['x'] = x + h
        j11 = (eng.eval_expr(eq1_str) - f1) / h
        j21 = (eng.eval_expr(eq2_str) - f2) / h
        eng.memory['x'] = x
        eng.memory['y'] = y + h
        j12 = (eng.eval_expr(eq1_str) - f1) / h
        j22 = (eng.eval_expr(eq2_str) - f2) / h
        eng.memory['x'] = x
        eng.memory['y'] = y
        det = j11 * j22 - j12 * j21
        if abs(det) < 1e-12:
            raise ValueError('Error: Singular (no unique solution)')
        dx = (-f1 * j22 + f2 * j12) / det
        dy = (-f2 * j11 + f1 * j21) / det
        x += dx
        y += dy
        if abs(dx) < 1e-10 and abs(dy) < 1e-10:
            break
    return {'x': round(x, 8), 'y': round(y, 8)}
