import micropython
from utime import ticks_us, ticks_diff
from task_share import Share

S0_INIT = micropython.const(0)
S1_RUN = micropython.const(1)

class task_line_follow:
    def __init__(self,
                 enable: Share,
                 base_speed: Share,
                 Kp_line: Share,
                 Ki_line: Share,
                 centroid: Share,
                 setpoint_L: Share,
                 setpoint_R: Share,
                 center=7.0,
                 delta_limit=0.10,
                 line_seen_share: Share = None):
        self._state = S0_INIT
        self._enable = enable
        self._base = base_speed
        self._kp = Kp_line
        self._ki = Ki_line
        self._centroid = centroid
        self._spL = setpoint_L
        self._spR = setpoint_R
        self._center = float(center)
        self._limit = float(delta_limit)
        self._line_seen = line_seen_share
        self._last_t = ticks_us()
        self._I = 0.0

    def run(self):
        while True:
            if self._state == S0_INIT:
                self._last_t = ticks_us()
                self._I = 0.0
                self._state = S1_RUN

            elif self._state == S1_RUN:
                if int(self._enable.get()):
                    now = ticks_us()
                    dt = ticks_diff(now, self._last_t) / 1_000_000.0
                    self._last_t = now
                    if dt <= 0:
                        dt = 1e-3

                    c = float(self._centroid.get())
                    err = c - self._center

                    self._I += err * dt
                    delta = float(self._kp.get()) * err + float(self._ki.get()) * self._I
                    if delta > self._limit:
                        delta = self._limit
                    elif delta < -self._limit:
                        delta = -self._limit

                    base = float(self._base.get())
                    left = base + delta
                    right = base - delta

                    if left < 0.0:
                        left = 0.0
                    if right < 0.0:
                        right = 0.0
                    if left > 0.35:
                        left = 0.35
                    if right > 0.35:
                        right = 0.35

                    self._spL.put(left)
                    self._spR.put(right)
                else:
                    self._I = 0.0
                    self._last_t = ticks_us()

            yield self._state
