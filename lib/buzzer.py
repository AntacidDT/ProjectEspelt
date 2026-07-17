"""Audio output via I2S speaker (MAX98357A)."""
import time

try:
    from lib.audio import AudioPlayer as _AudioPlayer
    _audio_available = True
except:
    _audio_available = False


class Buzzer:
    def __init__(self, pin=20):
        self._volume = 30
        self._audio = None

        if _audio_available:
            try:
                self._audio = _AudioPlayer()
                if self._audio.available:
                    self._audio.set_volume(self._volume)
            except:
                pass

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, val):
        self._volume = max(0, min(100, val))
        if self._audio and self._audio.available:
            self._audio.set_volume(self._volume)

    def tone(self, freq=1000, duration_ms=100):
        if self._volume == 0 or freq <= 0:
            return
        if self._audio and self._audio.available:
            self._audio.tone(freq, duration_ms)

    def beep(self, duration_ms=50):
        self.tone(1000, duration_ms)

    def off(self):
        if self._audio and self._audio.available:
            self._audio.off()

    def score_beep(self):
        self.tone(880, 25)

    def game_over_sound(self):
        self.tone(220, 150)
        self.tone(165, 200)

    def level_up_sound(self):
        self.tone(523, 40)
        self.tone(659, 40)
        self.tone(784, 60)

    def alarm(self):
        for _ in range(3):
            self.tone(1000, 100)
            self.tone(800, 100)

    def play_sequence(self, notes):
        for freq, dur in notes:
            if freq > 0:
                self.tone(freq, min(dur, 80))
            else:
                time.sleep_ms(min(dur, 50))

    def play_pcm(self, data, sample_rate=48000, bits=16):
        if self._audio and self._audio.available:
            self._audio.play_pcm(data, sample_rate, bits)

    def play_wav(self, path, callback=None):
        if self._audio and self._audio.available:
            self._audio.play_wav(path, callback)
