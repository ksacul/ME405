# line_sensor.py
# Pololu QTR-MD-07A (7ch, Analog Output) reflectance sensor array driver (MicroPython)

from pyb import Pin, ADC
from utime import sleep_us, sleep_ms

class QTRMD07A_Analog:
    """
    QTR-MD-07A analog array driver.
    Reads 7 ADC channels and provides:
      - raw readings
      - optional white/black calibration
      - normalized readings (0=white, 1=black)
      - centroid position (default positions 1..13 odd)

    Typical behavior for this sensor:
      - strong reflectance (white) -> LOWER voltage -> LOWER ADC
      - weak reflectance (black)   -> HIGHER voltage -> HIGHER ADC
    """

    def __init__(self,
                 pins=(Pin.cpu.B0, Pin.cpu.C3, Pin.cpu.C2, Pin.cpu.C4,
                       Pin.cpu.A5, Pin.cpu.A6, Pin.cpu.A7),
                 positions=(1, 3, 5, 7, 9, 11, 13),
                 oversample=1,
                 ctrl_odd=None,
                 ctrl_even=None):

        if len(pins) != 7:
            raise ValueError("QTRMD07A_Analog expects 7 ADC pins")

        self._pins = pins
        self._adcs = [ADC(Pin(p)) for p in pins]
        self._n = 7

        self._pos = tuple(positions)
        if len(self._pos) != 7:
            raise ValueError("positions must be length 7")

        self._os = max(1, int(oversample))

        # Calibration endpoints per channel (ADC counts)
        self._white = [4095.0] * self._n
        self._black = [0.0]    * self._n
        self._has_white = False
        self._has_black = False

        self._last_centroid = (self._pos[0] + self._pos[-1]) / 2

        # Optional emitter control pins (only if you wired CTRL ODD/EVEN)
        self._ctrl_odd = Pin(ctrl_odd, Pin.OUT_PP) if ctrl_odd else None
        self._ctrl_even = Pin(ctrl_even, Pin.OUT_PP) if ctrl_even else None
        if self._ctrl_odd:
            self._ctrl_odd.high()
        if self._ctrl_even:
            self._ctrl_even.high()

    def read_raw(self):
        """Return list of 7 raw ADC readings (0..4095)."""
        vals = [0.0] * self._n
        for i, adc in enumerate(self._adcs):
            acc = 0
            for _ in range(self._os):
                acc += adc.read()
                sleep_us(5)
            vals[i] = acc / self._os
        return vals

    def calibrate_white(self, samples=50, delay_ms=5):
        """Place sensors over WHITE/background and call this."""
        samples = max(1, int(samples))
        acc = [0.0] * self._n
        for _ in range(samples):
            r = self.read_raw()
            for i in range(self._n):
                acc[i] += r[i]
            sleep_ms(delay_ms)
        self._white = [acc[i] / samples for i in range(self._n)]
        self._has_white = True
        return self._white

    def calibrate_black(self, samples=50, delay_ms=5):
        """Place sensors over BLACK line and call this."""
        samples = max(1, int(samples))
        acc = [0.0] * self._n
        for _ in range(samples):
            r = self.read_raw()
            for i in range(self._n):
                acc[i] += r[i]
            sleep_ms(delay_ms)
        self._black = [acc[i] / samples for i in range(self._n)]
        self._has_black = True
        return self._black

    def read_normalized(self, clip=True):
        """
        Normalize to ~[0,1] using:
            x = (raw - white) / (black - white)
        so 0~white, 1~black.
        If not calibrated yet, returns raw/4095.
        """
        raw = self.read_raw()

        if not (self._has_white and self._has_black):
            return [v / 4095.0 for v in raw]

        out = [0.0] * self._n
        for i in range(self._n):
            denom = (self._black[i] - self._white[i])
            if abs(denom) < 1e-6:
                x = 0.0
            else:
                x = (raw[i] - self._white[i]) / denom

            if clip:
                if x < 0.0:
                    x = 0.0
                elif x > 1.0:
                    x = 1.0
            out[i] = x
        return out

    def centroid(self, normalized=None, min_sum=0.05):
        """
        Weighted centroid of the normalized "blackness" profile.

        Returns centroid in units of positions (default 1..13).
        If the line is "lost" (sum small), returns last centroid.
        """
        if normalized is None:
            normalized = self.read_normalized()

        s = 0.0
        ws = 0.0
        for x, p in zip(normalized, self._pos):
            s += x
            ws += x * p

        if s < float(min_sum):
            return self._last_centroid

        c = ws / s
        self._last_centroid = c
        return c

    def error(self, center=7.0, normalized=None):
        """Convenience: centroid error around the center sensor position."""
        return self.centroid(normalized=normalized) - float(center)

    def emitters_on(self):
        """Turn emitters on (only if CTRL pins wired)."""
        if self._ctrl_odd:
            self._ctrl_odd.high()
        if self._ctrl_even:
            self._ctrl_even.high()

    def emitters_off(self):
        """Turn emitters off (only if CTRL pins wired)."""
        if self._ctrl_odd:
            self._ctrl_odd.low()
        if self._ctrl_even:
            self._ctrl_even.low()
        sleep_ms(2)

    def __repr__(self):
        return "QTRMD07A_Analog(pins={}, oversample={})".format(self._pins, self._os)