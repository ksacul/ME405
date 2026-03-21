# Romi solution notes

## Current bumper setup
- One front bumper is installed.
- The code is already set for `PB7`.
- The bumper input is configured as `Pin.IN` with `Pin.PULL_UP`.
- The interrupt is `Pin.IRQ_FALLING` because the switch idles high and goes low when pressed.

## Startup behavior
- `AUTOSTART = False` in `main.py`
- With that setting, the robot stays idle at boot until you send a serial command.
- Change `AUTOSTART = True` later when you want the full course FSM to begin on power-up.

## Serial commands
- `g` full course
- `1` CP0 -> CP1 straight only
- `2` garage contact only
- `3` garage recovery spin only
- `4` CP2 -> CP3 only
- `5` CP3 -> CP4 only
- `6` CP4 -> CP5 return only
- `x` stop
- `l` show front bumper state
- `c` clear front bumper latch
- `f` slow forward jog
- `b` slow reverse jog
- `n` spin left
- `m` spin right

## What to tune next
- segment distances in `task_course.py`
- base speeds and line gains
- garage recovery timing and turn speed
- final auto-start setting before competition
