from lib.calc_buffer import (
    mk_frac, mk_power, mk_sqrt, mk_integral,
    mk_sum, mk_deriv, mk_limit, mk_subscript
)


def _is_capturable(e):
    if isinstance(e, str):
        return e.isalpha() or e.isdigit() or e in ('.', ')', ']')
    if isinstance(e, list):
        return True
    return False


def _capture_last(buf):
    if buf.ci > 0 and buf.at_top():
        prev = buf.cl[buf.ci - 1]
        if _is_capturable(prev):
            buf.cl.pop(buf.ci - 1)
            buf.ci -= 1
            return prev
    return None


def _enter_field(buf, node, lfi):
    from lib.calc_buffer import _LF
    lf = _LF.get(node[0], ())
    if lfi < len(lf):
        fi = lf[lfi]
        buf.stk.append((buf.cl, buf.ci - 1, lfi))
        buf.cl = node[fi]
        buf.ci = len(buf.cl)


def handle_key(ch, buf, frac_mode, help_lines, state):
    if ch == '\x85':
        buf.left()
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x84':
        buf.right()
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x80':
        buf.exit_to_top()
        return 'hist_prev', frac_mode, help_lines, 'normal'

    if ch == '\x81':
        buf.exit_to_top()
        return 'hist_next', frac_mode, help_lines, 'normal'

    if ch == '\x06':
        cap = _capture_last(buf)
        nd = mk_frac()
        if cap is not None:
            nd[1].append(cap)
        buf.insert(nd)
        _enter_field(buf, nd, 1)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x05':
        cap = _capture_last(buf)
        nd = mk_power()
        if cap is not None:
            nd[1].append(cap)
        buf.insert(nd)
        _enter_field(buf, nd, 1)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x02':
        nd = mk_sqrt()
        buf.insert(nd)
        _enter_field(buf, nd, 0)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x1e':
        nd = mk_integral()
        buf.insert(nd)
        _enter_field(buf, nd, 0)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x13':
        nd = mk_sum()
        buf.insert(nd)
        _enter_field(buf, nd, 0)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x04':
        nd = mk_deriv()
        buf.insert(nd)
        _enter_field(buf, nd, 0)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x0c':
        if buf.is_empty() and buf.at_top():
            return 'clear', frac_mode, help_lines, 'normal'
        nd = mk_limit()
        buf.insert(nd)
        _enter_field(buf, nd, 0)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x12':
        cap = _capture_last(buf)
        nd = mk_subscript()
        if cap is not None:
            nd[1].append(cap)
        buf.insert(nd)
        _enter_field(buf, nd, 1)
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x07':
        return 'graph', frac_mode, help_lines, 'normal'

    if ch == '\x15':
        return 'cas_toggle', frac_mode, help_lines, 'normal'

    if ch == '\r':
        buf.insert('%')
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x18':
        return 'exit', frac_mode, help_lines, 'normal'

    if ch == '\n':
        action = buf.enter()
        return action, frac_mode, help_lines, 'normal'

    if ch == '\t':
        buf.tab()
        return 'input', frac_mode, help_lines, 'normal'

    if ch == '\x1b':
        buf.clear()
        return 'escape', frac_mode, help_lines, 'normal'

    if ch == '\x03':
        buf.clear()
        return 'escape', frac_mode, help_lines, 'normal'

    if ch == '\b':
        buf.backspace()
        return 'input', frac_mode, help_lines, 'normal'

    if len(ch) == 1 and 32 <= ord(ch) <= 126:
        buf.insert(ch)
        return 'input', frac_mode, help_lines, 'normal'

    return 'none', frac_mode, help_lines, 'normal'
