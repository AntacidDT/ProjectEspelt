"""Generated sound effects as PCM byte arrays."""
import math


def _gen_tone(freq, duration_ms, sample_rate=48000, volume=20000):
    """Generate a square wave tone."""
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = bytearray(n_samples * 2)
    for i in range(n_samples):
        val = volume if (i * freq * 2 // sample_rate) % 2 == 0 else -volume
        buf[i * 2] = val & 0xFF
        buf[i * 2 + 1] = (val >> 8) & 0xFF
    return buf


def _gen_sine(freq, duration_ms, sample_rate=48000, volume=20000):
    """Generate a sine wave tone."""
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = bytearray(n_samples * 2)
    for i in range(n_samples):
        val = int(volume * math.sin(2 * math.pi * freq * i / sample_rate))
        buf[i * 2] = val & 0xFF
        buf[i * 2 + 1] = (val >> 8) & 0xFF
    return buf


def _gen_silence(duration_ms, sample_rate=48000):
    """Generate silence."""
    n_samples = int(sample_rate * duration_ms / 1000)
    return bytearray(n_samples * 2)


# ── Pre-generated sounds ──

def boot_sound():
    """Boot chime - ascending notes."""
    return (
        _gen_sine(523, 80) +  # C5
        _gen_silence(20) +
        _gen_sine(659, 80) +  # E5
        _gen_silence(20) +
        _gen_sine(784, 120)  # G5
    )


def success_sound():
    """Success chime - happy ascending."""
    return (
        _gen_sine(523, 60) +
        _gen_silence(10) +
        _gen_sine(659, 60) +
        _gen_silence(10) +
        _gen_sine(784, 60) +
        _gen_silence(10) +
        _gen_sine(1047, 100)
    )


def error_sound():
    """Error beep - descending."""
    return (
        _gen_sine(440, 100) +
        _gen_silence(20) +
        _gen_sine(330, 150)
    )


def notification_sound():
    """Notification ping."""
    return (
        _gen_sine(880, 50) +
        _gen_silence(10) +
        _gen_sine(1100, 80)
    )


def key_click():
    """UI key click."""
    return _gen_tone(1200, 15, volume=10000)


def score_sound():
    """Score increase - short high beep."""
    return _gen_sine(1047, 30)


def game_over_sound():
    """Game over - descending minor."""
    return (
        _gen_sine(392, 150) +  # G4
        _gen_silence(30) +
        _gen_sine(330, 150) +  # E4
        _gen_silence(30) +
        _gen_sine(262, 200)   # C4
    )


def level_up_sound():
    """Level up - ascending major."""
    return (
        _gen_sine(523, 50) +  # C5
        _gen_silence(10) +
        _gen_sine(659, 50) +  # E5
        _gen_silence(10) +
        _gen_sine(784, 50) +  # G5
        _gen_silence(10) +
        _gen_sine(1047, 100)  # C6
    )


def alarm_sound():
    """Alarm - alternating tones."""
    buf = bytearray()
    for _ in range(3):
        buf += _gen_sine(1000, 100)
        buf += _gen_silence(20)
        buf += _gen_sine(800, 100)
        buf += _gen_silence(20)
    return buf
