# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import commRaspMain
import PiBot
import time

class Log:
    def __init__(self):
        self.log = []

    def write(self, message: str):
        print(message)
        self.log.append(message)

    def dump(self, filename="test_results.log"):
        with open(filename) as f:
            for line in self.log:
                f.write(line + "\n")

class Test:
    def __init__(self, logger, prompt):
        self.logger = logger
        self.logger(prompt)
        
    def execute(self):
        pass

def main():
    # Place robot with ToF left laser 30 cm from wall
    # Place robot with ToF middle laser 30 cm from wall
    # Place robot with ToF right laser 30 cm from wall
    # Place robot with ToF left laser 50 cm from wall
    # Place robot with ToF middle laser 50 cm from wall
    # Place robot with ToF right laser 50 cm from wall

    # Place robot with IR left side 5 cm from wall
    # Place robot with IR left diagonal 5 cm from wall
    # Place robot with IR left rear 5 cm from wall
    # Place robot with IR right side 5 cm from wall
    # Place robot with IR right diagonal 5 cm from wall
    # Place robot with IR right rear 5 cm from wall

    # Place robot with with line sensors on white
    # Place robot with with line sensors on black

    # Testing compass by rotating 360 degrees

    # Place robot in free space... testing left motor 
    # Place robot in free space... testing right motor 

    # Clear gripper space... testing gripper up-down
    # Clear gripper space... testing gripper open-close

    # F L L
    # robot.tof_values[0]
    # F M L
    # robot.tof_values[1]
    # F R L
    # robot.tof_values[2]
    # IR left to right
    # line sensors
    # compass
    # motors
    # gripper
    try:
        number = os.environ["ROBOT_ID"]
    except:
        number = int(input("Enter robot number (1-5):"))
    # Do raw mode first...
    robot = commRaspMain.PiBot()
    robot._motors_enable()
    robot._encoders_enable()
    robot._servo_enable()

    robot._motorL_set(0)
    robot._motorR_set(0)

    robot._tof_init()
    robot._adc_conf(3)

    # robot._rotation_z
    #while True:
    #    robot._tof_read()
    #    print("l {} m {} r {}".format(robot.tof_values[0], robot.tof_values[1], robot.tof_values[2]))
    #    time.sleep(0.1)

    # Switch to non-raw
    time.sleep(1)
    robot = PiBot.PiBot(number)
    time.sleep(8)

if __name__ == "__main__":
    main()
