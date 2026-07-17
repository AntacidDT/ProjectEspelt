
import math


def _is_num(e):
    return isinstance(e, (int, float))


def _is_var(e):
    return isinstance(e, str) and len(e) == 1 and e.isalpha()


def _is_sym(e):
    return isinstance(e, list) and len(e) > 0


def _sym(op, *args):
    return [op] + list(args)


def _detect_vars(e):
    if _is_var(e):
        return {e}
    if _is_num(e) or not _is_sym(e):
        return set()
    v = set()
    for arg in e[1:]:
        v |= _detect_vars(arg)
    return v


def _collect_terms(e):
    if not _is_sym(e) or e[0] != '+':
        return [e]
    terms = []
    for arg in e[1:]:
        terms.extend(_collect_terms(arg))
    return terms


def _collect_factors(e):
    if not _is_sym(e) or e[0] != '*':
        return [e]
    factors = []
    for arg in e[1:]:
        factors.extend(_collect_factors(arg))
    return factors


def _has_var(e, v):
    return v in _detect_vars(e)


def _is_poly_term(term, var):
    if _is_num(term):
        return True, 0
    if term == var:
        return True, 1
    if _is_sym(term) and term[0] == 'pow' and term[1] == var and _is_num(term[2]):
        return True, int(term[2])
    if _is_sym(term) and term[0] == '*':
        return True, sum(_get_pow(f, var) for f in _collect_factors(term))
    if _is_sym(term) and term[0] == 'neg':
        return _is_poly_term(term[1], var)
    return False, 0


def _get_pow(e, var):
    if _is_num(e):
        return 0
    if e == var:
        return 1
    if _is_sym(e) and e[0] == 'pow' and e[1] == var and _is_num(e[2]):
        return int(e[2])
    return 0


def simplify(e):
    if _is_num(e) or _is_var(e):
        return e
    if not _is_sym(e):
        return e
    op = e[0]
    if op == 'neg':
        a = simplify(e[1])
        if _is_num(a):
            return -a
        if _is_sym(a) and a[0] == 'neg':
            return a[1]
        return _sym('neg', a)
    if op == '+':
        args = [simplify(a) for a in e[1:]]
        nums = 0
        syms = []
        for a in args:
            if _is_num(a):
                nums += a
            elif _is_sym(a) and a[0] == 'neg' and _is_num(a[1]):
                nums -= a[1]
            else:
                syms.append(a)
        if not syms:
            return nums
        if nums == 0:
            return syms[0] if len(syms) == 1 else _sym('+', *syms)
        return _sym('+', nums, *syms)
    if op == '-':
        left = simplify(e[1])
        right = simplify(e[2])
        if _is_num(left) and _is_num(right):
            return left - right
        if right == 0:
            return left
        return _sym('-', left, right)
    if op == '*':
        args = [simplify(a) for a in e[1:]]
        nums = 1
        has_zero = False
        syms = []
        for a in args:
            if _is_num(a):
                nums *= a
                if a == 0:
                    has_zero = True
            elif _is_sym(a) and a[0] == 'neg' and _is_num(a[1]):
                nums *= -a[1]
            else:
                syms.append(a)
        if has_zero or nums == 0:
            return 0
        if nums == 1 and syms:
            return syms[0] if len(syms) == 1 else _sym('*', *syms)
        if nums == -1 and syms:
            return _sym('neg', syms[0]) if len(syms) == 1 else _sym('neg', _sym('*', *syms))
        if syms:
            return _sym('*', nums, *syms)
        return nums
    if op == '/':
        left = simplify(e[1])
        right = simplify(e[2])
        if _is_num(left) and _is_num(right):
            if right == 0:
                return _sym('/', left, right)
            return left / right
        return _sym('/', left, right)
    if op == 'pow':
        base = simplify(e[1])
        exp = simplify(e[2])
        if _is_num(base) and _is_num(exp):
            try:
                return base ** exp
            except:
                pass
        if _is_num(exp):
            if exp == 0:
                return 1
            if exp == 1:
                return base
            if _is_sym(base) and base[0] == 'pow' and _is_num(base[2]) and _is_num(exp):
                return simplify(_sym('pow', base[1], base[2] * exp))
        if _is_num(base):
            if base == 0:
                return 0
            if base == 1:
                return 1
        return _sym('pow', base, exp)
    if op == 'fn':
        a = simplify(e[1])
        if _is_num(a):
            try:
                return _eval_fn(e[2], a)
            except:
                pass
        return _sym('fn', e[2], a)
    if op == '=':
        return _sym('=', simplify(e[1]), simplify(e[2]))
    return e


def _eval_fn(fname, x):
    if fname == 'sin':
        return math.sin(x)
    if fname == 'cos':
        return math.cos(x)
    if fname == 'tan':
        return math.tan(x)
    if fname == 'asin':
        return math.asin(x)
    if fname == 'acos':
        return math.acos(x)
    if fname == 'atan':
        return math.atan(x)
    if fname == 'sqrt':
        return math.sqrt(x)
    if fname == 'ln':
        return math.log(x)
    if fname == 'log':
        return math.log10(x)
    if fname == 'exp':
        return math.exp(x)
    if fname == 'abs':
        return abs(x)
    if fname == 'floor':
        return math.floor(x)
    if fname == 'ceil':
        return math.ceil(x)
    if fname == 'fact':
        r = 1
        for i in range(2, int(x) + 1):
            r *= i
        return r
    raise ValueError('Unknown function: ' + fname)


def diff(e, var):
    if _is_num(e) or (not _is_sym(e) and not _is_var(e)):
        return 0
    if _is_var(e):
        return 1 if e == var else 0
    op = e[0]
    if op == 'neg':
        return _sym('neg', diff(e[1], var))
    if op == '+':
        parts = [diff(a, var) for a in e[1:]]
        r = _sym('+', *parts) if len(parts) > 1 else parts[0]
        return simplify(r)
    if op == '-':
        return simplify(_sym('-', diff(e[1], var), diff(e[2], var)))
    if op == '*':
        f = e[1]
        g = e[2] if len(e) > 2 else e[1]
        if len(e) > 2:
            g = _sym('*', *e[2:])
        df = diff(f, var)
        dg = diff(g, var)
        return simplify(_sym('+', _sym('*', df, g), _sym('*', f, dg)))
    if op == 'pow':
        base = e[1]
        exp = e[2]
        bhv = _has_var(base, var)
        ehv = _has_var(exp, var)
        if bhv and not ehv:
            return simplify(_sym('*', exp, _sym('pow', base, _sym('-', exp, 1)), diff(base, var)))
        if ehv and not bhv:
            return simplify(_sym('*', e, _sym('fn', 'ln', base), diff(exp, var)))
        return simplify(_sym('*', e, _sym('+', _sym('*', diff(exp, var), _sym('fn', 'ln', base)), _sym('*', exp, _sym('/', diff(base, var), base)))))
    if op == 'fn':
        fname = e[2]
        a = e[1]
        da = diff(a, var)
        if fname == 'sin':
            return simplify(_sym('*', da, _sym('fn', 'cos', a)))
        if fname == 'cos':
            return simplify(_sym('neg', _sym('*', da, _sym('fn', 'sin', a))))
        if fname == 'tan':
            return simplify(_sym('*', da, _sym('+', 1, _sym('pow', _sym('fn', 'tan', a), 2))))
        if fname == 'ln':
            return simplify(_sym('*', da, _sym('/', 1, a)))
        if fname == 'exp':
            return simplify(_sym('*', da, e))
        if fname == 'sqrt':
            return simplify(_sym('*', da, _sym('/', 1, _sym('*', 2, _sym('fn', 'sqrt', a)))))
        if fname == 'asin':
            return simplify(_sym('*', da, _sym('/', 1, _sym('fn', 'sqrt', _sym('-', 1, _sym('pow', a, 2))))))
        if fname == 'acos':
            return simplify(_sym('neg', _sym('*', da, _sym('/', 1, _sym('fn', 'sqrt', _sym('-', 1, _sym('pow', a, 2)))))))
        if fname == 'atan':
            return simplify(_sym('*', da, _sym('/', 1, _sym('+', 1, _sym('pow', a, 2)))))
        return _sym('*', da, _sym('fn', 'd_' + fname, a))
    if op == '=':
        return _sym('=', diff(e[1], var), diff(e[2], var))
    return 0


def integrate(e, var):
    if _is_num(e):
        return _sym('*', e, var)
    if _is_var(e):
        if e == var:
            return _sym('/', _sym('pow', var, 2), 2)
        return _sym('*', e, var)
    if not _is_sym(e):
        return _sym('*', e, var)
    op = e[0]
    if op == 'neg':
        return _sym('neg', integrate(e[1], var))
    if op == '+':
        parts = [integrate(a, var) for a in e[1:]]
        return simplify(_sym('+', *parts) if len(parts) > 1 else parts[0])
    if op == '-':
        return simplify(_sym('-', integrate(e[1], var), integrate(e[2], var)))
    if op == '*':
        if _is_num(e[1]):
            return simplify(_sym('*', e[1], integrate(e[2], var)))
        if len(e) > 2 and _is_num(e[2]):
            return simplify(_sym('*', e[2], integrate(e[1], var)))
        return _sym('*', e, var)
    if op == 'pow':
        base = e[1]
        exp = e[2]
        if base == var and _is_num(exp):
            if exp == -1:
                return _sym('fn', 'ln', _sym('abs', var))
            return simplify(_sym('/', _sym('pow', var, _sym('+', exp, 1)), _sym('+', exp, 1)))
    if op == 'fn':
        fname = e[2]
        a = e[1]
        if a == var:
            if fname == 'sin':
                return _sym('neg', _sym('fn', 'cos', var))
            if fname == 'cos':
                return _sym('fn', 'sin', var)
            if fname == 'exp':
                return _sym('fn', 'exp', var)
            if fname == 'ln':
                return _sym('-', _sym('*', var, _sym('fn', 'ln', var)), var)
        return _sym('*', e, var)
    return _sym('*', e, var)


def expand(e):
    if not _is_sym(e):
        return e
    op = e[0]
    if op == '+':
        return simplify(_sym('+', *[expand(a) for a in e[1:]]))
    if op == '-':
        return simplify(_sym('-', expand(e[1]), expand(e[2])))
    if op == '*':
        if len(e) < 3:
            return simplify(expand(e[1]))
        left = expand(e[1])
        right = expand(_sym('*', *e[2:]))
        if _is_num(left) or _is_num(right):
            return simplify(_sym('*', left, right))
        if _is_sym(left) and left[0] == '+':
            return simplify(_sym('+', *[expand(_sym('*', t, right)) for t in left[1:]]))
        if _is_sym(right) and right[0] == '+':
            return simplify(_sym('+', *[expand(_sym('*', left, t)) for t in right[1:]]))
        return simplify(_sym('*', left, right))
    if op == 'pow':
        base = expand(e[1])
        exp = e[2]
        if _is_num(exp) and exp == int(exp) and exp > 0:
            n = int(exp)
            if n == 1:
                return base
            result = base
            for _ in range(n - 1):
                result = expand(_sym('*', result, base))
            return simplify(result)
        return _sym('pow', base, exp)
    return simplify(e)


def factor(e):
    if not _is_sym(e):
        return e
    op = e[0]
    if op == '+':
        terms = _collect_terms(e)
        gcf = None
        for t in terms:
            factors_t = _collect_factors(t)
            if gcf is None:
                gcf = set(factors_t)
            else:
                gcf &= set(factors_t)
        if gcf:
            remaining = []
            for t in terms:
                factors_t = _collect_factors(t)
                r = None
                for f in factors_t:
                    if f in gcf:
                        continue
                    r = f if r is None else _sym('*', r, f)
                remaining.append(r if r is not None else 1)
            gcf_expr = _sym('*', *gcf) if len(gcf) > 1 else list(gcf)[0] if gcf else 1
            rem_expr = _sym('+', *remaining)
            return simplify(_sym('*', gcf_expr, simplify(rem_expr)))
        return e
    if op == 'pow':
        base = e[1]
        exp = e[2]
        if _is_num(exp) and exp == 2 and _is_sym(base) and base[0] == '+':
            if len(base) == 3:
                a = base[1]
                b = base[2]
                if _is_var(a) and _is_num(b) and b > 0:
                    sq = math.sqrt(b)
                    if sq == int(sq):
                        s = int(sq)
                        return simplify(_sym('*', _sym('-', a, s), _sym('+', a, s)))
        return e
    return e


def solve_eq(e, var):
    if not _is_sym(e) or e[0] != '=':
        return []
    left = e[1]
    right = e[2]
    expr = simplify(_sym('-', left, right))
    deg = _poly_degree(expr, var)
    if deg == 0:
        val = simplify(expr)
        if _is_num(val) and val == 0:
            return ['All ' + var]
        return []
    if deg == 1:
        coeffs = _poly_coeffs(expr, var)
        a = coeffs[1] if len(coeffs) > 1 else 1
        b = coeffs[0] if len(coeffs) > 0 else 0
        if a == 0:
            return []
        x = simplify(_sym('/', _sym('neg', b), a))
        return [to_str(x)]
    if deg == 2:
        coeffs = _poly_coeffs(expr, var)
        a = coeffs[2] if len(coeffs) > 2 else 0
        b = coeffs[1] if len(coeffs) > 1 else 0
        c = coeffs[0] if len(coeffs) > 0 else 0
        if a == 0:
            return solve_eq(_sym('=', _sym('+', _sym('*', b, var), c), 0), var)
        disc = b * b - 4 * a * c
        if disc < 0:
            return ['No real solutions']
        if disc == 0:
            x = simplify(_sym('/', _sym('neg', b), _sym('*', 2, a)))
            return [to_str(x) + ' (double root)']
        sq = math.sqrt(disc)
        x1 = simplify(_sym('/', _sym('-', _sym('neg', b), sq), _sym('*', 2, a)))
        x2 = simplify(_sym('/', _sym('+', _sym('neg', b), sq), _sym('*', 2, a)))
        return [to_str(x1), to_str(x2)]
    return ['Degree {} — not supported'.format(deg)]


def _poly_degree(e, var):
    if _is_var(e) and e == var:
        return 1
    if _is_num(e) or (_is_var(e) and e != var):
        return 0
    if not _is_sym(e):
        return 0
    if e[0] == 'pow' and e[1] == var and _is_num(e[2]):
        return int(e[2])
    if e[0] == '+':
        return max(_poly_degree(a, var) for a in e[1:])
    if e[0] == '*':
        return sum(_poly_degree(a, var) for a in e[1:])
    if e[0] == 'neg':
        return _poly_degree(e[1], var)
    if e[0] == '-':
        return max(_poly_degree(e[1], var), _poly_degree(e[2], var))
    return 0


def _poly_coeffs(e, var):
    deg = _poly_degree(e, var)
    if deg == 0:
        val = simplify(e)
        return [val] if _is_num(val) else [0]
    coeffs = [0] * (deg + 1)
    terms = _collect_terms(e)
    for t in terms:
        c, d = _term_coeff_pow(t, var)
        if d <= deg:
            coeffs[d] += c
    return coeffs


def _term_coeff_pow(e, var):
    if _is_num(e):
        return e, 0
    if e == var:
        return 1, 1
    if _is_sym(e) and e[0] == 'pow' and e[1] == var and _is_num(e[2]):
        return 1, int(e[2])
    if _is_sym(e) and e[0] == 'neg':
        c, d = _term_coeff_pow(e[1], var)
        return -c, d
    if _is_sym(e) and e[0] == '*':
        c = 1
        d = 0
        for f in _collect_factors(e):
            if _is_num(f):
                c *= f
            else:
                cf, df = _term_coeff_pow(f, var)
                c *= cf
                d += df
        return c, d
    return simplify(e), 0


def to_str(e):
    if _is_num(e):
        if e == int(e) and abs(e) < 1e15:
            return str(int(e))
        return '{:.6g}'.format(e)
    if _is_var(e):
        return e
    if not _is_sym(e):
        return str(e)
    op = e[0]
    if op == 'neg':
        s = to_str(e[1])
        if _is_sym(e[1]) and e[1][0] in ('+', '-'):
            return '-(' + s + ')'
        return '-' + s
    if op == '+':
        parts = []
        for i, arg in enumerate(e[1:]):
            s = to_str(arg)
            if i == 0:
                parts.append(s)
            elif _is_sym(arg) and arg[0] == 'neg':
                parts.append('-' + to_str(arg[1]))
            elif _is_num(arg) and arg < 0:
                parts.append('-' + to_str(-arg))
            else:
                parts.append('+' + s)
        return ''.join(parts)
    if op == '-':
        return to_str(e[1]) + '-' + to_str(e[2])
    if op == '*':
        parts = []
        for arg in e[1:]:
            parts.append(_fmt_mul_factor(arg))
        return '*'.join(parts)
    if op == '/':
        left = to_str(e[1])
        right = to_str(e[2])
        if _is_sym(e[1]) and e[1][0] in ('+', '-'):
            left = '(' + left + ')'
        if _is_sym(e[2]) and e[2][0] in ('+', '-'):
            right = '(' + right + ')'
        return left + '/' + right
    if op == 'pow':
        base = to_str(e[1])
        exp = to_str(e[2])
        if _is_sym(e[1]) and e[1][0] in ('+', '-', '*', '/'):
            base = '(' + base + ')'
        return base + '^' + exp
    if op == 'fn':
        return e[2] + '(' + to_str(e[1]) + ')'
    if op == '=':
        return to_str(e[1]) + ' = ' + to_str(e[2])
    return str(e)


def _fmt_mul_factor(e):
    s = to_str(e)
    if _is_sym(e) and e[0] in ('+', '-'):
        return '(' + s + ')'
    return s


def _pretty_poly(e, var):
    if not _is_sym(e) or e[0] not in ('+', '-'):
        return to_str(e)
    parts = []
    terms = _collect_terms(e)
    for i, term in enumerate(terms):
        if _is_num(term):
            s = str(int(term)) if term == int(term) else '{:.4g}'.format(term)
            if i > 0 and term > 0:
                s = '+' + s
            parts.append(s)
        elif _is_sym(term) and term[0] == 'neg' and _is_num(term[1]):
            s = str(int(term[1])) if term[1] == int(term[1]) else '{:.4g}'.format(term[1])
            parts.append('-' + s)
        else:
            s = to_str(term)
            if i > 0 and s[0] not in ('-', '+'):
                s = '+' + s
            parts.append(s)
    return ''.join(parts) if parts else '0'


def _cas_tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i] in ' \t':
            i += 1
            continue
        if expr[i] in '+-*/^=(),':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit() or (expr[i] == '.' and i + 1 < len(expr) and expr[i + 1].isdigit()):
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            if j < len(expr) and expr[j] in 'eE':
                j += 1
                if j < len(expr) and expr[j] in '+-':
                    j += 1
                while j < len(expr) and expr[j].isdigit():
                    j += 1
            tokens.append(expr[i:j])
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalpha() or expr[j].isdigit() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            i += 1
    return tokens


def _cas_parse(expr_str):
    expr_str = expr_str.strip()
    tokens = _cas_tokenize(expr_str)
    pos = [0]

    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None

    def consume(expected=None):
        t = peek()
        if expected and t != expected:
            return None
        pos[0] += 1
        return t

    def parse_expr():
        return parse_add_sub()

    def parse_add_sub():
        left = parse_mul_div()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_mul_div()
            if op == '+':
                left = _sym('+', left, right)
            else:
                left = _sym('-', left, right)
        return left

    def parse_mul_div():
        left = parse_power()
        while peek() in ('*', '/'):
            op = consume()
            right = parse_power()
            if op == '*':
                left = _sym('*', left, right)
            else:
                left = _sym('/', left, right)
        return left

    def parse_power():
        left = parse_unary()
        if peek() == '^':
            consume()
            right = parse_unary()
            return _sym('pow', left, right)
        return left

    def parse_unary():
        if peek() == '-':
            consume()
            return _sym('neg', parse_unary())
        if peek() == '+':
            consume()
            return parse_unary()
        return parse_primary()

    def parse_primary():
        t = peek()
        if t is None:
            return 0
        if t == '(':
            consume('(')
            result = parse_expr()
            consume(')')
            return result
        if _is_number_token(t):
            consume()
            return float(t) if '.' in t or 'e' in t.lower() else int(t)
        if t.isalpha() or (t and t[0] == '_'):
            name = consume()
            if peek() == '(':
                consume('(')
                args = [parse_expr()]
                while peek() == ',':
                    consume(',')
                    args.append(parse_expr())
                consume(')')
                if len(args) == 1:
                    return _sym('fn', args[0], name)
                return _sym('fn', args[0], name)
            if peek() == '^':
                consume()
                exp = parse_unary()
                return _sym('pow', name, exp)
            if peek() is not None and peek().isalpha():
                right = parse_primary()
                return _sym('*', name, right)
            return name
        consume()
        return 0

    return simplify(parse_expr())


def _is_number_token(t):
    if t is None:
        return False
    if t[0].isdigit():
        return True
    if t[0] == '-' and len(t) > 1:
        return True
    return False


def _find_eq_sign(expr_str):
    depth = 0
    i = 0
    while i < len(expr_str):
        c = expr_str[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '=' and depth == 0:
            if i + 1 < len(expr_str) and expr_str[i + 1] == '=':
                i += 2
                continue
            if i > 0 and expr_str[i - 1] == '!':
                i += 1
                continue
            return i
        i += 1
    return -1


def cas_eval(expr_str):
    import re
    expr_str = expr_str.strip()

    m = re.match(r'diff\((.+),\s*([a-zA-Z])\)', expr_str)
    if m:
        inner = _cas_parse(m.group(1))
        var = m.group(2)
        result = diff(inner, var)
        simplified = simplify(result)
        vs = _detect_vars(simplified)
        display = _pretty_poly(simplified, list(vs)[0]) if vs else to_str(simplified)
        return to_str(simplified), display

    m = re.match(r'int\((.+),\s*([a-zA-Z])\)', expr_str)
    if m:
        inner = _cas_parse(m.group(1))
        var = m.group(2)
        result = integrate(inner, var)
        simplified = simplify(result)
        vs = _detect_vars(simplified)
        display = _pretty_poly(simplified, list(vs)[0]) if vs else to_str(simplified)
        return to_str(simplified), display + ' + C'

    m = re.match(r'solve\((.+),\s*([a-zA-Z])\)', expr_str)
    if m:
        eq_str = m.group(1)
        var = m.group(2)
        eq_sign = _find_eq_sign(eq_str)
        if eq_sign >= 0:
            left = _cas_parse(eq_str[:eq_sign])
            right = _cas_parse(eq_str[eq_sign + 1:])
            eq = _sym('=', left, right)
            solutions = solve_eq(eq, var)
            if not solutions:
                return 'No solutions', 'No solutions'
            result = var + ' = ' + ', '.join(solutions)
            return result, result
        return 'solve: invalid equation', 'solve: invalid equation'

    m = re.match(r'solve\((.+)\)', expr_str)
    if m:
        inner = m.group(1)
        eq_sign = _find_eq_sign(inner)
        if eq_sign >= 0:
            left = _cas_parse(inner[:eq_sign])
            right = _cas_parse(inner[eq_sign + 1:])
            eq = _sym('=', left, right)
            vs = _detect_vars(eq)
            if len(vs) == 1:
                var = list(vs)[0]
                solutions = solve_eq(eq, var)
                if not solutions:
                    return 'No solutions', 'No solutions'
                result = var + ' = ' + ', '.join(solutions)
                return result, result
            return 'solve: specify variable', 'solve: specify variable'
        return 'solve: specify variable', 'solve: specify variable'

    m = re.match(r'expand\((.+)\)', expr_str)
    if m:
        inner = _cas_parse(m.group(1))
        result = expand(inner)
        simplified = simplify(result)
        vs = _detect_vars(simplified)
        display = _pretty_poly(simplified, list(vs)[0]) if vs else to_str(simplified)
        return to_str(simplified), display

    m = re.match(r'factor\((.+)\)', expr_str)
    if m:
        inner = _cas_parse(m.group(1))
        result = factor(inner)
        simplified = simplify(result)
        return to_str(simplified), to_str(simplified)

    eq_sign = _find_eq_sign(expr_str)
    if eq_sign >= 0:
        left = _cas_parse(expr_str[:eq_sign])
        right = _cas_parse(expr_str[eq_sign + 1:])
        eq = _sym('=', left, right)
        vs = _detect_vars(eq)
        if len(vs) == 1:
            var = list(vs)[0]
            solutions = solve_eq(eq, var)
            if solutions:
                result = var + ' = ' + ', '.join(solutions)
                return result, result

    tree = _cas_parse(expr_str)
    simplified = simplify(tree)
    vs = _detect_vars(simplified)
    if vs:
        display = _pretty_poly(simplified, list(vs)[0])
    else:
        display = to_str(simplified)
    return to_str(simplified), display
