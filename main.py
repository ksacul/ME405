from motor_driver import motor_driver
from pyb          import Pin, Timer, repl_uart
from encoder      import encoder
from task_motor   import task_motor
from task_user    import task_user
from task_share   import Share, Queue, show_all
from cotask       import Task, task_list
from gc           import collect
repl_uart(None)
# Build all driver objects first

pwm_timer = Timer(2, freq=20000)  # 20 kHz PWM frequency
enc_timer_left = Timer(3, prescaler=0, period=0xFFFF)
enc_timer_right = Timer(1, prescaler=0, period=0xFFFF)

leftMotor    = motor_driver(Pin.cpu.B3, Pin.cpu.C1, Pin.cpu.C0, pwm_timer, 2)
rightMotor   = motor_driver(Pin.cpu.A0, Pin.cpu.A1, Pin.cpu.A4, pwm_timer, 1)
leftEncoder  = encoder(tim=enc_timer_left, chA_pin=Pin.cpu.B4, chB_pin=Pin.cpu.B5)
rightEncoder = encoder(tim=enc_timer_right, chA_pin=Pin.cpu.A8, chB_pin=Pin.cpu.A9)

# Build shares and queues
leftMotorGo   = Share("B",     name="Left Mot. Go Flag")
rightMotorGo  = Share("B",     name="Right Mot. Go Flag")
K_p           = Share("f",     name="Kp Value")
K_i           = Share("f",     name="Ki Value")
setpoint      = Share("f",     name="Setpoint Value")
dataValues_r    = Queue("f", 100, name="Data Collection Buffer Right")
timeValues_r    = Queue("L", 100, name="Time Buffer Right")
dataValues_l    = Queue("f", 100, name="Data Collection Buffer Left")
timeValues_l    = Queue("L", 100, name="Time Buffer Left")

# Build task class objects
leftMotorTask  = task_motor(leftMotor,  leftEncoder,
                            leftMotorGo, K_p, K_i, setpoint, dataValues_l, timeValues_l)
rightMotorTask = task_motor(rightMotor, rightEncoder,
                            rightMotorGo, K_p, K_i, setpoint, dataValues_r, timeValues_r)
userTask = task_user(leftMotorGo, rightMotorGo, K_p, K_i, setpoint, dataValues_r, timeValues_r, dataValues_l, timeValues_l)

# Add tasks to task list
task_list.append(Task(leftMotorTask.run, name="Left Mot. Task",
                      priority = 1, period = 50, profile=True))
task_list.append(Task(rightMotorTask.run, name="Right Mot. Task",
                      priority = 1, period = 50, profile=True))
task_list.append(Task(userTask.run, name="User Int. Task",
                      priority = 0, period = 0, profile=False))

# Run the garbage collector preemptively
collect()

# Run the scheduler until the user quits the program with Ctrl-C
while True:
    try:
        task_list.pri_sched()
        
    except KeyboardInterrupt:
        print("Program Terminating")
        leftMotor.disable()
        rightMotor.disable()
        break

print("\n")
print(task_list)
print(show_all())