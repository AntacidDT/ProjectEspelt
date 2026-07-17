# Project Espelt32

A MicroPython cyberdeck firmware for the **Waveshare ESP32-P4 Nano**.

## Overview

Espelt32 is a feature-rich command-line operating system for ESP32-P4, featuring a TFT touchscreen display, OLED status screen, USB keyboard input, and 100+ built-in commands.

### Key Features

- **TFT Display**: 480x320 ILI9488 with 4 color themes
- **OLED Display**: 128x64 SSD1306 with 50+ animations (runs on Core 1)
- **USB Keyboard**: Full HID keyboard support with shortcuts
- **SD Card**: Auto-mounted at `/sd`
- **WiFi**: ESP32-C6 coprocessor
- **WebREPL**: Remote access via browser
- **OTA Updates**: Upload firmware over WiFi

## Quick Start

### Prerequisites

- ESP32-P4 Nano (Waveshare)
- MicroPython firmware
- USB keyboard
- ILI9488 TFT display
- SSD1306 OLED display
- SD card (optional)

### Installation

1. Flash MicroPython to ESP32-P4
2. Upload all project files via WebREPL or serial
3. Reboot the device

### First Boot

```bash
# Connect to WebREPL
ws://<device-ip>:8266
Password: espelt2024

# Connect to WiFi
wlan MyWiFi MyPassword

# Start exploring
help
```

## Project Structure

```
Espelt32/
├── main.py              # Main entry point, REPL loop
├── boot.py              # Boot script (SD mount, WebREPL)
├── commands/            # Command modules
│   ├── dispatch.py      # Command router
│   ├── systemcmd.py     # System commands
│   ├── essentialcmd.py  # Games & core features
│   ├── apicmd.py        # Network/API commands
│   └── utilcmd.py       # Utility commands
├── lib/                 # Library modules
│   ├── ili9488.py       # TFT display driver
│   ├── ssd1306.py       # OLED display driver
│   ├── oled_ctrl.py     # OLED controller (50 animations)
│   ├── keyboard.py      # USB HID keyboard mapping
│   ├── calc_engine.py   # Calculator engine
│   ├── cas_engine.py    # Computer Algebra System
│   ├── physics_engine.py # Physics solver
│   └── ...              # More libraries
└── docs/                # This documentation
```

## Command Categories

| Category | Count | Examples |
|----------|-------|----------|
| System | 12 | `clock`, `info`, `sleep`, `reboot` |
| Files | 10 | `ls`, `cat`, `nano`, `fm` |
| Network | 20 | `wlan`, `wiki`, `weather`, `translate` |
| Games | 29 | `snake`, `tetris`, `2048`, `chess` |
| Math | 4 | `math`, `physics`, `convert`, `base` |
| Utilities | 25+ | `todo`, `notes`, `timer`, `encrypt` |
| OLED | 50 | `oled matrix`, `oled fire`, `oled pong` |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel / clear line |
| `Ctrl+L` | Clear screen |
| `Ctrl+3` | Stealth mode (all screens off) |
| `Ctrl+B` | Toggle backlight |
| `Ctrl+T` | Cycle color theme |
| `Ctrl+R` | Reboot |
| `Tab` | Auto-complete |
| `Up/Down` | Command history |

## Color Themes

- **default**: Cyan accent
- **warm**: Orange accent
- **cyber**: Blue accent
- **forest**: Green accent

## Documentation

- [Hardware Setup](HARDWARE.md) - Pinout and wiring
- [Commands Reference](COMMANDS.md) - All 100+ commands
- [Libraries](LIBRARIES.md) - API documentation
- [Development Guide](DEVELOPMENT.md) - Contributing

## License

Educational project. Use at your own risk.
