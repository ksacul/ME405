import micropython
from pyb import USB_VCP
from task_share import Share

S0_INIT = micropython.const(0)
S1_CMD = micropython.const(1)


class task_user:
    def __init__(self,
                 auto_start: Share,
                 course_mode: Share,
                 stop_request: Share,
                 left_go: Share,
                 right_go: Share,
                 line_enable: Share,
                 line_mode: Share,
                 base_speed: Share,
                 kp_inner: Share,
                 ki_inner: Share,
                 kp_line: Share,
                 ki_line: Share,
                 bump_state: Share,
                 setpoint_L: Share,
                 setpoint_R: Share):
        self._state = S0_INIT
        self._ser = USB_VCP()
        self._auto_start = auto_start
        self._course_mode = course_mode
        self._stop_request = stop_request
        self._left_go = left_go
        self._right_go = right_go
        self._line_enable = line_enable
        self._line_mode = line_mode
        self._base_speed = base_speed
        self._kp_inner = kp_inner
        self._ki_inner = ki_inner
        self._kp_line = kp_line
        self._ki_line = ki_line
        self._bump_state = bump_state
        self._spL = setpoint_L
        self._spR = setpoint_R

    def _stop(self):
        self._auto_start.put(0)
        self._course_mode.put(0)
        self._stop_request.put(1)
        self._line_enable.put(0)
        self._line_mode.put(0)
        self._spL.put(0.0)
        self._spR.put(0.0)
        self._left_go.put(0)
        self._right_go.put(0)

    def _start_course_mode(self, mode):
        self._bump_state.put(0)
        self._stop_request.put(0)
        self._course_mode.put(mode)
        self._auto_start.put(1)

    def _manual_drive(self, left_mps, right_mps):
        self._auto_start.put(0)
        self._course_mode.put(0)
        self._line_enable.put(0)
        self._line_mode.put(0)
        self._spL.put(left_mps)
        self._spR.put(right_mps)
        self._left_go.put(2)
        self._right_go.put(2)

    def _print_help(self):
        self._ser.write(
            "\nRomi checkpoint runner ready\n\r"
            "  g: go full auto course\n\r"
            "  1: test CP0 -> CP1 straight\n\r"
            "  2: test garage contact drive\n\r"
            "  3: test garage recovery spin to line\n\r"
            "  4: test CP2 -> CP3 line section\n\r"
            "  5: test CP3 -> CP4 line section\n\r"
            "  6: test CP4 -> CP5 return section\n\r"
            "  x: stop\n\r"
            "  l: show front bumper state\n\r"
            "  c: clear latched bumper state\n\r"
            "  f: short forward jog\n\r"
            "  b: short reverse jog\n\r"
            "  n: spin left in place\n\r"
            "  m: spin right in place\n\r"
            "  h: help\n\r> "
        )

    def run(self):
        while True:
            if self._state == S0_INIT:
                self._kp_inner.put(1.6)
                self._ki_inner.put(8.0)
                self._kp_line.put(0.02)
                self._ki_line.put(0.001)
                self._base_speed.put(0.10)
                self._print_help()
                self._state = S1_CMD

            elif self._state == S1_CMD:
                if self._ser.any():
                    ch = self._ser.read(1).decode()
                    if ch == 'g':
                        self._start_course_mode(1)
                        self._ser.write("Full auto course started.\n\r> ")
                    elif ch in ('1', '2', '3', '4', '5', '6'):
                        mode = int(ch) + 1
                        self._start_course_mode(mode)
                        self._ser.write("Segment {} started.\n\r> ".format(ch))
                    elif ch == 'x':
                        self._stop()
                        self._ser.write("Stopped.\n\r> ")
                    elif ch == 'l':
                        self._ser.write("Front bumper state={}\n\r> ".format(int(self._bump_state.get())))
                    elif ch == 'c':
                        self._bump_state.put(0)
                        self._ser.write("Front bumper latch cleared.\n> ")
                    elif ch == 'f':
                        self._manual_drive(0.10, 0.10)
                        self._ser.write("Manual forward jog enabled. Press x to stop.\n\r> ")
                    elif ch == 'b':
                        self._manual_drive(-0.08, -0.08)
                        self._ser.write("Manual reverse jog enabled. Press x to stop.\n\r> ")
                    elif ch == 'n':
                        self._manual_drive(-0.08, 0.08)
                        self._ser.write("Manual left spin enabled. Press x to stop.\n\r> ")
                    elif ch == 'm':
                        self._manual_drive(0.08, -0.08)
                        self._ser.write("Manual right spin enabled. Press x to stop.\n\r> ")
                    elif ch == 'h':
                        self._print_help()
                    elif ch in ('\r', '\n'):
                        self._ser.write("\n\r> ")

            yield self._state
