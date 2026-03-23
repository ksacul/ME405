Line Follow Task
================

.. py:module:: task_line_follow

Summary
-------
This task converts the measured line centroid into left and right wheel speed
commands. It acts as the outer line-following controller, while the two motor
tasks act as the inner wheel-speed controllers.

Important class
---------------
``task_line_follow(enable, base_speed, Kp_line, Ki_line, centroid, setpoint_L, setpoint_R, center=7.0, delta_limit=0.10, line_seen_share=None)``
   Generator-based line-following task that computes steering corrections from
   centroid error.

Important methods
-----------------
``run()``
   Reads the centroid, computes error from the centerline, applies PI control,
   clamps the steering correction, and updates the left and right wheel
   setpoints.

Important state constants
-------------------------
``S0_INIT``
   Initialization state.

``S1_RUN``
   Main control state.

Important variables
-------------------
``self._enable``
   Share that enables or disables the line-following controller.

``self._base``
   Share holding the base forward speed.

``self._kp`` / ``self._ki``
   PI gains for the line-following controller.

``self._centroid``
   Share containing the current centroid estimate from the line-sensor task.

``self._spL`` / ``self._spR``
   Shares that publish the left and right wheel setpoints.

``self._center``
   Desired centroid value corresponding to the middle of the sensor array.

``self._limit``
   Maximum steering correction magnitude applied to the base speed.

``self._I``
   Integral term for the line-following controller.

``self._last_t``
   Previous timestamp used to compute ``dt``.

``self._line_seen``
   Optional share passed into the task. In the current implementation it is
   stored but not used directly inside ``run()``.

Control behavior
----------------
When enabled, the task computes:

- ``err = centroid - center``
- ``delta = Kp_line * err + Ki_line * integral``

The steering correction ``delta`` is then clamped to ``±delta_limit``.
Finally, wheel setpoints are generated as:

- ``left = base + delta``
- ``right = base - delta``

Both commands are limited to the range ``0.0`` to ``0.35`` meters per second.
When the task is disabled, the integral term is cleared and the time base is
reset.
