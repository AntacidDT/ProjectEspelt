import os

_aliases = {}
THEME_COLORS = {}
_buzzer = None
OLED_REF = None

COMMANDS = [
    'help', 'ls', 'cat', 'clear', 'cd', 'mkdir', 'rm', 'touch', 'info',
    'uname', 'pwd', 'echo', 'clock', 'math', 'nano', 'run', 'sleep',
    'view', 'wlan', 'games', 'timer', 'encrypt',
    'decrypt', 'draw', 'oled', 'wiki', 'timetable', 'prayer', 'chat',
    'todo', 'notes', 'convert', 'base', 'passwd', 'weather', 'freq',
    'mem', 'uptime', 'ping', 'color', 'uuid', 'history', 'grep', 'head',
    'tail', 'wc', 'diff', 'quote', 'joke', 'cowsay', 'df', 'find',
    'brightness', 'fm', 'theme', 'translate', 'define', 'qr', 'stopwatch',
    'ota', 'webrepl', 'dice', 'flip', 'news', 'stock', 'crypto', 'timezone',
    'physics', 'ip', 'du', 'base64', 'ascii', 'cp', 'mv',
    'ipinfo', 'exchange', 'gh', 'ghrepo', 'holiday', 'aqi', 'bored',
    'search', 'dns', 'curl', 'backup', 'restore', 'speedtest',
    'startup', 'flag', 'buzzer',     'rss',
    'forecast', 'numfact', 'catfact', 'dogfact', 'trivia', 'dadjoke',
    'randomfact', 'xkcd', 'vocab', 'joke2', 'chem', 'chemtable',
    'bio', 'code', 'piano', 'music', 'ghrepofs', 'draw', 'calendar',
    'alarm', 'notes', 'remind', 'contacts', 'hexdump', 'timer', 'chemtable',
    'geo', 'npm', 'pypi', 'quote', 'roast', 'adventure',
    'chuck', 'earthquake', 'colorinfo', 'nasa_apod',
    'stamp', 'hash', 'leap', 'age', 'pct', 'rev', 'chars',
    'temp', 'about', 'thread', 'gc',
    'pick', 'tip', 'morse', 'chess', 'mastermind', 'nim', 'blackjack',
    'simon', 'random', 'disk', 'netdev', 'countdown', 'charref', 'sysinfo',
    'passcheck', 'freqcount', 'snippet', 'electronics', 'trolley', 'password',
    'mystery', 'ytchl', 'ytdt', 'reddit', 'ytsearch', 'hn', 'so', 'devto', 'ghtrending',
    'audio', 'tone', 'tree', 'du_top', 'conv', 'bsky',
    'life', 'tron', 'maze3d', 'snake2', 'tetris2', 'breakout2', 'pong3d', 'simon2',
    'cooking', 'sandbox', 'infinitecraft',
    'gmail', 'ytdt',
]


def dispatch(line, tft=None, oled_ctrl=None):
    line = line.strip()
    if not line:
        return

    parts = line.split(None, 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''

    if cmd == 'alias':
        return cmd_alias(args)
    elif cmd == 'unalias':
        return cmd_unalias(args)

    if cmd in _aliases:
        line = _aliases[cmd] + (' ' + args if args else '')
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''

    # system commands
    if cmd == 'help':
        return cmd_help_screen(args)
    elif cmd == 'ls':
        return cmd_ls(args)
    elif cmd == 'cat':
        return cmd_cat(args)
    elif cmd == 'clear':
        return ('clear',)
    elif cmd == 'cd':
        return cmd_cd(args)
    elif cmd == 'mkdir':
        return cmd_mkdir(args)
    elif cmd == 'rm':
        return cmd_rm(args)
    elif cmd == 'touch':
        return cmd_touch(args)
    elif cmd == 'info':
        return cmd_info(tft)
    elif cmd == 'pwd':
        return ('print', f'  {os.getcwd()}')
    elif cmd == 'echo':
        return ('print', args)
    elif cmd == 'uname':
        return ('print', '  Espelt OS v1.0 - ESP32-P4')

    # systemcmd
    elif cmd == 'clock':
        from commands.systemcmd import cmd_clock
        return cmd_clock(tft)
    elif cmd == 'math':
        from commands.systemcmd import cmd_math
        return cmd_math(args, tft, oled_ctrl)
    elif cmd == 'nano':
        from commands.systemcmd import cmd_nano
        return cmd_nano(args, tft)
    elif cmd == 'run':
        from commands.systemcmd import cmd_run
        return cmd_run(args)
    elif cmd == 'sleep':
        from commands.systemcmd import cmd_sleep
        return cmd_sleep(args, tft)
    elif cmd == 'view':
        from commands.systemcmd import cmd_bmpview
        return cmd_bmpview(args, tft)
    elif cmd == 'wlan':
        from commands.systemcmd import cmd_wlan
        return cmd_wlan(args)
    elif cmd == 'brightness':
        return cmd_brightness(args)

    # essentialcmd
    elif cmd == 'games':
        from commands.essentialcmd import cmd_games
        return cmd_games(args)
    elif cmd == 'adventure':
        from commands.systemcmd import cmd_adventure
        return cmd_adventure(args)
    elif cmd == 'timer':
        from commands.essentialcmd import cmd_timer
        return cmd_timer(args, oled_ctrl)
    elif cmd == 'encrypt':
        from commands.essentialcmd import cmd_encrypt
        return cmd_encrypt(args)
    elif cmd == 'decrypt':
        from commands.essentialcmd import cmd_decrypt
        return cmd_decrypt(args)
    elif cmd == 'draw':
        from commands.essentialcmd import cmd_draw
        return cmd_draw(args, tft)
    elif cmd == 'flag':
        from commands.essentialcmd import cmd_flag
        return cmd_flag(args, tft)
    elif cmd == 'qr':
        from commands.essentialcmd import cmd_qr
        return cmd_qr(args, tft)
    elif cmd == 'stopwatch':
        from commands.essentialcmd import cmd_stopwatch
        return cmd_stopwatch(args, oled_ctrl)
    elif cmd == 'oled':
        return cmd_oled(args, oled_ctrl)

    # apicmd
    elif cmd == 'wiki':
        from commands.apicmd import cmd_detailwiki
        return cmd_detailwiki(args)
    elif cmd == 'timetable':
        from commands.apicmd import cmd_timetable
        return cmd_timetable(args)
    elif cmd == 'prayer':
        from commands.apicmd import cmd_prayer
        return cmd_prayer(args)
    elif cmd == 'chat':
        from commands.apicmd import cmd_chat
        return cmd_chat(args)
    elif cmd == 'translate':
        from commands.apicmd import cmd_translate
        return cmd_translate(args)
    elif cmd == 'define':
        from commands.apicmd import cmd_define
        return cmd_define(args)

    # utilcmd
    elif cmd == 'todo':
        from commands.utilcmd import cmd_todo
        return cmd_todo(args, tft)
    elif cmd == 'notes':
        from commands.utilcmd import cmd_notes
        return cmd_notes(args)
    elif cmd == 'convert':
        from commands.utilcmd import cmd_convert
        return cmd_convert(args)
    elif cmd == 'base':
        from commands.utilcmd import cmd_base
        return cmd_base(args)
    elif cmd == 'passwd':
        from commands.utilcmd import cmd_passwd
        return cmd_passwd(args)
    elif cmd == 'weather':
        from commands.utilcmd import cmd_weather
        return cmd_weather(args)
    elif cmd == 'freq':
        from commands.utilcmd import cmd_freq
        return cmd_freq(args)
    elif cmd == 'mem':
        from commands.utilcmd import cmd_mem
        return cmd_mem(args)
    elif cmd == 'uptime':
        from commands.utilcmd import cmd_uptime
        return cmd_uptime(args)
    elif cmd == 'ping':
        from commands.utilcmd import cmd_ping
        return cmd_ping(args)
    elif cmd == 'color':
        from commands.utilcmd import cmd_color
        return cmd_color(args)
    elif cmd == 'uuid':
        from commands.utilcmd import cmd_uuid
        return cmd_uuid(args)
    elif cmd == 'history':
        from commands.utilcmd import cmd_history
        return cmd_history(args)
    elif cmd == 'grep':
        from commands.utilcmd import cmd_grep
        return cmd_grep(args)
    elif cmd == 'head':
        from commands.utilcmd import cmd_head
        return cmd_head(args)
    elif cmd == 'tail':
        from commands.utilcmd import cmd_tail
        return cmd_tail(args)
    elif cmd == 'wc':
        from commands.utilcmd import cmd_wc
        return cmd_wc(args)
    elif cmd == 'diff':
        from commands.utilcmd import cmd_diff
        return cmd_diff(args)
    elif cmd == 'quote':
        from commands.utilcmd import cmd_quote
        return cmd_quote(args)
    elif cmd == 'joke':
        from commands.utilcmd import cmd_joke
        return cmd_joke(args)
    elif cmd == 'cowsay':
        from commands.utilcmd import cmd_cowsay
        return cmd_cowsay(args)
    elif cmd == 'df':
        from commands.utilcmd import cmd_df
        return cmd_df(args)
    elif cmd == 'find':
        from commands.utilcmd import cmd_find
        return cmd_find(args)
    elif cmd == 'fm':
        return cmd_fm(args)
    elif cmd == 'theme':
        return cmd_theme(args)
    elif cmd == 'ota':
        return cmd_ota(args)
    elif cmd == 'webrepl':
        return cmd_webrepl(args)
    elif cmd == 'dice':
        from commands.utilcmd import cmd_dice
        return cmd_dice(args)
    elif cmd == 'flip':
        from commands.utilcmd import cmd_flip
        return cmd_flip(args)
    elif cmd == 'news':
        from commands.apicmd import cmd_news
        return cmd_news(args)
    elif cmd == 'stock':
        from commands.apicmd import cmd_stock
        return cmd_stock(args)
    elif cmd == 'crypto':
        from commands.apicmd import cmd_crypto
        return cmd_crypto(args)
    elif cmd == 'timezone':
        from commands.apicmd import cmd_timezone
        return cmd_timezone(args)
    elif cmd == 'ipinfo':
        from commands.apicmd import cmd_ipinfo
        return cmd_ipinfo(args)
    elif cmd == 'exchange':
        from commands.apicmd import cmd_exchange
        return cmd_exchange(args)
    elif cmd == 'gh':
        from commands.apicmd import cmd_gh
        return cmd_gh(args)
    elif cmd == 'ghrepo':
        from commands.apicmd import cmd_ghrepo
        return cmd_ghrepo(args)
    elif cmd == 'holiday':
        from commands.apicmd import cmd_holiday
        return cmd_holiday(args)
    elif cmd == 'aqi':
        from commands.apicmd import cmd_aqi
        return cmd_aqi(args)
    elif cmd == 'bored':
        from commands.apicmd import cmd_bored
        return cmd_bored(args)
    elif cmd == 'physics':
        from commands.systemcmd import cmd_physics
        return cmd_physics(args, tft, oled_ctrl)
    elif cmd == 'electronics':
        from commands.systemcmd import cmd_electronics
        return cmd_electronics(args, tft, oled_ctrl)
    elif cmd == 'chem':
        from commands.systemcmd import cmd_chem
        return cmd_chem(args)
    elif cmd == 'piano':
        from commands.systemcmd import cmd_piano
        return cmd_piano(args)
    elif cmd == 'music':
        from commands.systemcmd import cmd_music
        return cmd_music(args)
    elif cmd == 'ghrepofs':
        from commands.apicmd import cmd_ghrepofs
        return cmd_ghrepofs(args)
    elif cmd == 'draw':
        from commands.utilcmd_new import cmd_draw
        return cmd_draw(args, tft)
    elif cmd == 'calendar':
        from commands.utilcmd_new import cmd_calendar
        return cmd_calendar(args, tft)
    elif cmd == 'alarm':
        from commands.utilcmd_new import cmd_alarm
        return cmd_alarm(args)
    elif cmd == 'notes':
        from commands.utilcmd_new import cmd_notes
        return cmd_notes(args, tft)
    elif cmd == 'remind' or cmd == 'reminders':
        from commands.utilcmd_new import cmd_reminders
        return cmd_reminders(args, tft)
    elif cmd == 'contacts':
        from commands.utilcmd_new import cmd_contacts
        return cmd_contacts(args, tft)
    elif cmd == 'hexdump' or cmd == 'hex':
        from commands.utilcmd_new import cmd_hexdump
        return cmd_hexdump(args)
    elif cmd == 'timer':
        from commands.utilcmd_new import cmd_timer
        return cmd_timer(args, tft)
    elif cmd == 'chemtable':
        from commands.systemcmd import cmd_chemtable
        return cmd_chemtable(args, tft)
    elif cmd == 'bio':
        from commands.systemcmd import cmd_bio
        return cmd_bio(args)
    elif cmd == 'code':
        from commands.systemcmd import cmd_code
        return cmd_code(args)
    elif cmd == 'chemtable':
        from commands.systemcmd import cmd_chemtable
        return cmd_chemtable(args, tft)
    elif cmd == 'ip':
        from commands.utilcmd import cmd_ip
        return cmd_ip(args)
    elif cmd == 'du':
        from commands.utilcmd import cmd_du
        return cmd_du(args)
    elif cmd == 'tree':
        from commands.utilcmd import cmd_tree
        return cmd_tree(args)
    elif cmd == 'du_top':
        from commands.utilcmd import cmd_du_top
        return cmd_du_top(args)
    elif cmd == 'conv':
        from commands.utilcmd import cmd_conv
        return cmd_conv(args)
    elif cmd == 'base64':
        from commands.utilcmd import cmd_base64
        return cmd_base64(args)
    elif cmd == 'ascii':
        from commands.utilcmd import cmd_ascii
        return cmd_ascii(args, tft)
    elif cmd == 'cp':
        from commands.utilcmd import cmd_cp
        return cmd_cp(args)
    elif cmd == 'mv':
        from commands.utilcmd import cmd_mv
        return cmd_mv(args)
    elif cmd == 'search':
        from commands.utilcmd import cmd_search
        return cmd_search(args)
    elif cmd == 'dns':
        from commands.utilcmd import cmd_dns
        return cmd_dns(args)
    elif cmd == 'curl':
        from commands.utilcmd import cmd_curl
        return cmd_curl(args)
    elif cmd == 'backup':
        from commands.utilcmd import cmd_backup
        return cmd_backup(args)
    elif cmd == 'restore':
        from commands.utilcmd import cmd_restore
        return cmd_restore(args)
    elif cmd == 'speedtest':
        from commands.utilcmd import cmd_speedtest
        return cmd_speedtest(args)
    elif cmd == 'startup':
        from commands.utilcmd import cmd_startup
        return cmd_startup(args)
    elif cmd == 'buzzer':
        return cmd_buzzer(args)
    elif cmd == 'forecast':
        from commands.apicmd import cmd_forecast
        return cmd_forecast(args)
    elif cmd == 'lyrics' or cmd == 'numfact':
        from commands.apicmd import cmd_lyrics
        return cmd_lyrics(args)
    elif cmd == 'catfact':
        from commands.apicmd import cmd_catfact
        return cmd_catfact(args)
    elif cmd == 'dogfact':
        from commands.apicmd import cmd_dogfact
        return cmd_dogfact(args)
    elif cmd == 'trivia':
        from commands.apicmd import cmd_trivia
        return cmd_trivia(args)
    elif cmd == 'dadjoke':
        from commands.apicmd import cmd_dadjoke
        return cmd_dadjoke(args)
    elif cmd == 'randomfact':
        from commands.apicmd import cmd_randomfact
        return cmd_randomfact(args)
    elif cmd == 'xkcd':
        from commands.apicmd import cmd_xkcd
        return cmd_xkcd(args)
    elif cmd == 'vocab':
        from commands.apicmd import cmd_vocab
        return cmd_vocab(args)
    elif cmd == 'chemical' or cmd == 'joke2':
        from commands.apicmd import cmd_chemical
        return cmd_chemical(args)
    elif cmd == 'geo':
        from commands.apicmd import cmd_geo
        return cmd_geo(args)
    elif cmd == 'npm':
        from commands.apicmd import cmd_npm
        return cmd_npm(args)
    elif cmd == 'pypi':
        from commands.apicmd import cmd_pypi
        return cmd_pypi(args)
    elif cmd == 'quote':
        from commands.apicmd import cmd_quote
        return cmd_quote(args)
    elif cmd == 'roast':
        from commands.apicmd import cmd_roast
        return cmd_roast(args)
    elif cmd == 'rss':
        from commands.apicmd import cmd_rss
        return cmd_rss(args, tft)
    elif cmd == 'chuck':
        from commands.apicmd import cmd_chuck
        return cmd_chuck(args)
    elif cmd == 'earthquake':
        from commands.apicmd import cmd_earthquake
        return cmd_earthquake(args)
    elif cmd == 'colorinfo':
        from commands.apicmd import cmd_colorinfo
        return cmd_colorinfo(args)
    elif cmd == 'nasa_apod':
        from commands.apicmd import cmd_nasa_apod
        return cmd_nasa_apod(args)
    elif cmd == 'sunset':
        from commands.apicmd import cmd_sunset
        return cmd_sunset(args)
    elif cmd == 'randomuser':
        from commands.apicmd import cmd_randomuser
        return cmd_randomuser(args)
    elif cmd == 'ipwhois':
        from commands.apicmd import cmd_ipwhois
        return cmd_ipwhois(args)
    elif cmd == 'upcheck':
        from commands.apicmd import cmd_uptime_api
        return cmd_uptime_api(args)
    elif cmd == 'json':
        from commands.apicmd import cmd_json
        return cmd_json(args)
    elif cmd == 'wolfram':
        from commands.apicmd import cmd_wolfram
        return cmd_wolfram(args)
    elif cmd == 'zen':
        from commands.apicmd import cmd_zen
        return cmd_zen(args)
    elif cmd == 'books':
        from commands.apicmd import cmd_books
        return cmd_books(args)
    elif cmd == 'movies':
        from commands.apicmd import cmd_movies
        return cmd_movies(args)
    elif cmd == 'whoami':
        from commands.apicmd import cmd_whoami
        return cmd_whoami(args)
    elif cmd == 'ytchl':
        from commands.apicmd import cmd_ytchl
        return cmd_ytchl(args)
    elif cmd == 'ytdt':
        from commands.apicmd import cmd_ytdt
        return cmd_ytdt(args)
    elif cmd == 'reddit':
        from commands.apicmd import cmd_reddit
        return cmd_reddit(args)
    elif cmd == 'ytsearch':
        from commands.apicmd import cmd_ytsearch
        return cmd_ytsearch(args)
    elif cmd == 'hn':
        from commands.apicmd import cmd_hn
        return cmd_hn(args)
    elif cmd == 'so':
        from commands.apicmd import cmd_so
        return cmd_so(args)
    elif cmd == 'devto':
        from commands.apicmd import cmd_devto
        return cmd_devto(args)
    elif cmd == 'ghtrending':
        from commands.apicmd import cmd_ghtrending
        return cmd_ghtrending(args)
    elif cmd == 'bsky':
        from commands.apicmd import cmd_bsky
        return cmd_bsky(args)
    elif cmd == 'gmail':
        from commands.apicmd import cmd_gmail
        return cmd_gmail(args)

    # New commands (session 5)
    elif cmd == 'pick':
        from commands.systemcmd import cmd_pick
        return cmd_pick(args)
    elif cmd == 'tip':
        from commands.systemcmd import cmd_tip
        return cmd_tip(args)
    elif cmd == 'morse':
        from commands.systemcmd import cmd_morse
        return cmd_morse(args)
    elif cmd == 'chess':
        from commands.systemcmd import cmd_chess
        return cmd_chess(args)
    elif cmd == 'mastermind':
        from commands.systemcmd import cmd_mastermind
        return cmd_mastermind(args)
    elif cmd == 'nim':
        from commands.systemcmd import cmd_nim
        return cmd_nim(args)
    elif cmd == 'blackjack':
        from commands.systemcmd import cmd_blackjack
        return cmd_blackjack(args)
    elif cmd == 'simon':
        from commands.systemcmd import cmd_simon
        return cmd_simon(args)
    elif cmd == '2048':
        from commands.systemcmd import cmd_2048
        return cmd_2048(args)
    elif cmd == 'snake':
        from commands.systemcmd import cmd_snake
        return cmd_snake(args)
    elif cmd == 'tetris':
        from commands.systemcmd import cmd_tetris
        return cmd_tetris(args)
    elif cmd == 'breakout':
        from commands.systemcmd import cmd_breakout
        return cmd_breakout(args)
    elif cmd == 'flappy':
        from commands.systemcmd import cmd_flappy
        return cmd_flappy(args)
    elif cmd == 'minesweeper':
        from commands.systemcmd import cmd_minesweeper
        return cmd_minesweeper(args)
    elif cmd == 'random':
        from commands.systemcmd import cmd_random
        return cmd_random(args)
    elif cmd == 'disk':
        from commands.systemcmd import cmd_disk
        return cmd_disk(args)
    elif cmd == 'netdev':
        from commands.systemcmd import cmd_netdev
        return cmd_netdev(args)
    elif cmd == 'countdown':
        from commands.systemcmd import cmd_countdown
        return cmd_countdown(args)
    elif cmd == 'charref':
        from commands.systemcmd import cmd_charref
        return cmd_charref(args)
    elif cmd == 'sysinfo':
        from commands.systemcmd import cmd_sysinfo
        return cmd_sysinfo(args)
    elif cmd == 'passcheck':
        from commands.systemcmd import cmd_passcheck
        return cmd_passcheck(args)
    elif cmd == 'freqcount':
        from commands.systemcmd import cmd_freqcount
        return cmd_freqcount(args)
    elif cmd == 'snippet':
        from commands.systemcmd import cmd_snippet
        return cmd_snippet(args)
    elif cmd == 'trolley':
        from commands.systemcmd import cmd_trolley
        return cmd_trolley(args)
    elif cmd == 'password':
        from commands.systemcmd import cmd_password
        return cmd_password(args)
    elif cmd == 'mystery':
        from commands.systemcmd import cmd_mystery
        return cmd_mystery(args)
    elif cmd == 'life':
        from commands.systemcmd import cmd_life
        return cmd_life(args)
    elif cmd == 'tron':
        from commands.systemcmd import cmd_tron
        return cmd_tron(args)
    elif cmd == 'maze3d':
        from commands.systemcmd import cmd_maze3d
        return cmd_maze3d(args)
    elif cmd == 'snake2':
        from commands.systemcmd import cmd_snake2
        return cmd_snake2(args)
    elif cmd == 'tetris2':
        from commands.systemcmd import cmd_tetris2
        return cmd_tetris2(args)
    elif cmd == 'breakout2':
        from commands.systemcmd import cmd_breakout2
        return cmd_breakout2(args)
    elif cmd == 'pong':
        from commands.systemcmd import cmd_pong
        return cmd_pong(args)
    elif cmd == 'pong2p':
        from commands.systemcmd import cmd_pong2p
        return cmd_pong2p(args)
    elif cmd == 'pong3d':
        from commands.systemcmd import cmd_pong3d
        return cmd_pong3d(args)
    elif cmd == 'simon2':
        from commands.systemcmd import cmd_simon2
        return cmd_simon2(args)
    elif cmd == 'cooking':
        from lib.cooking_engine import cooking_loop
        return ('game', cooking_loop)
    elif cmd == 'sandbox':
        from lib.sandbox_engine import sandbox_loop
        return ('game', sandbox_loop)
    elif cmd == 'infinitecraft':
        from lib.infinitecraft_engine import infinitecraft_loop
        return ('game', infinitecraft_loop)
    elif cmd == 'audio':
        from commands.systemcmd import cmd_audio
        return cmd_audio(args)
    elif cmd == 'tone':
        from commands.systemcmd import cmd_tone
        return cmd_tone(args)

    else:
        return ('print', f"Unknown command: '{cmd}'.\n  Type 'help' for commands.")





def cmd_oled(args, oled_ctrl=None):
    if not oled_ctrl:
        return ('print', 'oled: display not available')
    parts = args.strip().split(None, 1) if args.strip() else []
    if not parts:
        return ('print_lines', [
            'oled: usage: oled [mode] or oled [page]',
            '',
            '  oled 1  - Info/Display modes',
            '  oled 2  - Animations',
            '  oled 3  - More animations',
        ])

    page = parts[0].lower()
    valid = ('status', 'ram', 'flash', 'info', 'text', 'dvd', 'wave', 'clock',
             'matrix', 'fire', 'starfield', 'bounce', 'plasma', 'rain',
             'fireworks', 'dna', 'equalizer', 'pong', 'lava', 'sparkle',
             'pulse', 'cube', 'textscroll', 'minisnake', 'heart', 'invader',
             'spiral', 'boot', 'glitch', 'disco', 'binary', 'eye', 'checker',
             'lightning', 'helplogo', 'skull', 'cat', 'dance', 'doom', 'potato',
             'chicken', 'esp32', 'pacman', 'tunnel', 'typewriter',
             'radar', 'tetrisfall', 'firefly', 'spectrum', 'osnake', 'stopwatch', 'random',
             'wlan', 'auto', 'notify', 'game_hud', 'engine_status')

    if page in ('1', '2', '3', '4'):
        pages = {
            '1': [
                '=== OLED 1/4 ===',
                '',
                '-- Info --',
                '  oled status    RAM bar + name',
                '  oled ram       Detailed RAM',
                '  oled flash     Flash storage',
                '  oled info      System info',
                '  oled text [s]  Display text',
                '',
                '-- Classic --',
                '  oled dvd       DVD logo bounce',
                '  oled wave      Sine wave',
                '  oled clock     Digital clock',
                '  oled bounce    Bouncing ball',
                '  oled rain      Rain drops',
                '  oled fireworks Particle explosions',
                '  oled starfield Moving stars',
                '  oled plasma    Plasma effect',
            ],
            '2': [
                '=== OLED 2/4 ===',
                '',
                '  oled matrix    Matrix rain',
                '  oled fire      Fire effect',
                '  oled dna       DNA helix',
                '  oled equalizer Audio bars',
                '  oled pong      Mini pong',
                '  oled lava      Lava lamp',
                '  oled sparkle   Twinkling stars',
                '  oled pulse     Expanding rings',
                '  oled cube      Rotating 3D cube',
                '  oled textscroll Star Wars crawl',
                '  oled minisnake Playable snake',
                '  oled heart     Beating heart',
                '  oled invader   Space invader',
                '  oled spiral    Rotating spiral',
                '  oled boot      Fake boot sequence',
            ],
            '3': [
                '=== OLED 3/4 ===',
                '',
                '  oled glitch    Glitch effect',
                '  oled disco     Disco mode',
                '  oled binary    Binary rain',
                '  oled eye       Watching eye',
                '  oled checker   Checkerboard',
                '  oled lightning Lightning bolts',
                '  oled helplogo  Bouncing HELP',
                '  oled skull     ASCII skull',
                '  oled cat       ASCII cat',
                '  oled dance     Dancing stick figure',
                '  oled doom      DOOM zoom',
                '  oled potato    potato.',
                '  oled stopwatch Count-up timer',
                '  oled random    Random (no repeats)',
            ],
            '4': [
                '=== OLED 4/4 - EVEN MORE ===',
                '',
                '  oled chicken    Walking chicken',
                '  oled esp32      Spinning ESP32',
                '  oled pacman     Pac-Man eating dots',
                '  oled tunnel     Shrinking tunnel',
                '  oled typewriter Typewriter text',
            '  oled radar      Sweeping radar',
            '  oled tetrisfall Falling tetris blocks',
            '  oled firefly    Blinking fireflies',
            '  oled spectrum   Fake spectrum analyzer',
            '  oled osnake     Snake with score (auto)',
            ],
        }
        return ('print_lines', pages[page])

    if page not in valid:
        return ('print', f'oled: unknown mode "{page}".\n  Use "oled 1" for help.')

    if page == 'text':
        text = parts[1] if len(parts) > 1 else ''
        oled_ctrl.set_mode('text', text=text)
    elif page in ('status', 'ram', 'flash', 'info'):
        oled_ctrl.set_mode('status', page=page)
    elif page == 'notify':
        text = parts[1] if len(parts) > 1 else 'Hello!'
        oled_ctrl.notify(text)
    else:
        oled_ctrl.set_mode(page)
    return ('print', f'oled: {page}')


def cmd_help_screen(args=''):
    page = args.strip().lower()

    # ── Calculator topic help (unchanged) ──
    if page == 'calc' or page == 'math':
        from lib.calc_help import HELP_TOPICS, HELP_TOPIC_LIST
        lines = ['=== CALCULATOR HELP ===', '', 'Usage: help math <topic>', '']
        lines.append('-- Topics --')
        for t in HELP_TOPIC_LIST:
            lines.append(f'  help math {t}')
        lines.append('')
        lines.append('Example: help math fractions')
        return ('print_lines', lines)

    if page.startswith('math '):
        topic = page.split(' ', 1)[1].strip()
        from lib.calc_help import HELP_TOPICS
        if topic in HELP_TOPICS:
            return ('print_lines', HELP_TOPICS[topic])
        from lib.calc_help import HELP_TOPIC_LIST
        lines = [f'Unknown topic: "{topic}"', '', 'Available topics:']
        for t in HELP_TOPIC_LIST:
            lines.append(f'  help calc {t}')
        return ('print_lines', lines)

    # ── System ──
    if page == 'system' or page == 'system 1':
        return ('print_lines', [
            '=== SYSTEM (1/2) ===',
            '',
            '  clock          Current time',
            '  info           System information',
            '  calc [expr]    Calculator',
            '  uname          System name',
            '  pwd            Working directory',
            '  clear          Clear screen',
            '  echo [text]    Print text',
            '  sleep          Sleep mode',
        ])

    if page == 'system 2':
        return ('print_lines', [
            '=== SYSTEM (2/2) ===',
            '',
            '  brightness [n] Set backlight',
            '  theme          Cycle themes',
            '  ip             Show local IP',
            '  startup [cmd]  Manage boot cmds',
            '  chemtable      Periodic table',
            '  about          About Espelt',
            '  mem            Memory info',
            '  uptime         System uptime',
        ])

    # ── Files ──
    if page == 'files' or page == 'files 1':
        return ('print_lines', [
            '=== FILES (1/2) ===',
            '',
            '  ls [dir]       List files',
            '  cat [file]     View file',
            '  cd [dir]       Change directory',
            '  touch [file]   Create file',
            '  mkdir [dir]    Make directory',
            '  rm [file]      Remove file',
            '  cp [src] [dst] Copy file',
            '  mv [src] [dst] Move file',
        ])

    if page == 'files 2':
        return ('print_lines', [
            '=== FILES (2/2) ===',
            '',
            '  nano [file]    Text editor',
            '  fm [dir]       File manager',
            '  run [file.py]  Run script',
            '  grep [pat] [f] Search file',
            '  find [name]    Find files',
            '  head [f] [n]   First N lines',
            '  tail [f] [n]   Last N lines',
            '  wc [f]         Word count',
        ])

    # ── Network ──
    if page == 'net' or page == 'net 1':
        return ('print_lines', [
            '=== NETWORK (1/6) ===',
            '',
            '  wlan [ss] [pw] WiFi connect',
            '  wiki [query]   Wikipedia',
            '  define [word]  Dictionary + synonyms',
            '  weather [city] Current + 3-day',
            '  forecast [city] 5-day detailed',
            '  news           Headlines',
            '  translate [f] [t] [txt] Translate',
            '  prayer [city]  Prayer times',
        ])

    if page == 'net 2':
        return ('print_lines', [
            '=== NETWORK (2/6) ===',
            '',
            '  ping [host]    Ping host',
            '  dns [host]     DNS lookup',
            '  curl [host]    HTTP GET',
            '  speedtest      Speed test',
            '  ipinfo         Public IP',
            '  webrepl        Web REPL info',
            '  ota            OTA server',
            '  ychl [ch]      YouTube channel',
        ])

    if page == 'net 3':
        return ('print_lines', [
            '=== NETWORK (3/6) ===',
            '',
            '  stock [sym]    Stock price',
            '  crypto [sym]   Crypto price',
            '  exchange [a] [f] [t] Currency',
            '  gh [user]      GitHub profile',
            '  ghrepo [user]  GitHub repos',
            '  holiday [cc]   Next holiday',
            '  forecast [city] 3-day forecast',
            '  numfact [num]  Number fact',
        ])

    if page == 'net 4':
        return ('print_lines', [
            '=== NETWORK (4/6) ===',
            '',
            '  rss [feed]     RSS feed reader',
            '  catfact        Cat fact',
            '  dogfact        Dog fact',
            '  trivia         Random trivia',
            '  randomfact     Random fact',
            '  xkcd           Latest XKCD comic',
            '  vocab          Word of the day',
            '  joke2          Random joke',
        ])

    if page == 'net 5':
        return ('print_lines', [
            '=== NETWORK (5/6) ===',
            '',
            '  geo            Your location',
            '  npm [pkg]      NPM package info',
            '  pypi [pkg]     PyPI package info',
            '  quote          Random quote',
            '  roast          Get roasted',
            '  chuck          Chuck Norris jokes',
            '  earthquake     Recent earthquakes',
            '  nasa_apod      NASA Picture of Day',
        ])

    if page == 'net 6':
        return ('print_lines', [
            '=== NETWORK (6/6) - MEDIA ===',
            '',
            '  reddit [sub]   Reddit subreddit',
            '  ytsearch [q]   YouTube search',
            '  ytchl [ch]     YouTube channel info',
            '  hn             Hacker News top stories',
            '  so [query]     Stack Overflow search',
            '  devto          Dev.to top posts',
            '  ghtrending     GitHub trending repos',
            '  bsky           Bluesky social (login first)',
            '  ytdt [name]    YouTube channel stats',
            '  gmail          Read/send emails',
        ])

    # ── Entertainment ──
    if page == 'entertainment' or page == 'fun':
        return ('print_lines', [
            '=== ENTERTAINMENT ===',
            '',
            '  adventure      Text adventure RPG',
            '  games          50 games',
            '  oled           55+ animations',
            '  piano          Interactive piano',
            '  music          Song player',
            '  cowsay [text]  Cow says text',
            '  dice [NdN]     Roll dice',
            '  flip           Flip coin',
        ])

    # ── Games pages ──
    if page == 'games' or page == 'games 1':
        return ('print_lines', [
            '=== GAMES (1/6) ===',
            '',
            '  snake          Classic snake',
            '  2048           Slide puzzle',
            '  tetris         Block stacker',
            '  flappy         Bird flyer',
            '  breakout       Brick breaker',
            '  pong           AI vs AI',
            '  minesweeper    Mine finder',
            '  hangman        Word guess',
        ])

    if page == 'games 2':
        return ('print_lines', [
            '=== GAMES (2/6) ===',
            '',
            '  rps            Rock Paper Scissors',
            '  tictactoe      Tic Tac Toe',
            '  guess          Number guess',
            '  memory         Simon memory',
            '  wordle         Wordle clone',
            '  asteroids      Space shooter',
            '  maze           Maze generator',
            '  connect4       Connect Four',
        ])

    if page == 'games 3':
        return ('print_lines', [
            '=== GAMES (3/6) ===',
            '',
            '  battleship     Battleship',
            '  trivia         Trivia quiz',
            '  typing         Typing speed',
            '  mathquiz       Math quiz',
            '  sudoku         4x4 Sudoku',
            '  lightsout      Lights Out',
            '  platformer     Side-scroller',
            '  simon2         Simon combos',
        ])

    if page == 'games 4':
        return ('print_lines', [
            '=== GAMES (4/6) ===',
            '',
            '  racing         Top-down racing',
            '  invaders       Space Invaders',
            '  checkers       Checkers (2P)',
            '  whack          Whack-a-mole',
            '  archery        Target shooting',
            '  othello        Othello (vs CPU)',
            '  pong2p         Pong 2P (PVP)',
            '  tank           Tank Battle',
        ])

    if page == 'games 5':
        return ('print_lines', [
            '=== GAMES (5/6) ===',
            '',
            '  hanoi          Tower of Hanoi',
            '  bomber         Bomber',
            '  fighter        Fighter (CPU)',
            '  dodge          Dodge (CPU)',
            '  tag            Tag (CPU)',
            '  chess          Chess vs CPU',
            '  mastermind     Code-breaking',
        ])

    if page == 'games 6':
        return ('print_lines', [
            '=== GAMES (6/6) ===',
            '',
            '  snake2         Snake w/ obstacles',
            '  tetris2        Tetris w/ hard drop',
            '  breakout2      Breakout multi-ball',
            '  pong3d         3D pong',
            '  maze3d         3D maze',
            '  tron           Light cycles',
            '  life           Game of Life',
            '  cooking        Recipe timing',
            '  sandbox        Pixel art + physics',
            '  infinitecraft  Element combining',
            '  games          Full list',
        ])

    # ── OLED pages ──
    if page == 'oled' or page == 'oled 1':
        return ('print_lines', [
            '=== OLED (1/8) ===',
            '',
            '  oled auto      Auto mode',
            '  oled wlan      WiFi status',
            '  oled status    System status',
            '  oled clock     Digital clock',
            '  oled notify [t] Popup alert',
            '  oled game_hud  Game stats',
            '  oled off       Turn off',
            '  oled on        Turn on',
        ])

    if page == 'oled 2':
        return ('print_lines', [
            '=== OLED (2/8) ===',
            '',
            '  oled dvd       DVD logo bounce',
            '  oled wave      Sine wave',
            '  oled bounce    Bouncing ball',
            '  oled rain      Rain drops',
            '  oled fireworks Particles',
            '  oled starfield Moving stars',
            '  oled plasma    Plasma effect',
            '  oled matrix    Matrix rain',
        ])

    if page == 'oled 3':
        return ('print_lines', [
            '=== OLED (3/8) ===',
            '',
            '  oled fire      Fire effect',
            '  oled dna       DNA helix',
            '  oled equalizer Audio bars',
            '  oled pong      Mini pong',
            '  oled lava      Lava lamp',
            '  oled sparkle   Twinkling stars',
            '  oled pulse     Expanding rings',
            '  oled cube      Rotating 3D cube',
        ])

    if page == 'oled 4':
        return ('print_lines', [
            '=== OLED (4/8) ===',
            '',
            '  oled textscroll Star Wars crawl',
            '  oled minisnake Playable snake',
            '  oled heart     Beating heart',
            '  oled invader   Space invader',
            '  oled spiral    Rotating spiral',
            '  oled boot      Fake boot',
            '  oled glitch    Glitch effect',
            '  oled disco     Disco mode',
        ])

    if page == 'oled 5':
        return ('print_lines', [
            '=== OLED (5/8) ===',
            '',
            '  oled binary    Binary rain',
            '  oled eye       Watching eye',
            '  oled checker   Checkerboard',
            '  oled lightning Lightning bolts',
            '  oled helplogo  Bouncing HELP',
            '  oled skull     ASCII skull',
            '  oled cat       ASCII cat',
            '  oled dance     Dancing figure',
        ])

    if page == 'oled 6':
        return ('print_lines', [
            '=== OLED (6/8) ===',
            '',
            '  oled doom      DOOM zoom',
            '  oled potato    Potato',
            '  oled chicken   Walking chicken',
            '  oled esp32     Spinning ESP32',
            '  oled pacman    Pac-Man',
            '  oled tunnel    Shrinking tunnel',
            '  oled radar     Sweeping radar',
            '  oled tetrisfall Falling blocks',
        ])

    if page == 'oled 7':
        return ('print_lines', [
            '=== OLED (7/8) ===',
            '',
            '  oled firefly   Blinking fireflies',
            '  oled spectrum  Fake analyzer',
            '  oled osnake    Auto snake',
            '  oled random    Random (no repeats)',
            '  oled stopwatch Count-up timer',
            '  oled timer     MM:SS countdown',
            '  oled text [s]  Custom text',
            '  oled flash     Flash storage',
        ])

    if page == 'oled 8':
        return ('print_lines', [
            '=== OLED (8/8) ===',
            '',
            '  oled ram       Detailed RAM',
            '  oled info      System info',
            '  oled typewriter Typewriter text',
            '  oled timer_debug Countdown+debug',
            '  oled 1-4       Help pages',
        ])

    # ── Productivity ──
    if page == 'prod' or page == 'prod 1':
        return ('print_lines', [
            '=== PRODUCTIVITY (1/2) ===',
            '',
            '  todo           Interactive todo',
            '  todo add [t]   Add task',
            '  todo list      List tasks',
            '  todo done [n]  Toggle done',
            '  todo rm [n]    Remove task',
            '  todo clear     Clear done',
            '  notes new [n]  Create note',
            '  notes list     List notes',
        ])

    if page == 'prod 2':
        return ('print_lines', [
            '=== PRODUCTIVITY (2/2) ===',
            '',
            '  notes read [n] Read note',
            '  notes rm [n]   Delete note',
            '  history        Command history',
            '  contacts       Contact list',
            '  remind [t]     Reminder',
            '  calendar       Calendar view',
        ])

    # ── Converters ──
    if page == 'converters' or page == 'convert':
        return ('print_lines', [
            '=== CONVERTERS ===',
            '',
            '  convert [v] [f] [t] Unit convert',
            '  base [num]     Base convert',
            '  color [hex]    Color convert',
            '  passwd [len]   Password gen',
            '  uuid           UUID generator',
            '  base64 enc/dec Base64',
            '  encrypt [m] [t] Encrypt text',
            '  decrypt [m] [t] Decrypt text',
        ])

    # ── Utilities ──
    if page == 'util' or page == 'util 1':
        return ('print_lines', [
            '=== UTILITIES (1/2) ===',
            '',
            '  ascii [text]   ASCII art on TFT',
            '  hexdump [file] Hex dump file',
            '  leap [year]    Leap year check',
            '  age [y] [m] [d] Age calculator',
            '  pct [val] [tot] Percentage calc',
            '  rev [text]     Reverse text',
            '  chars [n]      ASCII chart from n',
            '  hash [text]    Hash text (djb2)',
        ])

    if page == 'util 2':
        return ('print_lines', [
            '=== UTILITIES (2/2) ===',
            '',
            '  stamp          Timestamps',
            '  temp [c]       Temperature convert',
            '  morse enc/dec  Morse code',
            '  flag [country] Draw flag',
            '  qr [text]      QR code on TFT',
        ])

    if page == 'flag' or page == 'flags':
        return ('print_lines', [
            '=== FLAGS (1/2) ===',
            '',
            '  flag germany   Draw Germany',
            '  flag france    Draw France',
            '  flag italy     Draw Italy',
            '  flag spain     Draw Spain',
            '  flag uk        Draw UK',
            '  flag sweden    Draw Sweden',
            '  flag norway    Draw Norway',
            '  flag russia    Draw Russia',
        ])

    if page == 'flag 2':
        return ('print_lines', [
            '=== FLAGS (2/2) ===',
            '',
            '  flag greece    Draw Greece',
            '  flag turkey    Draw Turkey',
            '  flag portugal  Draw Portugal',
            '  flag switzerland Draw CH',
            '  flag austria   Draw Austria',
            '  flag poland    Draw Poland',
            '  flag ireland   Draw Ireland',
            '  flag denmark   Draw Denmark',
        ])

    # ── Shortcuts index ──
    # ── Help search ──
    if page.startswith('search '):
        import _thread
        keyword = page.split(' ', 1)[1].strip().lower()
        if not keyword:
            return ('print', 'help search: usage: help search <keyword>')
        # Search all help text
        results = []
        # Search through known commands
        all_cmds = list(COMMANDS)
        matches = [c for c in all_cmds if keyword in c.lower()]
        if not matches:
            return ('print', f'  No matches for "{keyword}"')
        lines = [f'=== Search: {keyword} ===']
        for m in matches[:8]:
            lines.append(f'  {m}')
        return ('print_lines', lines)

    # ── Help recent ──
    if page == 'recent':
        try:
            with open('/sd/recent_commands.txt', 'r') as f:
                recents = [l.strip() for l in f.readlines() if l.strip()][-8:]
            if not recents:
                return ('print', '  No recent commands yet')
            lines = ['=== Recent Commands ===']
            for r in recents:
                lines.append(f'  {r}')
            return ('print_lines', lines)
        except:
            return ('print', '  No recent commands yet')

    # ── Help favorites ──
    if page == 'favorites' or page == 'fav':
        try:
            with open('/sd/favorites.txt', 'r') as f:
                favs = [l.strip() for l in f.readlines() if l.strip()]
            if not favs:
                return ('print_lines', [
                    '=== Favorites ===',
                    '  No favorites yet',
                    '',
                    '  Add with: help fav add <cmd>',
                ])
            lines = ['=== Favorites ===']
            for f in favs[:8]:
                lines.append(f'  {f}')
            return ('print_lines', lines)
        except:
            return ('print_lines', [
                '=== Favorites ===',
                '  No favorites yet',
                '',
                '  Add with: help fav add <cmd>',
            ])

    if page == 'shortcuts' or page == 'keys':
        return ('print_lines', [
            '=== SHORTCUTS ===',
            '',
            '  help ctrl      CTRL shortcuts',
            '  help nav       Navigation keys',
            '  help nano      Nano editor keys',
            '  help fm        File manager keys',
            '  help todo      Todo keys',
            '  help calc keys Calculator keys',
        ])

    # ── CTRL shortcuts ──
    if page == 'ctrl' or page == 'ctrl 1':
        return ('print_lines', [
            '=== CTRL SHORTCUTS ===',
            '',
            '  Ctrl+C         Cancel',
            '  Ctrl+L         Clear screen',
            '  Ctrl+U         Clear input',
            '  Ctrl+A         Clear input',
            '  Ctrl+3         Stealth mode',
            '  Ctrl+B         Toggle backlight',
            '  Ctrl+T         Cycle theme',
            '  Ctrl+O         Toggle OLED',
        ])

    # ── Navigation ──
    if page == 'nav' or page == 'navigation':
        return ('print_lines', [
            '=== NAVIGATION ===',
            '',
            '  Up/PgUp        Previous cmd',
            '  Down/PgDn      Next cmd',
            '  Tab            Auto-complete',
        ])

    # ── Nano keys ──
    if page == 'nano' or page == 'nano keys':
        return ('print_lines', [
            '=== NANO KEYS (1/2) ===',
            '',
            '  Ctrl+E         Cursor up',
            '  Ctrl+D         Cursor down',
            '  Ctrl+S         Cursor left',
            '  Ctrl+F         Cursor right',
            '  Ctrl+A         Line start',
            '  Ctrl+W         Line end',
            '  Ctrl+G         First line',
            '  Ctrl+L         Last line',
        ])

    if page == 'nano 2' or page == 'nano keys 2':
        return ('print_lines', [
            '=== NANO KEYS (2/2) ===',
            '',
            '  Ctrl+K         Delete line',
            '  Ctrl+U         Delete char',
            '  Ctrl+O         Save file',
            '  Ctrl+X         Find text',
            '  Ctrl+R         Find replace',
            '  Tab            Insert spaces',
            '  Esc            Save & exit',
        ])

    # ── File manager keys ──
    if page == 'fm' or page == 'fm keys':
        return ('print_lines', [
            '=== FILE MANAGER KEYS ===',
            '',
            '  E              Move up',
            '  D              Move down',
            '  Enter          Open',
            '  Esc            Exit',
        ])

    # ── Todo keys ──
    if page == 'todo' or page == 'todo keys':
        return ('print_lines', [
            '=== TODO KEYS ===',
            '',
            '  A              Add task',
            '  Space/Enter    Toggle done',
            '  D              Delete task',
            '  C              Clear done',
            '  Up/Down        Navigate',
            '  Esc            Save & exit',
        ])

    # ── Calc keys ──
    if page == 'calc keys' or page == 'calc keys 1':
        return ('print_lines', [
            '=== CALC KEYS ===',
            '',
            '  Ctrl+F         Fraction',
            '  Ctrl+E         Power',
            '  Ctrl+B         Square root',
            '  Ctrl+^         Integral',
            '  Ctrl+S         Summation',
            '  Ctrl+D         Derivative',
            '  Ctrl+L         Limit',
            '  Ctrl+R         Subscript',
        ])

    # ── Engines index ──
    if page == 'engines':
        return ('print_lines', [
            '=== ENGINES ===',
            '',
            '  help engines chem     Chemistry',
            '  help engines bio      Biology',
            '  help engines code     Coding',
            '  help engines elec     Electronics',
            '  help engines calc     Calculator',
            '  help engines physics  Physics',
            '  help engines music    Music player',
            '  help engines piano    Piano',
            '  help engines audio    Audio/Speaker',
        ])

    # ── Audio ──
    if page == 'engines audio' or page == 'audio':
        return ('print_lines', [
            '=== AUDIO (MAX98357A) ===',
            '',
            '  audio vol [n]     Volume 0-100',
            '  audio tone [f] [d] Play tone (Hz, ms)',
            '  audio play [f]    Play WAV from SD',
            '  audio stop        Stop playback',
            '  audio status      Codec status',
            '  tone [freq] [ms]  Quick tone',
        ])

    # ── Physics ──
    if page == 'engines physics' or page == 'physics':
        return ('print_lines', [
            '=== PHYSICS ===',
            '',
            '  physics          Interactive TFT mode',
            '',
            '-- Categories --',
            '  Mechanics        Forces, motion, energy',
            '  Waves            Sound, light, optics',
            '  Electricity      Circuits, capacitance',
            '  Thermal          Heat, temperature',
            '  Fluids           Pressure, buoyancy',
            '  Nuclear          Decay, half-life',
            '  Relativity       Time dilation, E=mc2',
            '  Modern           Photoelectric, de Broglie',
        ])

    # ── Music ──
    if page == 'engines music' or page == 'music':
        return ('print_lines', [
            '=== MUSIC PLAYER ===',
            '',
            '  music            Song browser',
            '  music [song]     Play directly',
            '',
            '-- Songs --',
            '  Twinkle          Twinkle Twinkle',
            '  Ode to Joy       Beethoven',
            '  Happy Birthday   Happy Birthday',
            '  Jingle Bells     Jingle Bells',
        ])

    # ── Piano ──
    if page == 'engines piano' or page == 'piano':
        return ('print_lines', [
            '=== PIANO ===',
            '',
            '  piano            Interactive piano',
            '',
            '-- Controls --',
            '  z-x-c-v-b-n-m    Lower octave',
            '  q-w-e-r-t-y-u    Upper octave',
            '  Up/Down          Octave +/-',
            '  Left/Right       Volume +/-',
            '  Space            Record/play',
        ])

    # ── Calculator ──
    if page == 'engines calc' or page == 'calc' or page == 'math':
        from lib.calc_help import HELP_TOPICS, HELP_TOPIC_LIST
        lines = ['=== CALCULATOR ===', '', 'Usage: help engines calc <topic>', '']
        lines.append('-- Topics --')
        for t in HELP_TOPIC_LIST:
            lines.append(f'  help engines calc {t}')
        lines.append('')
        lines.append('Example: help engines calc fractions')
        return ('print_lines', lines)

    if page.startswith('engines calc '):
        topic = page.split(' ', 2)[2].strip()
        from lib.calc_help import HELP_TOPICS
        if topic in HELP_TOPICS:
            return ('print_lines', HELP_TOPICS[topic])
        from lib.calc_help import HELP_TOPIC_LIST
        lines = [f'Unknown topic: "{topic}"', '', 'Available topics:']
        for t in HELP_TOPIC_LIST:
            lines.append(f'  help engines calc {t}')
        return ('print_lines', lines)

    # ── Chemistry ──
    if page == 'engines chem' or page == 'chem' or page == 'chemistry':
        return ('print_lines', [
            '=== CHEMISTRY (1/2) ===',
            '',
            '  chem info [el]      Element info',
            '  chem mass [form]    Molar mass',
            '  chem parse [form]   Parse formula',
            '  chem ph [h+]        pH calculator',
            '  chem gas ...        Gas law PV=nRT',
            '  chem molarity ...   Solution molarity',
            '  chem dilute ...     C1V1=C2V2',
            '  chem moles [m] [f]  Mass to moles',
        ])

    if page == 'chem 2' or page == 'chemistry 2':
        return ('print_lines', [
            '=== CHEMISTRY (2/2) ===',
            '',
            '  chem grams [n] [f]  Moles to grams',
            '  chem percent [f]    % composition',
            '  chem config [el]    Electron config',
            '  chem balance [eq]   Balance equation',
            '  chem thermo [rxn]   Thermochemistry',
            '  chem organic [comp] Organic chemistry',
            '  chem trend [el]     Periodic trends',
            '  chemtable           Periodic table TFT',
        ])

    # ── Biology ──
    if page == 'engines bio' or page == 'bio' or page == 'biology':
        return ('print_lines', [
            '=== BIOLOGY (1/2) ===',
            '',
            '  bio dna [seq]       DNA complement',
            '  bio rna [seq]       DNA to mRNA',
            '  bio translate [s]   mRNA to amino acids',
            '  bio protein [seq]   Full DNA pipeline',
            '  bio amino [name]    Amino acid info',
            '  bio polar           By polarity',
            '  bio organelle [n]   Cell organelle info',
            '  bio cells           Cell comparison',
        ])

    if page == 'bio 2' or page == 'biology 2':
        return ('print_lines', [
            '=== BIOLOGY (2/2) ===',
            '',
            '  bio punnett [p] [p] Punnett square',
            '  bio punnett2 [...]  2-trait Punnett',
            '  bio hwe [p]         Hardy-Weinberg',
            '  bio biome [name]    Biome info',
            '  bio trophic         Trophic levels',
            '  bio taxonomy [n]    Classification',
            '  bio codon [AUG]     Codon lookup',
            '  bio system [name]   Body system info',
        ])

    # ── Coding ──
    if page == 'engines code' or page == 'code' or page == 'coding':
        return ('print_lines', [
            '=== CODING (1/2) ===',
            '',
            '  code base [n] [f] [t] Base convert',
            '  code ascii [char]   ASCII lookup',
            '  code ascii table    ASCII table',
            '  code rot13 [text]   ROT13 cipher',
            '  code caesar [n] [t] Caesar cipher',
            '  code morse enc/dec  Morse code',
            '  code b64 enc/dec    Base64',
            '  code ds [name]      Data structures',
        ])

    if page == 'code 2' or page == 'coding 2':
        return ('print_lines', [
            '=== CODING (2/2) ===',
            '',
            '  code algo [name]    Algorithms',
            '  code regex          Regex patterns',
            '  code regex meta     Regex metachars',
            '  code python         Python cheatsheet',
            '  code mp             MicroPython imports',
            '  code syntax         Syntax reference',
            '  code examples       Code examples',
        ])

    # ── Electronics ──
    if page == 'engines elec' or page == 'elec' or page == 'electronics':
        return ('print_lines', [
            '=== ELECTRONICS ===',
            '',
            '  electronics        Interactive TFT mode',
            '',
            '-- Quick access --',
            '  electronics (no args) for interactive',
        ])

    # ── Favorites add/rm ──
    if page.startswith('fav add ') or page.startswith('favorites add '):
        cmd = page.split(' ', 2)[2].strip()
        try:
            with open('/sd/favorites.txt', 'r') as f:
                favs = [l.strip() for l in f.readlines() if l.strip()]
        except:
            favs = []
        if cmd not in favs:
            favs.append(cmd)
            try:
                with open('/sd/favorites.txt', 'w') as f:
                    for fv in favs:
                        f.write(fv + '\n')
                return ('print', f'  Added "{cmd}" to favorites')
            except:
                return ('print', '  favorites: write failed')
        return ('print', f'  "{cmd}" already in favorites')

    if page.startswith('fav rm ') or page.startswith('favorites rm '):
        cmd = page.split(' ', 2)[2].strip()
        try:
            with open('/sd/favorites.txt', 'r') as f:
                favs = [l.strip() for l in f.readlines() if l.strip()]
            if cmd in favs:
                favs.remove(cmd)
                with open('/sd/favorites.txt', 'w') as f:
                    for fv in favs:
                        f.write(fv + '\n')
                return ('print', f'  Removed "{cmd}" from favorites')
            return ('print', f'  "{cmd}" not in favorites')
        except:
            return ('print', '  favorites: not found')

    # ── Default: category index ──
    return ('print_lines', [
        '=== HELP ===',
        '',
        '  help system    System commands',
        '  help files     File operations',
        '  help net       Network & API',
        '  help games     50 games',
        '  help oled      OLED display',
        '  help prod      Productivity',
        '  help util      Utilities',
        '  help engines   All engines',
        '  help shortcuts Keyboard shortcuts',
    ])


def cmd_ls(args):
    path = args.strip() if args.strip() else '.'
    try:
        entries = os.listdir(path)
    except:
        return ('print', f'ls: {path}: not found')
    lines = []
    for e in sorted(entries):
        try:
            full = path.rstrip('/') + '/' + e
            os.stat(full)
            lines.append(f'  {e}/')
        except:
            lines.append(f'  {e}')
    if not lines:
        lines.append('  (empty)')
    return ('print_lines', lines)


def cmd_alias(args):
    parts = args.strip().split('=', 1) if args.strip() else []
    if not parts or len(parts) < 2:
        if not _aliases:
            return ('print', '  No aliases defined')
        lines = ['=== Aliases ===']
        for k, v in sorted(_aliases.items()):
            lines.append(f'  {k} = {v}')
        return ('print_lines', lines)
    _aliases[parts[0].strip()] = parts[1].strip()
    return ('print', f'  alias: {parts[0].strip()} = {parts[1].strip()}')


def cmd_ota(args):
    from lib.ota_server import start_ota_server
    import _thread

    ok, msg = True, ''
    try:
        from lib.ota_server import _check_network
        if not _check_network():
            return ('print_lines', [
                'ota: not on trusted network',
                '  Connect to device WiFi or magic WiFi first',
            ])
    except:
        return ('print', 'ota: network check failed')

    def _run():
        try:
            from lib.ota_server import start_ota_server
            start_ota_server(port=80)
        except Exception as e:
            print(f'ota: server error: {e}')

    _thread.start_new_thread(_run, ())
    return ('print_lines', [
        'ota: server started on port 80',
        '  Open browser to upload .py files',
        '  Server runs until reboot or power off',
    ])


def cmd_webrepl(args):
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            return ('print', 'webrepl: connect to WiFi first (wlan)')
        ip = wlan.ifconfig()[0]
    except:
        return ('print', 'webrepl: network error')

    return ('print_lines', [
        '=== Web REPL ===',
        '',
        '  Open in browser:',
        f'  ws://{ip}:8266',
        '',
        '  Password: espelt2024',
        '',
        '  Features:',
        '  - Full REPL terminal',
        '  - Run commands remotely',
        '  - Transfer files',
        '',
        '  Use from any device on the network',
    ])


def cmd_unalias(args):
    name = args.strip()
    if not name:
        return ('print', 'unalias: usage: unalias [name]')
    if name in _aliases:
        del _aliases[name]
        return ('print', f'  unaliased: {name}')
    return ('print', f'  unalias: {name} not found')


def cmd_fm(args, tft=None):
    return ('fm', args.strip() if args.strip() else os.getcwd())


def cmd_theme(args):
    return ('theme',)


def cmd_cat(args):
    path = args.strip()
    if not path:
        return ('print', 'cat: missing filename')
    try:
        with open(path, 'r') as f:
            content = f.read()
        return ('print', content)
    except OSError as e:
        return ('print', f'cat: {e}')


def cmd_cd(args):
    path = args.strip()
    if not path:
        return ('print', f'  cwd: {os.getcwd()}')
    try:
        os.chdir(path)
        return ('print', f'  cwd: {os.getcwd()}')
    except OSError as e:
        return ('print', f'cd: {e}')


def cmd_mkdir(args):
    path = args.strip()
    if not path:
        return ('print', 'mkdir: missing directory name')
    try:
        os.mkdir(path)
        return ('print', f'  created: {path}')
    except OSError as e:
        return ('print', f'mkdir: {e}')


def cmd_rm(args):
    path = args.strip()
    if not path:
        return ('print', 'rm: missing filename')
    try:
        os.remove(path)
        return ('print', f'  removed: {path}')
    except OSError as e:
        return ('print', f'rm: {e}')


def cmd_touch(args):
    path = args.strip()
    if not path:
        return ('print', 'touch: missing filename')
    try:
        with open(path, 'a') as f:
            f.write('')
        return ('print', f'  created: {path}')
    except OSError as e:
        return ('print', f'touch: {e}')


def cmd_brightness(args):
    global _backlight
    val = args.strip()
    if not val:
        return ('print', 'brightness: usage: brightness [0-100]')
    try:
        pct = int(val)
        if pct < 0 or pct > 100:
            return ('print', 'brightness: 0-100')
        duty = int(pct * 65535 / 100)
        _backlight.duty_u16(duty)
        return ('print', f'  brightness: {pct}%')
    except ValueError:
        return ('print', 'brightness: usage: brightness [0-100]')


_backlight = None


def cmd_info(tft=None):
    import gc
    lines = [
        '=== Espelt System Info ===',
        f'  Board:      ESP32-P4',
        f'  OS:         Espelt OS v1.0',
        f'  Free RAM:   {gc.mem_free()} bytes',
        f'  Used RAM:   {gc.mem_alloc()} bytes',
        f'  cwd:        {os.getcwd()}',
    ]
    if tft:
        lines.append(f'  Display:    {tft.width}x{tft.height}')
    try:
        st = os.statvfs('/')
        total = st[0] * st[2]
        free = st[0] * st[3]
        lines.append(f'  Storage:    {total - free}/{total} bytes')
    except:
        pass
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            lines.append(f'  WiFi:       {wlan.ifconfig()[0]}')
        else:
            lines.append(f'  WiFi:       disconnected')
    except:
        lines.append(f'  WiFi:       N/A')
    return ('print_lines', lines)


def cmd_buzzer(args):
    global _buzzer
    if not _buzzer:
        return ('print', 'buzzer: not available')
    parts = args.strip().split() if args.strip() else []
    if not parts:
        return ('print_lines', [
            f'buzzer: volume: {_buzzer.volume}%',
            '',
            '  buzzer [0-100]    Set volume',
            '  buzzer beep       Short beep',
            '  buzzer tone [hz]  Play tone (default 1000)',
            '  buzzer off        Stop sound',
            '  buzzer test       Play test sequence',
        ])
    action = parts[0].lower()
    if action.isdigit():
        pct = int(action)
        if pct < 0 or pct > 100:
            return ('print', 'buzzer: volume 0-100')
        _buzzer.volume = pct
        return ('print', f'buzzer: volume {pct}%')
    elif action == 'beep':
        dur = int(parts[1]) if len(parts) > 1 else 100
        _buzzer.beep(dur)
        return ('print', 'buzzer: beep')
    elif action == 'tone':
        freq = int(parts[1]) if len(parts) > 1 else 1000
        dur = int(parts[2]) if len(parts) > 2 else 200
        _buzzer.tone(freq, dur)
        return ('print', f'buzzer: {freq}Hz for {dur}ms')
    elif action == 'off':
        _buzzer.off()
        return ('print', 'buzzer: off')
    elif action == 'test':
        _buzzer.score_beep()
        import time
        time.sleep_ms(50)
        _buzzer.level_up_sound()
        return ('print', 'buzzer: test complete')
    else:
        return ('print', f'buzzer: unknown action "{action}"')
