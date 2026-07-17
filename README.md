# Project Espelt

A portable cyberdeck OS for the **ESP32-P4 Nano** (Waveshare). Dual-screen REPL with 380+ commands, 50 games, 7 academic engines, and 55+ OLED animations — all on MicroPython.

**Stats:** 380 commands | 22 engines | 50 games | 55+ OLED animations | 4 themes

## Hardware

| Component | Details |
|-----------|---------|
| **MCU** | ESP32-P4 Nano — 32MB PSRAM, dual-core, WiFi via C6 coprocessor |
| **TFT** | 3.5" ILI9488 — 480x320, 20MHz SPI, PWM brightness (GPIO5) |
| **OLED** | 2.42" SSD1306 — 128x64, I2C 400kHz, runs on Core 1 |
| **Input** | USB-A keyboard (HID, custom USB-Host firmware) |
| **Audio** | Piezo buzzer on GPIO20 (bit-banged, school-compliant) |
| **Storage** | SD card auto-mounted at `/sd` |
| **Power** | USB power bank |

### Pin Layout

```
TFT (ILI9488):  CS=GPIO26  DC=GPIO27  RST=GPIO4  MOSI=GPIO6  SCK=GPIO23  LED=GPIO5
OLED (SSD1306): SCL=GPIO8  SDA=GPIO7  (addr 0x3C)
Buzzer:         GPIO20
SD Card:        CLK=39  CMD=40  D0-D3=41-44  CD=45
```

## Quick Start

```bash
# Flash MicroPython to ESP32-P4, then upload files via WebREPL or serial
# Connect to WebREPL: ws://<device-ip>:8266  (password: espelt2024)

wlan MyWiFi MyPassword   # Connect to WiFi
help                      # List all commands
help system               # Category help
```

## Features

### Calculator (90+ functions)
Scientific calculator with CAS (symbolic diff, solve, factor, expand, simplify). Complex numbers, matrices, lists & regression (L1-L6), numerical integration/differentiation, statistical distributions, hypothesis tests, OLED graphing, memory (Ans, L1-L6).

### Chemistry Engine (118 elements)
Periodic table, molar mass, pH, gas laws, stoichiometry, thermochemistry, organic chemistry, redox reactions, bonding/Lewis structures, electron configuration, equation balancing, titration calculator.

### Biology Engine
DNA/RNA transcription & translation, amino acids, Punnett squares, Hardy-Weinberg, taxonomy, anatomy (7 organs), body systems (10), cell cycle, mitosis/meiosis, evolution, microbiology, immune system, disease database.

### Physics Engine (82+ formulas, 8 categories)
Mechanics, waves/optics, electricity, thermal, nuclear, relativity, modern physics, physical constants. Variable solver for any unknown.

### Electronics Engine (51 formulas)
Circuit basics, AC circuits, LC resonance, digital logic (7 gates), transistors, op-amp circuits, power supply design. Resistor color code, voltage divider, LED calculator, IC pinouts reference.

### Coding Engine
Syntax-highlighted script editor, base conversion, ASCII table, ciphers (Caesar, Vigenère, ROT13, Morse, Base64), data structures reference, Big-O cheat sheet, regex tester, Python/MicroPython cheatsheet.

### 50 Games
Snake, 2048, Tetris, Flappy, Breakout, Pong (CPU/2P/3D), Minesweeper, Chess (minimax), Blackjack, Mastermind, Nim, Simon, Wordle, Sudoku, Checkers, Othello, Racing, Invaders, Platformer, Tron, Maze3D, Life, and more. All with difficulty system, sprites, particles, incremental rendering, and buzzer sounds.

### 55+ OLED Animations
DVD bounce, wave, clock, rain, fireworks, starfield, plasma, matrix fire, DNA helix, equalizer, lava, sparkle, cube, snake, heart, spiral, disco, radar, spectrum, and more. Utility modes: game HUD, WiFi status, auto (clock + context).

### 38+ Network Commands
Wikipedia, weather, news, stocks, crypto, translate, prayer times, air quality, DNS, speedtest, GitHub API, holidays, RSS feeds, cat/dog facts, trivia, dad jokes, XKCD, quotes, npm/PyPI search, currency exchange, IP info, and more.

### Productivity
Todo list, notes, calendar, alarms, reminders, contacts, paint app (16 colors, flood fill, undo), timer (countdown/pomodoro/stopwatch), file manager, nano editor, command history, backup/restore to SD.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel / clear line |
| `Ctrl+L` | Clear screen |
| `Ctrl+3` | Stealth mode (all screens off) |
| `Ctrl+B` | Toggle backlight |
| `Ctrl+T` | Cycle theme |
| `Ctrl+O` | Toggle OLED |
| `Ctrl+R` | Reboot |
| `Ctrl+F` | Show free RAM |
| `Tab` | Auto-complete |
| `Up/Down` | Command history |

## Themes

| Theme | Accent | Background |
|-------|--------|------------|
| **default** | Cyan | Dark blue |
| **warm** | Orange | Dark red |
| **cyber** | Blue | Black |
| **forest** | Green | Dark green |

## Project Structure

```
boot.py              — SD mount, WebREPL
main.py              — Orchestrator (REPL, rendering, modes, shortcuts)
commands/
  dispatch.py        — Command router + paginated help (~380 commands)
  systemcmd.py       — System commands (calc, clock, chem, bio, code, physics, piano, music, adventure)
  essentialcmd.py    — 50 games, timer, QR, encrypt/decrypt, flags
  apicmd.py          — Network API commands (38+ commands)
  utilcmd.py         — Utility commands (todo, notes, converters, search)
  utilcmd_new.py     — New utilities (draw, calendar, alarm, reminders, contacts, hexdump, timer)
lib/
  ili9488.py         — TFT driver (text15, text8, extended font with Ω, μ, π, √)
  ssd1306.py         — OLED driver
  oled_ctrl.py       — OLED controller (55+ animations, Core 1 thread)
  keyboard.py        — USB HID keyboard handler
  buzzer.py          — Piezo buzzer driver (bit-banged GPIO20)
  calc_engine.py     — Calculator engine (90+ functions, CAS, complex, matrix)
  cas_engine.py      — Computer Algebra System
  chem_engine.py     — Chemistry engine (118 elements)
  bio_engine.py      — Biology engine
  physics_engine.py  — Physics formula engine
  code_engine.py     — Coding engine
  electronics_engine.py — Electronics engine
  music_player.py    — Music player (6 songs)
  adventure_engine.py — Text RPG engine
  chess_engine.py    — Chess vs CPU (minimax)
  *_engine.py        — 22 total engines (7 academic + 15 games)
  sprite.py          — Particle system, 3D bevel, gradient fills
  audio.py           — I2S audio player
  ota_server.py      — OTA update server
flags/               — 47 European country SVG flags
docs/                — Documentation
```

## Design Principles

- **School-safe** — No browser, no speakers, no external connections without explicit command
- **Portable** — Powered by power bank, fits in pocket
- **Offline-first** — Works without WiFi; network features optional
- **REPL-based** — Everything is a command, no GUI complexity
- **Incremental rendering** — Games and animations use partial redraws
- **Modular** — Engines are independent, can be added/removed without breaking others

## Documentation

- [Hardware Setup](docs/HARDWARE.md)
- [Commands Reference](docs/COMMANDS.md)
- [Libraries](docs/LIBRARIES.md)
- [Development Guide](docs/DEVELOPMENT.md)

## License

Educational project. Use at your own risk.
