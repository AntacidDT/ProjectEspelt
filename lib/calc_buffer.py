_LF = {
    'F': (1, 2),
    'P': (1, 2),
    'S': (1,),
    'I': (1, 2, 3),
    'M': (2, 3, 4),
    'D': (2,),
    'L': (3,),
    'R': (1, 2),
}


def mk_frac():
    return ['F', [], []]


def mk_power():
    return ['P', [], []]


def mk_sqrt():
    return ['S', []]


def mk_integral():
    return ['I', [], [], []]


def mk_sum():
    return ['M', 'i', [], [], []]


def mk_deriv():
    return ['D', 'x', []]


def mk_limit():
    return ['L', 'x', '0', []]


def mk_subscript():
    return ['R', [], []]


class MathBuffer:
    def __init__(self):
        self.top = []
        self.cl = self.top
        self.ci = 0
        self.stk = []

    def left(self):
        if self.ci > 0:
            self.ci -= 1
        elif self.stk:
            self._xb()

    def right(self):
        if self.ci < len(self.cl):
            self.ci += 1
        elif self.stk:
            self._xf()

    def tab(self):
        if self.ci < len(self.cl):
            e = self.cl[self.ci]
            if isinstance(e, list) and len(e) > 1:
                lf = _LF.get(e[0])
                if lf:
                    self.stk.append((self.cl, self.ci, 0))
                    self.cl = e[lf[0]]
                    self.ci = len(self.cl)
                    return
        self._xf()

    def enter(self):
        if not self.stk and self.ci >= len(self.cl):
            return 'evaluate'
        if not self.stk and len(self.cl) > 0:
            return 'evaluate'
        self.tab()
        return 'input'

    def backspace(self):
        if self.ci > 0:
            self.cl.pop(self.ci - 1)
            self.ci -= 1
        elif self.stk:
            self._xb()
            if self.ci > 0:
                self.cl.pop(self.ci - 1)
                self.ci -= 1

    def insert(self, elem):
        self.cl.insert(self.ci, elem)
        self.ci += 1

    def clear(self):
        self.top.clear()
        self.cl = self.top
        self.ci = 0
        self.stk.clear()

    def is_empty(self):
        return len(self.top) == 0 and not self.stk

    def at_top(self):
        return not self.stk

    def exit_to_top(self):
        self.cl = self.top
        self.ci = len(self.top)
        self.stk.clear()

    def _xf(self):
        if not self.stk:
            return
        pl, ni, lfi = self.stk.pop()
        node = pl[ni]
        lf = _LF.get(node[0], ())
        nlfi = lfi + 1
        if nlfi < len(lf):
            self.stk.append((pl, ni, nlfi))
            self.cl = node[lf[nlfi]]
            self.ci = len(self.cl)
        else:
            self.cl = pl
            self.ci = ni + 1

    def _xb(self):
        if not self.stk:
            return
        pl, ni, lfi = self.stk.pop()
        node = pl[ni]
        lf = _LF.get(node[0], ())
        nlfi = lfi - 1
        if nlfi >= 0:
            self.stk.append((pl, ni, nlfi))
            self.cl = node[lf[nlfi]]
            self.ci = 0
        else:
            self.cl = pl
            self.ci = ni

    def load_string(self, s):
        self.clear()
        for ch in s:
            self.top.append(ch)
        self.ci = len(self.top)

    def flatten(self, elems=None):
        if elems is None:
            elems = self.top
        r = ''
        for e in elems:
            if isinstance(e, str):
                r += e
            elif isinstance(e, list):
                t = e[0]
                if t == 'F':
                    n = self.flatten(e[1])
                    d = self.flatten(e[2])
                    r += '(' + (n or '0') + ')/(' + (d or '0') + ')'
                elif t == 'P':
                    b = self.flatten(e[1])
                    x = self.flatten(e[2])
                    if b:
                        r += '(' + b + ')^(' + (x or '0') + ')'
                    else:
                        r += '(' + (x or '0') + ')'
                elif t == 'S':
                    r += 'sqrt(' + (self.flatten(e[1]) or '0') + ')'
                elif t == 'I':
                    r += 'integral(' + self.flatten(e[1]) + ',' + self.flatten(e[2]) + ',' + self.flatten(e[3]) + ')'
                elif t == 'M':
                    r += 'sum(' + e[1] + ',' + self.flatten(e[2]) + ',' + self.flatten(e[3]) + ',' + self.flatten(e[4]) + ')'
                elif t == 'D':
                    r += 'derivative(' + e[1] + ',' + self.flatten(e[2]) + ')'
                elif t == 'L':
                    r += 'lim(' + e[1] + ',' + e[2] + ',' + self.flatten(e[3]) + ')'
                elif t == 'R':
                    b = self.flatten(e[1])
                    s = self.flatten(e[2])
                    r += '(' + (b or '0') + ')[' + (s or '0') + ']'
        return r
