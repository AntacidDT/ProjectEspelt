# Commands Reference

Complete reference for all 100+ commands in Espelt32.

## Table of Contents

- [System Commands](#system-commands)
- [File Commands](#file-commands)
- [Network Commands](#network-commands)
- [Game Commands](#game-commands)
- [Math & Science](#math--science)
- [Utility Commands](#utility-commands)
- [OLED Commands](#oled-commands)
- [Keyboard Shortcuts](#keyboard-shortcuts)

---

## System Commands

### `clock`
Display current date and time.

```bash
clock
```

### `info`
Show system information (board, RAM, storage, WiFi).

```bash
info
```

### `math [expression]`
Calculator with CAS (Computer Algebra System).

```bash
math 2+2           # Basic arithmetic
math sin(45)       # Trigonometry
math sqrt(144)     # Square root
math diff(x^2, x)  # Differentiation
math solve(x+2=5)  # Equation solving
```

### `sleep`
Enter sleep mode. Press any key to wake.

```bash
sleep
```

### `brightness [0-100]`
Set TFT backlight brightness.

```bash
brightness 50     # Set to 50%
brightness        # Show current
```

### `theme`
Cycle through color themes.

```bash
theme             # default → warm → cyber → forest
```

### `uname`
Print system name.

```bash
uname             # Espelt OS v1.0 - ESP32-P4
```

### `pwd`
Print working directory.

```bash
pwd
```

### `echo [text]`
Print text to screen.

```bash
echo Hello World
```

### `clear`
Clear the screen.

```bash
clear
```

### `freq [mhz]`
Get/set CPU frequency.

```bash
freq              # Show current
freq 240          # Set to 240MHz
```

### `reboot`
Reboot the device.

```bash
reboot
```

---

## File Commands

### `ls [directory]`
List files in directory.

```bash
ls                # Current directory
ls /sd            # SD card
ls lib            # Library folder
```

### `cat [file]`
Display file contents.

```bash
cat boot.py
cat /sd/data.txt
```

### `cd [directory]`
Change working directory.

```bash
cd /sd
cd lib
cd ..             # Parent directory
```

### `mkdir [directory]`
Create a new directory.

```bash
mkdir mydir
mkdir /sd/backup
```

### `rm [file]`
Remove a file.

```bash
rm oldfile.txt
```

### `touch [file]`
Create an empty file.

```bash
touch newfile.txt
```

### `cp [source] [dest]`
Copy a file.

```bash
cp file.txt /sd/backup.txt
```

### `mv [source] [dest]`
Move or rename a file.

```bash
mv old.txt new.txt
mv file.txt /sd/archive/
```

### `nano [file]`
Open text editor.

```bash
nano myfile.py
```

**Nano Shortcuts**:
- `Ctrl+E/D/S/F` - Move cursor (up/down/left/right)
- `Ctrl+A/W` - Start/end of line
- `Ctrl+G/L` - First/last line
- `Ctrl+K` - Delete line
- `Ctrl+U` - Delete char at cursor
- `Ctrl+O` - Save
- `Ctrl+X` - Find
- `Ctrl+R` - Find & replace
- `ESC` - Save & exit

### `fm [directory]`
Open file manager.

```bash
fm                # Current directory
fm /sd            # SD card root
```

**File Manager Keys**:
- `E/D` - Navigate up/down
- `Enter` - Open file/directory
- `ESC` - Exit

### `run [file.py]`
Execute a Python script.

```bash
run myscript.py
```

### `find [name]`
Find files by name.

```bash
find *.py
```

### `grep [pattern] [file]`
Search for pattern in file.

```bash
grep "import" main.py
```

### `head [file] [lines]`
Show first N lines of file.

```bash
head main.py 10
```

### `tail [file] [lines]`
Show last N lines of file.

```bash
tail main.py 10
```

### `wc [file]`
Count lines, words, characters.

```bash
wc main.py
```

### `diff [file1] [file2]`
Compare two files.

```bash
diff file1.txt file2.txt
```

### `du [directory]`
Show directory size.

```bash
du /sd
```

### `df`
Show disk space usage.

```bash
df
```

### `backup`
Backup files to SD card.

```bash
backup
```

### `restore`
Restore files from SD card.

```bash
restore
```

---

## Network Commands

### `wlan [ssid] [password]`
Connect to WiFi network.

```bash
wlan                          # Show status
wlan scan                     # Scan networks
wlan MyWiFi MyPassword        # Connect
```

### `ip`
Show local IP address.

```bash
ip
```

### `ping [host]`
Ping a host.

```bash
ping google.com
ping 8.8.8.8
```

### `dns [host]`
DNS lookup.

```bash
dns example.com
```

### `curl [host]`
HTTP GET request.

```bash
curl example.com
```

### `speedtest`
Test download speed.

```bash
speedtest
```

### `webrepl`
Show WebREPL connection info.

```bash
webrepl
```

### `ota`
Start OTA update server.

```bash
ota
# Then open browser to upload .py files
```

### `wlan`
WiFi management.

```bash
wlan              # Show status
wlan scan         # Scan networks
wlan ssid pass    # Connect
```

---

## API Commands

### `weather [city]`
Get weather information.

```bash
weather London
weather          # Default city
```

### `wiki [query]`
Search Wikipedia.

```bash
wiki ESP32
```

### `startup [command]`
Manage startup commands that run on boot.

```bash
startup                    # List all startup commands
startup wlan h             # Add 'wlan h' to startup
startup wlan h -d          # Remove 'wlan h' from startup
startup -c                 # Clear all startup commands
```

### `translate [from] [to] [text]`
Translate text.

```bash
translate en tr hello
translate fr es bonjour
```

### `define [word]`
Dictionary lookup.

```bash
define algorithm
```

### `chat [message]`
AI chat (Llama model).

```bash
chat What is MicroPython?
```

### `news`
Get latest news.

```bash
news
```

### `prayer [city,country]`
Get prayer times. Default: Falkensee, Germany.

```bash
prayer
prayer Berlin
prayer Mecca, Saudi Arabia
```

### `timetable`
Show school timetable.

```bash
timetable
```

### `stock [symbol]`
Get stock price.

```bash
stock AAPL
```

### `crypto [coin]`
Get cryptocurrency price.

```bash
crypto bitcoin
```

### `exchange [amount] [from] [to]`
Currency conversion.

```bash
exchange 100 USD EUR
```

### `ipinfo`
Show public IP information.

```bash
ipinfo
```

### `gh [user]`
GitHub profile info.

```bash
gh torvalds
```

### `ghrepo [user]`
GitHub repositories.

```bash
ghrepo torvalds
```

### `holiday [cc]`
Next public holiday. Supports German states (DE-BY, DE-BE, etc).

```bash
holiday US
holiday DE-BY
holiday DE-BE
```

### `aqi [city]`
Air quality index (US AQI via Open-Meteo).

```bash
aqi Beijing
aqi London
aqi Tokyo
```

### `bored`
Random activity suggestion.

```bash
bored
```

### `timezone [timezone]`
Show time in timezone.

```bash
timezone EST
timezone UTC+3
```

---

## Game Commands

### `games`
List all available games.

```bash
games             # Show all games
games 1           # Page 1
games 2           # Page 2
games 3           # Page 3
```

### Available Games (29 total)

| Game | Description |
|------|-------------|
| `snake` | Classic snake game |
| `tetris` | Tetris blocks |
| `2048` | 2048 puzzle |
| `flappy` | Flappy bird clone |
| `minesweeper` | Mine sweeper |
| `pong` | Table tennis |
| `breakout` | Brick breaker |
| `chess` | Chess (vs AI) |
| `checkers` | Checkers (vs AI) |
| `sudoku` | Sudoku puzzle |
| `tictactoe` | Tic-tac-toe |
| `racer` | Racing game |
| `maze` | Maze navigator |
| `tetris64` | Tetris on OLED |
| `snake64` | Snake on OLED |
| `pong64` | Pong on OLED |
| `memory` | Memory matching |
| `simon` | Simon says |
| `rps` | Rock paper scissors |
| `quiz` | Quiz game |

---

## Math & Science

### `math [expression]`
Full calculator with CAS.

```bash
math 2+2              # 4
math 10*5-3           # 47
math sin(45)          # 0.707
math cos(0)           # 1
math sqrt(144)        # 12
math log(100)         # 2
math factorial(5)     # 120
math diff(x^2, x)     # 2*x
math integrate(x, x)  # x^2/2
math solve(x+2=5, x)  # x=3
math graph sin(x)     # Plot on OLED
```

**Calculator Topics**:
```bash
help math            # List all topics
help math basic      # Basic operations
help math trig       # Trigonometry
help math calc       # Calculus
help math algebra    # Algebra
help math fractions  # Fractions
help math matrices   # Matrices
```

### `physics [topic]`
Physics formulas and solver.

```bash
physics              # List topics
physics kinematics   # Motion equations
physics dynamics     # Forces
physics energy       # Energy & work
physics waves        # Wave equations
physics thermo       # Thermodynamics
physics optics       # Optics
physics em           # Electromagnetism
```

### `convert [value] [from] [to]`
Unit conversion.

```bash
convert 100 cm m        # meters
convert 72 fahrenheit c # celsius
convert 5 km miles      # miles
convert 1 kg lbs        # pounds
```

### `base [number]`
Number base converter.

```bash
base 255           # Show all bases
base 1010 bin      # Decimal to binary
base FF dec        # Hex to decimal
```

---

## Utility Commands

### Todo List

```bash
todo add "Buy groceries"    # Add task
todo list                   # List all
todo done 1                 # Mark #1 done
todo rm 1                   # Remove #1
todo clear                  # Clear done tasks
```

### Notes

```bash
notes new "My Note"         # Create note
notes list                  # List all
notes read "My Note"        # Read note
notes rm "My Note"          # Delete note
```

### `timer [type]`
Timer functions.

```bash
timer pomodoro       # 25min work + 5min break
timer countdown 60   # 60 second countdown
```

### `stopwatch`
Start stopwatch on OLED.

```bash
stopwatch
```

### `encrypt`
Encrypt text with password.

```bash
encrypt
# Enter text, then password
```

### `decrypt`
Decrypt text with password.

```bash
decrypt
# Enter encrypted text, then password
```

### `passwd [length]`
Generate random password.

```bash
passwd              # 16 chars
passwd 32           # 32 chars
```

### `uuid`
Generate UUID.

```bash
uuid
```

### `color [hex]`
Convert hex color.

```bash
color FF0000        # Show RGB values
```

### `base64 [encode|decode] [text]`
Base64 encode/decode.

```bash
base64 encode Hello
base64 decode SGVsbG8=
```

### `ascii [text]`
Display ASCII art on TFT.

```bash
ascii Hello
```

### `qr [text]`
Generate QR code on TFT.

```bash
qr https://example.com
```

### `draw [file]`
Drawing mode on TFT.

```bash
draw new
```

### `quote`
Random motivational quote.

```bash
quote
```

### `joke`
Random programming joke.

```bash
joke
```

### `cowsay [text]`
Cow says your text.

```bash
cowsay Moo!
```

### `history`
Show command history.

```bash
history
```

### `alias [name] [command]`
Create command alias.

```bash
alias ll=ls -la
alias gp=git push
unalias ll
```

### `dice`
Roll a dice.

```bash
dice
```

### `flip`
Flip a coin.

```bash
flip
```

### `search [pattern] [directory]`
Recursive file search.

```bash
search "*.py" /sd
```

---

## OLED Commands

### `oled [mode]`
Control OLED display.

```bash
oled                # Show help pages
oled 1              # Page 1 (modes 1-15)
oled 2              # Page 2 (modes 16-30)
oled 3              # Page 3 (modes 31-43)
oled 4              # Page 4 (modes 44-50)
```

### OLED Modes (50 total)

#### Info Modes
| Mode | Description |
|------|-------------|
| `oled status` | RAM bar + name |
| `oled ram` | Detailed RAM info |
| `oled flash` | Flash storage |
| `oled info` | System info |
| `oled text [s]` | Display custom text |

#### Classic Animations
| Mode | Description |
|------|-------------|
| `oled dvd` | DVD logo bounce |
| `oled wave` | Sine wave |
| `oled clock` | Digital clock |
| `oled bounce` | Bouncing ball |
| `oled rain` | Rain drops |
| `oled fireworks` | Particle explosions |
| `oled starfield` | Moving stars |
| `oled plasma` | Plasma effect |

#### Advanced Animations
| Mode | Description |
|------|-------------|
| `oled matrix` | Matrix rain |
| `oled fire` | Fire effect |
| `oled dna` | DNA helix |
| `oled equalizer` | Audio bars |
| `oled pong` | Mini pong |
| `oled lava` | Lava lamp |
| `oled sparkle` | Twinkling stars |
| `oled pulse` | Expanding rings |
| `oled cube` | Rotating 3D cube |
| `oled textscroll` | Star Wars crawl |
| `oled minisnake` | Playable snake |
| `oled heart` | Beating heart |
| `oled invader` | Space invader |
| `oled spiral` | Rotating spiral |
| `oled boot` | Fake boot sequence |

#### Extra Animations
| Mode | Description |
|------|-------------|
| `oled glitch` | Glitch effect |
| `oled disco` | Disco mode |
| `oled binary` | Binary rain |
| `oled eye` | Watching eye |
| `oled checker` | Checkerboard |
| `oled lightning` | Lightning bolts |
| `oled helplogo` | Bouncing HELP |
| `oled skull` | ASCII skull |
| `oled cat` | ASCII cat |
| `oled dance` | Dancing stick figure |
| `oled doom` | DOOM zoom |
| `oled potato` | potato. |
| `oled stopwatch` | Count-up timer |
| `oled random` | Random (no repeats) |

#### Fun Animations
| Mode | Description |
|------|-------------|
| `oled chicken` | Walking chicken |
| `oled esp32` | Spinning ESP32 |
| `oled pacman` | Pac-Man eating dots |
| `oled tunnel` | Shrinking tunnel |
| `oled typewriter` | Typewriter text |
| `oled radar` | Sweeping radar |
| `oled tetrisfall` | Falling tetris blocks |
| `oled firefly` | Blinking fireflies |
| `oled spectrum` | Fake spectrum analyzer |
| `oled osnake` | Snake with score (auto) |

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel / clear line |
| `Ctrl+L` | Clear screen + OLED |
| `Ctrl+U` | Clear input line |
| `Ctrl+A` | Clear input line |
| `Ctrl+3` | Stealth mode (all screens off) |
| `Ctrl+B` | Toggle backlight |
| `Ctrl+T` | Cycle color theme |
| `Ctrl+O` | Toggle OLED on/off |
| `Ctrl+R` | Reboot device |
| `Ctrl+F` | Show free RAM |
| `Tab` | Auto-complete |
| `Up/PgUp` | Previous command |
| `Down/PgDn` | Next command |

### Nano Editor Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+E` | Move cursor up |
| `Ctrl+D` | Move cursor down |
| `Ctrl+S` | Move cursor left |
| `Ctrl+F` | Move cursor right |
| `Ctrl+A` | Jump to start of line |
| `Ctrl+W` | Jump to end of line |
| `Ctrl+G` | Jump to first line |
| `Ctrl+L` | Jump to last line |
| `Ctrl+K` | Delete line |
| `Ctrl+U` | Delete char at cursor |
| `Ctrl+O` | Save without exiting |
| `Ctrl+H` | Redraw screen |
| `Ctrl+X` | Find/search text |
| `Ctrl+R` | Find & replace |
| `ESC` | Save & exit |
