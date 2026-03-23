Cooperative Tasking Framework
=============================

.. py:module:: cotask

Summary
-------
This module provides the cooperative multitasking framework used by the ROMI
project. It defines individual task objects, stores them in a priority-sorted
task list, and schedules them according to either round-robin or
priority-based rules.

Important classes
-----------------
``Task(run_fun, name="NoName", priority=0, period=None, profile=False, trace=False, shares=())``
   Represents one cooperatively scheduled task. The task code must be written
   as a generator that yields its current state.

``TaskList()``
   Stores all tasks grouped by priority and provides scheduling methods.

Important methods
-----------------
``Task.schedule()``
   Runs a task if it is ready, advances the generator to the next ``yield``,
   and optionally records profiling or state-trace information.

``Task.ready()``
   Determines whether a task should run. Timed tasks check their next-run
   timestamp, while untimed tasks rely on ``go_flag``.

``Task.go()``
   Sets the task's ready flag so it will run as soon as the scheduler allows.

``TaskList.append(task)``
   Adds a task to the scheduler and inserts it into the correct priority group.

``TaskList.rr_sched()``
   Runs tasks in round-robin order.

``TaskList.pri_sched()``
   Runs the highest-priority ready task, using round-robin ordering among tasks
   of equal priority.

Important variables
-------------------
``Task.name``
   Short human-readable task name used in diagnostics.

``Task.priority``
   Integer priority; higher values run first.

``Task.period``
   Task period in microseconds when the task is time-triggered.

``Task._next_run``
   Timestamp for the next scheduled run of a timed task.

``Task.go_flag``
   Boolean flag indicating whether the task is ready to run.

``Task._runs``
   Number of times the task has been run.

``Task._run_sum`` / ``Task._slowest``
   Profiling data used to compute average and maximum execution time.

``Task._late_sum`` / ``Task._latest``
   Timing data used to measure scheduler lateness for timed tasks.

``TaskList.pri_list``
   Internal list of task groups sorted by priority.

Global object
-------------
``task_list``
   The project-wide task scheduler created at import time. This is the object
   used in ``main.py`` to append tasks and repeatedly call ``pri_sched()``.
