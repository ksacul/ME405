User Command Task
=================

.. py:module:: task_user

Summary
-------
This task provides the USB serial command-line interface for the robot. It is
used to start the full course, run individual course segments, manually jog the
robot, inspect bumper state, and stop all motion.

Important class
---------------
``task_user(auto_start, course_mode, stop_request, left_go, right_go, line_enable, line_mode, base_speed, kp_inner, ki_inner, kp_line, ki_line, bump_state, setpoint_L, setpoint_R)``
   Generator-based user-interface task.

Important methods
-----------------
``run()``
   Main command-processing loop.

``_stop()``
   Forces the robot into a stopped state by clearing auto mode, setting the
   stop request, disabling line following, zeroing both wheel setpoints, and
   stopping both motor tasks.

``_start_course_mode(mode)``
   Starts the selected automatic course mode.

``_manual_drive(left_mps, right_mps)``
   Disables automatic behavior and directly commands left and right wheel
   speeds.

``_print_help()``
   Sends the command summary to the USB serial terminal.

Important state constants
-------------------------
``S0_INIT``
   Initialization state.

``S1_CMD``
   Main command-processing state.

Important variables
-------------------
``self._ser``
   USB serial interface used for command input and status output.

``self._auto_start``
   Share that tells the course task to begin running.

``self._course_mode``
   Share selecting either full-course mode or one of the individual segment
   test modes.

``self._stop_request``
   Share used to request an immediate stop.

``self._left_go`` / ``self._right_go``
   Shares controlling whether the left and right motor tasks are active.

``self._line_enable`` / ``self._line_mode``
   Shares controlling the line-following and line-sensor behavior.

``self._base_speed``
   Share holding the nominal forward speed used during line following.

``self._kp_inner`` / ``self._ki_inner``
   Inner motor-loop PI gains.

``self._kp_line`` / ``self._ki_line``
   Line-following PI gains.

``self._bump_state``
   Latched bumper state share shown to the user.

``self._spL`` / ``self._spR``
   Left and right wheel setpoint shares.

Default parameters
------------------
During initialization, this task sets:

- ``kp_inner = 1.6``
- ``ki_inner = 8.0``
- ``kp_line = 0.02``
- ``ki_line = 0.001``
- ``base_speed = 0.10``

Supported commands
------------------
``g``
   Start the full automatic course.

``1`` through ``6``
   Start individual segment-test modes.

``x``
   Stop the robot.

``l``
   Print the latched front bumper state.

``c``
   Clear the bumper latch.

``f``
   Manual forward jog.

``b``
   Manual reverse jog.

``n``
   Manual left spin.

``m``
   Manual right spin.

``h``
   Print the help text again.
