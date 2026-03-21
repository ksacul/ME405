from pyb import Pin, Timer, repl_uart
from gc import collect
from cotask import Task, task_list
from task_share import Share, Queue, show_all
from motor_driver import motor_driver
from encoder import encoder
from task_line_sensor import task_line_sensor
from task_line_follow import task_line_follow
from task_motor import task_motor
from task_user import task_user
from task_bump import task_bump
from task_course import task_course
from bumper import BumperSwitch

repl_uart(None)

AUTOSTART = True

pwm_timer = Timer(2, freq=20000)
enc_timer_left = Timer(3, prescaler=0, period=0xFFFF)
enc_timer_right = Timer(1, prescaler=0, period=0xFFFF)

leftMotor = motor_driver(Pin.cpu.B3, Pin.cpu.C1, Pin.cpu.C0, pwm_timer, 2)
rightMotor = motor_driver(Pin.cpu.A0, Pin.cpu.A1, Pin.cpu.A4, pwm_timer, 1)
leftEncoder = encoder(tim=enc_timer_left, chA_pin=Pin.cpu.B4, chB_pin=Pin.cpu.B5)
rightEncoder = encoder(tim=enc_timer_right, chA_pin=Pin.cpu.A8, chB_pin=Pin.cpu.A9)

BUMPER_PIN = Pin.cpu.B7
front_bumper = BumperSwitch(BUMPER_PIN, name="front")

leftMotorGo = Share('B', name='Left Motor Go')
rightMotorGo = Share('B', name='Right Motor Go')

K_p = Share('f', name='Inner Kp')
K_i = Share('f', name='Inner Ki')
setpoint_L = Share('f', name='Left Setpoint')
setpoint_R = Share('f', name='Right Setpoint')

lineGoFlag = Share('B', name='Line Sensor Mode')
lineEnable = Share('B', name='Line Follow Enable')
base_speed = Share('f', name='Base Speed')
Kp_line = Share('f', name='Line Kp')
Ki_line = Share('f', name='Line Ki')
centroid_share = Share('f', name='Centroid')
line_seen_share = Share('B', name='Line Seen')

auto_start = Share('B', name='Auto Start')
course_mode = Share('B', name='Course Mode')
stop_request = Share('B', name='Stop Request')
bump_mode = Share('B', name='Bump Mode')
bump_event = Share('B', name='Front Bump Event')
bump_state = Share('B', name='Front Bump State')

left_pos = Share('f', name='Left Position m')
right_pos = Share('f', name='Right Position m')
left_vel = Share('f', name='Left Velocity mps')
right_vel = Share('f', name='Right Velocity mps')

centroidQ = Queue('f', 200, name='Centroid Log')
timeCentroidQ = Queue('L', 200, name='Centroid Time')
dataValues_r = Queue('f', 100, name='Right Vel Log')
timeValues_r = Queue('L', 100, name='Right Time')
dataValues_l = Queue('f', 100, name='Left Vel Log')
timeValues_l = Queue('L', 100, name='Left Time')

for share, value in (
    (leftMotorGo, 0), (rightMotorGo, 0), (lineGoFlag, 2), (lineEnable, 0),
    (auto_start, int(AUTOSTART)), (course_mode, 1 if AUTOSTART else 0), (stop_request, 0),
    (bump_mode, 0), (bump_event, 0), (bump_state, 0),
    (left_pos, 0.0), (right_pos, 0.0), (left_vel, 0.0), (right_vel, 0.0),
    (centroid_share, 7.0), (line_seen_share, 0)
):
    share.put(value)

def _front_bump_irq(sw):
    bump_event.put(1, in_ISR=True)
    bump_state.put(1, in_ISR=True)

front_bumper.attach_irq(_front_bump_irq)

leftMotorTask = task_motor(leftMotor, leftEncoder, leftMotorGo, K_p, K_i, setpoint_L,
                           dataValues_l, timeValues_l, pos_share=left_pos, vel_share=left_vel)
rightMotorTask = task_motor(rightMotor, rightEncoder, rightMotorGo, K_p, K_i, setpoint_R,
                            dataValues_r, timeValues_r, pos_share=right_pos, vel_share=right_vel)

lineSensorTask = task_line_sensor(lineGoFlag, centroid_share, centroidQ, timeCentroidQ,
                                  line_seen_share, oversample=3)
lineFollowTask = task_line_follow(lineEnable, base_speed, Kp_line, Ki_line,
                                  centroid_share, setpoint_L, setpoint_R,
                                  center=7.0, delta_limit=0.08, line_seen_share=line_seen_share)

bumpTask = task_bump(bump_event, bump_mode, stop_request)
courseTask = task_course(auto_start, course_mode, stop_request, bump_mode,
                         leftMotorGo, rightMotorGo, lineEnable, lineGoFlag,
                         base_speed, setpoint_L, setpoint_R,
                         left_pos, right_pos, centroid_share, line_seen_share, lineEnable)

userTask = task_user(auto_start, course_mode, stop_request,
                     leftMotorGo, rightMotorGo,
                     lineEnable, lineGoFlag,
                     base_speed, K_p, K_i, Kp_line, Ki_line,
                     bump_state,
                     setpoint_L, setpoint_R)

task_list.append(Task(leftMotorTask.run, name='Left Motor', priority=2, period=20, profile=True))
task_list.append(Task(rightMotorTask.run, name='Right Motor', priority=2, period=20, profile=True))
task_list.append(Task(lineSensorTask.run, name='Line Sensor', priority=3, period=10, profile=True))
task_list.append(Task(lineFollowTask.run, name='Line Follow', priority=3, period=10, profile=True))
task_list.append(Task(bumpTask.run, name='Bump Task', priority=4, period=10, profile=True))
task_list.append(Task(courseTask.run, name='Course Task', priority=4, period=20, profile=True))
task_list.append(Task(userTask.run, name='User Task', priority=1, period=0, profile=False))

collect()

while True:
    try:
        task_list.pri_sched()
    except KeyboardInterrupt:
        leftMotor.disable()
        rightMotor.disable()
        break

print(task_list)
print(show_all())
