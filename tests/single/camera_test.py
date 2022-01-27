# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

"""Line follower bronze."""
from PiBot import PiBot
import time

robot = PiBot()
robot.set_grabber_height(10)
prev_time = robot.get_time()
for i in range(100):
    objects = robot.get_camera_objects()
    robot.set_wheels_speed(0)
    time = robot.get_time() - prev_time
    print(f"{time}: {objects}")
    prev_time = robot.get_time()
robot.set_wheels_speed(0)
