Motor Control Task
==================

.. py:module:: task_motor

Summary
-------
This task implements the inner wheel-speed control loop for one motor. It reads
the encoder, computes wheel speed, applies PI control, commands the motor
driver, and optionally logs velocity data.

Important class
---------------
``task_motor(mot, enc, goFlag, k_p, k_i, setpoint, dataValues, timeValues, pos_share=None, vel_share=None, invert_effort=False)``
   Generator-based motor-control task for one wheel.

Important methods
-----------------
``run()``
   Main task loop. It waits for an enable flag, zeros the encoder, enables the
   motor, computes measured speed, applies PI control, and sends effort to the
   driver.

``_mps_to_radps(speed_mps)``
   Converts linear wheel speed in meters per second to angular speed.

``_counts_us_to_radps(count_per_us)``
   Converts encoder count rate into angular speed.

``_write_telemetry(meas_radps)``
   Publishes velocity and position telemetry through shares.

Important state constants
-------------------------
``S0_INIT``
   Initialization state.

``S1_WAIT``
   Idle state waiting for a nonzero go flag.

``S2_RUN``
   Active closed-loop control state.

Important variables
-------------------
``self._mot``
   Motor-driver object used to command wheel effort.

``self._enc``
   Encoder object used to measure wheel motion.

``self._goFlag``
   Mode share controlling task behavior.

``self._k_p`` / ``self._k_i``
   PI gains for the inner speed loop.

``self._setpoint``
   Wheel speed command share in meters per second.

``self._dataValues`` / ``self._timeValues``
   Queues used to log measured wheel speed.

``self._pos_share`` / ``self._vel_share``
   Optional shares used to publish wheel position and wheel velocity.

``self._invert_effort``
   Optional sign inversion applied to the computed duty cycle.

``self._integral``
   Integral state of the PI controller.

``self._ref_vel``
   Most recent angular velocity setpoint.

``self._battery_volts``
   Battery voltage used to convert requested volts into PWM duty cycle.

``self._wheel_radius_m``
   Wheel radius used for unit conversions.

``self._counts_per_wheel_rev``
   Encoder counts per wheel revolution.

``self._two_pi``
   Cached constant used in the conversion formulas.

Go-flag meaning
---------------
``0``
   Stop. The motor is disabled and the task returns to the wait state.

``1``
   Run closed-loop control and log data until the logging queues fill, then
   stop automatically.

``2``
   Run continuous closed-loop control without auto-stop logging behavior.

Control behavior
----------------
The task converts the setpoint from meters per second to radians per second,
measures actual wheel speed from the encoder, and computes:

- ``error = reference - measured``
- ``integral += error * dt``
- ``effort_volts = Kp * error + Ki * integral``

The voltage command is converted into a duty cycle using the battery voltage
and clamped to the range ``-100`` to ``100`` percent before being sent to the
motor driver.
