from time import ticks_us, ticks_diff   # Use to get dt value in update()
from pyb import Pin, Timer

class encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim, chA_pin, chB_pin):
        '''Initializes an Encoder object'''
        self.chA = tim.channel(1, pin=chA_pin, mode=Timer.ENC_A)
        self.chB = tim.channel(2, pin=chB_pin, mode=Timer.ENC_B)
        self.AR = 0xFFFF        # Auto-reload value for the timer (16-bit)
        self.tim = tim
        self.position   = 0     # Total accumulated position of the encoder
        self.prev_count = 0     # Counter value from the most recent update
        self.delta      = 0     # Change in count between last two updates
        self.dt         = 0     # Amount of time between last two updates
        self.prev_time = ticks_us()

    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
           track of the change in count and check for counter reload'''
        #update current count and time
        self.curr_count = self.tim.counter()
        self.curr_time = ticks_us()

        #update time diff and count diff
        self.dt = ticks_diff(self.curr_time, self.prev_time)  #microseconds
        self.delta = self.curr_count - self.prev_count

        #handle wraparound
        if self.delta > (self.AR + 1) // 2:               #Handle underflow
            self.delta -= (self.AR + 1)
        elif self.delta < (-self.AR +1 ) // 2:            #Handle overflow
            self.delta += (self.AR + 1)
        self.delta = -self.delta                          #invert to match motor orientation
        #update position
        self.position += self.delta
        
        #update previous values for next run of update
        self.prev_count = self.curr_count
        self.prev_time = self.curr_time

            
    def get_position(self):
        '''Returns the most recently updated value of position as determined
           within the update() method'''
        return self.position
            
    def get_velocity(self):
        '''Returns a measure of velocity using the the most recently updated
           value of delta as determined within the update() method'''
        if self.dt == 0:
            return 0.0
        else:
            return self.delta/self.dt

    def zero(self):
        '''Sets the present encoder position to zero and causes future updates
           to measure with respect to the new zero position'''
        self.position = 0
        self.prev_count = self.tim.counter()
        self.prev_time = ticks_us()