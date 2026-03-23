Line Sensor Driver
==================

.. py:module:: line_sensor

Summary
-------
This module implements a MicroPython driver for the Pololu QTR-MD-07A analog
reflectance sensor array. It reads seven ADC channels, supports optional
white/black calibration, produces normalized line intensity values, and
computes a weighted centroid for line tracking.

Important class
---------------
``QTRMD07A_Analog(...)``
   Driver class for the seven-channel analog sensor array. By default it uses
   seven ADC pins and logical sensor positions ``(1, 3, 5, 7, 9, 11, 13)``.

Important methods
-----------------
``read_raw()``
   Reads all seven ADC channels and returns the raw sensor values.

``calibrate_white(samples=50, delay_ms=5)``
   Measures the white-background response for all channels.

``calibrate_black(samples=50, delay_ms=5)``
   Measures the black-line response for all channels.

``read_normalized(clip=True)``
   Converts raw sensor values into normalized blackness values, typically
   between 0 and 1.

``centroid(normalized=None, min_sum=0.05)``
   Computes the weighted centroid of the normalized sensor profile.

``error(center=7.0, normalized=None)``
   Convenience method that returns centroid error relative to the center.

``emitters_on()`` / ``emitters_off()``
   Control optional odd/even emitter pins when they are wired.

Important variables
-------------------
``self._pins``
   Tuple of ADC pins used by the seven sensor channels.

``self._adcs``
   List of ADC objects used to read the sensor voltages.

``self._pos``
   Logical sensor positions used for centroid calculation.

``self._os``
   Oversampling count used in ``read_raw()``.

``self._white`` / ``self._black``
   Calibration endpoints for white and black surfaces.

``self._has_white`` / ``self._has_black``
   Flags indicating whether calibration data has been captured.

``self._last_centroid``
   Last valid centroid value. This is reused when the line is temporarily lost.

``self._ctrl_odd`` / ``self._ctrl_even``
   Optional emitter-control pins.

Behavior notes
--------------
The module assumes that white surfaces produce lower ADC readings and black
surfaces produce higher ADC readings. If the sum of normalized blackness is
too small, the ``centroid()`` method returns the previous valid centroid
instead of generating a noisy line estimate.
