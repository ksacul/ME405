import micropython
from task_share import Share

S0_INIT = micropython.const(0)
S1_RUN = micropython.const(1)


class task_bump:
    """
    Monitors a single front bumper event share.

    bump_mode share values:
      0 = no bump
      1 = front bumper hit
    """

    def __init__(self, bump_event: Share, bump_mode: Share, stop_request: Share):
        self._state = S0_INIT
        self._bump_event = bump_event
        self._bump_mode = bump_mode
        self._stop_request = stop_request

    def run(self):
        while True:
            if self._state == S0_INIT:
                self._bump_mode.put(0)
                self._state = S1_RUN

            elif self._state == S1_RUN:
                event = int(self._bump_event.get())

                if event:
                    self._bump_mode.put(1)
                    self._stop_request.put(1)
                    self._bump_event.put(0)
                else:
                    self._bump_mode.put(0)

            yield self._state
