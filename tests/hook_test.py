# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# coding=utf-8
"""Test claw."""
from commRaspMain import PiBot
import time, math
robot = PiBot()

if __name__ == '__main__':
    robot._servo_enable()
    time.sleep(1)
    robot._servo_two_set(35)
    time.sleep(1)

    robot._servo_one_set(27)
    time.sleep(1)
    robot._servo_two_set(22)
    time.sleep(1)
    robot._servo_two_set(35)
    time.sleep(1)
    robot._servo_one_set(35)
    time.sleep(1)
