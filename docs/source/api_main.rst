Main Program
============

.. py:module:: main

Summary
-------
This file is the integration point for the entire ROMI project. It configures
the hardware timers, creates the motor, encoder, bumper, and line-sensing
objects, allocates all shared variables and queues, constructs each task, and
starts the cooperative scheduler.

System setup
------------
The program disables the UART REPL, enables automatic start by default, and
creates one PWM timer for the motors plus two encoder timers for the left and
right wheels. It then creates the two motor-driver objects, two encoder
objects, and one front bumper-switch object.

Important objects
-----------------
``leftMotor`` / ``rightMotor``
   Instances of ``motor_driver`` used to command the left and right wheels.

``leftEncoder`` / ``rightEncoder``
   Instances of ``encoder`` used to measure wheel position and velocity.

``front_bumper``
   Instance of ``BumperSwitch`` used to detect a front bumper hit.

Important shares and queues
---------------------------
``leftMotorGo`` / ``rightMotorGo``
   Mode flags for the left and right motor tasks. These select whether a motor
   task is stopped, logging, or running continuous closed-loop control.

``K_p`` / ``K_i``
   Inner-loop PI gains for the wheel-speed controller.

``setpoint_L`` / ``setpoint_R``
   Left and right wheel speed commands. These are consumed by the motor tasks.

``lineGoFlag``
   Mode flag for the line-sensor task. It selects whether the task simply
   updates the shared centroid value or also logs data.

``lineEnable``
   Enable flag for the line-following task.

``base_speed``
   Nominal forward speed used by the line-following controller.

``Kp_line`` / ``Ki_line``
   PI gains for the line-following controller.

``centroid_share``
   Shared line-centroid estimate produced by the line-sensor task.

``line_seen_share``
   Shared flag indicating whether the sensor array currently sees the line.

``auto_start`` / ``course_mode`` / ``stop_request``
   Supervisory control shares used by the course and user tasks.

``bump_mode`` / ``bump_event`` / ``bump_state``
   Bumper-related shares used to report contact events and latched bumper
   status.

``left_pos`` / ``right_pos``
   Wheel position estimates in meters.

``left_vel`` / ``right_vel``
   Wheel velocity estimates in meters per second.

``centroidQ`` / ``timeCentroidQ``
   Queues used to log line-centroid data.

``dataValues_l`` / ``timeValues_l`` and ``dataValues_r`` / ``timeValues_r``
   Queues used to log left and right wheel velocity data.

Interrupt behavior
------------------
The front bumper is connected to an interrupt service routine named
``_front_bump_irq()``. When the bumper is pressed, the ISR sets both the
``bump_event`` share and the ``bump_state`` share so the task layer can react
without polling the pin directly.

Task creation
-------------
The main program constructs the following tasks:

``leftMotorTask`` / ``rightMotorTask``
   Closed-loop wheel-speed tasks for the left and right motors.

``lineSensorTask``
   Task that reads the QTR array and publishes the line centroid.

``lineFollowTask``
   Task that converts centroid error into left and right wheel setpoints.

``bumpTask``
   Task that translates a bumper event into a stop request.

``courseTask``
   High-level supervisory task that runs the checkpoint sequence.

``userTask``
   USB serial command interface used to start, stop, and test segments.

Scheduler configuration
-----------------------
The task list is configured so that:

- left and right motor tasks run every 20 ms at priority 2
- line sensor and line-follow tasks run every 10 ms at priority 3
- bump task runs every 10 ms at priority 4
- course task runs every 20 ms at priority 4
- user task runs at priority 1 with no fixed period

Program flow
------------
After all objects are created, the garbage collector is run once and the
program enters an infinite loop which repeatedly calls ``task_list.pri_sched()``.
If a keyboard interrupt occurs, both motors are disabled and the program exits
the scheduler loop cleanly.
