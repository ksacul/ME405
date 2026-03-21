from pyb import Pin
import micropython

micropython.alloc_emergency_exception_buf(100)


class BumperSwitch:
    """
    Simple digital bumper input with optional IRQ latching.

    Pololu Romi bumper outputs are normally-open and should use pull-ups.
    With pull-ups enabled, the signal idles high and goes low when pressed.
    """

    def __init__(self, pin, name="bumper", pull=Pin.PULL_UP, active_low=True):
        self._pin = Pin(pin, mode=Pin.IN, pull=pull)
        self._active_low = active_low
        self._name = name
        self._pressed = 0
        self._callback = None

    def value(self):
        return self._pin.value()

    def is_pressed(self):
        raw = self._pin.value()
        return (raw == 0) if self._active_low else (raw == 1)

    def pressed(self):
        return self.is_pressed()

    def latched(self):
        return self._pressed

    def clear(self):
        self._pressed = 0

    def attach_irq(self, callback=None, trigger=Pin.IRQ_FALLING):
        self._callback = callback
        self._pin.irq(self._irq_handler, trigger=trigger)

    def _irq_handler(self, pin):
        self._pressed = 1
        if self._callback is not None:
            self._callback(self)

    def __repr__(self):
        return "BumperSwitch(name='{}', pressed={})".format(self._name, self.is_pressed())
