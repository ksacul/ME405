from motor_driver import motor_driver
from encoder import encoder
from task_share import Share, Queue
from utime import ticks_us, ticks_diff
import micropython

S0_INIT = micropython.const(0)
S1_WAIT = micropython.const(1)
S2_RUN = micropython.const(2)


class task_motor:
    """
    Inner wheel-speed loop.

    goFlag modes:
      0 = stop
      1 = log then stop when queues fill
      2 = continuous control
    """

    def __init__(self,
                 mot: motor_driver,
                 enc: encoder,
                 goFlag: Share,
                 k_p: Share,
                 k_i: Share,
                 setpoint: Share,
                 dataValues: Queue,
                 timeValues: Queue,
                 pos_share: Share = None,
                 vel_share: Share = None,
                 invert_effort: bool = False):

        self._state = S0_INIT
        self._mot = mot
        self._enc = enc
        self._goFlag = goFlag
        self._k_p = k_p
        self._k_i = k_i
        self._setpoint = setpoint
        self._dataValues = dataValues
        self._timeValues = timeValues
        self._pos_share = pos_share
        self._vel_share = vel_share
        self._invert_effort = invert_effort

        self._startTime = 0
        self._lastTime = 0
        self._integral = 0.0
        self._ref_vel = 0.0

        self._battery_volts = 7.2
        self._wheel_radius_m = 0.035
        self._counts_per_wheel_rev = 1440.0
        self._two_pi = 6.283185307

    def _mps_to_radps(self, speed_mps):
        return speed_mps / self._wheel_radius_m

    def _counts_us_to_radps(self, count_per_us):
        return count_per_us * 1_000_000.0 * self._two_pi / self._counts_per_wheel_rev

    def _write_telemetry(self, meas_radps):
        if self._vel_share is not None:
            self._vel_share.put(meas_radps * self._wheel_radius_m)
        if self._pos_share is not None:
            pos_m = (self._enc.get_position() / self._counts_per_wheel_rev) * self._two_pi * self._wheel_radius_m
            self._pos_share.put(pos_m)

    def run(self):
        while True:
            if self._state == S0_INIT:
                self._state = S1_WAIT

            elif self._state == S1_WAIT:
                if int(self._goFlag.get()) != 0:
                    self._startTime = ticks_us()
                    self._lastTime = self._startTime
                    self._integral = 0.0
                    self._enc.zero()
                    self._mot.enable()
                    self._state = S2_RUN

            elif self._state == S2_RUN:
                mode = int(self._goFlag.get())
                if mode == 0:
                    self._mot.disable()
                    self._state = S1_WAIT
                    yield self._state
                    continue

                self._enc.update()
                meas_radps = self._counts_us_to_radps(self._enc.get_velocity())
                self._write_telemetry(meas_radps)

                now = ticks_us()
                dt = ticks_diff(now, self._lastTime) / 1_000_000.0
                self._lastTime = now
                if dt <= 0:
                    dt = 1e-3

                self._ref_vel = self._mps_to_radps(float(self._setpoint.get()))
                err = self._ref_vel - meas_radps
                self._integral += err * dt

                effort_volts = float(self._k_p.get()) * err + float(self._k_i.get()) * self._integral
                duty = 100.0 * effort_volts / self._battery_volts
                if duty > 100.0:
                    duty = 100.0
                elif duty < -100.0:
                    duty = -100.0

                if self._invert_effort:
                    duty = -duty
                self._mot.set_effort(duty)

                if mode == 1:
                    if (not self._dataValues.full()) and (not self._timeValues.full()):
                        self._dataValues.put(meas_radps)
                        self._timeValues.put(ticks_diff(now, self._startTime))
                    else:
                        self._goFlag.put(0)
                        self._mot.disable()
                        self._state = S1_WAIT

            yield self._state
