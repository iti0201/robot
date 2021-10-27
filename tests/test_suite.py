"""Robot test suite."""
import sys
import os
import time
import datetime
import collections


class Log:
    """Log class for writing results into log file."""

    def __init__(self):
        """Initialize."""
        self.log = collections.OrderedDict()

    def query(self, message: str):
        """
        Query the user for input.

        Args:
          message - string to display the user and waits for input

        Returns:
          None
        """
        return input(message + " [Press ENTER to continue]")

    def write(self, identifier: str, message: str):
        """Write a message to log."""
        self.log[identifier] = message

    def dump(self, filename=None):
        """Dump the log into log file."""
        if filename is None:
            current_datetime = datetime.datetime.now()
            filename = current_datetime.strftime("results_%Y%m%d%H%M%S.csv")
        print("Writing results to \"{}\"".format(filename))
        identifiers = ""
        values = ""
        for entry in self.log.items():
            identifiers += ";" + entry[0] if len(identifiers) > 0 else str(entry[0])
            values += ";" + str(entry[1]) if len(values) > 0 else str(entry[1])
        with open(filename, 'a') as f:
            f.write(identifiers + "\n")
            f.write(values + "\n")


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
                print("Sending command {}".format(self.command))
                self.command(arg)
                time.sleep(self.delays[i])
                print("Done!")
        for i in range(len(self.result_query)):
            if callable(self.result_query[i]):
                result = self.result_query[i]()
            else:
                result = self.result_query[i]
            if i == len(self.result_query) - 1:
                print("Measured value is: {}".format(result))
                self.logger.write(self.identifier, result)


class Suite:
    """Full test suite containing multile single tests."""

    def __init__(self):
        """Initialize."""
        self.logger = Log()
        self.tests = []

    def add(self, prompt, identifier, command, args: list,
            delays: list, result_query: list):
        """Add a test to suite."""
        self.tests.append(Test(self.logger, prompt,
                               identifier, command, args,
                               delays, result_query))

    def execute(self):
        """Execute the test suite."""
        for test in self.tests:
            test.execute()
        self.logger.dump()
        print("Finished!")


def get_suite(robot):
    """
    Compile the test suite.

    Args:
      robot -- either PiBot.PiBot() or commRaspMain.PiBot()

    Returns:
      Suite instance
    """
    suite = Suite()
    measure = {}
    import PiBot
    if type(robot) == PiBot.PiBot:
        # Wrapped
        measure['FLL'] = [robot.get_front_left_laser]
        measure['FML'] = [robot.get_front_middle_laser]
        measure['FRL'] = [robot.get_front_right_laser]
    else:
        # Raw
        measure['FLL'] = [robot._tof_read, robot.tof_values[0]]
        measure['FML'] = [robot._tof_read, robot.tof_values[1]]
        measure['FRL'] = [robot._tof_read, robot.tof_values[2]]

    for distance in [10, 20, 30, 40, 50, 60]:
        suite.add("Place robot with ToF left laser {} cm from wall"
                  .format(distance),
                  "FLL@{}".format(distance),
                  None,
                  [], [], measure['FLL'])
        suite.add("Place robot with ToF middle laser {} cm from wall"
                  .format(distance),
                  "FML@{}".format(distance),
                  None,
                  [], [], measure['FML'])
        suite.add("Place robot with ToF right laser {} cm from wall"
                  .format(distance),
                  "FRL@{}".format(distance),
                  None,
                  [], [], measure['FRL'])

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
    return suite


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
                      [60, 10], [5, 5], [])
            suite.add("Clear gripper space... testing gripper open-close",
                      "gripper open-close", robot.close_grabber,
                      [80, 5], [5, 5], [])
    else:
        # Raw mode
        robot = commRaspMain.PiBot()
        suite = get_suite(robot)
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
    suite.execute()


if __name__ == "__main__":
    main()
