Bumper Switch Driver
====================

.. py:module:: task_bump

Summary
-------
This module provides a simple digital bumper-switch interface with optional
interrupt latching. It is designed for the Pololu ROMI bumper hardware, which
is normally open and typically used with pull-up resistors.

Important class
---------------
``BumperSwitch(pin, name="bumper", pull=Pin.PULL_UP, active_low=True)``
   Creates one bumper-switch object connected to a single digital input.

Important methods
-----------------
``value()``
   Returns the raw digital pin value.

``is_pressed()``
   Returns ``True`` when the bumper is currently pressed.

``pressed()``
   Alias for ``is_pressed()``.

``latched()``
   Returns the stored latched press flag.

``clear()``
   Clears the latched press flag.

``attach_irq(callback=None, trigger=Pin.IRQ_FALLING)``
   Attaches an interrupt handler so the bumper can latch events immediately.

Important variables
-------------------
``self._pin``
   Input pin object for the bumper signal.

``self._active_low``
   Indicates whether a logic-low input should be interpreted as a press.

``self._name``
   Readable name for diagnostics.

``self._pressed``
   Latched event flag set by the IRQ handler.

``self._callback``
   Optional callback function invoked when an interrupt occurs.

Behavior notes
--------------
With the default pull-up configuration, the bumper signal idles high and goes
low when pressed. The private interrupt handler sets ``self._pressed = 1`` and
optionally calls the user-supplied callback so the rest of the control system
can react quickly.
