Course Supervisor Task
======================

.. py:module:: task_course

Summary
-------
This task is the top-level finite-state machine for the ROMI time-trial run.
It decides when the robot should line-follow, when it should drive open-loop,
when it should stop, and how the robot transitions between checkpoint segments,
garage contact handling, recovery, and the return-home behavior.

Important class
---------------
``task_course(auto_start, course_mode, stop_request, bump_mode, left_go, right_go, line_enable, line_mode, base_speed, setpoint_L, setpoint_R, left_pos, right_pos, centroid_share, line_seen_share, line_enable_share)``
   Generator-based supervisory state machine that coordinates the whole course.

Important helper methods
------------------------
``_avg_dist()``
   Computes the average of the left and right wheel positions.

``_reset_segment()``
   Resets the segment start distance and segment start time.

``_seg_dist()``
   Returns distance traveled within the current segment.

``_seg_time()``
   Returns elapsed time within the current segment.

``_manual_drive(left_mps, right_mps)``
   Disables line following and directly commands the wheel setpoints.

``_line_drive(speed_mps)``
   Enables line following and sets the desired base speed.

``_stop()``
   Disables motion and zeroes wheel setpoints.

``_finish_segment_or_continue(next_state)``
   Either advances to the next full-course state or stops if the robot is only
   running a segment test.

``_start_mode(mode)``
   Starts the correct state based on the selected course mode.

Important state constants
-------------------------
``S0_INIT``
   Initial setup state.

``S1_WAIT_START``
   Waits for ``auto_start`` to become true.

``S2_CP0_TO_CP1``
   First segment, including line following and some scripted maneuvers.

``S3_GARAGE_CONTACT``
   Drives into the garage/contact segment and waits for a bumper-triggered stop.

``S4_GARAGE_RECOVER``
   Recovery state that searches for the line again.

``S5_CP2_TO_CP3``
   Intermediate line-following segment after recovery.

``S6_CP3_TO_CP4``
   Another timed line-following segment.

``S7_RETURN_HOME``
   Final open-loop return maneuver.

``S8_DONE``
   Final stopped state.

``S9_BUMP_RECOVERY``
   Emergency bump-recovery state used outside the garage-contact sequence.

Important mode constants
------------------------
``MODE_IDLE``
   No automatic motion.

``MODE_FULL``
   Run the full multi-segment course.

``MODE_SEG_CP0_CP1``
   Test only the first segment.

``MODE_SEG_GARAGE_CONTACT``
   Test the garage-contact segment.

``MODE_SEG_GARAGE_RECOVER``
   Test the recovery segment.

``MODE_SEG_CP2_CP3``
   Test the mid-course line-follow segment.

``MODE_SEG_CP3_CP4``
   Test the later line-follow segment.

``MODE_SEG_RETURN``
   Test the return-home segment.

Important variables
-------------------
``self._auto_start``
   Share that begins the selected course run.

``self._course_mode``
   Share that selects full-course or segment-test behavior.

``self._stop_request``
   Share that signals a stop or recovery condition.

``self._bump_mode``
   Share containing interpreted bumper status.

``self._left_go`` / ``self._right_go``
   Shares controlling the left and right motor tasks.

``self._line_enable`` / ``self._line_mode``
   Shares controlling the line follower and line-sensor task behavior.

``self._base_speed``
   Share holding the desired line-follow base speed.

``self._spL`` / ``self._spR``
   Wheel setpoint shares.

``self._left_pos`` / ``self._right_pos``
   Wheel position shares used to measure segment distance.

``self._centroid``
   Shared line-centroid estimate.

``self._line_seen``
   Shared flag indicating whether the line is currently detected.

``self._state_start_us``
   Timestamp marking the start of the current state.

``self._segment_start_dist``
   Reference distance used to compute how far the robot has traveled in the
   current segment.

``self._recover_turn_speed``
   Stored recovery-speed parameter for recovery maneuvers.

``self._recover_start_us``
   Timestamp used during recovery behavior.

State-machine behavior
----------------------
The task begins in a stopped state, waits for ``auto_start``, and then launches
either the full course or one selected segment test. The code mixes line
following with short open-loop maneuvers.

Some key hard-coded transition conditions include:

- first segment thresholds near ``0.63``, ``0.80``, ``0.82``, and ``0.90`` m
- first-segment completion when ``left_pos >= 1.011``
- line-follow transition after roughly ``7.0`` s in ``S5_CP2_TO_CP3``
- later segment transition after roughly ``21.0`` s in ``S6_CP3_TO_CP4``
- return-home completion after roughly ``1.5`` s
- emergency bump-recovery backup duration of roughly ``0.25`` s

Role in the project
-------------------
This module is the highest-level behavior controller in the project. It
decides which lower-level task should currently dominate: pure line following,
manual open-loop wheel commands, bumper handling, or final stop behavior.
