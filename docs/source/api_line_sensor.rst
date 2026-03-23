Line Sensor Task
================

.. py:module:: task_line_sensor

Summary
-------
This task reads the QTR line-sensor driver, computes the line centroid, updates
shared state for the rest of the control system, and optionally logs centroid
data over USB serial and into queues.

Important class
---------------
``task_line_sensor(goFlag, centroid_share, centroidQ, timeQ, line_seen_share, oversample=4)``
   Periodic sensing task that wraps the ``QTRMD07A_Analog`` driver and exports
   processed line information to the rest of the robot.

Important methods
-----------------
``run()``
   Generator-based task loop. It reads normalized sensor values, computes the
   centroid, updates the ``line_seen`` flag, and optionally logs time-stamped
   centroid data.

Important state constants
-------------------------
``S0_INIT``
   Initialization state.

``S1_RUN``
   Main sensing and logging state.

Important variables
-------------------
``self._goFlag``
   Share controlling task behavior. In this file, mode ``1`` enables
   time-stamped logging while other modes simply keep the centroid updated.

``self._centroid_share``
   Share that publishes the most recent centroid estimate.

``self._centroidQ`` / ``self._timeQ``
   Queues used to store logged centroid samples and timestamps.

``self._line_seen``
   Share that indicates whether the line is currently detected.

``self._ser``
   USB serial interface used to stream logged centroid data.

``self._printed_header``
   Flag used to print the CSV header only once per logging run.

``self._qtr``
   Instance of ``QTRMD07A_Analog`` used to acquire sensor data.

``self._startTime``
   Start timestamp for relative time logging.

Behavior notes
--------------
Each run computes normalized sensor values ``n`` and centroid ``c``, then
updates ``line_seen`` according to whether ``max(n) > 0.40``. When logging is
enabled, the task outputs CSV-style text with the header ``t_us,centroid`` and
stores matching samples in the centroid queues.
