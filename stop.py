from PiBot import PiBot

import time

if __name__ == "__main__":
    while True:
        try:
            robot = PiBot()
            robot.set_wheels_speed(0)
            break
        except Exception as e:
            time.sleep(1)
            continue
