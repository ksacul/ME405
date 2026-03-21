import micropython
from utime import ticks_us, ticks_diff
from pyb import Pin, USB_VCP
from task_share import Share, Queue
from line_sensor import QTRMD07A_Analog

S0_INIT = micropython.const(0)
S1_RUN  = micropython.const(1)

class task_line_sensor:
    def __init__(self, goFlag: Share, centroid_share: Share,
                 centroidQ: Queue, timeQ: Queue,
                 line_seen_share: Share, oversample=4):

        self._state = S0_INIT
        self._goFlag = goFlag
        self._centroid_share = centroid_share
        self._centroidQ = centroidQ
        self._timeQ = timeQ
        self._line_seen = line_seen_share
        self._ser = USB_VCP()
        self._printed_header = False
        self._qtr = QTRMD07A_Analog(
            pins=(Pin.cpu.B0, Pin.cpu.C3, Pin.cpu.C2, Pin.cpu.C4,
                  Pin.cpu.A5, Pin.cpu.A6, Pin.cpu.A7),
            positions=(1, 3, 5, 7, 9, 11, 13),
            oversample=oversample
        )
        self._startTime = 0

    def run(self):
        while True:
            if self._state == S0_INIT:
                self._startTime = ticks_us()
                self._printed_header = False
                self._state = S1_RUN

            elif self._state == S1_RUN:
                n = self._qtr.read_normalized()
                c = float(self._qtr.centroid(normalized=n))
                self._centroid_share.put(c)
                self._line_seen.put(1 if max(n) > 0.40 else 0)

                mode = int(self._goFlag.get())

                if mode == 1:
                    if not self._printed_header:
                        self._startTime = ticks_us()
                        self._ser.write("t_us,centroid\r\n")
                        self._printed_header = True

                    if (not self._centroidQ.full()) and (not self._timeQ.full()):
                        t = ticks_us()
                        t_rel = ticks_diff(t, self._startTime)
                        self._centroidQ.put(c)
                        self._timeQ.put(t_rel)
                        self._ser.write("{},{}\r\n".format(t_rel, c))
                    else:
                        self._goFlag.put(0)
                        self._printed_header = False
                else:
                    self._printed_header = False

            yield self._state
