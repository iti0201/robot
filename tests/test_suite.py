"""Robot test suite."""
import sys
import os
import time
import datetime


class Log:
    """Log class for writing results into log file."""

    def __init__(self):
        """Initialize."""
        self.log = []

    def query(self, message: str):
        """
        Query the user for input.

        Args:
          message - string to display the user

        Returns:
          None
        """
        pass

    def write(self, message: str):
        """Write a message to log."""
        print(message)
        self.log.append(message)

    def dump(self, filename=None):
        """Dump the log into log file."""
        if filename is None:
            current_datetime = datetime.datetime.now()
            filename = current_datetime.strftime("results_%Y%m%d%H%M%S.csv")
        with open(filename) as f:
            for line in self.log:
                f.write(line + "\n")


class Test:
    """Test class for executing a single test."""

    def __init__(self, logger, prompt,
                 identifier, command, args, delays, result_query):
        """Initialize."""
        self.logger = logger
        self.prompt = prompt
        self.identifier = identifier
        self.command = command
        self.args = args
        self.delays = delays
        self.result_query = result_query

    def execute(self):
        """Execute the test."""
        self.logger.query(self.prompt)
        for i, arg in enumerate(self.args):
            if self.command is not None:
                self.command(arg)
                time.sleep(self.delays[i])
                print("Done!")
                if self.result_query is not None:
                    result = self.result_query()
                    self.logger.write("Result = {}".format(result))


class Suite:
    """Full test suite containing multile single tests."""

    def __init__(self):
        """Initialize."""
        self.logger = Log()
        self.tests = []

    def add(self, prompt, identifier, command, args, delays, result_query):
        """Add a test to suite."""
        self.tests.append(Test(self.logger, prompt,
                               identifier, command, args,
                               delays, result_query))


def get_suite(robot):
    """Compile a test suite."""
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
    pass


def main():
    """Start the program via main entry point."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 "..")))
    import commRaspMain
    import PiBot
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
    if input("Mode 0=raw / 1=wrapper: ? [0]") == "1":
        # Wrapped mode
        try:
            number = os.environ["ROBOT_ID"]
        except KeyError:
            number = int(input("Enter robot number (1-5):"))
        robot = PiBot.PiBot(robot_nr=number, directory="../")
        suite = get_suite(robot)
        gripper = input("Include gripper tests (0=no, 1=yes)? [1]")
        if gripper != "0":
            suite.add("Clear gripper space... testing gripper up-down",
                      "gripper up-down", robot.set_grabber_height,
                      [60, 10], [5, 5], None)
            suite.add("Clear gripper space... testing gripper open-close",
                      "gripper open-close", robot.close_grabber,
                      [80, 5], [5, 5], None)
        time.sleep(8)

        sys.exit()
    else:
        # Raw mode
        suite = get_suite(robot)
        robot = commRaspMain.PiBot()
        robot._motors_enable()
        robot._encoders_enable()
        robot._servo_enable()

        robot._motorL_set(0)
        robot._motorR_set(0)

        robot._tof_init()
        robot._adc_conf(3)

        # robot._rotation_z
        # while True:
        #    robot._tof_read()
        #    print("l {} m {} r {}".format(robot.tof_values[0],
        #                                  robot.tof_values[1],
        #                                  robot.tof_values[2]))
        #    time.sleep(0.1)


if __name__ == "__main__":
    main()
