# Libraries Reference

API documentation for Espelt32 library modules.

## Table of Contents

- [Display Drivers](#display-drivers)
- [Calculator](#calculator)
- [Physics Engine](#physics-engine)
- [OLED Controller](#oled-controller)
- [Keyboard](#keyboard)
- [Other Libraries](#other-libraries)

---

## Display Drivers

### `lib/ili9488.py` - TFT Display Driver

ILI9488 TFT display driver for 480x320 displays over SPI.

#### Constructor

```python
from lib.ili9488 import ILI9488
from machine import Pin, SPI

spi = SPI(1, baudrate=40000000, polarity=0, phase=0,
          sck=Pin(23), mosi=Pin(6))
tft = ILI9488(spi, cs=Pin(26), dc=Pin(27), rst=Pin(4))
```

#### Methods

| Method | Description |
|--------|-------------|
| `fill(color)` | Fill entire screen with color |
| `fill_rect(x, y, w, h, color)` | Fill rectangle |
| `pixel(x, y, color)` | Set single pixel |
| `hline(x, y, w, color)` | Draw horizontal line |
| `vline(x, y, h, color)` | Draw vertical line |
| `rect(x, y, w, h, color)` | Draw rectangle outline |
| `text(s, x, y, color, bg, scale)` | Draw 8x8 text |
| `text15(s, x, y, color, bg)` | Draw 12x14 text (main UI) |
| `text8(s, x, y, color, bg)` | Draw 8x10 text (small) |
| `blit_bitmap(buf, x, y, w, h)` | Draw bitmap buffer |

#### Color Format

RGB565 16-bit color:

```python
color565(r, g, b)  # Create color from RGB

# Common colors
BLACK   = 0x0000
WHITE   = 0xFFFF
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
CYAN    = 0x07FF
YELLOW  = 0xFFE0
ORANGE  = 0xFD20
```

#### Example

```python
tft.fill(0x0000)                    # Clear to black
tft.fill_rect(10, 10, 100, 50, 0x07FF)  # Cyan rectangle
tft.text15('Hello', 10, 10, 0xFFFF, 0x0000)  # White text
tft.hline(0, 160, 480, 0xFF00)     # Yellow line
```

---

### `lib/ssd1306.py` - OLED Display Driver

SSD1306 OLED display driver for 128x64 I2C displays.

#### Constructor

```python
from lib.ssd1306 import SSD1306
from machine import I2C

i2c = I2C(0, freq=400000)
oled = SSD1306(128, 64, i2c)
```

#### Methods

| Method | Description |
|--------|-------------|
| `fill(color)` | Fill display (0 or 1) |
| `pixel(x, y, color)` | Set pixel |
| `text(string, x, y)` | Draw text |
| `show()` | Update display |
| `fill_rect(x, y, w, h, color)` | Fill rectangle |
| `hline(x, y, w, color)` | Horizontal line |
| `vline(x, y, h, color)` | Vertical line |
| `invert(color)` | Invert display |
| `contrast(contrast)` | Set contrast (0-255) |
| `poweroff()` | Turn off display |
| `poweron()` | Turn on display |

#### Example

```python
oled.fill(0)              # Clear
oled.text('Hello', 0, 0)  # Draw text
oled.show()               # Update
```

---

### `lib/oled_ctrl.py` - OLED Controller

High-level OLED controller with 50+ animations.

#### Constructor

```python
from lib.oled_ctrl import OLEDController

oled = OLEDController()
```

#### Methods

| Method | Description |
|--------|-------------|
| `run()` | Start animation loop (blocking) |
| `set_mode(mode, **kwargs)` | Switch animation mode |
| `screen_on()` | Turn OLED on |
| `screen_off()` | Turn OLED off |

#### Modes

```python
oled.set_mode('status')     # System status
oled.set_mode('matrix')     # Matrix rain
oled.set_mode('fire')       # Fire effect
oled.set_mode('clock')      # Digital clock
oled.set_mode('pong')       # Mini pong game
oled.set_mode('stopwatch')  # Stopwatch
oled.set_mode('text', text='Hello')  # Custom text
oled.set_mode('random')     # Random animation
```

#### Threading

The OLED controller runs on Core 1 in a separate thread:

```python
import _thread

def oled_loop():
    oled.run()

_thread.start_new_thread(oled_loop, ())
```

---

## Calculator

### `lib/calc_engine.py` - Calculator Engine

Full-featured calculator with trigonometry, statistics, and matrices.

#### Functions

```python
from lib.calc_engine import calc

calc('2+2')           # Basic arithmetic
calc('10*5-3')        # Order of operations
calc('sin(45)')       # Trigonometry (degrees)
calc('cos(0)')
calc('tan(30)')
calc('sqrt(144)')     # Square root
calc('log(100)')      # Logarithm (base 10)
calc('ln(2.718)')     # Natural log
calc('factorial(5)')  # Factorial
calc('abs(-5)')       # Absolute value
calc('pi')            # Pi constant
calc('e')             # Euler's number
```

#### Statistics

```python
calc('mean(1,2,3,4,5)')    # Mean
calc('median(1,2,3,4,5)')  # Median
calc('std(1,2,3,4,5)')     # Standard deviation
calc('var(1,2,3,4,5)')     # Variance
```

#### Matrices

```python
calc('[[1,2],[3,4]]')       # 2x2 matrix
calc('det([[1,2],[3,4]])')   # Determinant
calc('inv([[1,2],[3,4]])')   # Inverse
calc('T([[1,2],[3,4]])')     # Transpose
```

---

### `lib/cas_engine.py` - Computer Algebra System

Symbolic mathematics engine.

#### Functions

```python
from lib.cas_engine import simplify, expand, factor

simplify('x + x')           # 2*x
expand('(x+1)^2')           # x^2 + 2*x + 1
factor('x^2 - 1')           # (x-1)*(x+1)
factor('x^2 + 2*x + 1')     # (x+1)^2
```

#### Calculus

```python
from lib.cas_engine import diff, integrate

diff('x^2', 'x')            # 2*x
diff('sin(x)', 'x')          # cos(x)
diff('e^x', 'x')             # e^x
integrate('x', 'x')          # x^2/2
integrate('sin(x)', 'x')     # -cos(x)
```

#### Equation Solving

```python
from lib.cas_engine import solve

solve('x + 2 = 5', 'x')     # x = 3
solve('x^2 = 4', 'x')       # x = 2, -2
solve('2*x + 1 = 7', 'x')   # x = 3
```

---

### `lib/calc_graph.py` - Function Graphing

Graph functions on OLED display.

```python
from lib.calc_graph import graph_function

graph_function('sin(x)')     # Plot sine wave
graph_function('x^2')        # Plot parabola
```

---

### `lib/calc_renderer.py` - Calculator Display

Renders calculator output on TFT display.

Supports:
- Fractions
- Integrals
- Sums
- Matrices
- Mathematical notation

---

### `lib/calc_buffer.py` - Math Buffer

Tree-based buffer for visual equation editing.

---

### `lib/calc_input.py` - Calculator Input

Keyboard input handler for calculator mode.

---

### `lib/calc_session.py` - Calculator History

Persists calculator history and memory to `/.data/`.

---

### `lib/calc_help.py` - Calculator Help

319 lines of help topics for the calculator.

```bash
help math            # List all topics
help math basic      # Basic operations
help math trig       # Trigonometry
help math calc       # Calculus
help math algebra    # Algebra
help math fractions  # Fractions
help math matrices   # Matrices
```

---

## Physics Engine

### `lib/physics_engine.py` - Physics Solver

Solves physics problems across multiple domains.

#### Topics

```python
from lib.physics_engine import physics

# Kinematics
physics('kinematics', v0=0, a=9.8, t=5)    # Final velocity

# Dynamics
physics('dynamics', m=10, F=100)            # Acceleration

# Energy
physics('energy', m=5, v=10)                # Kinetic energy

# Waves
physics('waves', f=440, l=0.77)             # Wave speed

# Thermo
physics('thermo', Q=1000, m=2, c=4186)     # Temperature change

# Optics
physics('optics', f=0.1, do=0.2)           # Image distance

# Electromagnetism
physics('em', q=1.6e-19, v=1e6, B=0.1)    # Magnetic force
```

### `lib/physics_renderer.py` - Physics UI

Renders physics formulas and results on TFT display.

---

## Keyboard

### `lib/keyboard.py` - USB HID Keyboard

Maps USB HID key codes to characters.

#### Functions

```python
from lib.keyboard import hid_to_char

char = hid_to_char(report)  # Convert HID report to char
```

#### Modifier Support

Supports:
- Shift (uppercase, symbols)
- Ctrl (shortcuts)
- Alt
- Caps Lock

---

## Other Libraries

### `lib/jpegdec.py` - JPEG Decoder

Pure-MicroPython JPEG decoder.

```python
from lib.jpegdec import decode_jpeg

# Decode JPEG to RGB565 buffer
buf = decode_jpeg('image.jpg')
tft.blit_bitmap(buf, 0, 0, width, height)
```

### `lib/ota_server.py` - OTA Server

HTTP server for over-the-air updates.

```python
from lib.ota_server import start_ota_server

start_ota_server(port=80)
# Upload .py files via browser
```

### `lib/system_monitor.py` - System Monitor

Displays system info on OLED.

```python
from lib.system_monitor import show_status

show_status(oled)  # RAM, flash usage
```

### `lib/calc_engine.py` - Calculator

Full calculator with CAS mode.

### `lib/physics_engine.py` - Physics

Physics formulas and calculations.
