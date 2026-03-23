Encoder Driver
==============

.. py:module:: encoder

Summary
-------
This module implements a quadrature encoder interface using a timer configured
in encoder mode. It tracks cumulative wheel position, recent count change, and
a time-based velocity estimate.

Important class
---------------
``encoder(tim, chA_pin, chB_pin)``
   Creates an encoder object using one timer and two encoder pins.

Important methods
-----------------
``update()``
   Reads the current timer count, computes the change in count since the
   previous update, corrects for wraparound, updates the accumulated position,
   and measures the time elapsed since the previous update.

``get_position()``
   Returns the current accumulated encoder position in counts.

``get_velocity()``
   Returns the most recent count-rate estimate as ``delta / dt``.

``zero()``
   Resets the accumulated position and updates the reference count and time.

Important variables
-------------------
``self.AR``
   Auto-reload value for the timer. In this file it is fixed at ``0xFFFF`` for
   a 16-bit counter.

``self.position``
   Accumulated encoder position in counts.

``self.prev_count`` / ``self.curr_count``
   Previous and current timer counts used to compute motion between updates.

``self.delta``
   Incremental count change between the two most recent updates.

``self.prev_time`` / ``self.curr_time``
   Previous and current timestamps from ``ticks_us()``.

``self.dt``
   Time elapsed between the two most recent updates, in microseconds.

Implementation details
----------------------
The ``update()`` method explicitly corrects for timer wraparound by checking
whether the raw count difference exceeds half the timer range. After the
wraparound correction, the sign of ``delta`` is inverted so that encoder
motion matches the motor sign convention used elsewhere in the project.
