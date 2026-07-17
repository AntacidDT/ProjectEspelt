
_BG = 0x0000
_FG = 0xFFFF
_ACCENT = 0x07FF
_GREEN = 0x07E0
_RED = 0xF800
_YELLOW = 0xFFE0
_GRAY = 0x8410
_DGRAY = 0x4208

HEADER_H = 24
LINE_H = 16
CAT_Y = 26
CAT_H = 156
FORMULA_Y = 184
FORMULA_H = 72
INPUT_Y = 260
INPUT_H = 50
RESULT_Y = 312
RESULT_H = 8


def set_theme(theme_colors):
    global _BG, _FG, _ACCENT, _GREEN, _RED, _YELLOW, _GRAY, _DGRAY
    _BG = theme_colors['bg']
    _FG = theme_colors['white']
    _ACCENT = theme_colors['accent']
    _GREEN = theme_colors['green']
    _YELLOW = theme_colors['yellow']
    _RED = theme_colors['red']
    _GRAY = _DGRAY


def render_header(tft, title):
    tft.fill_rect(0, 0, 480, HEADER_H, 0x1082)
    tft.text15(title, 4, 4, _ACCENT, 0x1082)
    tft.hline(0, HEADER_H, 480, _ACCENT)


def render_categories(tft, cats, selected, scroll):
    tft.fill_rect(0, CAT_Y, 480, CAT_H, _BG)
    visible = CAT_H // LINE_H
    start = max(0, scroll)
    end = min(len(cats), start + visible)
    y = CAT_Y
    for i in range(start, end):
        key, label = cats[i]
        bg = _ACCENT if i == selected else _BG
        tft.fill_rect(0, y, 480, LINE_H, bg)
        prefix = '> ' if i == selected else '  '
        tft.text15(prefix + label[:36], 4, y, _FG if i == selected else _GRAY, bg)
        y += LINE_H
    tft.hline(0, FORMULA_Y, 480, _DGRAY)


def render_formulas(tft, formulas, selected, scroll):
    tft.fill_rect(0, FORMULA_Y, 480, FORMULA_H, _BG)
    visible = FORMULA_H // LINE_H
    start = max(0, scroll)
    end = min(len(formulas), start + visible)
    y = FORMULA_Y
    for i in range(start, end):
        formula, desc = formulas[i]
        bg = _GREEN if i == selected else _BG
        tft.fill_rect(0, y, 480, LINE_H, bg)
        prefix = '> ' if i == selected else '  '
        tft.text15(prefix + formula[:36], 4, y, _FG if i == selected else _YELLOW, bg)
        y += LINE_H


def render_input_area(tft, formula_info, var_values, editing_var, cursor_pos):
    tft.fill_rect(0, INPUT_Y, 480, INPUT_H, _BG)
    tft.hline(0, INPUT_Y, 480, _ACCENT)
    if not formula_info:
        tft.text15('Select a formula', 4, INPUT_Y + 4, _GRAY, _BG)
        return
    vars_list = formula_info.get('vars', [])
    x = 4
    y = INPUT_Y + 4
    for var in vars_list:
        val = var_values.get(var, '_')
        is_editing = (var == editing_var)
        if is_editing:
            tft.fill_rect(x - 2, y - 1, len(var) * 12 + 50, LINE_H, _ACCENT)
            tft.text15(var + '=' + val + '_', x, y, _FG, _ACCENT)
        else:
            tft.text15(var + '=' + val, x, y, _YELLOW, _BG)
        x += len(var) * 12 + 50
        if x > 400:
            x = 4
            y += LINE_H
    tft.text15('Enter=calc  Tab=next  Esc=back', 4, INPUT_Y + 36, _GRAY, _BG)


def render_result(tft, msg, is_error=False):
    tft.fill_rect(0, RESULT_Y, 480, RESULT_H, _BG)
    color = _GREEN if not is_error else _RED
    tft.text15(msg[:58], 4, RESULT_Y, color, _BG)


def render_full(tft, title, cats, cat_scroll, cat_sel,
                formulas, form_scroll, form_sel,
                formula_info, var_values, editing_var,
                result_msg='', result_error=False):
    tft.fill(_BG)
    render_header(tft, title)
    render_categories(tft, cats, cat_sel, cat_scroll)
    render_formulas(tft, formulas, form_sel, form_scroll)
    render_input_area(tft, formula_info, var_values, editing_var, 0)
    if result_msg:
        render_result(tft, result_msg, result_error)
