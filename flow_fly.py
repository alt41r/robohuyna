import time
import math

import rospy

from std_msgs.msg import Float64MultiArray

from clever import srv
from std_srvs.srv import Trigger


rospy.init_node('fly')

get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry, persistent=True)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
navigate_global = rospy.ServiceProxy('navigate_global', srv.NavigateGlobal)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)
set_velocity = rospy.ServiceProxy('set_velocity', srv.SetVelocity)
# set_attitude = rospy.ServiceProxy('set_attitude', srv.SetAttitude)
# set_rates = rospy.ServiceProxy('set_rates', srv.SetRates)
land = rospy.ServiceProxy('land', Trigger)

start_velocity = 0.5
max_velocity = 1
time_to_max_velocity = 6
velocity = start_velocity

yaw_p = 0.75
y_p = 0.010
midle_yaw = 0


def up_speed():
    global velocity
    if start_time + time_to_max_velocity > time.time():
        delta_speed = (1 - (start_time + time_to_max_velocity - time.time()) / time_to_max_velocity) * (max_velocity - start_velocity)
        velocity = start_velocity + delta_speed
    else:
        velocity = max_velocity


def get_velocity(_yaw):
    up_speed()
    return velocity * (1 - abs(_yaw) / math.pi)


def yaw_to_y(_y, _yaw, method=3):
    if method == 0:
        return _y * y_p * (abs(_yaw) / math.pi)
    elif method == 1:
        return 370 * (_y * y_p * (abs(_yaw) / math.pi)) ** 4
    elif method == 2:
        return 60 * _y * y_p * (abs(_yaw) / math.pi) ** 3
    elif method == 3:
        return max(yaw_to_y(_y, _yaw, method=0), yaw_to_y(_y, _yaw, method=2), key=abs)


def yaw_msg_callback(data):
    yaw, y = data.data
    print "yaw: {}, y velocity: {}".format(yaw, y * y_p)
    y_vel = -yaw_to_y(y, yaw)
    set_velocity(vx=get_velocity(yaw), vy=y_vel, vz=0, yaw=-yaw * yaw_p, frame_id="body")
    return


navigate(x=0, y=0, z=1.2, speed=0.75, auto_arm=True, frame_id='body')
rospy.sleep(5)

print 'Subscribe'
take_yaw = rospy.Subscriber('computer_vision_sample/yaw', Float64MultiArray, yaw_msg_callback, queue_size=1)

start_time = time.time()

rospy.spin()