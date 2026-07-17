# Hardware Setup

## Board: Waveshare ESP32-P4 Nano

- **MCU**: ESP32-P4 (dual-core, 32MB PSRAM)
- **WiFi**: ESP32-C6 coprocessor
- **Storage**: Internal flash + SD card slot

## Pin Assignments

### TFT Display (ILI9488)

| Signal | GPIO | Notes |
|--------|------|-------|
| SCK | 23 | SPI clock |
| MOSI | 6 | SPI data |
| CS | 26 | Chip select |
| DC | 27 | Data/Command |
| RST | 4 | Reset |
| BLK | 5 | Backlight (PWM) |

**SPI Config**: 40MHz, Mode 0 (CPOL=0, CPHA=0)

### OLED Display (SSD1306)

| Signal | GPIO | Notes |
|--------|------|-------|
| SDA | I2C | Default I2C SDA |
| SCL | I2C | Default I2C SCL |

**I2C Config**: 400kHz

### USB Host

- Uses ESP32-P4 built-in USB host
- Module: `usb_host` (MicroPython built-in)
- Supports HID keyboards

### SD Card

- Auto-mounted at `/sd` in `boot.py`
- Uses `machine.SDCard()` default pins

## Wiring Diagram

```
ESP32-P4 Nano
┌─────────────────────────────────┐
│                                 │
│  ┌─────────────────────────┐   │
│  │     ILI9488 TFT         │   │
│  │  SCK ← GPIO 23          │   │
│  │  MOSI ← GPIO 6          │   │
│  │  CS ← GPIO 26           │   │
│  │  DC ← GPIO 27           │   │
│  │  RST ← GPIO 4           │   │
│  │  BLK ← GPIO 5 (PWM)     │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │     SSD1306 OLED        │   │
│  │  SDA ← I2C SDA          │   │
│  │  SCL ← I2C SCL          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │     USB Host            │   │
│  │  USB-A connector        │   │
│  │  (keyboard input)       │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │     SD Card Slot        │   │
│  │  (auto-mounted /sd)     │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

## Power Requirements

- **USB-C**: 5V/2A recommended
- **TFT Backlight**: PWM controlled (GPIO 5)
- **OLED**: Powered via I2C (3.3V)

## Display Specifications

### ILI9488 TFT

- **Resolution**: 480x320 pixels
- **Color**: 16-bit (RGB565) / 18-bit (RGB666)
- **Interface**: SPI
- **Refresh Rate**: ~30 FPS (depends on content)
- **Text Sizes**: 8x10 (text8), 12x14 (text15)

### SSD1306 OLED

- **Resolution**: 128x64 pixels
- **Color**: Monochrome (white/blue)
- **Interface**: I2C
- **Refresh Rate**: ~60 FPS
- **Animations**: 50+ built-in

## Troubleshooting

### Display not working

1. Check SPI/I2C connections
2. Verify GPIO pins match code
3. Ensure 3.3V power supply is stable
4. Try lowering SPI speed in code

### Keyboard not detected

1. Ensure USB keyboard is plugged in before boot
2. Check if `usb_host` module is available
3. Try a different USB keyboard

### SD card not mounting

1. Format SD card as FAT32
2. Insert card before boot
3. Check card is not write-protected
