import time
import os


def _repl_loop(tft, read_key, header, dispatch_fn, help_pages, theme_colors=None, tab_commands=None, oled=None):
    """10/10 REPL: two-panel output, auto-clear, paginated help, tab completion."""
    lines = []
    step_lines = []
    buf = ''
    CW_L = 22
    CW_R = 14
    CONTENT_Y = 26
    PROMPT_Y = 272
    LINE_H = 16
    MAX_VIS = 15
    help_page = 0
    total_help_pages = len(help_pages)
    hist_file = '/sd/.' + header.replace(' ', '_').lower() + '_hist.txt'

    def _load_hist():
        try:
            with open(hist_file, 'r') as f:
                return [l.strip() for l in f.readlines() if l.strip()][-50:]
        except:
            return []

    def _save_hist(h):
        try:
            with open(hist_file, 'w') as f:
                for item in h[-50:]:
                    f.write(item + '\n')
        except:
            pass

    hist = _load_hist()
    hist_idx = -1

    def _header():
        try:
            from commands.dispatch import THEME_COLORS
            tc = THEME_COLORS
        except:
            tc = theme_colors
        c = tc.get('accent', 0x07FF) if tc else 0x07FF
        bg = tc.get('header', 0x1082) if tc else 0x1082
        fg = tc.get('green', 0x07E0) if tc else 0x07E0
        tft.fill_rect(0, 0, 480, 24, bg)
        tft.text15(header, max(0, (480 - len(header) * 12) // 2), 4, c, bg)
        tft.hline(0, 24, 480, c)

    def _draw_prompt():
        try:
            from commands.dispatch import THEME_COLORS
            tc = THEME_COLORS
        except:
            tc = theme_colors
        prompt_bg = tc.get('header', 0x1082) if tc else 0x1082
        prompt_fg = tc.get('green', 0x07E0) if tc else 0x07E0
        tft.fill_rect(0, PROMPT_Y, 480, 48, prompt_bg)
        prompt = '> ' + buf
        line1 = prompt[:38]
        line2 = prompt[38:76] if len(prompt) > 38 else ''
        tft.text15(line1, 4, PROMPT_Y + 4, prompt_fg, prompt_bg)
        if line2:
            tft.text15(line2, 4, PROMPT_Y + 20, prompt_fg, prompt_bg)
        tft.text('TAB Q', 380, PROMPT_Y + 4, 0x8410, prompt_bg)

    def _draw_content():
        tft.fill_rect(0, CONTENT_Y, 480, PROMPT_Y - CONTENT_Y, 0x0000)
        vis_l = lines[-MAX_VIS:] if len(lines) > MAX_VIS else lines
        vis_s = step_lines[-MAX_VIS:] if len(step_lines) > MAX_VIS else step_lines
        max_len = max(len(vis_l), len(vis_s))
        y = CONTENT_Y + 2
        for i in range(max_len):
            if i < len(vis_l):
                tft.text15(vis_l[i][:CW_L], 4, y, 0xFFFF, 0x0000)
            if i < len(vis_s):
                tft.text15(vis_s[i][:CW_R], 272, y, 0x07FF, 0x0000)
            y += LINE_H

    def _append_result(result_lines, steps=None):
        nonlocal lines, step_lines
        lines.clear()
        step_lines.clear()
        for l in result_lines:
            lines.append(l)
        if steps:
            for s in steps:
                step_lines.append(s)
        _draw_content()

    def _tab_complete():
        nonlocal buf
        if not tab_commands or not buf:
            return
        parts = buf.split()
        if not parts:
            return
        prefix = parts[-1].lower()
        matches = [c for c in tab_commands if c.lower().startswith(prefix)]
        if len(matches) == 1:
            parts[-1] = matches[0]
            buf = ' '.join(parts)
            _draw_prompt()
        elif len(matches) > 1:
            lines.clear()
            step_lines.clear()
            lines.append('  ' + ' '.join(matches[:8]))
            _draw_content()
            _draw_prompt()

    def _show_help():
        nonlocal help_page
        lines.clear()
        step_lines.clear()
        lines.append(f'=== Help ({help_page + 1}/{total_help_pages}) ===')
        lines.append('')
        for l in help_pages[help_page]:
            lines.append(l)
        if total_help_pages > 1:
            lines.append('')
            lines.append(f'ESC: next page ({help_page + 1}/{total_help_pages})')
        _draw_content()
        _draw_prompt()

    _header()
    _draw_content()
    _draw_prompt()

    while True:
        ch = read_key()
        if ch is None:
            continue
        if ch == 'q' or ch == 'Q':
            _save_hist(hist)
            return
        elif ch == '\x1b':
            if total_help_pages > 1:
                help_page = (help_page + 1) % total_help_pages
            _show_help()
        elif ch == '\t':
            _tab_complete()
        elif ch == '\n':
            if buf.strip():
                hist.append(buf.strip())
                if len(hist) > 50:
                    hist.pop(0)
                hist_idx = -1
                _save_hist(hist)
                result = dispatch_fn(buf.strip())
                new_lines = []
                new_steps = []
                if isinstance(result, tuple):
                    if result[0] == 'print_lines':
                        new_lines = result[1]
                    elif result[0] == 'print':
                        new_lines = result[1].split('\n')
                    elif result[0] == 'result_steps':
                        new_lines = result[1]
                        new_steps = result[2] if len(result) > 2 else []
                    elif result[0] == 'clear':
                        lines.clear()
                        step_lines.clear()
                        _draw_content()
                        buf = ''
                        _draw_prompt()
                        continue
                elif isinstance(result, list):
                    new_lines = [str(l) for l in result]
                elif isinstance(result, str):
                    new_lines = result.split('\n')
                if new_lines:
                    _append_result(new_lines, new_steps if new_steps else None)
                    if oled:
                        first_line = new_lines[0] if new_lines else ''
                        oled.set_engine_status(header.replace('Espelt ', ''),
                            line0=buf.strip()[:20],
                            line1=first_line[:20])
            buf = ''
            _draw_prompt()
        elif ch == '\b' or ch == '\x7f':
            if buf:
                buf = buf[:-1]
                _draw_prompt()
        elif ch == '\x80':
            if hist:
                if hist_idx == -1:
                    hist_idx = len(hist) - 1
                elif hist_idx > 0:
                    hist_idx -= 1
                buf = hist[hist_idx]
                _draw_prompt()
        elif ch == '\x81':
            if hist and hist_idx >= 0:
                if hist_idx < len(hist) - 1:
                    hist_idx += 1
                    buf = hist[hist_idx]
                else:
                    hist_idx = -1
                    buf = ''
                _draw_prompt()
        elif len(ch) == 1 and ord(ch) >= 32 and ord(ch) <= 126 and len(buf) < 76:
            buf += ch
            _draw_prompt()


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


def cmd_math(args, tft=None, oled_ctrl=None):
    if args.strip().lower() == 'physics':
        return cmd_physics('', tft, oled_ctrl)
    if not args.strip():
        def _calc_loop(tft, read_key):
            import time
            from commands.dispatch import THEME_COLORS
            from lib.calc_engine import CalcEngine
            from lib.calc_renderer import (
                render_header, render_prompt, render_results_area,
                render_math_display, render_error, render_info, _fmt_num, set_theme
            )
            from lib.calc_session import save_history, load_history, save_memory, load_memory
            from lib.calc_graph import graph_on_oled
            from lib.calc_input import handle_key
            from lib.calc_buffer import MathBuffer

            if THEME_COLORS:
                set_theme(THEME_COLORS)

            engine = CalcEngine()
            engine.memory = load_memory()
            saved_history = load_history()
            engine.history = list(saved_history)

            buf = MathBuffer()
            frac_mode = False
            results = []
            help_lines = []
            last_result = None
            state = 'normal'
            hist_idx = -1

            tft.fill(0x0000)
            tft.hline(0, 24, 480, 0x07FF)
            if oled_ctrl:
                oled_ctrl.set_engine_status('Math',
                    line0=engine.angle_mode + ' | H:' + str(len(engine.history)),
                    line1='CAS: ' + ('ON' if engine.cas_mode else 'OFF'))
            render_math_display(tft)
            render_prompt(tft, buf, frac_mode, engine.angle_mode)

            while True:
                ch = read_key()

                action, frac_mode, help_lines, state = handle_key(
                    ch, buf, frac_mode, help_lines, state
                )

                if action == 'exit':
                    save_history(engine.history)
                    save_memory(engine.memory)
                    tft.fill(0x0000)
                    tft.hline(0, 24, 480, 0x07FF)
                    render_info(tft, 'Saved! Exiting math...')
                    time.sleep_ms(400)
                    return

                elif action == 'clear':
                    tft.fill(0x0000)
                    tft.hline(0, 24, 480, 0x07FF)
                    results.clear()
                    engine.last_steps = []
                    last_result = None
                    render_math_display(tft)
                    render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'graph':
                    expr_str = buf.flatten()
                    if oled and expr_str.strip():
                        render_info(tft, 'Graphing on OLED...')
                        try:
                            graph_on_oled(oled._oled, expr_str)
                            render_info(tft, 'Graph plotted!')
                        except Exception as e:
                            render_error(tft, 'Graph error: ' + str(e)[:30])
                        time.sleep_ms(800)
                        render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'cas_toggle':
                    engine.cas_mode = not engine.cas_mode
                    mode = 'CAS ON' if engine.cas_mode else 'CAS OFF'
                    render_info(tft, mode + ' - symbolic algebra ' + ('enabled' if engine.cas_mode else 'disabled'))
                    time.sleep_ms(800)
                    render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'evaluate':
                    expr_str = buf.flatten()
                    if expr_str.strip():
                        results.append('> ' + expr_str)
                        try:
                            result = engine.eval_expr(expr_str.strip())
                            last_result = result
                            if isinstance(result, str):
                                result_str = result
                            else:
                                result_str = _fmt_num(result, frac_mode)
                            results.append('= ' + result_str)
                            render_results_area(tft, results, last_steps=engine.last_steps)
                            render_math_display(tft, result, frac_mode)
                            render_info(tft, '= ' + result_str[:36])
                            if oled_ctrl:
                                oled_ctrl.set_engine_status('Math',
                                    line0=engine.angle_mode + ' | H:' + str(len(engine.history)),
                                    line1='CAS: ' + ('ON' if engine.cas_mode else 'OFF'),
                                    line2='Ans=' + result_str[:18])
                                if oled_ctrl._oled and not isinstance(result, str):
                                    try:
                                        from lib.calc_graph import graph_on_oled
                                        graph_on_oled(oled._oled, expr_str)
                                    except:
                                        pass
                        except Exception as e:
                            err_msg = str(e)
                            results.append('Error: ' + err_msg)
                            engine.last_steps = []
                            render_results_area(tft, results)
                            render_math_display(tft)
                            render_error(tft, err_msg[:38])
                        if len(results) > 6:
                            results[:] = results[-6:]
                        buf.clear()
                        hist_idx = -1
                        tft.hline(0, 24, 480, 0x07FF)
                        render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'help':
                    if help_lines:
                        tft.fill(0x0000)
                        tft.hline(0, 24, 480, 0x07FF)
                        render_results_area(tft, help_lines)
                        render_math_display(tft, help_lines=help_lines[:2])
                        render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'escape':
                    buf.clear()
                    hist_idx = -1
                    render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'hist_prev':
                    if engine.history:
                        if hist_idx == -1:
                            hist_idx = len(engine.history) - 1
                        elif hist_idx > 0:
                            hist_idx -= 1
                        buf.load_string(engine.history[hist_idx])
                        render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'hist_next':
                    if engine.history and hist_idx >= 0:
                        if hist_idx < len(engine.history) - 1:
                            hist_idx += 1
                            buf.load_string(engine.history[hist_idx])
                        else:
                            hist_idx = -1
                            buf.clear()
                        render_prompt(tft, buf, frac_mode, engine.angle_mode)

                elif action == 'input':
                    render_prompt(tft, buf, frac_mode, engine.angle_mode)

                time.sleep_ms(10)

        return ('game', _calc_loop)
    expr = args.strip()
    try:
        from lib.calc_engine import CalcEngine
        from lib.calc_renderer import _fmt_num
        engine = CalcEngine()
        result = engine.eval_expr(expr)
        return ('print', '  = ' + _fmt_num(result))
    except Exception as e:
        return ('print', 'calc: ' + str(e))


def cmd_physics(args, tft=None, oled_ctrl=None):
    def _physics_loop(tft, read_key):
        import time
        from commands.dispatch import THEME_COLORS
        from lib.physics_engine import (
            get_category_display, get_formula_display, get_formula_info,
            solve_formula, format_result, PHYS_CONSTANTS, CONST_NAMES, CATEGORIES
        )
        from lib.physics_renderer import (
            set_theme, render_full, render_result, render_input_area,
            render_categories, render_formulas, render_header
        )

        if THEME_COLORS:
            set_theme(THEME_COLORS)

        screen = 'categories'
        cat_display = get_category_display()
        cat_sel = 0
        cat_scroll = 0
        formula_display = []
        form_sel = 0
        form_scroll = 0
        current_cat = None
        current_formula_info = None
        var_values = {}
        editing_var = None
        edit_buf = ''
        result_msg = ''
        result_error = False

        def _refresh():
            render_full(tft, 'Espelt Physics', cat_display, cat_scroll, cat_sel,
                       formula_display, form_scroll, form_sel,
                       current_formula_info, var_values, editing_var,
                       result_msg, result_error)

        tft.fill(0x0000)
        _refresh()

        while True:
            ch = read_key()

            if ch == '\x18':
                tft.fill(0x0000)
                render_header(tft, 'Espelt Physics')
                render_result(tft, 'Exiting physics...')
                time.sleep_ms(300)
                return

            if screen == 'categories':
                if ch == '\x80':
                    if cat_sel > 0:
                        cat_sel -= 1
                        if cat_sel < cat_scroll:
                            cat_scroll = cat_sel
                elif ch == '\x81':
                    if cat_sel < len(cat_display) - 1:
                        cat_sel += 1
                        visible = 156 // 16
                        if cat_sel >= cat_scroll + visible:
                            cat_scroll = cat_sel - visible + 1
                elif ch == '\n' or ch == '\x84':
                    cat_key = cat_display[cat_sel][0]
                    if cat_key == 'constants':
                        result_msg = 'c=3e8 g=9.81 G=6.67e-11'
                        result_error = False
                        _refresh()
                    else:
                        current_cat = cat_key
                        formula_display = get_formula_display(cat_key)
                        form_sel = 0
                        form_scroll = 0
                        screen = 'formulas'
                        formula_display_local = formula_display
                elif ch == '\x1b' or ch == '\x03':
                    tft.fill(0x0000)
                    render_header(tft, 'Espelt Physics')
                    render_result(tft, 'Exiting physics...')
                    time.sleep_ms(300)
                    return

            elif screen == 'formulas':
                if ch == '\x80':
                    if form_sel > 0:
                        form_sel -= 1
                        if form_sel < form_scroll:
                            form_scroll = form_sel
                elif ch == '\x81':
                    if form_sel < len(formula_display) - 1:
                        form_sel += 1
                        visible = 72 // 16
                        if form_sel >= form_scroll + visible:
                            form_scroll = form_sel - visible + 1
                elif ch == '\n' or ch == '\x84':
                    formula_key = formula_display[form_sel][0]
                    current_formula_info = get_formula_info(current_cat, formula_key)
                    var_values = {}
                    editing_var = None
                    edit_buf = ''
                    result_msg = ''
                    result_error = False
                    screen = 'input'
                    if oled_ctrl:
                        oled_ctrl.set_engine_status('Physics',
                            line0=CATEGORIES[current_cat]['name'],
                            line1=formula_key,
                            line2=current_formula_info.get('desc', '') if current_formula_info else '')
                elif ch == '\x1b' or ch == '\x03':
                    screen = 'categories'
                    formula_display = []
                    current_formula_info = None
                elif ch == '\x85':
                    screen = 'categories'

            elif screen == 'input':
                if ch == '\x1b' or ch == '\x03':
                    if editing_var:
                        editing_var = None
                        edit_buf = ''
                    else:
                        screen = 'formulas'
                        current_formula_info = None
                        var_values = {}
                elif ch == '\t':
                    if current_formula_info:
                        vars_list = current_formula_info.get('vars', [])
                        if editing_var:
                            idx = vars_list.index(editing_var) if editing_var in vars_list else -1
                            if idx >= 0 and edit_buf:
                                var_values[editing_var] = edit_buf
                            idx += 1
                            if idx < len(vars_list):
                                editing_var = vars_list[idx]
                                edit_buf = var_values.get(editing_var, '')
                            else:
                                editing_var = None
                                edit_buf = ''
                        else:
                            if vars_list:
                                editing_var = vars_list[0]
                                edit_buf = var_values.get(editing_var, '')
                elif ch == '\n':
                    if editing_var and edit_buf:
                        var_values[editing_var] = edit_buf
                        editing_var = None
                        edit_buf = ''
                    if current_formula_info:
                        known = {}
                        for v in current_formula_info.get('vars', []):
                            if v in var_values and var_values[v]:
                                try:
                                    known[v] = float(var_values[v])
                                except:
                                    pass
                        result, unknown = solve_formula(current_cat,
                            formula_display[form_sel][0], known)
                        if result is not None:
                            result_msg = unknown + ' = ' + format_result(result)
                            result_error = False
                            var_values[unknown] = format_result(result).split()[0]
                            if oled_ctrl:
                                oled_ctrl.set_engine_status('Physics',
                                    line0=CATEGORIES[current_cat]['name'],
                                    line1=formula_display[form_sel][0],
                                    line2=result_msg[:20])
                        else:
                            result_msg = 'Error: ' + str(unknown)
                            result_error = True
                elif ch == '\b':
                    if editing_var and edit_buf:
                        edit_buf = edit_buf[:-1]
                elif ch == '\x85':
                    if current_formula_info:
                        vars_list = current_formula_info.get('vars', [])
                        if editing_var:
                            idx = vars_list.index(editing_var) if editing_var in vars_list else -1
                            if idx >= 0 and edit_buf:
                                var_values[editing_var] = edit_buf
                            idx -= 1
                            if idx >= 0:
                                editing_var = vars_list[idx]
                                edit_buf = var_values.get(editing_var, '')
                            else:
                                editing_var = None
                                edit_buf = ''
                elif len(ch) == 1 and (ch.isdigit() or ch in '.+-eE'):
                    edit_buf += ch
                elif ch == '-' and (not editing_var or not edit_buf):
                    edit_buf += ch

            _refresh()
            time.sleep_ms(10)

    return ('game', _physics_loop)


def cmd_electronics(args, tft=None, oled_ctrl=None):
    def _electronics_loop(tft, read_key):
        import time
        from commands.dispatch import THEME_COLORS
        from lib.electronics_engine import (
            get_category_display, get_formula_display, get_formula_info,
            solve_formula, format_result, CATEGORIES,
            get_tools_display, get_reference_display,
            tool_rcalc, tool_vdiv, tool_led, tool_rcfilt, tool_lcfilt,
            tool_baud, tool_cap, ref_ic, ref_wire, ref_led, ref_truth, ref_smd_cap,
            SI_PREFIX_DATA, _parse_val, fmt_val
        )
        from lib.electronics_renderer import (
            set_theme, render_full, render_result, render_input_area,
            render_categories, render_formulas, render_header
        )

        if THEME_COLORS:
            set_theme(THEME_COLORS)

        screen = 'categories'
        cat_display = get_category_display()
        cat_sel = 0
        cat_scroll = 0
        formula_display = []
        form_sel = 0
        form_scroll = 0
        current_cat = None
        current_formula_info = None
        var_values = {}
        editing_var = None
        edit_buf = ''
        result_msg = ''
        result_error = False

        def _refresh():
            render_full(tft, 'Espelt Electronics', cat_display, cat_scroll, cat_sel,
                       formula_display, form_scroll, form_sel,
                       current_formula_info, var_values, editing_var,
                       result_msg, result_error)

        tft.fill(0x0000)
        _refresh()

        while True:
            ch = read_key()

            if ch == '\x18':
                tft.fill(0x0000)
                render_header(tft, 'Espelt Electronics')
                render_result(tft, 'Exiting electronics...')
                time.sleep_ms(300)
                return

            if screen == 'categories':
                if ch == '\x80':
                    if cat_sel > 0:
                        cat_sel -= 1
                        if cat_sel < cat_scroll:
                            cat_scroll = cat_sel
                elif ch == '\x81':
                    if cat_sel < len(cat_display) - 1:
                        cat_sel += 1
                        visible = 156 // 16
                        if cat_sel >= cat_scroll + visible:
                            cat_scroll = cat_sel - visible + 1
                elif ch == '\n' or ch == '\x84':
                    cat_key = cat_display[cat_sel][0]
                    if cat_key == 'constants':
                        lines = []
                        for sym, name, val in SI_PREFIX_DATA:
                            lines.append(sym + ' ' + name + ' = ' + str(val))
                        result_msg = lines[0] if lines else ''
                        result_error = False
                    elif cat_key == 'tools':
                        formula_display = get_tools_display()
                        form_sel = 0
                        form_scroll = 0
                        screen = 'formulas'
                    elif cat_key == 'reference':
                        formula_display = get_reference_display()
                        form_sel = 0
                        form_scroll = 0
                        screen = 'formulas'
                    else:
                        current_cat = cat_key
                        formula_display = get_formula_display(cat_key)
                        form_sel = 0
                        form_scroll = 0
                        screen = 'formulas'
                elif ch == '\x1b' or ch == '\x03':
                    tft.fill(0x0000)
                    render_header(tft, 'Espelt Electronics')
                    render_result(tft, 'Exiting electronics...')
                    time.sleep_ms(300)
                    return

            elif screen == 'formulas':
                if ch == '\x80':
                    if form_sel > 0:
                        form_sel -= 1
                        if form_sel < form_scroll:
                            form_scroll = form_sel
                elif ch == '\x81':
                    if form_sel < len(formula_display) - 1:
                        form_sel += 1
                        visible = 72 // 16
                        if form_sel >= form_scroll + visible:
                            form_scroll = form_sel - visible + 1
                elif ch == '\n' or ch == '\x84':
                    formula_key = formula_display[form_sel][0]
                    cat_key = cat_display[cat_sel][0]
                    if cat_key == 'tools':
                        result_msg = 'Enter tool params...'
                        result_error = False
                    elif cat_key == 'reference':
                        ref_name = formula_key
                        if ref_name == 'ic':
                            result_msg = 'ic [name] e.g. ic 555'
                        elif ref_name == 'wire':
                            result_msg = 'wire [awg] e.g. wire 22'
                        elif ref_name == 'led':
                            result_msg = 'led [color] e.g. led red'
                        elif ref_name == 'truth':
                            result_msg = 'truth [gate] e.g. truth AND'
                        elif ref_name == 'smd_cap':
                            lines = ref_smd_cap()
                            result_msg = lines[0] if lines else ''
                        result_error = False
                    else:
                        current_formula_info = get_formula_info(cat_key, formula_key)
                        var_values = {}
                        editing_var = None
                        edit_buf = ''
                        result_msg = ''
                        result_error = False
                        screen = 'input'
                        if oled_ctrl:
                            oled_ctrl.set_engine_status('Elec',
                                line0=cat_display[cat_sel][1],
                                line1=formula_key,
                                line2=current_formula_info.get('desc', '') if current_formula_info else '')
                elif ch == '\x1b' or ch == '\x03':
                    screen = 'categories'
                    formula_display = []
                    current_formula_info = None
                elif ch == '\x85':
                    screen = 'categories'

            elif screen == 'input':
                if ch == '\x1b' or ch == '\x03':
                    if editing_var:
                        editing_var = None
                        edit_buf = ''
                    else:
                        screen = 'formulas'
                        current_formula_info = None
                        var_values = {}
                elif ch == '\t':
                    if current_formula_info:
                        vars_list = current_formula_info.get('vars', [])
                        if editing_var:
                            idx = vars_list.index(editing_var) if editing_var in vars_list else -1
                            if idx >= 0 and edit_buf:
                                var_values[editing_var] = edit_buf
                            idx += 1
                            if idx < len(vars_list):
                                editing_var = vars_list[idx]
                                edit_buf = var_values.get(editing_var, '')
                            else:
                                editing_var = None
                                edit_buf = ''
                        else:
                            if vars_list:
                                editing_var = vars_list[0]
                                edit_buf = var_values.get(editing_var, '')
                elif ch == '\n':
                    if editing_var and edit_buf:
                        var_values[editing_var] = edit_buf
                        editing_var = None
                        edit_buf = ''
                    if current_formula_info:
                        known = {}
                        for v in current_formula_info.get('vars', []):
                            if v in var_values and var_values[v]:
                                try:
                                    known[v] = float(var_values[v])
                                except:
                                    pass
                        cat_key = cat_display[cat_sel][0]
                        result, unknown = solve_formula(cat_key,
                            formula_display[form_sel][0], known)
                        if result is not None:
                            result_msg = unknown + ' = ' + format_result(result)
                            result_error = False
                            var_values[unknown] = format_result(result).split()[0]
                            if oled_ctrl:
                                oled_ctrl.set_engine_status('Elec',
                                    line0=cat_display[cat_sel][1],
                                    line1=formula_display[form_sel][0],
                                    line2=result_msg[:20])
                        else:
                            result_msg = 'Error: ' + str(unknown)
                            result_error = True
                elif ch == '\b':
                    if editing_var and edit_buf:
                        edit_buf = edit_buf[:-1]
                elif ch == '\x85':
                    if current_formula_info:
                        vars_list = current_formula_info.get('vars', [])
                        if editing_var:
                            idx = vars_list.index(editing_var) if editing_var in vars_list else -1
                            if idx >= 0 and edit_buf:
                                var_values[editing_var] = edit_buf
                            idx -= 1
                            if idx >= 0:
                                editing_var = vars_list[idx]
                                edit_buf = var_values.get(editing_var, '')
                            else:
                                editing_var = None
                                edit_buf = ''
                elif len(ch) == 1 and (ch.isdigit() or ch in '.+-eE'):
                    edit_buf += ch
                elif ch == '-' and (not editing_var or not edit_buf):
                    edit_buf += ch

            _refresh()
            time.sleep_ms(10)

    return ('game', _electronics_loop)


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
        return ('print', 'view: usage: view [filename.bmp]')
    if not tft:
        return ('print', 'view: no display available')
    try:
        with open(filename, 'rb') as f:
            header = f.read(54)
            if header[:2] != b'BM':
                return ('print', 'view: not a BMP file')
            width = int.from_bytes(header[18:22], 'little')
            height = int.from_bytes(header[22:26], 'little')
            planes = int.from_bytes(header[26:28], 'little')
            bits = int.from_bytes(header[28:30], 'little')
            compression = int.from_bytes(header[30:34], 'little')
            if planes != 1 or bits != 24 or compression != 0:
                return ('print', 'view: only 24-bit uncompressed BMP supported')
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
        return ('print', f'view: {filename} ({max_w}x{max_h})')
    except Exception as e:
        return ('print', f'view: {e}')


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
                try:
                    from commands.dispatch import OLED_REF
                    OLED_REF.notify('WiFi: ' + ssid)
                except:
                    pass
                return ('print', f'wlan: connected to {ssid}\n  IP: {ip}')
            time.sleep(0.5)
        return ('print', f'wlan: failed to connect to {ssid}')
    except Exception as e:
        return ('print', f'wlan: {e}')


def cmd_passcheck(args):
    """Check password strength. Usage: passcheck [password]"""
    pw = args.strip()
    if not pw:
        return ('print_lines', [
            'passcheck: usage: passcheck [password]',
            '',
            '  passcheck myP@ssw0rd',
            '  passcheck 123456',
        ])
    score = 0
    flags = []
    if len(pw) >= 8:
        score += 1; flags.append('8+ chars')
    if len(pw) >= 12:
        score += 1; flags.append('12+ chars')
    if any(c.isupper() for c in pw):
        score += 1; flags.append('uppercase')
    if any(c.islower() for c in pw):
        score += 1; flags.append('lowercase')
    if any(c.isdigit() for c in pw):
        score += 1; flags.append('digits')
    if any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?/~`' for c in pw):
        score += 1; flags.append('symbols')
    # Penalty for patterns
    if pw.lower() in ('password', '123456', 'qwerty', 'abc123', 'letmein', 'admin'):
        score = 0; flags.append('COMMON!')
    if len(set(pw)) < len(pw) * 0.5:
        score -= 1; flags.append('repetitive')
    labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong', 'Excellent']
    label = labels[min(max(score, 0), 5)]
    color = ['Weak', 'Weak', 'Fair', 'Strong', 'Strong', 'Strong'][min(max(score, 0), 5)]
    entropy = len(pw) * 4  # rough estimate
    lines = [
        f'  Password: {"*" * min(len(pw), 20)}',
        f'  Strength: {label}',
        f'  Score:    {score}/6',
        f'  Entropy:  ~{entropy} bits',
        f'  Length:   {len(pw)}',
    ]
    if flags:
        lines.append(f'  Flags:    {", ".join(flags)}')
    return ('print_lines', lines)


def cmd_freqcount(args):
    """Character frequency analysis. Usage: freqcount [text] or freqcount -f [file]"""
    parts = args.strip().split(None, 1) if args.strip() else []
    if not parts:
        return ('print_lines', [
            'freqcount: usage:',
            '  freqcount [text]       Analyze text',
            '  freqcount -f [file]   Analyze file',
        ])
    if parts[0] == '-f' and len(parts) > 1:
        try:
            with open(parts[1], 'r') as f:
                text = f.read()
        except OSError:
            return ('print', f'freqcount: {parts[1]}: not found')
    else:
        text = parts[0] if len(parts) == 1 else parts[1] if len(parts) > 1 else parts[0]
    if not text:
        return ('print', 'freqcount: empty text')
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    total = len(text)
    sorted_freq = sorted(freq.items(), key=lambda x: -x[1])[:12]
    lines = [f'=== Character Frequency ({total} chars) ===']
    for ch, count in sorted_freq:
        pct = count * 100 / total
        bar = '#' * int(pct / 2)
        display = repr(ch) if ch in ('\n', '\r', '\t') else ch
        lines.append(f'  {display:>5s} {count:4d} {pct:5.1f}% {bar}')
    return ('print_lines', lines)


def cmd_snippet(args):
    """Quick note snippets. Usage: snippet save/load/list/del"""
    import os
    snippet_dir = '/sd/.snippets'
    parts = args.strip().split(None, 1) if args.strip() else []
    if not parts:
        return ('print_lines', [
            'snippet: usage:',
            '  snippet save [name] [text]   Save a snippet',
            '  snippet load [name]          Load a snippet',
            '  snippet list                 List all snippets',
            '  snippet del [name]           Delete a snippet',
        ])
    action = parts[0].lower()
    try:
        os.mkdir(snippet_dir)
    except:
        pass
    if action == 'list':
        try:
            files = os.listdir(snippet_dir)
            if not files:
                return ('print', '  No snippets saved')
            lines = ['=== Snippets ===']
            for f in sorted(files):
                size = os.stat(snippet_dir + '/' + f)[6]
                lines.append(f'  {f} ({size}B)')
            return ('print_lines', lines)
        except:
            return ('print', '  No snippets saved')
    elif action == 'save':
        if len(parts) < 3:
            return ('print', 'snippet: usage: snippet save [name] [text]')
        name = parts[1].split()[0]
        text = parts[1] if len(parts[1]) > len(name) else ''
        # Reconstruct text after the name
        words = parts[1].split()
        if len(words) > 1:
            text = parts[1][len(words[0]):].strip()
        else:
            text = ''
        path = snippet_dir + '/' + name + '.txt'
        with open(path, 'w') as f:
            f.write(text)
        return ('print', f'  Saved: {name} ({len(text)} chars)')
    elif action == 'load':
        if len(parts) < 2:
            return ('print', 'snippet: usage: snippet load [name]')
        name = parts[1].strip()
        path = snippet_dir + '/' + name + '.txt'
        try:
            with open(path, 'r') as f:
                content = f.read()
            return ('print_lines', [f'=== {name} ==='] + content.split('\n')[:15])
        except:
            return ('print', f'  Snippet "{name}" not found')
    elif action == 'del':
        if len(parts) < 2:
            return ('print', 'snippet: usage: snippet del [name]')
        name = parts[1].strip()
        path = snippet_dir + '/' + name + '.txt'
        try:
            os.remove(path)
            return ('print', f'  Deleted: {name}')
        except:
            return ('print', f'  Snippet "{name}" not found')
    return ('print', f'  Unknown action: {action}')


def cmd_chem(args):
    if args.strip():
        return _chem_dispatch(args.strip())
    def _chem_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS, OLED_REF
        _repl_loop(tft, read_key, 'Espelt Chemistry', _chem_dispatch, [
            ['element [sym]   Element info',
             'mass [formula]  Molar mass',
             'parse [form]    Parse formula',
             'ph [h+]         pH calculator',
             'gas ...         Gas law PV=nRT',
             'molarity ...    Solution molarity',
             'dilute ...      C1V1=C2V2',
             'moles [m] [f]   Mass to moles'],
            ['grams [n] [f]  Moles to grams',
             'percent [f]     % composition',
             'config [el]     Electron config',
             'balance [eq]    Balance equation',
             'thermo [rxn]    Thermochemistry',
             'organic [comp]  Organic chemistry',
             'table           Periodic table TFT',
             'known           Common molecules'],
            ['list            All elements',
             'charles ...     Charles Law V1/T1',
             'combined ...    Combined gas law',
             'graham ...      Graham effusion',
             'dalton ...      Dalton partial P',
             'redox [rxn]     Redox reactions',
             'trend [el]      Periodic trends',
             'bond [el] [el]  Bond type'],
            ['lewis [el]      Lewis dot notation',
             'valence [el]    Valence electrons',
             'titrate ...     Titration calculator',
             'history         Calculation history',
             'clear           Clear screen',
             '[formula]       Direct molar mass',
             '',
             'Example: mass H2O',
             'Example: ph 0.001',
             'Example: thermo combustion'],
        ], THEME_COLORS, [
            'element', 'mass', 'parse', 'ph', 'gas', 'molarity',
            'dilute', 'moles', 'grams', 'percent', 'config',
            'balance', 'thermo', 'organic', 'table', 'known',
            'list', 'charles', 'combined', 'graham', 'dalton',
            'redox', 'trend', 'bond', 'lewis', 'valence', 'titrate',
            'history', 'clear',
        ], oled=OLED_REF)
    return ('game', _chem_loop)


def _chem_dispatch(cmd_str):
    from lib.chem_engine import (
        parse_formula, molar_mass, element_info, electron_config_full,
        calc_ph, calc_gas_law, calc_molarity, calc_dilution,
        stoich_mass, stoich_moles, percent_composition,
        balance_equation, thermo_info, organic_info, all_elements_list,
        KNOWN_MOLECULES, ELEMENTS, COMMON_EQUATIONS
    )
    parts = cmd_str.split()
    cmd = parts[0].lower()

    if cmd == 'element' or cmd == 'info':
        if len(parts) < 2:
            return ('print', '  Usage: element [symbol]')
        el = parts[1]
        info = element_info(el)
        if info is None:
            return ('print', f'  Unknown element "{el}"')
        result = [info[0], info[1], info[2], info[3]]
        steps = []
        for extra in info[4:]:
            steps.append(extra)
        return ('result_steps', result, steps)

    elif cmd == 'mass':
        if len(parts) < 2:
            return ('print', '  Usage: mass [formula]')
        formula = parts[1]
        mm = molar_mass(formula)
        if mm is None:
            return ('print', f'  Unknown element in "{formula}"')
        comp = parse_formula(formula)
        name = KNOWN_MOLECULES.get(formula, '')
        result = [f'{formula}']
        if name:
            result.append(f'  {name}')
        steps = []
        total = 0.0
        for elem, count in sorted(comp.items()):
            em = ELEMENTS.get(elem, ('', '', 0))[2]
            contribution = em * count
            total += contribution
            result.append(f'{elem}: {contribution:.2f}')
            steps.append(f'{elem} {count}x{em:.2f}')
        result.append(f'Total: {total:.3f}')
        steps.append(f'= {total:.3f} g/mol')
        return ('result_steps', result, steps)

    elif cmd == 'parse':
        if len(parts) < 2:
            return ('print', '  Usage: parse [formula]')
        comp = parse_formula(parts[1])
        if not comp:
            return ('print', f'  Could not parse "{parts[1]}"')
        lines = [f'=== {parts[1]} ===']
        for elem, count in sorted(comp.items()):
            lines.append(f'  {elem}: {count}')
        return ('print_lines', lines)

    elif cmd == 'ph':
        if len(parts) < 2:
            return ('print', '  Usage: ph [H+] concentration')
        try:
            h = float(parts[1])
            ph = calc_ph(conc_h=h)
            if ph is None:
                return ('print', '  Invalid input')
            poh = 14 - ph
            oh = 10 ** (-poh)
            acid_base = 'Acidic' if ph < 7 else 'Basic' if ph > 7 else 'Neutral'
            result = [f'[H+] = {h:.4g} M', f'pH = {ph:.3f}', f'{acid_base}']
            steps = [f'-log({h:.4g})', f'pOH=14-{ph:.3f}={poh:.3f}', f'[OH-]={oh:.4g}']
            return ('result_steps', result, steps)
        except ValueError:
            return ('print', '  Invalid number')

    elif cmd == 'gas':
        if len(parts) < 2:
            return ('print_lines', ['  PV=nRT calculator', '  Use: gas p=1 v=2 n=? t=300'])
        vals = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                vals[k.lower()] = None if v == '?' else float(v)
        result_val = calc_gas_law(p=vals.get('p'), v=vals.get('v'), n=vals.get('n'), t=vals.get('t'))
        if result_val is None:
            return ('print', '  Need 3 of 4 values')
        solved = [k for k, v in vals.items() if v is None]
        if solved:
            vals[solved[0]] = result_val
        result = [f'P={vals.get("p","?")} V={vals.get("v","?")}',
                  f'n={vals.get("n","?")} T={vals.get("t","?")}',
                  f'{solved[0]}={result_val:.4f}' if solved else '']
        steps = [f'PV=nRT', f'R=0.08206',
                 f'{solved[0]}={result_val:.4f}'] if solved else []
        return ('result_steps', result, steps)

    elif cmd == 'molarity':
        if len(parts) < 2:
            return ('print', '  Usage: molarity moles=0.5 vol=1')
        vals = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                vals[k.lower()] = float(v)
        result = calc_molarity(moles=vals.get('moles'), volume_l=vals.get('vol'),
                               mass=vals.get('mass'), molar_mass_val=vals.get('mm'),
                               volume_ml=vals.get('ml'))
        if result is None:
            return ('print', '  Need (moles,vol) or (mass,mm,vol/ml)')
        return ('print_lines', [f'=== Molarity ===', f'  {result:.4f} M'])

    elif cmd == 'dilute':
        if len(parts) < 2:
            return ('print', '  Usage: dilute c1=1 v1=100 c2=? v2=500')
        vals = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                vals[k.lower()] = None if v == '?' else float(v)
        result = calc_dilution(c1=vals.get('c1'), v1=vals.get('v1'), c2=vals.get('c2'), v2=vals.get('v2'))
        if result is None:
            return ('print', '  Need 3 of 4 values')
        solved = [k for k, v in vals.items() if v is None]
        if solved:
            vals[solved[0]] = result
        return ('print_lines', [
            f'=== Dilution ===',
            f'  C1={vals.get("c1","?")} V1={vals.get("v1","?")}',
            f'  C2={vals.get("c2","?")} V2={vals.get("v2","?")}',
        ])

    elif cmd == 'moles':
        if len(parts) < 3:
            return ('print', '  Usage: moles [mass] [formula]')
        try:
            mass = float(parts[1])
            formula = parts[2]
            result = stoich_moles(mass, formula)
            if result is None:
                return ('print', f'  Unknown in "{formula}"')
            return ('print_lines', [f'=== Moles ===', f'  {mass}g {formula} = {result:.4f} mol'])
        except ValueError:
            return ('print', '  Invalid number')

    elif cmd == 'grams':
        if len(parts) < 3:
            return ('print', '  Usage: grams [moles] [formula]')
        try:
            mol = float(parts[1])
            formula = parts[2]
            result = stoich_mass(formula, mol)
            if result is None:
                return ('print', f'  Unknown in "{formula}"')
            return ('print_lines', [f'=== Grams ===', f'  {mol}mol {formula} = {result:.4f}g'])
        except ValueError:
            return ('print', '  Invalid number')

    elif cmd == 'percent':
        if len(parts) < 2:
            return ('print', '  Usage: percent [formula]')
        result = percent_composition(parts[1])
        if result is None:
            return ('print', f'  Unknown in "{parts[1]}"')
        mm = molar_mass(parts[1])
        lines = [f'=== % Composition ===', f'  {parts[1]} = {mm:.3f} g/mol']
        for elem, pct in result:
            lines.append(f'  {elem}: {pct:.1f}%')
        return ('print_lines', lines)

    elif cmd == 'config':
        if len(parts) < 2:
            return ('print', '  Usage: config [element]')
        symbol = parts[1].strip()
        if len(symbol) > 0:
            symbol = symbol[0].upper() + symbol[1:].lower()
        if symbol not in ELEMENTS:
            return ('print', f'  Unknown element "{parts[1]}"')
        num = ELEMENTS[symbol][0]
        full = electron_config_full(num)
        return ('print_lines', [f'=== {symbol} ==='] + [f'  {full[i:i+36]}' for i in range(0, len(full), 36)])

    elif cmd == 'balance':
        if len(parts) < 2:
            return ('print', '  Usage: balance [equation]')
        eq_str = ' '.join(parts[1:])
        result = balance_equation(eq_str)
        if result:
            return ('print_lines', [f'=== Balanced ===', f'  {result}'])
        return ('print', '  Could not balance equation')

    elif cmd == 'thermo':
        if len(parts) < 2:
            return ('print_lines', [
                '  Reactions: combustion,',
                '  neutralization, photosynthesis,',
                '  rusting, synthesis_water,',
                '  decomposition, respiration',
            ])
        name = ' '.join(parts[1:])
        return ('print_lines', thermo_info(name))

    elif cmd == 'organic':
        if len(parts) < 2:
            return ('print_lines', [
                '  Compounds: methane, ethanol,',
                '  glucose, acetic acid, benzene,',
                '  acetone, glycerol, formaldehyde,',
                '  phenol, urea, citric acid',
            ])
        name = ' '.join(parts[1:])
        return ('print_lines', organic_info(name))

    elif cmd in ('charles', 'charles_law'):
        from lib.chem_engine import charles_law
        vals = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                vals[k.lower()] = None if v == '?' else float(v)
        result = charles_law(v1=vals.get('v1'), t1=vals.get('t1'), t2=vals.get('t2'), v2=vals.get('v2'))
        if result is None:
            return ('print_lines', ['  V1/T1 = V2/T2', '  Use: charles v1=10 t1=300 t2=? v2=20', '  Temperatures in Kelvin'])
        solved = [k for k, v in vals.items() if v is None]
        if solved:
            vals[solved[0]] = result
        return ('print_lines', [
            f'=== Charles Law ===',
            f'  V1={vals.get("v1","?")} T1={vals.get("t1","?")}',
            f'  V2={vals.get("v2","?")} T2={vals.get("t2","?")}',
            f'  {solved[0]}={result:.4f}' if solved else '',
        ])

    elif cmd in ('combined', 'combined_gas'):
        from lib.chem_engine import combined_gas_law
        vals = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                vals[k.lower()] = None if v == '?' else float(v)
        result = combined_gas_law(
            p1=vals.get('p1'), v1=vals.get('v1'), t1=vals.get('t1'),
            p2=vals.get('p2'), v2=vals.get('v2'), t2=vals.get('t2')
        )
        if result is None:
            return ('print_lines', ['  P1*V1/T1 = P2*V2/T2', '  Provide 5 of 6 values'])
        solved = [k for k, v in vals.items() if v is None]
        if solved:
            vals[solved[0]] = result
        return ('print_lines', [
            f'=== Combined Gas Law ===',
            f'  {solved[0]}={result:.4f}' if solved else '',
        ])

    elif cmd in ('graham', 'graham_law'):
        from lib.chem_engine import graham_rate
        if len(parts) < 3:
            return ('print_lines', ['  Graham: rate1/rate2 = sqrt(M2/M1)', '  Use: graham [m1] [m2]'])
        try:
            m1, m2 = float(parts[1]), float(parts[2])
            ratio = graham_rate(m1, m2)
            if ratio is None:
                return ('print', '  Invalid masses')
            return ('print_lines', [
                f'=== Graham Law ===',
                f'  M1={m1}, M2={m2}',
                f'  Rate ratio: {ratio:.4f}',
                f'  Gas 1 effuses {ratio:.2f}x faster',
            ])
        except ValueError:
            return ('print', '  Invalid numbers')

    elif cmd in ('dalton', 'dalton_law'):
        from lib.chem_engine import dalton_law
        if len(parts) < 2:
            return ('print_lines', ['  Dalton: P_total = P1 + P2 + ...', '  Use: dalton 0.5 0.3 0.2'])
        try:
            pressures = [float(p) for p in parts[1:]]
            total = dalton_law(*pressures)
            return ('print_lines', [
                f'=== Dalton Law ===',
                f'  Pressures: {pressures}',
                f'  Total: {total:.4f} atm',
            ])
        except ValueError:
            return ('print', '  Invalid numbers')

    elif cmd == 'redox':
        from lib.chem_engine import redox_info
        if len(parts) < 2:
            return ('print_lines', ['  Reactions: zn_cu, fe_cu, mg_hcl,', '  h2_o2, fe_rust'])
        name = ' '.join(parts[1:])
        return ('print_lines', redox_info(name))

    elif cmd == 'trend':
        from lib.chem_engine import periodic_trend
        if len(parts) < 2:
            return ('print', '  Usage: trend [element]')
        return ('print_lines', periodic_trend(parts[1]))

    elif cmd == 'bond':
        from lib.chem_engine import bond_type
        if len(parts) < 3:
            return ('print', '  Usage: bond [el1] [el2]')
        return ('print_lines', bond_type(parts[1], parts[2]))

    elif cmd == 'lewis':
        from lib.chem_engine import lewis_dots
        if len(parts) < 2:
            return ('print', '  Usage: lewis [element]')
        return ('print_lines', lewis_dots(parts[1]))

    elif cmd == 'valence':
        from lib.chem_engine import valence_electrons
        if len(parts) < 2:
            return ('print', '  Usage: valence [element]')
        v = valence_electrons(parts[1])
        if v is None:
            return ('print', f'  Unknown element "{parts[1]}"')
        return ('print_lines', [f'{parts[1]}: {v} valence electrons'])

    elif cmd == 'titrate':
        from lib.chem_engine import titration_calc
        vals = {}
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
                vals[k.lower()] = None if v == '?' else float(v)
        result = titration_calc(
            c_acid=vals.get('ca'), v_acid=vals.get('va'),
            c_base=vals.get('cb'), v_base=vals.get('vb'),
            n_ratio=vals.get('n', 1)
        )
        if result is None:
            return ('print_lines', ['  C_acid*V_acid/n = C_base*V_base', '  Use: titrate ca=? va=25 cb=0.1 vb=30'])
        solved = [k for k, v in vals.items() if v is None]
        if solved:
            vals[solved[0]] = result
        return ('print_lines', [
            f'=== Titration ===',
            f'  Ca={vals.get("ca","?")} Va={vals.get("va","?")}',
            f'  Cb={vals.get("cb","?")} Vb={vals.get("vb","?")}',
            f'  {solved[0]}={result:.4f}' if solved else '',
        ])

    elif cmd == 'table':
        from commands.systemcmd import cmd_chemtable
        return cmd_chemtable('', tft=None)

    elif cmd == 'known':
        lines = ['=== Common Molecules ===']
        for f, n in list(KNOWN_MOLECULES.items())[:30]:
            lines.append(f'  {f:12s} {n}')
        return ('print_lines', lines)

    elif cmd == 'list':
        return ('print_lines', all_elements_list())

    elif cmd == 'history':
        return ('print_lines', ['  (No history in session)'])

    elif cmd == 'clear':
        return ('clear',)

    else:
        mm = molar_mass(cmd)
        if mm is not None:
            comp = parse_formula(cmd)
            name = KNOWN_MOLECULES.get(cmd, '')
            lines = [f'=== {cmd} ===']
            if name:
                lines.append(f'  {name}')
            lines.append(f'  Molar mass: {mm:.3f} g/mol')
            for elem, count in sorted(comp.items()):
                em = ELEMENTS.get(elem, ('', '', 0))[2]
                lines.append(f'  {elem}: {count}x{em:.3f}={em*count:.3f}')
            return ('print_lines', lines)
        return ('print', f'  Unknown command "{cmd}"')


def _wrap_chem(text, width):
    words = text.split()
    lines = []
    line = ''
    for w in words:
        test = (line + ' ' + w).strip() if line else w
        if len(test) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def cmd_chemtable(args, tft=None):
    from lib.chem_engine import ELEMENTS

    if not tft:
        return ('print', 'chemtable: no display available')

    CAT_COLORS = {
        1: 0x07E0,
        2: 0x07FF,
        3: 0xF800,
        4: 0xFD20,
        5: 0xFFE0,
        6: 0xA81F,
        7: 0x8410,
        8: 0xC618,
        9: 0xFC1F,
        10: 0xF81F,
    }

    CAT_LABELS = {
        1: 'Nonmetal', 2: 'Noble Gas', 3: 'Alkali', 4: 'Alkaline',
        5: 'Metalloid', 6: 'Halogen', 7: 'Trans.M', 8: 'Post-T.M',
        9: 'Lanthanid', 10: 'Actinide',
    }

    # (row, col, symbol, atomic_number)
    # row 8 is a gap row between main table and lanthanides/actinides
    LAYOUT = [
        (1, 1, 'H', 1), (1, 18, 'He', 2),
        (2, 1, 'Li', 3), (2, 2, 'Be', 4), (2, 13, 'B', 5), (2, 14, 'C', 6),
        (2, 15, 'N', 7), (2, 16, 'O', 8), (2, 17, 'F', 9), (2, 18, 'Ne', 10),
        (3, 1, 'Na', 11), (3, 2, 'Mg', 12), (3, 13, 'Al', 13), (3, 14, 'Si', 14),
        (3, 15, 'P', 15), (3, 16, 'S', 16), (3, 17, 'Cl', 17), (3, 18, 'Ar', 18),
        (4, 1, 'K', 19), (4, 2, 'Ca', 20), (4, 3, 'Sc', 21), (4, 4, 'Ti', 22),
        (4, 5, 'V', 23), (4, 6, 'Cr', 24), (4, 7, 'Mn', 25), (4, 8, 'Fe', 26),
        (4, 9, 'Co', 27), (4, 10, 'Ni', 28), (4, 11, 'Cu', 29), (4, 12, 'Zn', 30),
        (4, 13, 'Ga', 31), (4, 14, 'Ge', 32), (4, 15, 'As', 33), (4, 16, 'Se', 34),
        (4, 17, 'Br', 35), (4, 18, 'Kr', 36),
        (5, 1, 'Rb', 37), (5, 2, 'Sr', 38), (5, 3, 'Y', 39), (5, 4, 'Zr', 40),
        (5, 5, 'Nb', 41), (5, 6, 'Mo', 42), (5, 7, 'Tc', 43), (5, 8, 'Ru', 44),
        (5, 9, 'Rh', 45), (5, 10, 'Pd', 46), (5, 11, 'Ag', 47), (5, 12, 'Cd', 48),
        (5, 13, 'In', 49), (5, 14, 'Sn', 50), (5, 15, 'Sb', 51), (5, 16, 'Te', 52),
        (5, 17, 'I', 53), (5, 18, 'Xe', 54),
        (6, 1, 'Cs', 55), (6, 2, 'Ba', 56),
        (6, 4, 'Hf', 72), (6, 5, 'Ta', 73), (6, 6, 'W', 74), (6, 7, 'Re', 75),
        (6, 8, 'Os', 76), (6, 9, 'Ir', 77), (6, 10, 'Pt', 78), (6, 11, 'Au', 79),
        (6, 12, 'Hg', 80), (6, 13, 'Tl', 81), (6, 14, 'Pb', 82), (6, 15, 'Bi', 83),
        (6, 16, 'Po', 84), (6, 17, 'At', 85), (6, 18, 'Rn', 86),
        (7, 1, 'Fr', 87), (7, 2, 'Ra', 88),
        (7, 4, 'Rf', 104), (7, 5, 'Db', 105), (7, 6, 'Sg', 106), (7, 7, 'Bh', 107),
        (7, 8, 'Hs', 108), (7, 9, 'Mt', 109), (7, 10, 'Ds', 110), (7, 11, 'Rg', 111),
        (7, 12, 'Cn', 112), (7, 13, 'Nh', 113), (7, 14, 'Fl', 114), (7, 15, 'Mc', 115),
        (7, 16, 'Lv', 116), (7, 17, 'Ts', 117), (7, 18, 'Og', 118),
        (9, 3, 'La', 57), (9, 4, 'Ce', 58), (9, 5, 'Pr', 59), (9, 6, 'Nd', 60),
        (9, 7, 'Pm', 61), (9, 8, 'Sm', 62), (9, 9, 'Eu', 63), (9, 10, 'Gd', 64),
        (9, 11, 'Tb', 65), (9, 12, 'Dy', 66), (9, 13, 'Ho', 67), (9, 14, 'Er', 68),
        (9, 15, 'Tm', 69), (9, 16, 'Yb', 70), (9, 17, 'Lu', 71),
        (10, 3, 'Ac', 89), (10, 4, 'Th', 90), (10, 5, 'Pa', 91), (10, 6, 'U', 92),
        (10, 7, 'Np', 93), (10, 8, 'Pu', 94), (10, 9, 'Am', 95), (10, 10, 'Cm', 96),
        (10, 11, 'Bk', 97), (10, 12, 'Cf', 98), (10, 13, 'Es', 99), (10, 14, 'Fm', 100),
        (10, 15, 'Md', 101), (10, 16, 'No', 102), (10, 17, 'Lr', 103),
    ]

    FALLBACK_CAT = {
        99: 10, 100: 10, 101: 10, 102: 10, 103: 10,
        104: 7, 105: 7, 106: 7, 107: 7, 108: 7, 109: 7,
        110: 7, 111: 7, 112: 7, 113: 8, 114: 8, 115: 8,
        116: 8, 117: 6, 118: 2,
    }

    CW = 25
    CH = 14
    SX = 6
    SY = 16
    GAP = 1

    tft.fill(0x0000)

    tft.text15('PERIODIC TABLE', 130, 1, 0x07FF, 0x0000)

    for row, col, sym, num in LAYOUT:
        if sym in ELEMENTS:
            cat = ELEMENTS[sym][3]
        else:
            cat = FALLBACK_CAT.get(num, 7)
        color = CAT_COLORS.get(cat, 0x8410)

        x = SX + (col - 1) * (CW + GAP)
        y = SY + (row - 1) * (CH + GAP)

        tft.fill_rect(x, y, CW, CH, color)

        tft.text(str(num), x + 1, y + 1, 0x0000, color)

        sx_pos = x + (CW - len(sym) * 8) // 2
        tft.text(sym, sx_pos, y + 4, 0x0000, color)

    legend_y = SY + 10 * (CH + GAP) + 1
    legend_cats = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    col_w = 48
    for i, cat_id in enumerate(legend_cats):
        lx = (i % 5) * col_w + 2
        ly = legend_y + (i // 5) * 12
        tft.fill_rect(lx, ly, 8, 8, CAT_COLORS[cat_id])
        tft.text(CAT_LABELS[cat_id], lx + 10, ly, 0xFFFF, 0x0000)

    return ('print_lines', [])


def cmd_bio(args):
    if args.strip():
        return _bio_dispatch(args.strip())
    def _bio_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS, OLED_REF
        _repl_loop(tft, read_key, 'Espelt Biology', _bio_dispatch, [
            ['dna [seq]       DNA analysis',
             'rna [seq]       DNA to mRNA',
             'translate [s]   mRNA to amino acids',
             'protein [seq]   Full DNA pipeline',
             'amino [name]    Amino acid info',
             'polar           By polarity',
             'codon [AUG]     Codon lookup',
             'organelle [n]   Cell organelle info'],
            ['cells           Cell comparison',
             'punnett [p] [p] Visual Punnett square',
             'punnett2 [...]  2-trait Punnett',
             'hwe [q]         Hardy-Weinberg',
             'biome [name]    Biome info',
             'trophic         Trophic levels',
             'taxonomy [n]    Classification',
             'heart           Heart anatomy'],
            ['brain           Brain anatomy',
             'lung            Lung anatomy',
             'kidney          Kidney anatomy',
             'system [name]   Body systems',
             'mutate [seq]    DNA mutation',
             'mutation [type] Mutation type info',
             'effect [o] [m]  Mutation effect',
             'protein_s [l]   Protein structure'],
            ['denature        Denaturing factors',
             'cellcycle [ph]  Cell cycle phase',
             'mitosis [stg]   Mitosis stages',
             'meiosis [i/ii]  Meiosis divisions',
             'compare_mm      Mitosis vs Meiosis',
             'evolution [c]   Evolution concepts',
             'speciation [t]  Speciation types',
             'microbe [type]  Microbiology info'],
            ['immune [b]      Immune response',
             'disease [name]  Disease info',
             'clear           Clear screen',
             '',
             'Example: dna ATCG',
             'Example: mutate ATCG point_sub 2 G',
             'Example: evolution natural_selection'],
        ], THEME_COLORS, [
            'dna', 'rna', 'translate', 'protein', 'amino', 'polar',
            'codon', 'organelle', 'cells', 'punnett', 'punnett2',
            'hwe', 'biome', 'trophic', 'taxonomy',
            'heart', 'brain', 'lung', 'kidney', 'liver', 'stomach', 'eye',
            'system', 'mutate', 'mutation', 'effect', 'protein_s', 'denature',
            'cellcycle', 'mitosis', 'meiosis', 'compare_mm', 'evolution',
            'speciation', 'microbe', 'immune', 'disease', 'clear',
        ], oled=OLED_REF)
    return ('game', _bio_loop)


def _bio_dispatch(cmd_str):
    from lib.bio_engine import (
        complement, transcribe, translate, dna_to_protein,
        amino_info, amino_by_polarity,
        organelle_info, cell_comparison,
        punnett_1trait, punnett_2trait, hardy_weinberg,
        biome_info, trophic_info, taxonomy_info, codon_lookup,
        anatomy_info, system_info,
        _CODON_TABLE, AA_LIST
    )
    parts = cmd_str.split()
    cmd = parts[0].lower()

    if cmd == 'dna':
        seq = parts[1].upper() if len(parts) > 1 else ''
        if not seq:
            return ('print', '  Usage: dna [ATCG]')
        c = complement(seq)
        rc = ''.join(c[i] for i in range(len(c) - 1, -1, -1))
        gc = sum(1 for x in seq if x in 'GC')
        gc_pct = gc / len(seq) * 100 if seq else 0
        result = [f'Seq: {seq} ({len(seq)}bp)', f'Comp: {c}', f'Rev:  {rc}', f'GC: {gc_pct:.0f}%']
        steps = [f'A<->T C<->G', f'{gc} GC bases']
        return ('result_steps', result, steps)

    elif cmd == 'rna':
        seq = parts[1].upper() if len(parts) > 1 else ''
        if not seq:
            return ('print', '  Usage: rna [DNA]')
        mRNA = transcribe(seq)
        result = [f'DNA:  {seq}', f'mRNA: {mRNA}']
        steps = [f'T->A A->U', f'{len(seq)} bases']
        return ('result_steps', result, steps)

    elif cmd == 'translate':
        seq = parts[1].upper() if len(parts) > 1 else ''
        if not seq:
            return ('print', '  Usage: translate [mRNA]')
        aas = translate(seq)
        if not aas:
            return ('print', '  No protein')
        result = [' '.join(aas[i:i+4]) for i in range(0, len(aas), 4)]
        steps = [f'{len(aas)} amino acids', 'Codon table lookup']
        return ('result_steps', result, steps)

    elif cmd == 'protein':
        seq = parts[1].upper() if len(parts) > 1 else ''
        if not seq:
            return ('print', '  Usage: protein [DNA]')
        raw = dna_to_protein(seq)
        result = raw[:5]
        steps = raw[5:] if len(raw) > 5 else []
        return ('result_steps', result, steps)

    elif cmd == 'amino':
        name = parts[1] if len(parts) > 1 else ''
        if not name:
            return ('print', '  Usage: amino [name]')
        return ('print_lines', amino_info(name))

    elif cmd == 'polar':
        pol = parts[1].lower() if len(parts) > 1 else 'all'
        if pol == 'all':
            return ('print_lines', ['=== All Amino Acids ==='] + [f'  {aa}' for aa in AA_LIST])
        result = amino_by_polarity(pol)
        if not result:
            return ('print', f'  Unknown polarity: {pol}')
        titled = pol[0].upper() + pol[1:] if pol else pol
        return ('print_lines', [f'=== {titled} Amino Acids ==='] + [f'  {aa}' for aa in result])

    elif cmd == 'codon':
        codon = parts[1].upper() if len(parts) > 1 else ''
        if not codon or len(codon) != 3:
            return ('print', '  Usage: codon [AUG]')
        return ('print_lines', [codon_lookup(codon)])

    elif cmd == 'organelle':
        name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        if not name:
            return ('print', '  Usage: organelle [name]')
        return ('print_lines', organelle_info(name))

    elif cmd == 'cells':
        return ('print_lines', cell_comparison())

    elif cmd == 'punnett':
        if len(parts) < 3:
            return ('print', '  Usage: punnett [Aa] [Aa]')
        p1, p2 = parts[1], parts[2]
        g1, g2 = list(p1[:2].upper())
        g3, g4 = list(p2[:2].upper())
        combos = [(g1, g3), (g1, g4), (g2, g3), (g2, g4)]
        genotypes = [''.join(c) for c in combos]
        dom = sum(1 for a, b in combos if a.isupper() or b.isupper())
        rec = 4 - dom
        result = [f'{p1} x {p2}', f'{g1+g3} {g1+g4} {g2+g3} {g2+g4}',
                  f'Dom: {dom}/4 ({dom*25}%)', f'Rec: {rec}/4 ({rec*25}%)']
        steps = [f'  |{g3}  {g4}', f'{g1} |{g1+g3} {g1+g4}', f'{g2} |{g2+g3} {g2+g4}']
        return ('result_steps', result, steps)

    elif cmd == 'punnett2':
        if len(parts) < 5:
            return ('print', '  Usage: punnett2 [Aa] [Bb] [Aa] [Bb]')
        return ('print_lines', punnett_2trait(parts[1], parts[2], parts[3], parts[4]))

    elif cmd == 'hwe':
        try:
            q = float(parts[1]) if len(parts) > 1 else 0.5
            return ('print_lines', hardy_weinberg(q))
        except (ValueError, IndexError):
            return ('print', '  Usage: hwe [q]')

    elif cmd == 'biome':
        name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        if not name:
            return ('print_lines', ['  Biomes: Tropical Rainforest, Temperate Forest, Boreal Forest, Grassland, Desert, Tundra, Freshwater, Marine, Taiga, Savanna'])
        return ('print_lines', biome_info(name))

    elif cmd == 'trophic':
        return ('print_lines', trophic_info())

    elif cmd == 'taxonomy':
        name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        if not name:
            return ('print_lines', ['  Organisms: Human, Dog, Cat, Rice, E. coli, Yeast, Fruit Fly, Mouse, Oak Tree, Mushroom'])
        return ('print_lines', taxonomy_info(name))

    elif cmd in ('heart', 'brain', 'lung', 'kidney', 'liver', 'stomach', 'eye'):
        return ('print_lines', anatomy_info(cmd))

    elif cmd == 'system':
        name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        if not name:
            return ('print_lines', ['  Systems: circulatory, nervous, respiratory, digestive, excretory, skeletal, muscular, endocrine, immune, reproductive'])
        return ('print_lines', system_info(name))

    elif cmd == 'mutate':
        from lib.bio_engine import mutate_dna
        if len(parts) < 3:
            return ('print_lines', [
                '  Usage: mutate [seq] [type] [pos] [base]',
                '  Types: point_sub, insertion, deletion,',
                '         duplication, inversion',
            ])
        seq = parts[1].upper()
        mut_type = parts[2].lower()
        pos = int(parts[3]) if len(parts) > 3 else 0
        base = parts[4].upper() if len(parts) > 4 else 'A'
        mutated, desc = mutate_dna(seq, mut_type, pos, base)
        result = [f'Original: {seq}', f'Mutated:  {mutated}', f'Change: {desc}']
        steps = [f'Type: {mut_type}', f'Position: {pos}']
        return ('result_steps', result, steps)

    elif cmd == 'mutation':
        from lib.bio_engine import MUTATION_TYPES
        if len(parts) < 2:
            lines = ['=== Mutation Types ===']
            for key in ['point_sub', 'insertion', 'deletion', 'frameshift', 'silent', 'missense', 'nonsense']:
                if key in MUTATION_TYPES:
                    lines.append(f'  {key}: {MUTATION_TYPES[key]["name"]}')
            lines.append('')
            lines.append('Use: mutation [type] for details')
            return ('print_lines', lines)
        key = parts[1].lower().replace(' ', '_')
        d = MUTATION_TYPES.get(key)
        if not d:
            return ('print', f'  Unknown mutation type: {parts[1]}')
        return ('print_lines', [
            d['name'],
            f'  {d["description"]}',
            f'  Effect: {d["effect"]}',
        ])

    elif cmd == 'effect':
        from lib.bio_engine import mutation_effect
        if len(parts) < 3:
            return ('print', '  Usage: effect [original] [mutated]')
        original = parts[1].upper()
        mutated = parts[2].upper()
        eff, desc = mutation_effect(original, mutated)
        return ('print_lines', [
            f'=== Mutation Effect ===',
            f'  Original: {original}',
            f'  Mutated:  {mutated}',
            f'  Effect: {eff}',
            f'  {desc}',
        ])

    elif cmd in ('protein_s', 'protein_struct'):
        from lib.bio_engine import protein_structure_info
        if len(parts) < 2:
            return ('print_lines', [
                '  Levels: primary, secondary,',
                '  tertiary, quaternary',
                '  Use: protein_s [level]',
            ])
        return ('print_lines', protein_structure_info(parts[1]))

    elif cmd == 'denature':
        from lib.bio_engine import denaturing_info
        return ('print_lines', denaturing_info())

    elif cmd in ('cellcycle', 'cell_cycle'):
        from lib.bio_engine import cell_cycle_info
        if len(parts) < 2:
            return ('print_lines', [
                '  Phases: g1, s, g2, m',
                '  Use: cellcycle [phase]',
            ])
        return ('print_lines', cell_cycle_info(parts[1]))

    elif cmd == 'mitosis':
        from lib.bio_engine import mitosis_info
        if len(parts) < 2:
            return ('print_lines', mitosis_info())
        return ('print_lines', mitosis_info(parts[1]))

    elif cmd == 'meiosis':
        from lib.bio_engine import meiosis_info
        if len(parts) < 2:
            return ('print_lines', meiosis_info())
        return ('print_lines', meiosis_info(parts[1]))

    elif cmd in ('compare_mm', 'compare_mitosis'):
        from lib.bio_engine import compare_mitosis_meiosis
        return ('print_lines', compare_mitosis_meiosis())

    elif cmd == 'evolution':
        from lib.bio_engine import evolution_info
        if len(parts) < 2:
            return ('print_lines', [
                '  Concepts: natural_selection, genetic_drift,',
                '  gene_flow, mutation, non_random_mating',
                '  Use: evolution [concept]',
            ])
        name = ' '.join(parts[1:])
        return ('print_lines', evolution_info(name))

    elif cmd == 'speciation':
        from lib.bio_engine import speciation_info
        if len(parts) < 2:
            return ('print_lines', speciation_info())
        return ('print_lines', speciation_info(parts[1]))

    elif cmd == 'microbe':
        from lib.bio_engine import microbe_info
        if len(parts) < 2:
            return ('print_lines', [
                '  Types: bacteria, virus, fungus, protozoa',
                '  Use: microbe [type]',
            ])
        return ('print_lines', microbe_info(parts[1]))

    elif cmd == 'immune':
        from lib.bio_engine import immune_info
        if len(parts) < 2:
            return ('print_lines', immune_info())
        return ('print_lines', immune_info(parts[1]))

    elif cmd == 'disease':
        from lib.bio_engine import disease_info
        if len(parts) < 2:
            return ('print_lines', [
                '  Diseases: malaria, tuberculosis,',
                '  diabetes, asthma',
                '  Use: disease [name]',
            ])
        name = ' '.join(parts[1:])
        return ('print_lines', disease_info(name))

    elif cmd == 'clear':
        return ('clear',)

    else:
        return ('print', f'  Unknown command "{cmd}"')


def cmd_code(args):
    a = args.strip()
    if a == 'run':
        return ('print', '  Usage: code run [filename]')
    if a.startswith('run '):
        from lib.code_engine import code_run
        name = a[4:].strip()
        result = code_run(name)
        return ('print_lines', result) if isinstance(result, list) else ('print', str(result))
    if a == 'list':
        from lib.code_engine import code_list
        return ('print_lines', code_list())
    if a == 'syntax' or a == 'functions' or a == 'libraries' or a == 'examples' or a == 'mp':
        from lib.code_engine import code_dispatch
        result = code_dispatch(a)
        return ('print_lines', result) if isinstance(result, list) else ('print', str(result))
    def _code_loop(tft, read_key):
        from lib.code_engine import (
            code_new, code_save, code_load, code_list,
            code_delete, code_run
        )

        code_state = None
        edit_lines = ['']
        filename = a
        if filename:
            state, loaded = code_load(filename)
            if state:
                code_state = state
                edit_lines = list(state.get('lines', ['']))
                for i in range(len(edit_lines)):
                    if not isinstance(edit_lines[i], str):
                        edit_lines[i] = str(edit_lines[i])
                if not edit_lines:
                    edit_lines = ['']
            else:
                code_state = code_new(filename)
                edit_lines = ['']
        else:
            code_state = code_new('untitled.py')
            edit_lines = ['']

        edit_idx = 0
        scroll_off = 0
        col = 0
        EDIT_VIS = 15
        CONTENT_Y = 26
        STATUS_Y = 272
        PROMPT_Y = 288
        LINE_H = 16
        MINIMAP_W = 40
        MINIMAP_X = 436
        modified = False
        showing_help = False
        help_page = 0
        showing_list = False

        PY_KW = {'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
                  'import', 'from', 'try', 'except', 'finally', 'with', 'as',
                  'pass', 'break', 'continue', 'yield', 'lambda', 'global',
                  'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is',
                  'raise', 'assert', 'del', 'nonlocal'}
        PY_BI = {'print', 'len', 'range', 'int', 'str', 'float', 'list',
                 'dict', 'set', 'tuple', 'type', 'isinstance', 'sorted',
                 'map', 'filter', 'zip', 'enumerate', 'min', 'max', 'sum',
                 'abs', 'round', 'open', 'input', 'any', 'all', 'format',
                 'repr', 'hex', 'oct', 'bin', 'chr', 'ord'}

        def _line_y(idx):
            """Get y position for a line index (or -1 if off-screen)."""
            if idx < scroll_off or idx >= scroll_off + EDIT_VIS:
                return -1
            return CONTENT_Y + 2 + (idx - scroll_off) * LINE_H

        def _safe_line(idx):
            """Get a safe string version of a line."""
            if idx < 0 or idx >= len(edit_lines):
                return ''
            l = edit_lines[idx]
            if l is None:
                edit_lines[idx] = ''
                return ''
            if not isinstance(l, str):
                try:
                    l = str(l)
                    edit_lines[idx] = l
                except:
                    return ''
            return l

        def _draw_single_line(idx):
            """Draw a single line."""
            y = _line_y(idx)
            if y < 0:
                return
            l = _safe_line(idx)
            is_cur = (idx == edit_idx)

            tft.fill_rect(42, y - 1, MINIMAP_X - 42, LINE_H, 0x10A4 if is_cur else 0x0000)

            ln = idx + 1
            if ln < 10:
                ln_str = '  ' + str(ln)
            elif ln < 100:
                ln_str = ' ' + str(ln)
            else:
                ln_str = str(ln)
            tft.text15(ln_str, 2, y, 0xFFE0 if is_cur else 0x6B6D, 0x0000)

            tft.fill_rect(44, y, MINIMAP_X - 44, LINE_H, 0x0000)
            if l:
                tft.text15(l[:35], 44, y, 0xFFFF, 0x0000)

            if is_cur:
                cur_x = 44 + (col if col < len(l) else len(l)) * 12
                if cur_x < MINIMAP_X - 2:
                    tft.fill_rect(cur_x, y + LINE_H - 2, 10, 2, 0x07E0)

            spaces = 0
            for c in l:
                if c == ' ':
                    spaces += 1
                elif c == '\t':
                    spaces += 4
                else:
                    break
            if spaces >= 4:
                for il in range(4, spaces, 4):
                    gx = 44 + il * 6
                    if gx < MINIMAP_X - 5:
                        tft.fill_rect(gx, y, 1, LINE_H - 2, 0x2949 if is_cur else 0x1082)

        def _draw_header():
            bg = 0x1082
            tft.fill_rect(0, 0, 480, 24, bg)
            tft.hline(0, 24, 480, 0x07FF)
            if oled:
                fname = code_state['name'] if code_state else 'untitled'
                mod = ' *' if modified else ''
                total = len(edit_lines)
                oled.set_engine_status('Code',
                    line0=fname + mod,
                    line1='Ln ' + str(edit_idx + 1) + '/' + str(total),
                    line2=str(col) + ' col')

        def _draw_minimap():
            tft.fill_rect(MINIMAP_X, CONTENT_Y, MINIMAP_W, STATUS_Y - CONTENT_Y, 0x0D18)
            total = len(edit_lines)
            if total == 0:
                return
            mh = STATUS_Y - CONTENT_Y - 4
            for i in range(total):
                l = _safe_line(i)
                my = CONTENT_Y + 2 + int(i * mh / total)
                if my >= STATUS_Y - 2:
                    break
                indent = 0
                for c in l:
                    if c == ' ':
                        indent += 1
                    elif c == '\t':
                        indent += 4
                    else:
                        break
                color = 0x8410
                stripped = l.strip()
                if stripped:
                    if stripped.startswith('def ') or stripped.startswith('class '):
                        color = 0x07FF
                    elif stripped.startswith('#'):
                        color = 0x4208
                    elif stripped.startswith('import ') or stripped.startswith('from '):
                        color = 0xF81F
                w = min(len(stripped) // 4 + 1, MINIMAP_W - 4)
                tft.fill_rect(MINIMAP_X + 4 + indent // 2, my, max(w, 1), 1, color)
            vp_top = int(scroll_off * mh / total)
            vp_bot = int((scroll_off + EDIT_VIS) * mh / total)
            vp_bot = max(vp_bot, vp_top + 2)
            tft.fill_rect(MINIMAP_X, CONTENT_Y + 2 + vp_top, MINIMAP_W, vp_bot - vp_top, 0x2925)

        def _draw_scrollbar():
            total = len(edit_lines)
            if total <= EDIT_VIS:
                return
            sb_h = STATUS_Y - CONTENT_Y - 4
            sb_x = MINIMAP_X + MINIMAP_W - 4
            tft.fill_rect(sb_x, CONTENT_Y + 2, 3, sb_h, 0x1082)
            thumb_h = max(8, int(EDIT_VIS * sb_h / total))
            thumb_y = CONTENT_Y + 2 + int(scroll_off * sb_h / total)
            tft.fill_rect(sb_x, thumb_y, 3, thumb_h, 0x8410)

        def _draw_status():
            bg = 0x1082
            tft.fill_rect(0, STATUS_Y, 480, 16, bg)
            fname = code_state['name'] if code_state else 'untitled'
            tft.text15(fname[:22], 4, STATUS_Y + 1, 0xFFFF, bg)
            tft.text15(str(edit_idx + 1) + ':' + str(col + 1), 320, STATUS_Y + 1, 0xFFE0, bg)
            pct = int((scroll_off + EDIT_VIS) * 100 / max(len(edit_lines), 1))
            tft.text15(str(min(pct, 100)) + '%', 400, STATUS_Y + 1, 0x8410, bg)
            tft.text15(str(len(edit_lines)) + 'L', 440, STATUS_Y + 1, 0x6B6D, bg)

        def _draw_output(msg):
            tft.fill_rect(0, PROMPT_Y, 480, 32, 0x0D18)
            tft.text15(msg[:40], 4, PROMPT_Y + 2, 0x07E0, 0x0D18)

        def _show_run_result(result):
            tft.fill_rect(0, PROMPT_Y, 480, 32, 0x0D18)
            if isinstance(result, list):
                for i, l in enumerate(result[:2]):
                    tft.text15(l[:40], 4, PROMPT_Y + 2 + i * 14, 0x07E0, 0x0D18)
            else:
                tft.text15(str(result)[:40], 4, PROMPT_Y + 2, 0x07E0, 0x0D18)

        def _draw_help():
            tft.fill_rect(0, CONTENT_Y, 480, STATUS_Y - CONTENT_Y, 0x0000)
            help_lines = [
                '=== Keyboard Shortcuts ===',
                '',
                '  Ctrl+S      Save file',
                '  Ctrl+X      Save & quit',
                '  Ctrl+Q      Quit (no save)',
                '  Ctrl+O      Open file',
                '  Ctrl+N      New file',
                '  Ctrl+R      Run file',
                '  Ctrl+L      List files',
                '  Ctrl+D      Delete file',
                '  Ctrl+H      This help',
                '',
                '  Up/Down     Move line',
                '  Left/Right  Move cursor',
                '  Enter       New line',
                '  Backspace   Delete char',
                '  Tab         Autocomplete',
            ]
            y = CONTENT_Y + 2
            for l in help_lines:
                tft.text15(l[:36], 4, y, 0xFFFF, 0x0000)
                y += LINE_H

        def _show_list():
            tft.fill_rect(0, CONTENT_Y, 480, STATUS_Y - CONTENT_Y, 0x0000)
            result = code_list()
            y = CONTENT_Y + 2
            for l in (result if isinstance(result, list) else [str(result)])[:15]:
                tft.text15(l[:36], 4, y, 0xFFFF, 0x0000)
                y += LINE_H

        def _redraw():
            """Full redraw — for first time, file open, scroll, etc."""
            try:
                _draw_header()
                tft.fill_rect(0, CONTENT_Y, MINIMAP_X, STATUS_Y, 0x0000)
                for i in range(scroll_off, min(scroll_off + EDIT_VIS, len(edit_lines))):
                    _draw_single_line(i)
                _draw_minimap()
                _draw_scrollbar()
                _draw_status()
            except Exception as e:
                tft.fill_rect(0, CONTENT_Y, 480, STATUS_Y - CONTENT_Y, 0x0000)
                err = str(e)
                tft.text15('Error:', 4, CONTENT_Y + 2, 0xF800, 0x0000)
                for i in range(0, min(len(err), 36), 36):
                    tft.text15(err[i:i+36], 4, CONTENT_Y + 20 + i//36 * 16, 0xFFFF, 0x0000)

        def _redraw_incremental(prev_idx, prev_scroll):
            """Incremental redraw — only redraw what changed."""
            try:
                scroll_changed = (prev_scroll != scroll_off)
                idx_changed = (prev_idx != edit_idx)

                if scroll_changed:
                    tft.fill_rect(0, CONTENT_Y, MINIMAP_X, STATUS_Y, 0x0000)
                    for i in range(scroll_off, min(scroll_off + EDIT_VIS, len(edit_lines))):
                        _draw_single_line(i)
                    _draw_minimap()
                    _draw_scrollbar()
                elif idx_changed:
                    _draw_single_line(prev_idx)
                    _draw_single_line(edit_idx)
                else:
                    _draw_single_line(edit_idx)

                _draw_status()
            except:
                _redraw()

        _redraw()

        while True:
            ch = read_key()
            if ch is None:
                continue

            if showing_help:
                if ch in ('\x1b', 'q', 'Q', '\x08'):
                    showing_help = False
                    _redraw()
                continue

            if showing_list:
                if ch in ('\x1b', 'q', 'Q', '\x08'):
                    showing_list = False
                    _redraw()
                continue

            # Ctrl shortcuts
            if ch == '\x13':  # Ctrl+S — save
                if code_state:
                    code_state['lines'] = edit_lines
                    code_save(code_state)
                    modified = False
                _redraw()
                continue

            if ch == '\x18':  # Ctrl+X — save and quit
                if code_state:
                    code_state['lines'] = edit_lines
                    code_save(code_state)
                return

            if ch == '\x11':  # Ctrl+Q — quit without saving
                return

            if ch == '\x0f':  # Ctrl+O — open file
                showing_list = True
                _show_list()
                continue

            if ch == '\x0e':  # Ctrl+N — new file
                code_state = code_new('untitled.py')
                edit_lines = ['']
                edit_idx = 0
                col = 0
                scroll_off = 0
                modified = False
                _redraw()
                continue

            if ch == '\x12':  # Ctrl+R — run file
                if code_state:
                    code_state['lines'] = edit_lines
                    code_save(code_state)
                    result = code_run(code_state['name'])
                    _show_run_result(result)
                    modified = False
                _redraw()
                continue

            if ch == '\x0c':  # Ctrl+L — list files
                showing_list = True
                _show_list()
                continue

            if ch == '\x04':  # Ctrl+D — delete file
                if code_state:
                    code_delete(code_state['name'])
                _redraw()
                continue

            # Arrow keys
            if ch == '\x80':  # Up
                prev_idx = edit_idx
                prev_scroll = scroll_off
                if edit_idx > 0:
                    edit_idx -= 1
                    col = min(col, len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0)
                    if edit_idx < scroll_off:
                        scroll_off = edit_idx
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            if ch == '\x81':  # Down
                prev_idx = edit_idx
                prev_scroll = scroll_off
                if edit_idx < len(edit_lines) - 1:
                    edit_idx += 1
                    col = min(col, len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0)
                    if edit_idx >= scroll_off + EDIT_VIS:
                        scroll_off = edit_idx - EDIT_VIS + 1
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            if ch == '\x82':  # Page Up
                prev_idx = edit_idx
                prev_scroll = scroll_off
                edit_idx = max(0, edit_idx - EDIT_VIS)
                scroll_off = max(0, scroll_off - EDIT_VIS)
                col = min(col, len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0)
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            if ch == '\x83':  # Page Down
                prev_idx = edit_idx
                prev_scroll = scroll_off
                edit_idx = min(len(edit_lines) - 1, edit_idx + EDIT_VIS)
                scroll_off = min(max(0, len(edit_lines) - EDIT_VIS), scroll_off + EDIT_VIS)
                col = min(col, len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0)
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            if ch == '\x86':  # Left
                prev_idx = edit_idx
                prev_scroll = scroll_off
                if col > 0:
                    col -= 1
                elif edit_idx > 0:
                    edit_idx -= 1
                    col = len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0
                    if edit_idx < scroll_off:
                        scroll_off = edit_idx
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            if ch == '\x87':  # Right
                prev_idx = edit_idx
                prev_scroll = scroll_off
                cur_len = len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0
                if col < cur_len:
                    col += 1
                elif edit_idx < len(edit_lines) - 1:
                    edit_idx += 1
                    col = 0
                    if edit_idx >= scroll_off + EDIT_VIS:
                        scroll_off = edit_idx - EDIT_VIS + 1
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            # Home / End
            if ch == '\x88':  # Home
                prev_idx = edit_idx
                col = 0
                _redraw_incremental(prev_idx, scroll_off)
                continue

            if ch == '\x89':  # End
                prev_idx = edit_idx
                col = len(edit_lines[edit_idx]) if isinstance(edit_lines[edit_idx], str) else 0
                _redraw_incremental(prev_idx, scroll_off)
                continue

            # Enter — new line
            if ch == '\n':
                prev_idx = edit_idx
                prev_scroll = scroll_off
                line = edit_lines[edit_idx] if isinstance(edit_lines[edit_idx], str) else ''
                before = line[:col]
                after = line[col:]
                edit_lines[edit_idx] = before
                edit_lines.insert(edit_idx + 1, after)
                edit_idx += 1
                col = 0
                modified = True
                if edit_idx >= scroll_off + EDIT_VIS:
                    scroll_off = edit_idx - EDIT_VIS + 1
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            # Backspace
            if ch in ('\b', '\x7f'):
                prev_idx = edit_idx
                prev_scroll = scroll_off
                if col > 0:
                    line = edit_lines[edit_idx] if isinstance(edit_lines[edit_idx], str) else ''
                    edit_lines[edit_idx] = line[:col-1] + line[col:]
                    col -= 1
                    modified = True
                elif edit_idx > 0:
                    prev = edit_lines[edit_idx - 1] if isinstance(edit_lines[edit_idx - 1], str) else ''
                    cur = edit_lines[edit_idx] if isinstance(edit_lines[edit_idx], str) else ''
                    prev_len = len(prev)
                    edit_lines[edit_idx - 1] = prev + cur
                    edit_lines.pop(edit_idx)
                    edit_idx -= 1
                    col = prev_len
                    modified = True
                    if edit_idx < scroll_off:
                        scroll_off = edit_idx
                _redraw_incremental(prev_idx, prev_scroll)
                continue

            # Tab — insert spaces
            if ch == '\t':
                prev_idx = edit_idx
                line = edit_lines[edit_idx] if isinstance(edit_lines[edit_idx], str) else ''
                edit_lines[edit_idx] = line[:col] + '    ' + line[col:]
                col += 4
                modified = True
                _redraw_incremental(prev_idx, scroll_off)
                continue

            # Printable character — insert at cursor
            if len(ch) == 1 and 32 <= ord(ch) <= 126:
                prev_idx = edit_idx
                prev_scroll = scroll_off
                line = edit_lines[edit_idx] if isinstance(edit_lines[edit_idx], str) else ''
                edit_lines[edit_idx] = line[:col] + ch + line[col:]
                col += 1
                modified = True
                _redraw_incremental(prev_idx, prev_scroll)
                continue

    return ('game', _code_loop)



def cmd_music(args):
    if args.strip():
        from lib.music_player import WAV_SONGS, WAV_NAMES
        name = args.strip().lower()
        match = [s for s in WAV_NAMES if name in s.lower()]
        if match:
            wav_path = WAV_SONGS[match[0]]
            return ('game', lambda tft, rk, _p=wav_path, _n=match[0]: _music_play_wav(tft, rk, _p, _n))
        return ('print', 'music: unknown song "' + args.strip() + '"')

    def _music_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS, OLED_REF
        from lib.music_player import WAV_SONGS, WAV_NAMES
        import os

        tc = THEME_COLORS if THEME_COLORS else {}
        HDR = tc.get('header', 0x1082)
        ACC = tc.get('accent', 0x07FF)
        GRN = tc.get('green', 0x07E0)
        YEL = tc.get('yellow', 0xFFE0)
        RED = tc.get('red', 0xF800)

        sel = 0
        scroll_off = 0
        volume = 30

        try:
            from lib.audio import AudioPlayer
            _audio_ref = AudioPlayer()
            _audio_ref.set_volume(volume)
        except:
            _audio_ref = None

        HEADER_H = 24
        CONTENT_Y = 26
        FOOTER_Y = 280
        LINE_H = 20

        def _draw_header():
            tft.fill_rect(0, 0, 480, HEADER_H, HDR)
            tft.text15('Music Player', 4, 4, ACC, HDR)
            tft.hline(0, HEADER_H, 480, ACC)

        def _draw_song_list():
            nonlocal scroll_off
            tft.fill_rect(0, CONTENT_Y, 480, FOOTER_Y - CONTENT_Y, 0x0000)
            vis_count = (FOOTER_Y - CONTENT_Y) // LINE_H
            if sel < scroll_off:
                scroll_off = sel
            if sel >= scroll_off + vis_count:
                scroll_off = sel - vis_count + 1
            y = CONTENT_Y + 6
            for i in range(vis_count):
                idx = scroll_off + i
                if idx >= len(WAV_NAMES):
                    break
                name = WAV_NAMES[idx]
                wav_path = WAV_SONGS[name]
                marker = '> ' if idx == sel else '  '
                color = ACC if idx == sel else 0xFFFF
                try:
                    st = os.stat(wav_path)
                    size_kb = st[6] // 1024
                    info = name + ' (' + str(size_kb) + 'KB)'
                except:
                    info = name + ' (missing)'
                    color = RED
                tft.text15(marker + info, 4, y, color, 0x0000)
                y += LINE_H

        def _update_selection(old_sel, new_sel):
            vis_count = (FOOTER_Y - CONTENT_Y) // LINE_H
            for s in [old_sel, new_sel]:
                if s < scroll_off or s >= scroll_off + vis_count:
                    continue
                si = s - scroll_off
                sy = CONTENT_Y + 6 + si * LINE_H
                tft.fill_rect(0, sy, 480, LINE_H, 0x0000)
                name = WAV_NAMES[s]
                wav_path = WAV_SONGS[name]
                marker = '> ' if s == new_sel else '  '
                color = ACC if s == new_sel else 0xFFFF
                try:
                    st = os.stat(wav_path)
                    size_kb = st[6] // 1024
                    info = name + ' (' + str(size_kb) + 'KB)'
                except:
                    info = name + ' (missing)'
                    color = RED
                tft.text15(marker + info, 4, sy, color, 0x0000)

        def _draw_footer():
            tft.fill_rect(0, FOOTER_Y, 480, 40, 0x0000)
            tft.text8('Up/Down=select  Enter=play  Q=quit', 4, FOOTER_Y + 2, 0x8410, 0x0000)
            tft.text8(str(sel + 1) + '/' + str(len(WAV_NAMES)) + '  Vol:' + str(volume) + '%', 4, FOOTER_Y + 16, 0x8410, 0x0000)

        _draw_header()
        _draw_song_list()
        _draw_footer()

        while True:
            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q' or ch == '\x1b':
                return
            elif ch == '\x86':
                volume = min(100, volume + 10)
                if _audio_ref:
                    _audio_ref.set_volume(volume)
                _draw_footer()
            elif ch == '\x87':
                volume = max(0, volume - 10)
                if _audio_ref:
                    _audio_ref.set_volume(volume)
                _draw_footer()
            elif ch == '\x88':
                volume = 0
                if _audio_ref:
                    _audio_ref.set_volume(0)
                _draw_footer()
            elif ch == '\x80':
                old = sel
                sel = max(0, sel - 1)
                if sel != old:
                    _update_selection(old, sel)
                    _draw_footer()
            elif ch == '\x81':
                old = sel
                sel = min(len(WAV_NAMES) - 1, sel + 1)
                if sel != old:
                    _update_selection(old, sel)
                    _draw_footer()
            elif ch == '\n':
                wav_name = WAV_NAMES[sel]
                wav_path = WAV_SONGS[wav_name]
                _music_play_wav(tft, read_key, wav_path, wav_name)
                _draw_header()
                _draw_song_list()
                _draw_footer()
            elif ch == '\t':
                sel = (sel + 1) % len(WAV_NAMES)
                _draw_song_list()
                _draw_footer()

    return ('game', _music_loop)


def _music_play_wav(tft, read_key, wav_path, song_name):
    from commands.dispatch import THEME_COLORS, OLED_REF
    import os

    tc = THEME_COLORS if THEME_COLORS else {}
    HDR = tc.get('header', 0x1082)
    ACC = tc.get('accent', 0x07FF)
    GRN = tc.get('green', 0x07E0)
    YEL = tc.get('yellow', 0xFFE0)
    RED = tc.get('red', 0xF800)

    try:
        st = os.stat(wav_path)
    except:
        tft.fill(0x0000)
        tft.text15('WAV not found', 4, 100, RED, 0x0000)
        tft.text15(wav_path, 4, 120, 0x8410, 0x0000)
        time.sleep_ms(2000)
        return

    wav_size = st[6]
    size_kb = wav_size // 1024

    tft.fill(0x0000)
    tft.fill_rect(0, 0, 480, 24, HDR)
    tft.text15(song_name, 4, 4, ACC, HDR)
    tft.hline(0, 24, 480, ACC)

    tft.text15('Now Playing', 4, 50, GRN, 0x0000)
    tft.text15(song_name, 4, 70, 0xFFFF, 0x0000)
    tft.text8(str(size_kb) + ' KB  ' + wav_path, 4, 90, 0x8410, 0x0000)

    bar_y = 130
    bar_w = 460
    tft.fill_rect(10, bar_y, bar_w, 14, 0x2104)
    tft.rect(10, bar_y, bar_w, 14, 0x8410)

    tft.text8('Space=stop  Q=quit', 4, 270, 0x8410, 0x0000)

    if OLED_REF:
        OLED_REF.set_engine_status('Music',
            line0=song_name[:18],
            line1='Playing WAV...',
            line2=str(size_kb) + ' KB',
            line3='')

    from lib.audio import AudioPlayer
    audio = AudioPlayer()
    volume = 30

    play_start = time.ticks_ms()

    def _wav_callback(bytes_read, total):
        if total > 0:
            filled = bar_w * bytes_read // total
            tft.fill_rect(11, bar_y + 1, filled, 12, GRN)
            pct = bytes_read * 100 // total
            tft.text8(str(pct) + '%  Vol:' + str(volume) + '%', 180, bar_y + 2, 0xFFFF, 0x0000)

    audio.set_volume(volume)

    stopped = [False]
    chunk_counter = [0]
    def _stop_check():
        nonlocal volume
        chunk_counter[0] += 1
        if chunk_counter[0] % 12 != 0:
            return False
        ch = read_key()
        if ch in ('q', 'Q', '\x1b', ' '):
            stopped[0] = True
            audio.off()
            return True
        if ch in ('\x86', '\x87'):
            if ch == '\x86':
                volume = min(100, volume + 10)
            else:
                volume = max(0, volume - 10)
            audio.set_volume(volume)
        return False

    audio.play_wav(wav_path, callback=_wav_callback, stop_check=_stop_check)

    elapsed = time.ticks_diff(time.ticks_ms(), play_start)
    mins = elapsed // 60000
    secs = (elapsed % 60000) // 1000

    if stopped[0]:
        tft.fill_rect(10, bar_y, bar_w, 14, 0x2104)
        tft.text8('Stopped  ' + str(mins) + 'm ' + str(secs) + 's', 180, bar_y + 2, YEL, 0x0000)
    else:
        tft.fill_rect(10, bar_y, bar_w, 14, GRN)
        tft.text8('Done!  ' + str(mins) + 'm ' + str(secs) + 's', 180, bar_y + 2, 0xFFFF, 0x0000)

    if OLED_REF:
        OLED_REF.set_engine_status('Music',
            line0=song_name[:18],
            line1='Done!' if not stopped[0] else 'Stopped',
            line2=str(mins) + 'm ' + str(secs) + 's',
            line3='')

    time.sleep_ms(1500)


def cmd_adventure(args):
    from lib.adventure_engine import (
        create_game, process_command, get_room_description,
        get_player_status, get_inventory_display
    )

    game_state = create_game()

    def _adv_dispatch(cmd_str):
        nonlocal game_state
        lines, game_state = process_command(game_state, cmd_str)
        if game_state.get('game_over'):
            from lib.highscores import set as _hs_set, get as _hs_get
            score = game_state.get('gold', 0) + game_state.get('xp', 0)
            prev = _hs_get('ADVENTURE')
            if score > prev:
                _hs_set('ADVENTURE', score)
            best = _hs_get('ADVENTURE')
            lines.append(f'Score: {score}  Best: {best}')
        return ('print_lines', lines)

    def _adv_loop(tft, read_key):
        from commands.dispatch import THEME_COLORS, OLED_REF
        _repl_loop(tft, read_key, 'Espelt Adventure RPG', _adv_dispatch, [
            ['go [dir]        Move direction',
             'n/s/e/w          Quick move',
             'take [item]      Pick up item',
             'use [item]       Use consumable',
             'equip [item]     Equip weapon/armor',
             'attack/fight     Attack enemy',
             'flee             Run from combat'],
            ['i                Inventory',
             'look (l)         Look around',
             'status (st)      Player stats',
             'map (m)          Dungeon map',
             'open             Unlock door (key)',
             'drop [item]      Drop item',
             'q                Quit game'],
            ['Explore 12 rooms, find the key,',
             'defeat the dragon, and claim the',
             'treasury! Collect weapons and',
             'potions along the way.',
             '',
             'Type "help" for all commands.'],
        ], THEME_COLORS, [
            'go', 'north', 'south', 'east', 'west', 'n', 's', 'e', 'w',
            'take', 'get', 'use', 'equip', 'attack', 'fight', 'flee',
            'inventory', 'i', 'look', 'l', 'status', 'map', 'm',
            'open', 'drop', 'help', 'quit', 'potion', 'torch', 'key',
            'sword', 'shield',
        ], oled=OLED_REF)
    return ('game', _adv_loop)


def cmd_temp(args):
    try:
        import machine
        sensor = machine.ADC(machine.Pin(4))
        raw = sensor.read()
        temp = (raw / 4095) * 3.3
        temp_c = (temp - 0.76) / 0.0025 + 25
        return ('print_lines', [
            '=== CPU Temperature ===',
            f'  Raw:     {raw}',
            f'  Voltage: {temp:.3f}V',
            f'  Temp:    {temp_c:.1f}C',
            f'          {temp_c * 9/5 + 32:.1f}F',
        ])
    except Exception as e:
        return ('print', f'temp: {e}')


def cmd_about(args):
    return ('print_lines', [
        '=== Project Espelt ===',
        '',
        '  A portable cyberdeck built on',
        '  ESP32-P4 with MicroPython.',
        '',
        '  Hardware:',
        '    MCU: ESP32-P4 (32MB RAM)',
        '    TFT: ILI9488 480x320',
        '    OLED: SSD1306 128x64',
        '    Keyboard: USB HID',
        '    Buzzer: GPIO20',
        '',
        '  Features:',
        '    50 games (CPU opponents)',
        '    Chemistry/Biology/Coding engines',
        '    Music player + Piano',
        '    Text adventure RPG',
        '    3D wireframe renderer',
        '    Paint app',
        '    50+ OLED animations',
        '    200+ commands',
        '',
        '  Author: AntacidDT',
        '  Repo: AntacidDT/MPY-with-USBHost',
    ])


def cmd_thread(args):
    import _thread
    import gc
    lines = [
        '=== Threads ===',
        f'  Active: {_thread.get_ident()} (main)',
        f'  Free RAM: {gc.mem_free()} bytes',
        f'  Used RAM: {gc.mem_alloc()} bytes',
        f'  Total: {gc.mem_free() + gc.mem_alloc()} bytes',
    ]
    return ('print_lines', lines)


def cmd_gc(args):
    import gc
    gc.collect()
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    pct = int(alloc * 100 / total) if total > 0 else 0
    return ('print_lines', [
        '=== Memory (GC) ===',
        f'  Free:      {free} bytes',
        f'  Allocated: {alloc} bytes ({pct}%)',
        f'  Total:     {total} bytes',
        '  Collected garbage.',
    ])


def cmd_piano(args):
    def _piano_loop(tft, read_key):
        from lib.audio import AudioPlayer
        audio = AudioPlayer()
        octave = 4
        volume = 70
        recording = False
        recorded = []
        rec_start = 0

        NOTES = {
            'z': ('C', 0), 's': ('C#', 1), 'x': ('D', 2),
            'd': ('D#', 3), 'c': ('E', 4), 'v': ('F', 5),
            'g': ('F#', 6), 'b': ('G', 7), 'h': ('G#', 8),
            'n': ('A', 9), 'j': ('A#', 10), 'm': ('B', 11),
            'q': ('C', 12), '2': ('C#', 13), 'w': ('D', 14),
            '3': ('D#', 15), 'e': ('E', 16), 'r': ('F', 17),
            '5': ('F#', 18), 't': ('G', 19), '6': ('G#', 20),
            'y': ('A', 21), '7': ('A#', 22), 'u': ('B', 23),
        }

        def note_freq(note_name, octave):
            semitones = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
            n = semitones[note_name]
            return int(440 * 2 ** ((n - 9 + (octave - 4) * 12) / 12))

        WHITE_KEYS = ['C','D','E','F','G','A','B']
        BLACK_KEYS = ['C#','D#','F#','G#','A#']

        def _header():
            tft.fill_rect(0, 0, 480, 24, 0x1082)
            tft.text15('Espelt Piano', 160, 4, 0x07FF, 0x1082)
            tft.hline(0, 24, 480, 0x07FF)

        def _draw_keyboard():
            tft.fill_rect(0, 25, 480, 160, 0x0000)
            # Draw white keys
            key_w = 480 // 7
            for i, note in enumerate(WHITE_KEYS):
                x = i * key_w
                tft.fill_rect(x + 1, 40, key_w - 2, 120, 0xFFFF)
                tft.rect(x, 40, key_w, 120, 0x8410)
                tft.text15(note + str(octave), x + key_w // 2 - 12, 140, 0x0000, 0xFFFF)
            # Draw black keys
            black_positions = [0, 1, 3, 4, 5]
            for i, pos in enumerate(black_positions):
                x = pos * key_w + key_w // 2 - 10
                tft.fill_rect(x, 40, 20, 75, 0x0000)
                tft.rect(x - 1, 40, 22, 75, 0x8410)
                tft.text15(BLACK_KEYS[i], x + 3, 95, 0xFFFF, 0x0000)
            # Key labels for bottom row
            bottom = ['z','s','x','d','c','v','g','b','h','n','j','m']
            labels = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
            y = 180
            for i in range(0, len(bottom), 2):
                x = (i // 2) * 70 + 10
                tft.text15(f'{bottom[i]}={labels[i//2]}{octave}', x, y, 0x8410, 0x0000)

        def _draw_status():
            tft.fill_rect(0, 200, 480, 120, 0x0000)
            tft.text15(f'Octave: {octave}  Vol: {volume}%', 4, 208, 0xFFFF, 0x0000)
            rec_text = 'REC' if recording else ''
            tft.text15(rec_text, 350, 208, 0xF800, 0x0000)
            tft.text('Z-M=play  Q=quit', 4, 230, 0x07E0, 0x0000)
            tft.text('Left/Right=octave', 4, 246, 0x07E0, 0x0000)
            tft.text('Up/Down=volume', 4, 262, 0x07E0, 0x0000)
            tft.text('Space=record/play', 4, 278, 0x07E0, 0x0000)

        def _highlight_key(note_name, pressed):
            key_w = 480 // 7
            if note_name in WHITE_KEYS:
                idx = WHITE_KEYS.index(note_name)
                x = idx * key_w + 1
                color = 0x07E0 if pressed else 0xFFFF
                tft.fill_rect(x, 40, key_w - 2, 120, color)
                tft.rect(x, 40, key_w, 120, 0x8410)
                tft.text15(note_name + str(octave), x + key_w // 2 - 12, 140, 0x0000, color)
            elif note_name in BLACK_KEYS:
                idx = BLACK_KEYS.index(note_name)
                white_pos = [0, 1, 3, 4, 5][idx]
                x = white_pos * key_w + key_w // 2 - 10
                color = 0x07E0 if pressed else 0x0000
                tft.fill_rect(x, 40, 20, 75, color)
                if not pressed:
                    tft.rect(x - 1, 40, 22, 75, 0x8410)
                tft.text15(note_name, x + 3, 95, 0xFFFF if pressed else 0x0000, color)

        _header()
        _draw_keyboard()
        _draw_status()

        while True:
            ch = read_key()
            if ch is None:
                continue
            if ch == 'q' or ch == 'Q':
                audio.off()
                return
            elif ch == '\x80':
                volume = min(100, volume + 10)
                audio.set_volume(volume)
                _draw_status()
            elif ch == '\x81':
                volume = max(0, volume - 10)
                audio.set_volume(volume)
                _draw_status()
            elif ch == '\x84':
                # Right arrow — octave up
                octave = min(6, octave + 1)
                _draw_keyboard()
                _draw_status()
            elif ch == '\x85':
                # Left arrow — octave down
                octave = max(2, octave - 1)
                _draw_keyboard()
                _draw_status()
            elif ch == ' ':
                # Space — toggle recording
                if recording:
                    recording = False
                    # Play back
                    for note_name, dur in recorded:
                        freq = note_freq(note_name, octave)
                        audio.piano_note(freq, dur)
                    recorded = []
                    _draw_status()
                else:
                    recording = True
                    recorded = []
                    rec_start = time.ticks_ms()
                    _draw_status()
            elif ch in NOTES:
                note_name, semitone = NOTES[ch]
                freq = note_freq(note_name, octave)
                _highlight_key(note_name, True)
                audio.piano_note(freq, 150)
                _highlight_key(note_name, False)
                if recording:
                    dur = 150
                    recorded.append((note_name, dur))
                from commands.dispatch import OLED_REF
                if OLED_REF:
                    OLED_REF.set_engine_status('Piano',
                        line0=note_name + str(octave) + ' ' + str(freq) + 'Hz',
                        line1='Octave: ' + str(octave),
                        line2='Vol: ' + str(volume) + '%',
                        line3='REC' if recording else '')

    return ('game', _piano_loop)


def cmd_dice(args):
    """Roll dice. Usage: dice [NdN] (e.g. dice 2d6, dice d20)"""
    import random
    spec = args.strip().lower().replace(' ', '') if args.strip() else '1d6'
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
        return ('print', f'  [{faces}] -> {total}')
    details = ', '.join(str(r) for r in rolls)
    return ('print_lines', [
        f'  {n}d{faces}: {details}',
        f'  Total: {total}',
    ])


def cmd_pick(args):
    """Pick a random item. Usage: pick item1 item2 item3 ..."""
    items = args.strip().split() if args.strip() else []
    if not items:
        return ('print_lines', [
            'pick: usage: pick <item1> <item2> ...',
            '',
            '  pick red blue green',
            '  pick alice bob charlie',
            '  pick rock paper scissors',
        ])
    import random
    chosen = random.choice(items)
    return ('print_lines', [
        f'  Items: {", ".join(items)}',
        f'  -> {chosen}',
    ])


def cmd_tip(args):
    """Calculate tip. Usage: tip <bill> [percent] [split]"""
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            'tip: usage: tip <bill> [percent] [split]',
            '',
            '  tip 50           50.00 bill, 15% tip',
            '  tip 50 20        50.00 bill, 20% tip',
            '  tip 50 15 3      50.00 bill, 15% tip, 3 people',
        ])
    try:
        bill = float(parts[0])
    except ValueError:
        return ('print', 'tip: invalid bill amount')
    pct = float(parts[1]) if len(parts) > 1 else 15.0
    split_n = int(parts[2]) if len(parts) > 2 else 1
    tip_amt = bill * pct / 100.0
    total = bill + tip_amt
    per_person = total / split_n if split_n > 0 else total
    lines = [
        f'  Bill:      {bill:.2f}',
        f'  Tip:       {tip_amt:.2f} ({pct:.0f}%)',
        f'  Total:     {total:.2f}',
    ]
    if split_n > 1:
        lines.append(f'  Per person:{per_person:.2f} ({split_n} people)')
    return ('print_lines', lines)


def cmd_morse(args):
    """Morse code encode/decode. Usage: morse enc/dec <text>"""
    parts = args.strip().split(None, 1) if args.strip() else []
    if len(parts) < 2:
        return ('print_lines', [
            'morse: usage:',
            '  morse enc <text>    Encode to morse',
            '  morse dec <morse>   Decode from morse',
            '',
            '  Example: morse enc SOS',
            '  Example: morse dec ... --- ...',
        ])
    mode = parts[0].lower()
    data = parts[1]
    E = {
        'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
        'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
        'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
        'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
        'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
        'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
        'Y': '-.--',  'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--',
        '?': '..--..', '!': '-.-.--', '/': '-..-.', '@': '.--.-.',
        '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
        ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-',
        '_': '..--.-', '"': '.-..-.', '$': '...-..-', ' ': '/',
    }
    D = {v: k for k, v in E.items() if k != ' '}
    if mode in ('enc', 'encode', 'e'):
        out = ' '.join(E.get(c.upper(), '?') for c in data)
        return ('print_lines', ['  ' + data.upper(), '  ' + out])
    elif mode in ('dec', 'decode', 'd'):
        words = data.split(' / ')
        decoded = []
        for word in words:
            letters = word.split(' ')
            decoded.append(''.join(D.get(l, '?') for l in letters))
        result = ' '.join(decoded)
        return ('print_lines', ['  ' + data, '  ' + result])
    return ('print', 'morse: use enc or dec')


def cmd_chess(args):
    """Play chess vs CPU."""
    from lib.chess_engine import chess_loop
    return ('game', chess_loop)


def cmd_mastermind(args):
    """Play mastermind vs CPU."""
    from lib.mastermind_engine import mastermind_loop
    return ('game', mastermind_loop)


def cmd_nim(args):
    """Play nim vs CPU."""
    from lib.nim_engine import nim_loop
    return ('game', nim_loop)


def cmd_blackjack(args):
    """Play blackjack vs dealer."""
    from lib.blackjack_engine import blackjack_loop
    return ('game', blackjack_loop)


def cmd_simon(args):
    """Play Simon memory game."""
    from lib.simon_engine import simon_loop
    return ('game', simon_loop)


def cmd_2048(args):
    """Play 2048 puzzle."""
    from lib.game2048_engine import _2048_loop
    return ('game', _2048_loop)


def cmd_snake(args):
    """Play Snake game."""
    from lib.snake_engine import snake_loop
    return ('game', snake_loop)


def cmd_tetris(args):
    """Play Tetris."""
    from lib.tetris_engine import tetris_loop
    return ('game', tetris_loop)


def cmd_breakout(args):
    """Play Breakout."""
    from lib.breakout_engine import breakout_loop
    return ('game', breakout_loop)


def cmd_flappy(args):
    """Play Flappy Bird."""
    from lib.flappy_engine import flappy_loop
    return ('game', flappy_loop)


def cmd_minesweeper(args):
    """Play Minesweeper."""
    from lib.minesweeper_engine import minesweeper_loop
    return ('game', minesweeper_loop)


def cmd_random(args):
    """Quick random number. Usage: random [min] [max]"""
    import random as _rand
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print', f'  {_rand.randint(0, 100)}')
    if len(parts) == 1:
        try:
            mx = int(parts[0])
            return ('print', f'  {_rand.randint(0, mx)}')
        except ValueError:
            return ('print', 'random: invalid number')
    try:
        mn, mx = int(parts[0]), int(parts[1])
        if mn > mx:
            mn, mx = mx, mn
        return ('print', f'  {_rand.randint(mn, mx)}')
    except ValueError:
        return ('print', 'random: usage: random [min] [max]')


def cmd_disk(args):
    """Disk usage breakdown. Usage: disk [dir]"""
    path = args.strip() if args.strip() else '/'
    try:
        entries = os.listdir(path)
    except OSError:
        return ('print', f'disk: {path}: not found')
    items = []
    total = 0
    for e in entries:
        full = path.rstrip('/') + '/' + e
        try:
            st = os.stat(full)
            size = st[6]
            is_dir = bool(st[0] & 0x4000)
            items.append((e, size, is_dir))
            total += size
        except OSError:
            pass
    items.sort(key=lambda x: -x[1])
    lines = [f'=== {path} ({len(items)} items) ===']
    for name, size, is_dir in items[:12]:
        if is_dir:
            lines.append(f'  {name}/')
        else:
            if size >= 1024 * 1024:
                sz = f'{size / 1048576:.1f}MB'
            elif size >= 1024:
                sz = f'{size / 1024:.1f}KB'
            else:
                sz = f'{size}B'
            bar_len = int(20 * size / max(total, 1))
            bar = '#' * bar_len + '.' * (20 - bar_len)
            lines.append(f'  {sz:>8s} {bar} {name}')
    if len(items) > 12:
        lines.append(f'  ... +{len(items) - 12} more')
    if total >= 1024 * 1024:
        lines.append(f'  Total: {total / 1048576:.1f}MB')
    elif total >= 1024:
        lines.append(f'  Total: {total / 1024:.1f}KB')
    else:
        lines.append(f'  Total: {total}B')
    return ('print_lines', lines)


def cmd_netdev(args):
    """Scan local network for devices. Usage: netdev"""
    import network
    import usocket
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        return ('print', 'netdev: connect to WiFi first (wlan)')
    ip = wlan.ifconfig()[0]
    prefix = '.'.join(ip.split('.')[:3])
    found = []
    found.append(f'=== Network Scan ({prefix}.x) ===')
    found.append(f'  Your IP: {ip}')
    found.append('')
    for host in range(1, 255):
        addr = f'{prefix}.{host}'
        try:
            sock = usocket.socket()
            sock.settimeout(0.1)
            sock.connect((addr, 80))
            sock.close()
            label = ' (you)' if addr == ip else ''
            found.append(f'  {addr}{label}')
        except:
            pass
    if len(found) <= 3:
        found.append('  No other devices found')
    found.append(f'  Found {len(found) - 3} device(s)')
    return ('print_lines', found)


def cmd_countdown(args):
    """Countdown timer with buzzer. Usage: countdown [time] (e.g. countdown 5m, countdown 30s)"""
    import time as _time
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            'countdown: usage: countdown [time]',
            '',
            '  countdown 30s    30 seconds',
            '  countdown 5m     5 minutes',
            '  countdown 1h30m  1 hour 30 minutes',
        ])
    # Parse time string
    total_secs = 0
    buf = ''
    for ch in parts[0]:
        if ch.isdigit():
            buf += ch
        elif ch == 'h' and buf:
            total_secs += int(buf) * 3600; buf = ''
        elif ch == 'm' and buf:
            total_secs += int(buf) * 60; buf = ''
        elif ch == 's' and buf:
            total_secs += int(buf); buf = ''
    if buf:
        total_secs += int(buf)
    if total_secs <= 0:
        return ('print', 'countdown: invalid time')
    # Find buzzer
    try:
        from lib.buzzer import Buzzer
        bz = Buzzer(20)
    except:
        bz = None
    start = _time.ticks_ms()
    end = _time.ticks_add(start, total_secs * 1000)
    while _time.ticks_diff(end, _time.ticks_ms()) > 0:
        remaining = _time.ticks_diff(end, _time.ticks_ms()) // 1000
        mins = remaining // 60
        secs = remaining % 60
        print(f'\r  {mins:02d}:{secs:02d}', end='')
        _time.sleep_ms(250)
    print('\r  00:00  DONE!')
    if bz:
        for _ in range(3):
            bz.beep(200)
            _time.sleep_ms(100)
    return ('print', '  Countdown complete!')


def cmd_charref(args):
    """Character reference table. Usage: charref [code]"""
    parts = args.strip().split() if args.strip() else []
    if parts:
        try:
            code = int(parts[0])
            ch = chr(code)
            return ('print_lines', [
                f'  Code: {code}',
                f'  Hex:  0x{code:02X}',
                f'  Oct:  0o{code:03o}',
                f'  Bin:  0b{code:08b}',
                f'  Char: {ch}',
            ])
        except (ValueError, OverflowError):
            return ('print', 'charref: invalid code')
    lines = ['=== ASCII Table (32-126) ===']
    row = ''
    for i in range(32, 127):
        row += f'{i:3d}={chr(i)} '
        if len(row) >= 52:
            lines.append('  ' + row)
            row = ''
    if row:
        lines.append('  ' + row)
    return ('print_lines', lines)


def cmd_sysinfo(args):
    """Full system status. Usage: sysinfo"""
    import gc
    import network
    lines = ['=== System Info ===']
    try:
        from machine import freq
        f = freq()
        lines.append(f'  CPU:     {f // 1000000}MHz')
    except:
        lines.append('  CPU:     N/A')
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    pct = int(alloc * 100 / total) if total > 0 else 0
    lines.append(f'  RAM:     {free // 1024}KB free / {total // 1024}KB ({pct}% used)')
    try:
        st = os.statvfs('/')
        total_f = st[0] * st[2]
        free_f = st[0] * st[3]
        used_f = total_f - free_f
        lines.append(f'  Flash:   {used_f // 1024}KB used / {total_f // 1024}KB')
    except:
        pass
    try:
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            cfg = wlan.ifconfig()
            lines.append(f'  WiFi:    {cfg[0]} ({wlan.config("essid")})')
        else:
            lines.append('  WiFi:    disconnected')
    except:
        lines.append('  WiFi:    N/A')
    return ('print_lines', lines)


def cmd_trolley(args):
    """Play trolley problem moral dilemma game."""
    from lib.trolley_engine import trolley_loop
    return ('game', trolley_loop)


def cmd_password(args):
    """Play password game with progressive rules."""
    from lib.password_engine import password_loop
    return ('game', password_loop)


def cmd_mystery(args):
    """Play mystery game (random mini-game)."""
    from lib.mystery_engine import mystery_loop
    return ('game', mystery_loop)


def cmd_life(args):
    """Play Game of Life."""
    from lib.life_engine import life_loop
    return ('game', life_loop)


def cmd_tron(args):
    """Play Tron light cycles."""
    from lib.tron_engine import tron_loop
    return ('game', tron_loop)


def cmd_maze3d(args):
    """Play 3D maze."""
    from lib.maze3d_engine import maze3d_loop
    return ('game', maze3d_loop)


def cmd_snake2(args):
    """Play Snake 2 (with obstacles)."""
    from lib.snake_engine import snake_loop
    return ('game', snake_loop)


def cmd_tetris2(args):
    """Play Tetris 2 (hard drop, hold)."""
    from lib.tetris_engine import tetris_loop
    return ('game', tetris_loop)


def cmd_breakout2(args):
    """Play Breakout 2 (multi-ball, levels)."""
    from lib.breakout_engine import breakout_loop
    return ('game', breakout_loop)


def cmd_pong(args):
    """Play Pong."""
    from lib.pong_engine import pong_loop
    return ('game', pong_loop)


def cmd_pong2p(args):
    """Play Pong 2 Player."""
    from lib.pong_engine import pong_loop
    return ('game', pong_loop)


def cmd_pong3d(args):
    """Play Pong 3D."""
    from lib.pong_engine import pong_loop
    return ('game', pong_loop)


def cmd_simon2(args):
    """Play Simon 2 (combos)."""
    from lib.simon_engine import simon_loop
    return ('game', simon_loop)


def cmd_audio(args):
    """Audio control: volume, play, stop, status."""
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            '=== AUDIO ===',
            '',
            '  audio vol [n]     Set volume (0-100)',
            '  audio play [f]    Play WAV from SD',
            '  audio stop        Stop playback',
            '  audio tone [f] [d] Play tone (Hz, ms)',
            '  audio status      Show audio status',
        ])
    cmd = parts[0].lower()
    try:
        from lib.audio import AudioPlayer
        a = AudioPlayer()
        if not a.available:
            return ('print', 'audio: I2S not available (no ES8311 codec)')
    except:
        return ('print', 'audio: module not found')

    if cmd == 'vol' or cmd == 'volume':
        if len(parts) < 2:
            return ('print', f'audio: volume = {a._volume}')
        try:
            vol = int(parts[1])
            a.set_volume(vol)
            return ('print', f'audio: volume = {vol}')
        except:
            return ('print', 'audio: usage: audio vol 80')

    elif cmd == 'play':
        if len(parts) < 2:
            return ('print', 'audio: usage: audio play /sd/songs/tiki.wav')
        path = parts[1]
        if not path.startswith('/'):
            path = '/sd/' + path
        ok = a.play_wav(path)
        if ok:
            return ('print', f'audio: playing {path}')
        else:
            return ('print', f'audio: failed to play {path}\n  Check file exists + is WAV format')

    elif cmd == 'stop':
        a.off()
        return ('print', 'audio: stopped')

    elif cmd == 'tone':
        freq = int(parts[1]) if len(parts) > 1 else 440
        dur = int(parts[2]) if len(parts) > 2 else 500
        a.tone(freq, dur)
        return ('print', f'audio: tone {freq}Hz {dur}ms')

    elif cmd == 'status':
        return ('print_lines', [
            f'  Codec: ES8311 {"OK" if a._codec.available else "FAIL"}',
            f'  I2S: {"OK" if a._available else "FAIL"}',
            f'  Volume: {a._volume}',
            f'  PA: enabled',
        ])

    return ('print', f'audio: unknown subcommand "{cmd}"')
