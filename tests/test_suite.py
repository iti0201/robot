# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import commRaspMain
import time

class Test:
    pass

def main():
    # F M L
    # robot.tof_values[0]
    # F L L
    # F R L
    # IR left to right
    # line sensors
    # compass
    # motors
    # gripper
    robot = commRaspMain.PiBot()
    robot._motors_enable()
    robot._encoders_enable()
    robot._servo_enable()

    robot._motorL_set(0)
    robot._motorR_set(0)

    robot._tof_init()
    robot._adc_conf(3)

    # robot._rotation_z
    while True:
        robot._update_tof_sensors()
        print("l {} m {} r {}".format(robot.tof_values[0], robot.tof_values[1], robot.tof_values[2]))
        time.sleep(0.1)

if __name__ == "__main__":
    main()
