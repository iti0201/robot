# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PiBot import PiBot

def up(r):
    r.set_grabber_height(60)
    r.close_grabber(80) # UPDOWN

def grab(r):
    r.set_grabber_height(60)
    r.close_grabber(5)

def open(r):
    r.set_grabber_height(10)
    r.close_grabber(5)

def grab_test(r):
    grab(r)
    r.sleep(2)
    up(r)
    r.set_wheels_speed(11)
    r.sleep(8)
    open(r)
    r.set_wheels_speed(0)


if __name__ == "__main__":
    robot = PiBot()
    robot.set_wheels_speed(0)
    #grab_test(robot)
    while True:
        print("l {}  m {}  r {}".format(robot.get_front_left_laser(), robot.get_front_middle_laser(), robot.get_front_right_laser()))
        robot.sleep(0.2)
