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
                print("Sending command {} with arg {}".format(self.command, arg))
                self.command(arg)
                time.sleep(self.delays[i])
                print("Done!")
        i = 0
        while i < len(self.result_query):
            if callable(self.result_query[i][0]):
                if len(self.result_query[i]) == 1:
                    result = self.result_query[i][0]()
                else:
                    result = self.result_query[i][0](self.result_query[i][1])
            else:
                if len(self.result_query[i]) > 1:
                    result = self.result_query[i][0][self.result_query[i][1]]
                else:
                    result = self.result_query[i][0]
                if result is None:
                    i = -1
            if i == len(self.result_query) - 1:
                print("Measured value is: {}".format(result))
                self.logger.write(self.identifier, result)
            i += 1


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
        measure['FLL'] = [[robot.get_front_left_laser]]
        measure['FML'] = [[robot.get_front_middle_laser]]
        measure['FRL'] = [[robot.get_front_right_laser]]
        measure['RLS'] = [[robot.get_rear_left_side_ir]]
        measure['RLD'] = [[robot.get_rear_left_diagonal_ir]]
        measure['RLF'] = [[robot.get_rear_left_straight_ir]]
        measure['RRS'] = [[robot.get_rear_right_side_ir]]
        measure['RRD'] = [[robot.get_rear_right_diagonal_ir]]
        measure['RRF'] = [[robot.get_rear_right_straight_ir]]
        measure['LSL'] = [[robot.get_leftmost_line_sensor]]
        measure['LSSL'] = [[robot.get_second_line_sensor_from_left]]
        measure['LSTL'] = [[robot.get_third_line_sensor_from_left]]
        measure['LSR'] = [[robot.get_rightmost_line_sensor]]
        measure['LSSR'] = [[robot.get_second_line_sensor_from_right]]
        measure['LSTR'] = [[robot.get_third_line_sensor_from_right]]
    else:
        # Raw
        measure['FLL'] = [[robot._tof_read], [robot.tof_values, 0]]
        measure['FML'] = [[robot._tof_read], [robot.tof_values, 1]]
        measure['FRL'] = [[robot._tof_read], [robot.tof_values, 2]]
        measure['RLS'] = [[robot._adc_read, 1], [robot.sensor, 0]]
        measure['RLD'] = [[robot._adc_read, 1], [robot.sensor, 1]]
        measure['RLF'] = [[robot._adc_read, 1], [robot.sensor, 2]]
        measure['RRS'] = [[robot._adc_read, 1], [robot.sensor, 5]]
        measure['RRD'] = [[robot._adc_read, 1], [robot.sensor, 4]]
        measure['RRF'] = [[robot._adc_read, 1], [robot.sensor, 3]]
        measure['LSL'] = [[robot._adc_read, 2], [robot.sensor, 13]]
        measure['LSSL'] = [[robot._adc_read, 2], [robot.sensor, 12]]
        measure['LSTL'] = [[robot._adc_read, 2], [robot.sensor, 11]]
        measure['LSR'] = [[robot._adc_read, 2], [robot.sensor, 8]]
        measure['LSSR'] = [[robot._adc_read, 2], [robot.sensor, 9]]
        measure['LSTR'] = [[robot._adc_read, 2], [robot.sensor, 10]]

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
    for distance in [4, 8, 12]:
        suite.add("Place robot with IR left side {} cm from wall"
                  .format(distance),
                  "RLS@{}".format(distance),
                  None,
                  [], [], measure['RLS'])
        suite.add("Place robot with IR left diagonal {} cm from wall"
                  .format(distance),
                  "RLD@{}".format(distance),
                  None,
                  [], [], measure['RLD'])
        suite.add("Place robot with IR left straight {} cm from wall"
                  .format(distance),
                  "RLF@{}".format(distance),
                  None,
                  [], [], measure['RLF'])
        suite.add("Place robot with IR right side {} cm from wall"
                  .format(distance),
                  "RRS@{}".format(distance),
                  None,
                  [], [], measure['RRS'])
        suite.add("Place robot with IR right diagonal {} cm from wall"
                  .format(distance),
                  "RRD@{}".format(distance),
                  None,
                  [], [], measure['RRD'])
        suite.add("Place robot with IR right straight {} cm from wall"
                  .format(distance),
                  "RRF@{}".format(distance),
                  None,
                  [], [], measure['RRF'])
    for color in ["white", "black"]:
        suite.add("Place robot with leftmost line sensor on {}"
                  .format(color),
                  "LS leftmost@{}".format(color),
                  None,
                  [], [], measure['LSL'])
        suite.add("Place robot with second line sensor from left on {}"
                  .format(color),
                  "LS second from left@{}".format(color),
                  None,
                  [], [], measure['LSSL'])
        suite.add("Place robot with third line sensor from left on {}"
                  .format(color),
                  "LS third from left@{}".format(color),
                  None,
                  [], [], measure['LSTL'])
        suite.add("Place robot with rightmost line sensor on {}"
                  .format(color),
                  "LS rightmost@{}".format(color),
                  None,
                  [], [], measure['LSR'])
        suite.add("Place robot with second line sensor from right on {}"
                  .format(color),
                  "LS second from right@{}".format(color),
                  None,
                  [], [], measure['LSSR'])
        suite.add("Place robot with third line sensor from right on {}"
                  .format(color),
                  "LS third from right@{}".format(color),
                  None,
                  [], [], measure['LSTR'])


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
    # compass
    # motors
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
        while not all(map(lambda fn: fn(), [robot._motors_enable, robot._encoders_enable, robot._servo_enable])):
            time.sleep(0.05)
        robot._tof_init()
        robot._gyro_start()
        robot._adc_conf(3)
        suite = get_suite(robot)

        robot._motorL_set(0)
        robot._motorR_set(0)


        # robot._rotation_z
    suite.execute()


if __name__ == "__main__":
    main()
