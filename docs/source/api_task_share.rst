Shared Data Framework
=====================

.. py:module:: task_share

Summary
-------
This module provides the shared variables and queues used to move data safely
between cooperative tasks. It is the main communication layer between sensing,
control, and supervisory logic.

Important classes
-----------------
``BaseShare(type_code, thread_protect=True, name=None)``
   Common parent class for both queues and single-value shares.

``Queue(type_code, size, thread_protect=False, overwrite=False, name=None)``
   FIFO buffer used to pass multiple values between tasks.

``Share(type_code, thread_protect=True, name=None)``
   Single shared value used to publish the most recent state, command, or
   measurement.

Important functions
-------------------
``show_all()``
   Returns a diagnostic string describing all currently allocated queues and
   shares.

Important variables
-------------------
``share_list``
   Global list of all share and queue objects. This is used to generate
   diagnostic printouts.

``type_code_strings``
   Dictionary mapping array type codes to readable type names.

Queue-specific variables
------------------------
``self._buffer``
   Array used to store the queue contents.

``self._size``
   Maximum number of items the queue can hold.

``self._overwrite``
   Determines whether old data may be overwritten when the queue is full.

``self._rd_idx`` / ``self._wr_idx``
   Read and write indices for the circular buffer.

``self._num_items``
   Current number of items in the queue.

``self._max_full``
   Maximum fill level observed so far.

Share-specific variables
------------------------
``self._buffer``
   Single-element array that stores the shared value.

``self._name``
   Readable name used in diagnostic printouts.

Usage in this project
---------------------
The ROMI project uses shares for mode flags, controller gains, setpoints,
positions, velocities, and event flags. It uses queues primarily for data
logging, such as wheel velocity histories and centroid histories collected
during testing.
