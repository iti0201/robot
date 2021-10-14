# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from commRaspMain import PiBot
import time, os
robot = PiBot()
robot._motors_enable()
robot._encoders_enable()
robot._adc_conf(1)
robot._adc_read()


def main():
    while True:
        robot._adc_read()
        print(robot.sensor[0:6])
        time.sleep(0.02)


if __name__ == '__main__':
    main()
