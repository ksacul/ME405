import micropython
from utime import ticks_us, ticks_diff
from task_share import Share

S0_INIT = micropython.const(0)
S1_WAIT_START = micropython.const(1)
S2_CP0_TO_CP1 = micropython.const(2)
S3_GARAGE_CONTACT = micropython.const(3)
S4_GARAGE_RECOVER = micropython.const(4)
S5_CP2_TO_CP3 = micropython.const(5)
S6_CP3_TO_CP4 = micropython.const(6)
S7_RETURN_HOME = micropython.const(7)
S8_DONE = micropython.const(8)
S9_BUMP_RECOVERY = micropython.const(9)

MODE_IDLE = micropython.const(0)
MODE_FULL = micropython.const(1)
MODE_SEG_CP0_CP1 = micropython.const(2)
MODE_SEG_GARAGE_CONTACT = micropython.const(3)
MODE_SEG_GARAGE_RECOVER = micropython.const(4)
MODE_SEG_CP2_CP3 = micropython.const(5)
MODE_SEG_CP3_CP4 = micropython.const(6)
MODE_SEG_RETURN = micropython.const(7)

class task_course:
    def __init__(self,
                 auto_start: Share,
                 course_mode: Share,
                 stop_request: Share,
                 bump_mode: Share,
                 left_go: Share,
                 right_go: Share,
                 line_enable: Share,
                 line_mode: Share,
                 base_speed: Share,
                 setpoint_L: Share,
                 setpoint_R: Share,
                 left_pos: Share,
                 right_pos: Share,
                 centroid_share: Share,
                 line_seen_share: Share,
                 line_enable_share: Share):
        self._state = S0_INIT
        self._auto_start = auto_start
        self._course_mode = course_mode
        self._stop_request = stop_request
        self._bump_mode = bump_mode
        self._left_go = left_go
        self._right_go = right_go
        self._line_enable = line_enable
        self._line_mode = line_mode
        self._base_speed = base_speed
        self._spL = setpoint_L
        self._spR = setpoint_R
        self._left_pos = left_pos
        self._right_pos = right_pos
        self._centroid = centroid_share
        self._line_seen = line_seen_share
        self._line_enable = line_enable_share
        self._state_start_us = ticks_us()
        self._segment_start_dist = 0.0
        self._recover_turn_speed = 0.07
        self._recover_start_us = ticks_us()

    def _avg_dist(self):
        return 0.5 * (float(self._left_pos.get()) + float(self._right_pos.get()))

    def _reset_segment(self):
        self._segment_start_dist = self._avg_dist()
        self._state_start_us = ticks_us()

    def _seg_dist(self):
        return self._avg_dist() - self._segment_start_dist

    def _seg_time(self):
        return ticks_diff(ticks_us(), self._state_start_us) / 1_000_000.0

    def _manual_drive(self, left_mps, right_mps):
        self._line_enable.put(0)
        self._line_mode.put(0)
        self._spL.put(left_mps)
        self._spR.put(right_mps)
        self._left_go.put(2)
        self._right_go.put(2)

    def _line_drive(self, speed_mps):
        self._base_speed.put(speed_mps)
        self._line_enable.put(1)
        self._line_mode.put(2)
        self._left_go.put(2)
        self._right_go.put(2)

    def _stop(self):
        self._line_enable.put(0)
        self._line_mode.put(0)
        self._spL.put(0.0)
        self._spR.put(0.0)
        self._left_go.put(0)
        self._right_go.put(0)

    def _finish_segment_or_continue(self, next_state):
        if int(self._course_mode.get()) == MODE_FULL:
            self._reset_segment()
            self._state = next_state
        else:
            self._stop()
            self._auto_start.put(0)
            self._course_mode.put(MODE_IDLE)
            self._state = S8_DONE

    def _start_mode(self, mode):
        
        self._stop_request.put(0)
        self._reset_segment()
        if mode == MODE_FULL or mode == MODE_SEG_CP0_CP1:
            self._line_drive(0.12)
            self._state = S2_CP0_TO_CP1
        elif mode == MODE_SEG_GARAGE_CONTACT:
            self._manual_drive(0.10, 0.10)
            self._state = S3_GARAGE_CONTACT
        elif mode == MODE_SEG_GARAGE_RECOVER:
            self._line_seen.put(0)
            self._recover_start_us = ticks_us()
            self._manual_drive(-0.06, 0.0)
            self._state = S4_GARAGE_RECOVER
        elif mode == MODE_SEG_CP2_CP3:
            self._line_drive(0.10)
            self._state = S5_CP2_TO_CP3
        elif mode == MODE_SEG_CP3_CP4:
            self._line_drive(0.08)
            self._state = S6_CP3_TO_CP4
        elif mode == MODE_SEG_RETURN:
            self._line_drive(0.12)
            self._state = S7_RETURN_HOME

    def run(self):
        while True:
            if self._state == S0_INIT:
                self._stop()
                self._state = S1_WAIT_START

            elif self._state == S1_WAIT_START:
                if int(self._auto_start.get()):
                    mode = int(self._course_mode.get())
                    if mode != MODE_IDLE:
                        self._start_mode(mode)

            elif self._state == S2_CP0_TO_CP1:
                if self._seg_dist() >= 0.63:
                    self._stop()
                    self._line_drive(0.05)
                    if self._seg_dist() >= 0.8:
                        self._stop()
                        self._manual_drive(0.055, 0)
                        if self._seg_dist() >= 0.82:
                            self._stop()
                            self._manual_drive(0.095, 0.095)
                            if self._seg_dist() >= 0.90:
                                self._stop()
                                self._manual_drive(0.04, -0.04)
                                if self._left_pos.get() >= 1.011:
                                    self._stop()
                                    print("Segment CP0 to CP1 complete")
                                    self._finish_segment_or_continue(S3_GARAGE_CONTACT)
                                    if self._state == S3_GARAGE_CONTACT:
                                        self._manual_drive(0.06, 0.06)

            elif self._state == S3_GARAGE_CONTACT:
                if int(self._stop_request.get()) == 1:
                    self._stop()
                    self._stop_request.put(0)
                    self._line_seen.put(0)
                    print("Garage contact detected! Stopping and preparing for recovery.")
                    self._finish_segment_or_continue(S4_GARAGE_RECOVER)
                    if self._state == S4_GARAGE_RECOVER:
                        self._line_enable.put(0)
                        self._recover_start_pos = ticks_us()
                        self._manual_drive(-0.08, 0.0)

            elif self._state == S4_GARAGE_RECOVER:
                self._stop_request.put(0)

                if int(self._line_seen.get()) == 1:
                    self._line_drive(0.04)
                    self._finish_segment_or_continue(S5_CP2_TO_CP3)
                    if self._state == S5_CP2_TO_CP3:
                        self._line_drive(0.04)


            elif self._state == S5_CP2_TO_CP3:
                if int(self._line_seen.get()) == 0:
                    self._manual_drive(0.1, -0.1)

                if int(self._line_seen.get()) == 1:
                    self._line_drive(0.04)
                    if self._seg_time() >= 7.0:
                        self._finish_segment_or_continue(S6_CP3_TO_CP4)
                        if self._state == S6_CP3_TO_CP4:
                            self._stop()

            elif self._state == S6_CP3_TO_CP4:
                self._line_drive(0.04)
                if self._seg_time() >= 21.0:
                    self._finish_segment_or_continue(S7_RETURN_HOME)
                    self._stop()

            elif self._state == S7_RETURN_HOME:
                self._manual_drive(-0.13, -0.2)
                if self._seg_time() >= 1.5:
                    self._stop()
                    print("Return home segment complete")
                    self._finish_segment_or_continue(S8_DONE)
                    

            elif self._state == S8_DONE:
                self._stop()

            if int(self._stop_request.get()) and self._state not in (S3_GARAGE_CONTACT, S4_GARAGE_RECOVER, S8_DONE, S1_WAIT_START):
                self._stop_request.put(0)
                self._reset_segment()
                self._manual_drive(-0.06, -0.06)
                self._state = S9_BUMP_RECOVERY

            elif self._state == S9_BUMP_RECOVERY:
                if self._seg_time() > 0.25:
                    self._stop()
                    self._auto_start.put(0)
                    self._course_mode.put(MODE_IDLE)
                    self._state = S8_DONE

            yield self._state
