# Development Guide

Guide for contributing to Espelt32.

## Getting Started

### Prerequisites

- ESP32-P4 Nano (Waveshare)
- MicroPython firmware
- PyMakr VS Code extension (recommended)
- USB keyboard
- ILI9488 TFT + SSD1306 OLED

### Development Environment

```bash
# Install PyMakr
code --install-extension pycom.pymakr

# Or use WebREPL
# Connect to ws://<device-ip>:8266
# Password: espelt2024
```

## Project Structure

```
Espelt32/
├── main.py              # Entry point, REPL loop
├── boot.py              # Boot script
├── commands/            # Command modules
│   ├── dispatch.py      # Command router
│   ├── systemcmd.py     # System commands
│   ├── essentialcmd.py  # Games & core
│   ├── apicmd.py        # Network/API
│   └── utilcmd.py       # Utilities
├── lib/                 # Libraries
│   ├── ili9488.py       # TFT driver
│   ├── ssd1306.py       # OLED driver
│   ├── oled_ctrl.py     # OLED controller
│   ├── keyboard.py      # HID keyboard
│   └── ...              # More libs
├── docs/                # Documentation
└── pymakr.conf          # PyMakr config
```

## Adding a New Command

### Step 1: Create Command Function

Add to appropriate file in `commands/`:

```python
# commands/utilcmd.py

def cmd_mycommand(args, tft=None):
    """My new command."""
    if not args:
        return ('print', 'mycommand: usage: mycommand [args]')
    
    # Your logic here
    result = f'  Result: {args}'
    return ('print', result)
```

### Step 2: Register in Dispatch

Add to `commands/dispatch.py`:

```python
# In COMMANDS list
COMMANDS = [
    ...,
    'mycommand',
    ...

# In dispatch function
elif cmd == 'mycommand':
    from commands.utilcmd import cmd_mycommand
    return cmd_mycommand(args, tft)
```

### Step 3: Add Help Text

Add to `cmd_help_screen()` in `dispatch.py`:

```python
'  mycommand      Description of my command',
```

### Step 4: Test

```bash
mycommand test
```

## Command Return Types

Commands return tuples that control UI behavior:

```python
# Print text
return ('print', 'Hello World')

# Print multiple lines
return ('print_lines', ['Line 1', 'Line 2'])

# Clear screen
return ('clear',)

# Run game (pass tft and read_key)
return ('game', my_game_function)

# Open editor
return ('edit', filename, content)

# Open file manager
return ('fm', '/path')

# Cycle theme
return ('theme',)

# Start stopwatch on OLED
return ('stopwatch',)
```

## Adding a New Game

### Step 1: Create Game Function

```python
# commands/essentialcmd.py

def game_mysnake(tft, read_key):
    """My snake game."""
    # Initialize game state
    snake = [(5, 5)]
    food = (10, 10)
    direction = 'right'
    
    while True:
        # Draw game
        tft.fill(0x0000)
        for x, y in snake:
            tft.fill_rect(x*10, y*10, 10, 10, 0x07E0)
        tft.fill_rect(food[0]*10, food[1]*10, 10, 10, 0xF800)
        
        # Get input
        key = read_key(timeout_ms=100)
        if key == '\x1b':  # ESC to quit
            break
        
        # Update game logic
        # ...
    
    return None
```

### Step 2: Register in Games List

```python
# In cmd_games()
'  mysnake        My awesome snake game'

# In dispatch
elif cmd == 'mysnake':
    from commands.essentialcmd import game_mysnake
    return ('game', game_mysnake)
```

## Adding a New Library

### Step 1: Create Library File

```python
# lib/mylib.py

class MyLibrary:
    def __init__(self, param):
        self.param = param
    
    def method(self):
        return self.param
```

### Step 2: Import and Use

```python
# In commands or main.py
from lib.mylib import MyLibrary

lib = MyLibrary(42)
result = lib.method()
```

## Code Style

### Conventions

- **Functions**: `snake_case` for functions, `PascalCase` for classes
- **Variables**: `snake_case`
- **Constants**: `UPPER_CASE`
- **Private**: Leading underscore `_private_func`
- **Imports**: Group by stdlib, lib, commands

### Comments

- Use docstrings for public functions
- Avoid inline comments unless necessary
- Comment complex algorithms only

### Example

```python
def cmd_example(args, tft=None):
    """Example command with proper style."""
    if not args:
        return ('print', 'usage: example [args]')
    
    result = _process_args(args)
    return ('print', f'  {result}')


def _process_args(args):
    """Internal helper function."""
    return args.upper()
```

## Testing

### Manual Testing

```bash
# Upload and run
pymakr upload main.py
pymakr run

# Or via WebREPL
# Upload files, then reboot
```

### Unit Tests

Create test files:

```python
# tests/test_calc.py

from lib.calc_engine import calc

def test_basic():
    assert calc('2+2') == 4

def test_trig():
    assert abs(calc('sin(45)') - 0.707) < 0.01

test_basic()
test_trig()
print('All tests passed!')
```

Run tests:

```bash
python tests/test_calc.py
```

## Deployment

### Using PyMakr

```bash
# Upload all files
pymakr upload

# Upload specific file
pymakr upload main.py

# Run
pymakr run
```

### Using WebREPL

1. Open browser to `ws://<device-ip>:8266`
2. Use upload feature
3. Reboot device

### Using OTA

```bash
# Start OTA server on device
ota

# Open browser to http://<device-ip>
# Upload .py files
```

## Troubleshooting

### Common Issues

**ImportError**: Module not found
- Check file exists in `lib/` or `commands/`
- Check spelling and case

**MemoryError**: Not enough RAM
- Use `gc.collect()` to free memory
- Optimize data structures
- Use generators instead of lists

**Display not updating**
- Check SPI/I2C connections
- Verify GPIO pins
- Try lowering SPI speed

**Keyboard not working**
- Ensure `usb_host` module available
- Try different keyboard
- Check USB connection

### Debugging

```python
# Print to serial
print('Debug:', variable)

# Check memory
import gc
print('Free:', gc.mem_free())

# List files
import os
print(os.listdir('/'))

# Check version
import sys
print(sys.version)
```

## Performance Tips

1. **Use `text15()`** for main UI (fastest)
2. **Batch screen updates** when possible
3. **Use `_thread`** for OLED (Core 1)
4. **Cache colors** and constants
5. **Minimize SPI writes** by buffering

## Security Notes

- WebREPL password is hardcoded: `espelt2024`
- No encryption for WiFi connections
- OTA server has no authentication
- SD card files are unprotected

For production, consider:
- Stronger passwords
- WPA2/WPA3 WiFi
- HTTPS for OTA
- File permissions
