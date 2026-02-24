''' This file demonstrates an example motor task using a custom class with a
    run method implemented as a generator
'''
from motor_driver import motor_driver
from encoder      import encoder
from task_share   import Share, Queue
from utime        import ticks_us, ticks_diff
import micropython

S0_INIT = micropython.const(0) # State 0 - initialiation
S1_WAIT = micropython.const(1) # State 1 - wait for go command
S2_RUN  = micropython.const(2) # State 2 - run closed loop control

class task_motor:
    '''
    A class that represents a motor task. The task is responsible for reading
    data from an encoder, performing closed loop control, and actuating a motor.
    Multiple objects of this class can be created to work with multiple motors
    and encoders.
    '''

    def __init__(self,
                 mot: motor_driver, enc: encoder,
                 goFlag: Share, k_p: Share, k_i: Share, setpoint: Share, dataValues: Queue, timeValues: Queue):
        '''
        Initializes a motor task object
        
        Args:
            mot (motor_driver): A motor driver object
            enc (encoder):      An encoder object
            goFlag (Share):     A share object representing a boolean flag to
                                start data collection
            k_p (Share):        A share object representing the proportional gain
            k_i (Share):        A share object representing the integral gain
            setpoint (Share):   A share object representing the desired setpoint value
            dataValues (Queue): A queue object used to store collected encoder
                                position values
            timeValues (Queue): A queue object used to store the time stamps
                                associated with the collected encoder data
        '''

        self._state: int        = S0_INIT    # The present state of the task       
        
        self._mot: motor_driver = mot        # A motor object
        
        self._enc: encoder      = enc        # An encoder object
        
        self._goFlag: Share     = goFlag     # A share object representing a
                                             # flag to start data collection
        self._k_p: Share        = k_p        # A share object representing the proportional gain

        self._k_i: Share        = k_i        # A share object representing the integral gain

        self._setpoint: Share   = setpoint   # A share object representing the desired setpoint value
        
        self._dataValues: Queue = dataValues # A queue object used to store
                                             # collected encoder position
        
        self._timeValues: Queue = timeValues # A queue object used to store the
                                             # time stamps associated with the
                                             # collected encoder data
        
        self._startTime: int    = 0          # The start time (in microseconds)
                                             # for a batch of collected data
    
    
        
        print("Motor Task object instantiated")
        
    def run(self):
        '''
        Runs one iteration of the task
        '''
        
        while True:
            
            if self._state == S0_INIT: # Init state (can be removed if unneeded)
                # print("Initializing motor task")
                self._state = S1_WAIT
                
            elif self._state == S1_WAIT: # Wait for "go command" state
                if self._goFlag.get():
                    # print("Starting motor loop")
                    
                    # Capture a start time in microseconds so that each sample
                    # can be timestamped with respect to this start time. The
                    # start time will be off by however long it takes to
                    # transition and run the next state, so the time values may
                    # need to be zeroed out again during data processing.
                    self._startTime = ticks_us()
                    self._mot.enable()
                    self.setpoint_linear = self._setpoint.get()                 #desired setpoint for linear velocity [m/s]
                    self.ref_vel = self.setpoint_linear/0.036              #converts setpoint from m/s to rad/sec
                    print(f"Reference velocity: {self.ref_vel} rad/sec")
                    self.bat_life_percent = 100                               #battery life percentage (used to scale controller output voltage)
                    self._total_integral = 0.0                        #initialize integral term [rad]
                    self._state = S2_RUN
                    self._lastTime = self._startTime
                    self._enc.zero()

            elif self._state == S2_RUN: # Closed-loop control state
                # print(f"Running motor loop, cycle {self._dataValues.num_in()}")
                
                # Run the encoder update algorithm and then capture the present
                # position of the encoder. You will eventually need to capture
                # the motor speed instead of position here.

                self._enc.update()
                pos = self._enc.get_position()
                meas_vel = self._enc.get_velocity()*4372   #converts measured velocity from counts/us to rad/sec
                self._current_error = self.ref_vel - meas_vel                 #calculate error [rad/sec]
                # Collect a timestamp to use for this sample
                t   = ticks_us()
                dt = ticks_diff(t, self._lastTime)/1_000_000  #time slice in seconds
                self._lastTime = t
                self._single_pass_integral = self._current_error * dt    #integral for single pass [rad]
                self._total_integral += self._single_pass_integral       #total integral [rad]

                self.Controller_Output_Voltage = (self._k_p.get()* self._current_error + self._k_i.get() * self._total_integral)                        #calculate controller output voltage using proportional control law
                L = self.bat_life_percent*self.Controller_Output_Voltage/7.2   #convert controller output voltage to a duty cycle percentage (0-100)
                self._mot.set_effort(L)
                
                # Store the sampled values in the queues
                self._dataValues.put(meas_vel)
                self._timeValues.put(ticks_diff(t, self._startTime))
                
                # When the queues are full, data collection is over
                if self._dataValues.full():
                    # print("Exiting motor loop")
                    self._state = S1_WAIT
                    self._mot.disable()
                    self._goFlag.put(False)
            
            yield self._state