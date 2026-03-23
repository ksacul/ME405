Motor Driver
============

.. py:module:: motor_driver

Summary
-------
This module provides a compact MicroPython driver for one DRV8838-style motor
channel on the Pololu ROMI chassis. It wraps the direction, sleep, and PWM
signals needed to control a single DC motor.

Important class
---------------
``motor_driver(PWM_pin, DIR_pin, nSLP_pin, tim, chan)``
   Creates one motor-driver object using a PWM output pin, a direction pin,
   a sleep pin, one timer, and one PWM channel number.

Important methods
-----------------
``set_effort(effort)``
   Sets the requested motor effort on a scale from ``-100`` to ``100``.
   Positive values drive one direction and negative values reverse the motor.
   The absolute value is written as the PWM duty cycle.

``enable()``
   Takes the motor driver out of sleep mode by driving the sleep pin high.

``disable()``
   Puts the driver into sleep mode and also forces the PWM duty cycle to zero.

Important variables
-------------------
``self.nSLP_pin``
   Output pin connected to the driver's sleep input. This pin determines
   whether the motor driver is active.

``self.DIR_pin``
   Output pin that selects the motor direction.

``self.PWM_chan``
   Timer channel configured for PWM output. This carries the duty cycle
   corresponding to the requested motor effort.

Behavior notes
--------------
The class initializes the sleep pin low, so the motor starts disabled until
``enable()`` is called. In ``set_effort()``, a positive effort drives the
direction pin low and a negative effort drives it high. This establishes the
sign convention used by the rest of the project.
