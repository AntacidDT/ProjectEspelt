# Project Espelt — All Commands

## System (14)

| Command | Usage | Description |
|---------|-------|-------------|
| `help [page]` | `help 1` | Show help pages (1-6) |
| `help calc` | | List all calc help topics |
| `help calc [topic]` | `help calc fractions` | Calc help by topic |
| `clock` | | Current time on TFT (DD/MM/YY HH:MM:SS) |
| `info` | | System information |
| `calc [expr]` | `calc 2+2` | Calculator (REPL on empty) |
| `uname` | | System name |
| `pwd` | | Print working directory |
| `clear` | | Clear screen + reset OLED to status |
| `echo [text]` | `echo hello` | Print text |
| `sleep` | | Enter sleep mode |
| `brightness [n]` | `brightness 50` | Set backlight 0-100% |
| `theme` | | Cycle color themes (default/warm/cyber/forest) |
| `ip` | | Show local IP, netmask, gateway |
| `ascii [text]` | `ascii HELLO` | Display ASCII art on TFT |
| `dice [NdN]` | `dice 2d6` | Roll dice (e.g. d20, 3d6) |
| `pick item1 ...` | `pick red blue green` | Pick random item |
| `tip bill [%] [n]` | `tip 50 15 2` | Tip calculator with split |
| `morse enc/dec` | `morse enc SOS` | Morse code encode/decode |

## Files (22)

| Command | Usage | Description |
|---------|-------|-------------|
| `ls [dir]` | `ls /sd` | List files |
| `cat [file]` | `cat notes.txt` | View file contents |
| `cd [dir]` | `cd /sd` | Change directory |
| `mkdir [dir]` | `mkdir test` | Create directory |
| `rm [file]` | `rm file.txt` | Remove file |
| `cp [src] [dst]` | `cp a.txt b.txt` | Copy file |
| `mv [src] [dst]` | `mv old.txt new.txt` | Move/rename file |
| `touch [file]` | `touch file.txt` | Create empty file |
| `nano [file]` | `nano script.py` | Interactive text editor |
| `fm [dir]` | `fm /sd` | Visual file manager |
| `run [file.py]` | `run script.py` | Run Python script |
| `view [file.bmp]` | `view photo.bmp` | View BMP image on TFT |
| `draw [file.jpg]` | `draw image.jpg` | Draw JPEG on screen |
| `head [file] [n]` | `head file.txt 5` | First N lines of file |
| `tail [file] [n]` | `tail file.txt 5` | Last N lines of file |
| `wc [file]` | `wc file.txt` | Word/line/char count |
| `diff [f1] [f2]` | `diff a.txt b.txt` | Compare two files |
| `grep [pat] [file]` | `grep hello file.txt` | Search text in file |
| `search [pat] [dir]` | `search def commands/` | Recursive search across files |
| `find [name]` | `find *.py` | Find files by name |
| `df` | | Disk space usage |
| `du [dir]` | `du /sd` | Directory size usage |
| `backup` | | Save important files to SD |
| `restore` | | Load files from SD backup |

## Aliases (2)

| Command | Usage | Description |
|---------|-------|-------------|
| `alias [k=v]` | `alias ll=ls -l` | Create/list aliases |
| `unalias [name]` | `unalias ll` | Remove alias |

## Network (42)

| Command | Usage | Description |
|---------|-------|-------------|
| `wlan [ssid] [pass]` | `wlan MyWiFi pass123` | WiFi connect/scan (auto-syncs NTP time) |
| `wiki [query]` | `wiki esp32` | Wikipedia article intro (first paragraph) |
| `define [word]` | `define ephemeral` | Dictionary lookup (definition + synonyms) |
| `weather [city]` | `weather Amsterdam` | Current weather + 3-day forecast |
| `forecast [city]` | `forecast Berlin` | 5-day detailed weather forecast |
| `news [region]` | `news us` | Top headlines |
| `translate [fr] [to] [text]` | `translate en de hello` | Google Translate |
| `prayer [city,country]` | `prayer Berlin` | Prayer times (default Falkensee, Germany) |
| `timetable` | | School timetable |
| `ping [host]` | `ping google.com` | Ping a host |
| `dns [host]` | `dns google.com` | DNS lookup |
| `curl [host] [path]` | `curl example.com` | Raw HTTP GET request |
| `speedtest` | | Test download speed |
| `ipinfo` | | Your public IP + city + country |
| `stock [symbol]` | `stock AAPL` | Stock price + daily change |
| `crypto [symbol]` | `crypto BTC` | Crypto price |
| `timezone [city]` | `timezone Tokyo` | Time in any city |
| `exchange [amt] [from] [to]` | `exchange 100 USD EUR` | Currency exchange |
| `gh [user]` | `gh torvalds` | GitHub profile |
| `ghrepo [user]` | `ghrepo torvalds` | GitHub repos list |
| `holiday [cc]` | `holiday DE-BY` | Next public holiday (supports German states like DE-BY, DE-BE) |
| `aqi [city]` | `aqi London` | Air quality index (US AQI via Open-Meteo) |
| `bored` | | Random activity suggestion |
| `numfact [num]` | `numfact 42` | Number fact (via Numbers API) |
| `catfact` | | Random cat fact |
| `dogfact` | | Random dog fact |
| `trivia` | | Random trivia question |
| `dadjoke` | | Random dad joke |
| `randomfact` | | Random fact |
| `xkcd` | | Latest XKCD comic |
| `vocab` | | Word of the day |
| `joke2` | | Random joke (Official Joke API) |
| `geo` | | Your location (lat/lng via IP) |
| `npm [pkg]` | `npm express` | NPM package info |
| `pypi [pkg]` | `pypi requests` | PyPI package info |
| `quote` | | Random motivational quote |
| `roast` | | Get roasted |
| `rss [feed]` | `rss hn` | RSS feed reader (HN, Lobsters, Reddit, BBC, TechCrunch) |
| `ghrepofs [user]` | `ghrepofs torvalds` | GitHub repo filesystem browser |
| `ytchl [channel]` | `ytchl mkbhd` | YouTube channel recent videos |
| `ytdt [channel]` | `ytdt mkbhd` | YouTube channel stats (subs, videos, bio) |
| `bsky [handle]` | `bsky alice.bsky.social` | Bluesky social (login first) |
| `gmail` | | Read/send Gmail (login with app password) |

> `chat` is disabled (HuggingFace API gated). `lyrics` is unavailable (service deprecated).

## Games (50)

Merged games offer mode selection at startup (Classic, Obstacles, etc.).
All real-time games have difficulty selection (Easy/Medium/Hard) on start.
Visual upgrades: sprites, particles, 3D bevels, parallax, trails, screen effects.

| Command | Description |
|---------|-------------|
| `snake` | Snake (modes: Classic, Obstacles) |
| `snake2` | Snake (same engine, mode selector) |
| `2048` | 2048 puzzle |
| `tetris` | Tetris (modes: Classic, Hard Drop + Hold) |
| `tetris2` | Tetris (same engine, mode selector) |
| `flappy` | Flappy Bird |
| `breakout` | Breakout (modes: Classic, Multi-ball + Levels) |
| `breakout2` | Breakout (same engine, mode selector) |
| `pong` | Pong (modes: Classic CPU, 2 Player, 3D) |
| `pong2p` | Pong (same engine, mode selector) |
| `pong3d` | Pong (same engine, mode selector) |
| `minesweeper` | Minesweeper |
| `hangman` | Word guessing |
| `rps` | Rock Paper Scissors |
| `tictactoe` | Tic Tac Toe |
| `guess` | Number guessing |
| `memory` | Simon (modes: Classic, Speed Challenge) |
| `wordle` | Wordle clone |
| `asteroids` | Space shooter |
| `maze` | Maze generator |
| `maze3d` | First-person 3D maze (raycasting) |
| `connect4` | Connect Four |
| `battleship` | Battleship |
| `trivia` | Trivia quiz |
| `typing` | Typing speed test |
| `mathquiz` | Math quiz |
| `sudoku` | 4x4 Sudoku |
| `lightsout` | Lights Out puzzle |
| `platformer` | Side-scroll runner |
| `life` | Conway's Game of Life |
| `tron` | Tron light cycles (vs CPU) |
| `racing` | Top-down racing |
| `invaders` | Space Invaders |
| `checkers` | Checkers (2-player) |
| `whack` | Whack-a-mole |
| `othello` | Othello (vs CPU) |
| `tank` | Tank Battle |
| `hanoi` | Tower of Hanoi |
| `bomber` | Bomber |
| `fighter` | Fighter |
| `dodge` | Dodge |
| `tag` | Tag |
| `archery` | Archery |
| `sumo` | Sumo |
| `3d` | 3D wireframe |
| `chess` | Chess vs CPU (minimax AI) |
| `mastermind` | Code-breaking vs CPU |
| `nim` | Nim vs CPU (XOR optimal) |
| `blackjack` | Blackjack vs dealer |
| `simon` | Simon (same engine as memory) |
| `simon2` | Simon (same engine, mode selector) |
| `cooking` | Recipe timing game |
| `sandbox` | Pixel art + physics sandbox |
| `infinitecraft` | Element combining discovery |
| `trolley` | Trolley Problem moral dilemmas |
| `password` | Password game (progressive rules) |
| `mystery` | Mystery game (random mini-game) |

## Timer (3)

| Command | Usage | Description |
|---------|-------|-------------|
| `timer pomodoro [min]` | `timer pomodoro 25` | Pomodoro timer on OLED |
| `timer countdown [sec]` | `timer countdown 60` | Countdown timer on OLED |
| `stopwatch` | | Count-up timer on OLED (MM:SS.CC) |

## OLED Modes (55+)

| Command | Description |
|---------|-------------|
| `oled status` | RAM bar + name |
| `oled ram` | Detailed RAM usage |
| `oled flash` | Flash storage info |
| `oled info` | System info |
| `oled text [s]` | Display custom text |
| `oled dvd` | DVD logo bounce |
| `oled wave` | Sine wave |
| `oled clock` | Digital clock |
| `oled matrix` | Matrix rain |
| `oled fire` | Fire effect |
| `oled starfield` | Moving stars |
| `oled bounce` | Bouncing ball |
| `oled plasma` | Plasma effect |
| `oled rain` | Rain drops |
| `oled fireworks` | Particle explosions |
| `oled dna` | DNA helix |
| `oled equalizer` | Audio bars |
| `oled pong` | Mini pong (CPU vs CPU) |
| `oled lava` | Lava lamp |
| `oled sparkle` | Twinkling stars |
| `oled pulse` | Expanding rings |
| `oled cube` | Rotating 3D cube |
| `oled textscroll` | Star Wars crawl |
| `oled minisnake` | Playable snake on OLED |
| `oled heart` | Beating heart |
| `oled invader` | Space invader |
| `oled spiral` | Rotating spiral |
| `oled boot` | Fake boot sequence |
| `oled glitch` | Glitch effect |
| `oled disco` | Disco mode |
| `oled binary` | Binary rain |
| `oled eye` | Watching eye |
| `oled checker` | Checkerboard |
| `oled lightning` | Lightning bolts |
| `oled helplogo` | Bouncing HELP text |
| `oled skull` | ASCII skull |
| `oled cat` | ASCII cat |
| `oled dance` | Dancing stick figure |
| `oled doom` | DOOM zoom |
| `oled potato` | Potato |
| `oled chicken` | Walking chicken |
| `oled esp32` | Spinning ESP32 |
| `oled pacman` | Pac-Man eating dots |
| `oled tunnel` | Shrinking tunnel |
| `oled typewriter` | Typewriter text |
| `oled radar` | Sweeping radar |
| `oled tetrisfall` | Falling tetris blocks |
| `oled firefly` | Blinking fireflies |
| `oled spectrum` | Fake spectrum analyzer |
| `oled osnake` | Snake with score (auto-play) |
| `oled stopwatch` | Count-up timer |
| `oled random` | Random animation (no repeats) |
| `oled timer` | MM:SS countdown |
| `oled timer_debug` | MM:SS countdown with debug info |
| `oled game_hud` | Game stats HUD (score/lives/level) — auto-activated during games |
| `oled wlan` | WiFi status display |
| `oled auto` | Context-aware (clock + game HUD when active) |
| `oled notify [text]` | Popup alert message (2s) |

## Media (3)

| Command | Usage | Description |
|---------|-------|-------------|
| `view [file.bmp]` | `view photo.bmp` | View BMP image on TFT |
| `draw [file.jpg]` | `draw image.jpg` | Draw JPEG on screen |
| `qr [text]` | `qr hello world` | QR code on TFT |

## Converters (6)

| Command | Usage | Description |
|---------|-------|-------------|
| `convert [v] [from] [to]` | `convert 100 km mi` | Unit converter |
| `base [num] [to]` | `base 255 hex` | Number base converter (bin/oct/hex/dec) |
| `color [hex]` | `color 0xFF0000` | Color hex/RGB/TFT converter |
| `passwd [len]` | `passwd 20` | Random password generator |
| `uuid` | | UUID generator |
| `base64 enc/dec [text]` | `base64 enc hello` | Base64 encode/decode |

## Encryption (2)

| Command | Usage | Description |
|---------|-------|-------------|
| `encrypt [type] [text]` | `encrypt binary hello` | Encrypt text (binary/ASCII/HEX) |
| `decrypt [type] [data]` | `decrypt binary 01101...` | Decrypt data (binary/ASCII/HEX) |

## Productivity (14)

| Command | Usage | Description |
|---------|-------|-------------|
| `todo` | | Interactive todo list (REPL) |
| `todo add [task]` | `todo add homework` | Add a task |
| `todo list` | | List all tasks |
| `todo done [n]` | `todo done 1` | Toggle task done |
| `todo rm [n]` | `todo rm 1` | Remove a task |
| `todo clear` | | Clear completed tasks |
| `notes new [name]` | `notes new ideas` | Create note (opens nano) |
| `notes list` | | List all notes |
| `notes read [name]` | `notes read ideas` | Read a note |
| `notes rm [name]` | `notes rm ideas` | Delete a note |
| `history` | | Command history |
| `calendar` | | Interactive calendar |
| `alarm [time]` | `alarm 07:30` | Set alarm |
| `reminders` | | Interactive reminders (REPL) |
| `remind [text] [time]` | `remind "meeting" 14:00` | Set a reminder |
| `contacts` | | Interactive contacts list (REPL) |
| `draw/paint [file]` | `draw/paint canvas` | Pixel art drawing tool |
| `hexdump [file]` | `hexdump file.bin` | Hex dump of file |
| `timer` | | Full timer REPL with presets |

## System Info (5)

| Command | Usage | Description |
|---------|-------|-------------|
| `freq [mhz]` | `freq 240` | Show/set CPU frequency |
| `mem` | | Memory usage info |
| `uptime` | | Time since boot |
| `ping [host]` | `ping google.com` | Ping a host |
| `startup [cmd]` | `startup wlan h` | Manage boot commands (`-d` to remove, `-c` to clear) |

## Buzzer (5)

| Command | Usage | Description |
|---------|-------|-------------|
| `buzzer [0-100]` | `buzzer 50` | Set volume (0-100%) |
| `buzzer beep` | `buzzer beep 100` | Short beep (ms, default 100) |
| `buzzer tone [hz] [ms]` | `buzzer tone 880 200` | Play tone at frequency |
| `buzzer off` | | Stop all sounds |
| `buzzer test` | | Play test sequence |

## Chemistry (30)

| Command | Usage | Description |
|---------|-------|-------------|
| `chem info [el]` | `chem info Fe` | Element info |
| `chem mass [formula]` | `chem mass H2O` | Molar mass |
| `chem parse [formula]` | `chem parse NaCl` | Parse formula into elements |
| `chem ph [H+]` | `chem ph 0.001` | pH calculator |
| `chem gas [args]` | `chem gas p 1.5 v 2 n 0.1` | Gas law (PV=nRT) |
| `chem molarity [mol] [L]` | `chem molarity 0.5 1` | Solution molarity |
| `chem dilute [c1] [v1] [v2]` | `chem dilute 2 100 200` | Dilution (C1V1=C2V2) |
| `chem moles [mass] [formula]` | `chem moles 18 H2O` | Mass to moles |
| `chem grams [mol] [formula]` | `chem grams 1 H2O` | Moles to grams |
| `chem percent [formula]` | `chem percent H2O` | Percent composition |
| `chem config [el]` | `chem config Fe` | Electron configuration |
| `chem balance [formula]` | `chem balance H2+O2` | Balance chemical equation |
| `chem thermo [reaction]` | | Thermochemistry calculations |
| `chem organic [name]` | | Organic chemistry structures |
| `chem charles ...` | `chem charles v1=10 t1=300 t2=? v2=20` | Charles Law (V1/T1=V2/T2) |
| `chem combined ...` | `chem combined p1=1 v1=10 t1=300 p2=? v2=20 t2=400` | Combined Gas Law |
| `chem graham [m1] [m2]` | `chem graham 2 32` | Graham's Law (effusion rate) |
| `chem dalton [P1] [P2] ...` | `chem dalton 0.5 0.3 0.2` | Dalton's Law (partial pressures) |
| `chem redox [rxn]` | `chem redox zn_cu` | Redox reactions |
| `chem trend [el]` | `chem trend Fe` | Periodic trends (EN, IE, radius) |
| `chem bond [el1] [el2]` | `chem bond Na Cl` | Bond type prediction |
| `chem lewis [el]` | `chem lewis O` | Lewis dot notation |
| `chem valence [el]` | `chem valence C` | Valence electrons |
| `chem titrate ...` | `chem titrate ca=? va=25 cb=0.1 vb=30` | Titration calculator |
| `chemtable` | | Periodic table on TFT |
| `chem known` | | List known molecules |
| `chem list` | | Element list |
| `chem [formula]` | `chem H2O` | Quick formula lookup |

## Biology (36)

| Command | Usage | Description |
|---------|-------|-------------|
| `bio dna [seq]` | `bio dna ATCG` | DNA complement |
| `bio rna [seq]` | `bio rna ATCG` | DNA to mRNA transcription |
| `bio translate [seq]` | `bio translate AUG` | mRNA to amino acids |
| `bio protein [seq]` | `bio protein ATG` | Full DNA pipeline |
| `bio amino [name]` | `bio amino Glycine` | Amino acid info |
| `bio polar` | | Amino acids by polarity |
| `bio codon [codon]` | `bio codon AUG` | Codon to amino acid |
| `bio organelle [name]` | `bio organelle nucleus` | Cell organelle info |
| `bio cells` | | Prokaryote vs Eukaryote |
| `bio punnett [p1] [p2]` | `bio punnett Aa Aa` | 1-trait Punnett square |
| `bio punnett2 [...]` | `bio punnett2 AaBb AaBb` | 2-trait Punnett square |
| `bio hwe [p]` | `bio hwe 0.5` | Hardy-Weinberg equilibrium |
| `bio biome [name]` | `bio biome rainforest` | Biome info |
| `bio trophic` | | Trophic levels |
| `bio taxonomy [name]` | `bio taxonomy dog` | Organism classification |
| `bio heart` | | Human heart anatomy |
| `bio brain` | | Human brain anatomy |
| `bio lung` | | Human lung anatomy |
| `bio kidney` | | Human kidney anatomy |
| `bio system` | | Body systems overview |
| `bio mutate [seq] [type]` | `bio mutate ATCG point_sub 2 G` | Apply DNA mutation |
| `bio mutation [type]` | `bio mutation missense` | Mutation type info |
| `bio effect [orig] [mut]` | `bio effect ATG ATT` | Mutation effect prediction |
| `bio protein_s [level]` | `bio protein_s tertiary` | Protein structure info |
| `bio denature` | | Denaturing factors |
| `bio cellcycle [phase]` | `bio cellcycle s` | Cell cycle phase info |
| `bio mitosis [stage]` | `bio mitosis prophase` | Mitosis stage info |
| `bio meiosis [i/ii]` | `bio meiosis i` | Meiosis division info |
| `bio compare_mm` | | Mitosis vs Meiosis comparison |
| `bio evolution [concept]` | `bio evolution natural_selection` | Evolution concepts |
| `bio speciation [type]` | `bio speciation allopatric` | Speciation types |
| `bio microbe [type]` | `bio microbe bacteria` | Microbiology info |
| `bio immune [branch]` | `bio immune adaptive` | Immune response info |
| `bio disease [name]` | `bio disease malaria` | Disease information |
| `bio clear` | | Clear biology display |

## Coding (16)

| Command | Usage | Description |
|---------|-------|-------------|
| `code base [num] [base]` | `code base 255 hex` | Number base conversion |
| `code ascii [char\|code]` | `code ascii A` | ASCII lookup |
| `code ascii table [s] [e]` | `code ascii table 32 127` | ASCII table range |
| `code rot13 [text]` | `code rot13 hello` | ROT13 cipher |
| `code caesar [text] [n]` | `code caesar hello 3` | Caesar cipher |
| `code morse enc [text]` | `code morse enc SOS` | Morse encode |
| `code morse dec [data]` | `code morse dec ... --- ...` | Morse decode |
| `code b64 enc [text]` | `code b64 enc hello` | Base64 encode |
| `code b64 dec [data]` | `code b64 dec aGVsbG8=` | Base64 decode |
| `code ds [name]` | `code ds stack` | Data structures reference |
| `code algo [name]` | `code algo bubblesort` | Algorithms reference |
| `code regex [patterns\|meta]` | `code regex patterns` | Regex patterns / metacharacters |
| `code regex meta` | | Regex metacharacter reference |
| `code python syntax` | | Python syntax reference |
| `code python builtins` | | Python builtins reference |
| `code mp` | | MicroPython imports reference |
| `code syntax` | | Code syntax highlighting reference |
| `code functions` | | Code function reference |
| `code libraries` | | Code library reference |
| `code examples` | | Code examples |
| `code music` | | Music code reference |

## Electronics (51)

| Command | Usage | Description |
|---------|-------|-------------|
| `electronics` | | Interactive TFT mode (formula browser + solver) |
| `help electronics` | | Electronics help (1/2) |
| `help electronics 2` | | Electronics help (2/2) |

### Categories (7)

| Category | Formulas | Description |
|----------|----------|-------------|
| Circuit Basics | 11 | Ohm, power, resistors, dividers, RC/RL |
| AC Circuits | 7 | Impedance, reactance, phase, RMS |
| LC Resonance | 5 | Resonant freq, Q factor, bandwidth, energy |
| Digital Logic | 10 | Gates, De Morgan, full adder, mux |
| Transistors | 5 | BJT (Ic, Vce, bias), MOSFET (Vgs, Rdson) |
| Op-Amp Circuits | 7 | Inv/non-inv gain, summing, follower, int/diff |
| Power Supply | 6 | Buck, boost, buck-boost, ripple, LDO, heatsink |

### Tools

| Tool | Usage | Description |
|------|-------|-------------|
| rcalc | rcalc color yellow violet red | Resistor color code decode |
| rcalc | rcalc value 4700 | Value to color code |
| vdiv | vdiv vin=5 r1=10k r2=10k | Voltage divider calc |
| led | led vs=5 vf=2.1 if=20 | LED current-limiting resistor |
| rcfilt | rcfilt r=10k c=100n | RC filter cutoff freq |
| lcfilt | lcfilt l=100u c=100n | LC resonant frequency |
| baud | baud 115200 | UART frame timing |
| cap | cap 104 | SMD capacitor code decode |

### Reference

| Reference | Usage | Description |
|-----------|-------|-------------|
| ic | ic 555 | IC pinouts (555, 7805, LM358, etc.) |
| wire | wire 22 | AWG wire gauge table |
| led | led red | LED forward voltages |
| truth | truth AND | Logic gate truth tables |
| smd_cap | smd_cap | SMD capacitor code reference |

## Music (1)

| Command | Usage | Description |
|---------|-------|-------------|
| `music` | | Song player with 6 songs, buzzer playback, TFT sheet music display |

## Piano (1)

| Command | Usage | Description |
|---------|-------|-------------|
| `piano` | | Buzzer keyboard, 2 octaves, record/play functionality |

## Keyboard Shortcuts

### CTRL Shortcuts (10)

| Shortcut | Description |
|----------|-------------|
| `Ctrl+C` | Cancel / clear line |
| `Ctrl+L` | Clear screen + reset OLED |
| `Ctrl+U` | Clear input line |
| `Ctrl+A` | Clear input line |
| `Ctrl+3` | Stealth mode (all screens off/on) |
| `Ctrl+B` | Toggle backlight on/off |
| `Ctrl+T` | Cycle color theme |
| `Ctrl+O` | OLED mode selector (W=WiFi S=Status C=Clock A=Auto O=Off) |
| `Ctrl+R` | Reboot device |
| `Ctrl+F` | Show free RAM |

### Navigation (5)

| Key | Description |
|-----|-------------|
| `Up Arrow / PgUp` | Previous command |
| `Down Arrow / PgDn` | Next command |
| `Tab` | Auto-complete command |
| `Ctrl+1` | Previous command (alt) |
| `Ctrl+2` | Next command (alt) |

### Nano Editor (19)

| Key | Description |
|-----|-------------|
| `Ctrl+E` | Cursor up |
| `Ctrl+D` | Cursor down |
| `Ctrl+S` | Cursor left |
| `Ctrl+F` | Cursor right |
| `Ctrl+A` | Start of line |
| `Ctrl+W` | End of line |
| `Ctrl+G` | Go to first line |
| `Ctrl+L` | Go to last line |
| `Ctrl+K` | Delete line |
| `Ctrl+U` | Delete char at cursor |
| `Ctrl+O` | Save without exiting |
| `Ctrl+H` | Redraw screen |
| `Ctrl+X` | Find/search text |
| `Ctrl+R` | Find and replace |
| `Esc` | Save and exit |
| `Enter` | New line |
| `Tab` | Insert 4 spaces |
| `Backspace` | Delete character |

### File Manager (4)

| Key | Description |
|-----|-------------|
| `E` | Move up |
| `D` | Move down |
| `Enter/O` | Open file/directory |
| `Esc` | Exit file manager |

### Todo REPL (7)

| Key | Description |
|-----|-------------|
| `A` | Add new task |
| `Space/Enter` | Toggle done |
| `D` | Delete task (press twice to confirm) |
| `C` | Clear completed tasks |
| `Up/Down` | Navigate tasks |
| `Esc` | Save and exit |

### Themes (4)

| Theme | Colors |
|-------|--------|
| `default` | Cyan header, white text |
| `warm` | Orange header, white text |
| `cyber` | Blue header, cyan text |
| `forest` | Green header, green text |

## Calculator (CALC)

The `calc` command launches an interactive scientific calculator with full-screen REPL interface. Press `Ctrl+X` to exit and save history/memory.

### Core Features
- **Basic Arithmetic**: `+ - * / %` with operator precedence
- **Fractions**: `2/3 + 1/4 = 11/12` (exact arithmetic), mixed fraction display (`5/2` -> `2 1/2`)
- **Scientific Functions**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `log`, `ln`, `exp`
- **Hyperbolic**: `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`
- **Special Functions**: `fact`, `nPr`, `nCr`, `rand`, `randint`
- **Statistics**: `mean`, `stddev`, `pol`, `rec`
- **Constants**: `pi`, `e`, `g`, `c`, `phi`
- **Memory**: `Ans`, `A-F`, `X`, `Y`, `M` (persistent across sessions)
- **Implicit Multiplication**: `2pi`, `2(x+1)`, `(2)(3)` all work
- **Factorial Postfix**: `5!` = 120
- **Comparisons**: `<`, `>`, `<=`, `>=`, `==`, `!=` (return 1 or 0)
- **Multi-arg Functions**: `min(1,2,3)`, `max(4,5,6)`, `gcd(12,8)`, `lcm(4,6)`, `clamp(val,lo,hi)`, `log(x,base)`, `hypot(x,y)`

### Complex Numbers
- **Notation**: `3+4i`, `i`, `2i`, `a+bi`
- **Arithmetic**: `+`, `-`, `*`, `/`, `^` on complex numbers
- **Functions**: `re(z)`, `im(z)`, `conj(z)`, `abs(z)`, `arg(z)`, `polar(z)`
- **Complex math**: `sqrt(-1)=i`, `exp(i*pi)=-1`, trig on complex args

### Matrix Operations
- **Syntax**: `[1,2;3,4]` (semicolon = new row)
- **Arithmetic**: `A+B`, `A*B`, `k*A`, `A/B` (= A*inv(B))
- **Functions**: `det(A)`, `inv(A)`, `tr(A)`, `transpose(A)`, `rref(A)`
- **Constructors**: `eye(n)`, `zeros(m,n)`

### Lists & Regression
- **List syntax**: `L1={1,2,3,4}` (L1-L6 available)
- **List functions**: `length(L1)`, `sum(L1)`, `sort(L1)`, `mean(L1)`, `stddev(L1)`
- **Regression**: `linreg(L1,L2)`, `quadreg`, `expreg`, `logreg`, `pwreg`, `MedMed`
- **Correlation**: `corr(L1,L2)`

### Numerical Methods
- **Summation**: `summate(x^2, x, 1, 10)` (sigma notation)
- **Product**: `product(x, x, 1, 5)` (pi notation)
- **Integration**: `fnInt(x^2, x, 0, 1)` (Simpson's rule)
- **Differentiation**: `fnDiff(x^2, x, 3)` (central difference)
- **Sequences**: `seq(x^2, x, 1, 5)` = {1, 4, 9, 16, 25}

### Statistical Distributions
- **Normal**: `normalpdf(x,μ,σ)`, `normalcdf(a,b,μ,σ)`, `invNorm(p,μ,σ)`
- **Binomial**: `binompdf(n,p,x)`, `binomcdf(n,p,x)`
- **Poisson**: `poissonpdf(λ,x)`, `poissoncdf(λ,x)`
- **Other**: `tcdf`, `χ²cdf`, `fcdf`
- **Tests**: `ztest(μ₀,σ,x̄,n)`, `ttest(μ₀,s,x̄,n)`

### Systems & Piecewise
- **System solver**: `solve2(x+y-5, x-y-1, 0, 0)` (Newton's method)
- **Conditional**: `when(5>3, 10, 20)`, `piecewise(expr1, cond1, expr2, cond2, ...)`

### Advanced Features
- **Angle Modes**: `DEG`, `RAD`, `GRAD` (toggles with mode switching)
- **Graphing**: `Ctrl+G` to graph expressions on OLED (`sin(x)`, `x^2`, etc.)
- **Fraction-Decimal Toggle**: `Ctrl+D` switches between mixed fraction and decimal display
- **Auto-complete**: `Tab` for function autocompletion
- **History**: Command history with up/down arrow navigation
- **Session Persistence**: Auto-saves history and memory to `/sd/calc_history.txt` and `/sd/calc_memory.txt`
- **Left-to-Right Power**: `2^3^2` = 512 (standard math convention)
- **Scientific Notation**: `1e6`, `2.5e-3` work as expected
- **Percentage**: `50%` = 0.5, use `Ctrl+M` to insert `%`
- **Help System**: `help calc` lists topics, `help calc <topic>` shows detailed help
- **Themes**: Calc, todo, and nano all respect the current color theme (Ctrl+T to cycle)

### Help Topics
`help calc complex`, `help calc matrix`, `help calc regression`, `help calc numerical`, `help calc distributions`, `help calc systems`, `help calc functions`, `help calc constants`, `help calc memory`, `help calc fractions`, `help calc percentage`, `help calc trig`, `help calc calculus`, `help calc cas`, `help calc shortcuts`

## Totals

| Category | Count |
|----------|-------|
| System commands | 18 |
| File commands | 22 |
| Alias commands | 2 |
| Network commands | 42 |
| Games | 57 |
| Timer commands | 3 |
| OLED modes | 55+ |
| Media commands | 3 |
| Converters | 6 |
| Encryption | 2 |
| Productivity | 14 |
| System Info | 5 |
| Buzzer | 5 |
| Chemistry | 30 |
| Biology | 36 |
| Coding | 21 |
| Electronics | 51 |
| Music | 1 |
| Piano | 1 |
| CTRL shortcuts | 10 |
| Navigation keys | 5 |
| Nano shortcuts | 19 |
| File manager keys | 4 |
| Todo REPL keys | 7 |
| Themes | 4 |
| Calculator | (see above) |
| **Total unique commands** | **~380** |
