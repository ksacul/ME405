Overview
========

Purpose
-------

The Romi robot is designed to complete a time trial course, following a line, navigating a "garage", and avoiding obstacles during a slalom section for best completion.

Apart from the STM32L476 Nucleo board, IMU, and custom PCB (ShoeOfBrian) running MicroPython, students were expected to supply and choose their own sensor suite to accomplish the aforementioned tasks.

Our Romi Design
---------------

Our Romi uses a 7-segment IR sensor in conjunction with a bump sensor for line following and garage navigation, respectively. The IR sensor is mounted to the front and sits below the robot's chasis. The bump sensor sits at the front of the chasis. More details can be found in the Hardware section.
