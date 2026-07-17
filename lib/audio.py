"""I2S audio output via MAX98357A DAC+amp."""
import time
from machine import Pin

# MAX98357A pins
_I2S_BCLK = 22
_I2S_WS = 21
_I2S_SD = 20
_PA_CTRL = 53


class AudioPlayer:
    """I2S speaker output via MAX98357A."""

    def __init__(self):
        self._i2s = None
        self._pa = Pin(_PA_CTRL, Pin.OUT, value=0)
        self._volume = 30
        self._available = False

        try:
            from machine import I2S
            self._I2S = I2S
            self._init_i2s()
            self._available = True
            self._pa.value(1)
        except:
            pass

    def _init_i2s(self, rate=48000, bits=16):
        if self._i2s:
            try:
                self._i2s.deinit()
            except:
                pass
        self._i2s = self._I2S(
            0,
            sck=Pin(_I2S_BCLK),
            ws=Pin(_I2S_WS),
            sd=Pin(_I2S_SD),
            mode=self._I2S.TX,
            bits=bits,
            format=self._I2S.MONO,
            rate=rate,
            ibuf=4096
        )

    @property
    def available(self):
        return self._available

    def set_volume(self, vol):
        self._volume = max(0, min(100, vol))

    def tone(self, freq=1000, duration_ms=100):
        if not self._available or freq <= 0 or self._volume == 0:
            return
        self._pa.value(1)
        import math
        sample_rate = 16000
        amplitude = int(8000 * self._volume / 100)

        period_samples = sample_rate // freq if freq > 0 else sample_rate
        if period_samples < 4:
            period_samples = 4

        period = bytearray(period_samples * 2)
        for i in range(period_samples):
            val = int(amplitude * math.sin(2 * math.pi * i / period_samples))
            period[i * 2] = val & 0xFF
            period[i * 2 + 1] = (val >> 8) & 0xFF

        total_samples = sample_rate * duration_ms // 1000
        repeats = total_samples // period_samples

        chunk = bytes(period)
        for _ in range(repeats):
            self._i2s.write(chunk)

    def piano_note(self, freq=440, duration_ms=300):
        if not self._available or freq <= 0 or self._volume == 0:
            return
        self._pa.value(1)
        import math
        sample_rate = 16000
        amplitude = int(7000 * self._volume / 100)
        total_samples = sample_rate * duration_ms // 1000

        attack = min(total_samples // 4, sample_rate * 30 // 1000)
        decay = min(total_samples // 6, sample_rate * 50 // 1000)
        sustain_level = 0.6
        release = min(total_samples // 4, sample_rate * 80 // 1000)
        sustain_start = attack + decay
        release_start = total_samples - release

        buf = bytearray(total_samples * 2)
        for i in range(total_samples):
            if i < attack:
                env = i / attack
            elif i < sustain_start:
                env = 1.0 - (1.0 - sustain_level) * ((i - attack) / decay)
            elif i < release_start:
                env = sustain_level
            else:
                env = sustain_level * (1.0 - (i - release_start) / release)

            t = i / sample_rate
            val = math.sin(2 * math.pi * freq * t)
            val += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            val += 0.15 * math.sin(2 * math.pi * freq * 3 * t)
            val += 0.08 * math.sin(2 * math.pi * freq * 4 * t)
            val *= env * amplitude
            sample = int(max(-32768, min(32767, val)))
            buf[i * 2] = sample & 0xFF
            buf[i * 2 + 1] = (sample >> 8) & 0xFF

        chunk_size = 4096
        pos = 0
        while pos < len(buf):
            end = min(pos + chunk_size, len(buf))
            self._i2s.write(buf[pos:end])
            pos = end

    def beep(self, duration_ms=50):
        self.tone(1000, duration_ms)

    def score_beep(self):
        self.tone(880, 25)

    def game_over_sound(self):
        self.tone(220, 150)
        time.sleep_ms(50)
        self.tone(165, 200)

    def level_up_sound(self):
        self.tone(523, 40)
        time.sleep_ms(20)
        self.tone(659, 40)
        time.sleep_ms(20)
        self.tone(784, 60)

    def alarm(self):
        for _ in range(3):
            self.tone(1000, 100)
            time.sleep_ms(20)
            self.tone(800, 100)
            time.sleep_ms(20)

    def play_sequence(self, notes):
        for freq, dur in notes:
            if freq > 0:
                self.tone(freq, min(dur, 80))
            else:
                time.sleep_ms(min(dur, 50))

    def play_pcm(self, data, sample_rate=48000, bits=16):
        if not self._available or self._volume == 0:
            return
        self._pa.value(1)
        try:
            self._init_i2s(sample_rate, bits)
            chunk = 4096
            pos = 0
            while pos < len(data):
                end = min(pos + chunk, len(data))
                self._i2s.write(data[pos:end])
                pos = end
        except:
            pass

    def play_wav(self, path, callback=None, stop_check=None):
        if not self._available or self._volume == 0:
            return False
        try:
            with open(path, 'rb') as f:
                riff = f.read(4)
                if riff != b'RIFF':
                    return False
                f.read(4)
                wave = f.read(4)
                if wave != b'WAVE':
                    return False

                channels = 1
                sample_rate = 48000
                bits = 16
                data_size = 0
                found_data = False

                while True:
                    chunk_hdr = f.read(8)
                    if len(chunk_hdr) < 8:
                        break
                    chunk_id = chunk_hdr[:4]
                    chunk_len = int.from_bytes(chunk_hdr[4:8], 'little')

                    if chunk_id == b'fmt ':
                        fmt = f.read(min(chunk_len, 16))
                        if len(fmt) >= 16:
                            channels = fmt[2]
                            sample_rate = int.from_bytes(fmt[4:8], 'little')
                            bits = fmt[14]
                        if chunk_len > 16:
                            f.read(chunk_len - 16)
                    elif chunk_id == b'data':
                        data_size = chunk_len
                        found_data = True
                        break
                    else:
                        f.read(chunk_len)
                        if chunk_len & 1:
                            f.read(1)

                if not found_data or data_size == 0:
                    return False

                self._pa.value(1)
                self._init_i2s(sample_rate, bits)

                chunk_size = 4096
                bytes_read = 0
                while bytes_read < data_size:
                    if stop_check and stop_check():
                        self._i2s.deinit()
                        return False
                    to_read = min(chunk_size, data_size - bytes_read)
                    data = f.read(to_read)
                    if not data:
                        break
                    if bits == 8:
                        buf = bytearray(len(data) * 2)
                        for i in range(len(data)):
                            val = (data[i] - 128) * 256
                            buf[i * 2] = val & 0xFF
                            buf[i * 2 + 1] = (val >> 8) & 0xFF
                        self._i2s.write(buf)
                    else:
                        self._i2s.write(data)
                    bytes_read += to_read
                    if callback:
                        callback(bytes_read, data_size)
                return True
        except:
            return False

    def get_mic_level(self):
        return 0

    def off(self):
        self._pa.value(0)
