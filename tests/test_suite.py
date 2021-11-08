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
            identifiers += ((";" if len(identifiers) > 0 else "")
                            + str(entry[0]))
            values += ";" + str(entry[1]) if len(values) > 0 else str(entry[1])
        with open(filename, 'a') as f:
            f.write(identifiers + "\n")
            f.write(values + "\n")


class Test:
    """Test class for executing a single test."""

    def __init__(self, logger, prompt,
                 identifier, command, args, delays, result_query,
                 initial_value_query, measurement_count):
        """Initialize."""
        self.logger = logger
        self.prompt = prompt
        self.identifier = identifier
        self.command = command
        self.args = args
        self.delays = delays
        self.result_query = result_query
        self.initial_value_query = initial_value_query
        self.measurement_count = measurement_count

    def _single_measure(self, query):
        i = 0
        result = None
        while i < len(query):
            if callable(query[i][0]):
                if len(query[i]) == 1:
                    result = query[i][0]()
                else:
                    result = query[i][0](query[i][1])
            else:
                if len(query[i]) > 1:
                    result = query[i][0][query[i][1]]
                else:
                    result = query[i][0]
                if result is None:
                    i = -1
            i += 1
        return result

    def _measure(self, query):
        if len(query) == 0:
            return None
        measurements = []
        for _ in range(self.measurement_count):
            measurements.append(self._single_measure(query))
            time.sleep(0.2)
        ordered = sorted(measurements)
        return_value = ordered[(len(measurements) // 2)]
        print("Measured values are: {} returning {}".format(ordered,
                                                            return_value))
        if type(return_value) == str:
            return_value = int(return_value)
        return return_value

    def execute(self):
        """Execute the test."""
        self.logger.query(self.prompt)
        # Store the initial value if necessary
        initial_value = self._measure(self.initial_value_query)
        for i, arg in enumerate(self.args):
            if self.command is not None:
                print("Sending command {} with arg {}".format(self.command,
                                                              arg))
                self.command(arg)
                time.sleep(self.delays[i])
                print("Done!")
        final_value = self._measure(self.result_query)
        if initial_value is None:
            self.logger.write(self.identifier, final_value)
        else:
            self.logger.write(self.identifier, final_value - initial_value)


class Suite:
    """Full test suite containing multile single tests."""

    def __init__(self):
        """Initialize."""
        self.logger = Log()
        self.tests = []

    def add(self, prompt, identifier, command, args: list,
            delays: list, result_query: list,
            initial_value_query: list, measurement_count: int):
        """Add a test to suite."""
        self.tests.append(Test(self.logger, prompt,
                               identifier, command, args,
                               delays, result_query, initial_value_query,
                               measurement_count))

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
    actuate = {}
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
        measure['COMPASS'] = [[robot.get_rotation]]
        measure['LE'] = [[robot.get_left_wheel_encoder]]
        measure['RE'] = [[robot.get_right_wheel_encoder]]
        actuate['LEFT'] = robot.set_left_wheel_speed
        actuate['RIGHT'] = robot.set_right_wheel_speed
    else:
        # Raw
        measure['FLL'] = [[robot._tof_read], [robot.tof_values, 0]]
        measure['FML'] = [[robot._tof_read], [robot.tof_values, 1]]
        measure['FRL'] = [[robot._tof_read], [robot.tof_values, 2]]
        measure['RLS'] = [[robot._adc_read], [robot.sensor, 0]]
        measure['RLD'] = [[robot._adc_read], [robot.sensor, 1]]
        measure['RLF'] = [[robot._adc_read], [robot.sensor, 2]]
        measure['RRS'] = [[robot._adc_read], [robot.sensor, 5]]
        measure['RRD'] = [[robot._adc_read], [robot.sensor, 4]]
        measure['RRF'] = [[robot._adc_read], [robot.sensor, 3]]
        measure['LSL'] = [[robot._adc_read], [robot.sensor, 13]]
        measure['LSSL'] = [[robot._adc_read], [robot.sensor, 12]]
        measure['LSTL'] = [[robot._adc_read], [robot.sensor, 11]]
        measure['LSR'] = [[robot._adc_read], [robot.sensor, 8]]
        measure['LSSR'] = [[robot._adc_read], [robot.sensor, 9]]
        measure['LSTR'] = [[robot._adc_read], [robot.sensor, 10]]
        measure['COMPASS'] = [[lambda: robot._rotation_z]]
        measure['LE'] = [[robot._encoders_get], [robot.encoder, 1]]
        measure['RE'] = [[robot._encoders_get], [robot.encoder, 0]]
        actuate['LEFT'] = robot._motorL_set
        actuate['RIGHT'] = robot._motorR_set

    for distance in [10, 20, 30, 40, 50, 60]:
        suite.add("Place robot with ToF left laser {} cm from wall"
                  .format(distance),
                  "FLL@{}".format(distance),
                  None,
                  [], [], measure['FLL'], [], 5)
        suite.add("Place robot with ToF middle laser {} cm from wall"
                  .format(distance),
                  "FML@{}".format(distance),
                  None,
                  [], [], measure['FML'], [], 5)
        suite.add("Place robot with ToF right laser {} cm from wall"
                  .format(distance),
                  "FRL@{}".format(distance),
                  None,
                  [], [], measure['FRL'], [], 5)
    for distance in [4, 8, 12]:
        suite.add("Place robot with IR left side {} cm from wall"
                  .format(distance),
                  "RLS@{}".format(distance),
                  None,
                  [], [], measure['RLS'], [], 5)
        suite.add("Place robot with IR left diagonal {} cm from wall"
                  .format(distance),
                  "RLD@{}".format(distance),
                  None,
                  [], [], measure['RLD'], [], 5)
        suite.add("Place robot with IR left straight {} cm from wall"
                  .format(distance),
                  "RLF@{}".format(distance),
                  None,
                  [], [], measure['RLF'], [], 5)
        suite.add("Place robot with IR right side {} cm from wall"
                  .format(distance),
                  "RRS@{}".format(distance),
                  None,
                  [], [], measure['RRS'], [], 5)
        suite.add("Place robot with IR right diagonal {} cm from wall"
                  .format(distance),
                  "RRD@{}".format(distance),
                  None,
                  [], [], measure['RRD'], [], 5)
        suite.add("Place robot with IR right straight {} cm from wall"
                  .format(distance),
                  "RRF@{}".format(distance),
                  None,
                  [], [], measure['RRF'], [], 5)
    for color in ["white", "black"]:
        suite.add("Place robot with leftmost line sensor on {}"
                  .format(color),
                  "LS leftmost@{}".format(color),
                  None,
                  [], [], measure['LSL'], [], 5)
        suite.add("Place robot with second line sensor from left on {}"
                  .format(color),
                  "LS second from left@{}".format(color),
                  None,
                  [], [], measure['LSSL'], [], 5)
        suite.add("Place robot with third line sensor from left on {}"
                  .format(color),
                  "LS third from left@{}".format(color),
                  None,
                  [], [], measure['LSTL'], [], 5)
        suite.add("Place robot with rightmost line sensor on {}"
                  .format(color),
                  "LS rightmost@{}".format(color),
                  None,
                  [], [], measure['LSR'], [], 5)
        suite.add("Place robot with second line sensor from right on {}"
                  .format(color),
                  "LS second from right@{}".format(color),
                  None,
                  [], [], measure['LSSR'], [], 5)
        suite.add("Place robot with third line sensor from right on {}"
                  .format(color),
                  "LS third from right@{}".format(color),
                  None,
                  [], [], measure['LSTR'], [], 5)
    # Compass test
    suite.add("Clear rotation space for compass test",
              "compass",
              actuate['LEFT'],
              [20, 0], [5, 0], measure['COMPASS'], measure['COMPASS'], 3)
    # Motor tests
    speed_list = [8, 10, 12, 15, 18, 20, 24]
    speed_list = speed_list + list(map(lambda x: -x, speed_list))
    for speed in speed_list:
        suite.add("Clear space for LEFT motor test at speed {}".format(speed),
                  "left motor@{}".format(speed),
                  actuate['LEFT'],
                  [speed, 0], [4, 0], measure['LE'], measure['LE'], 1)
    for speed in speed_list:
        suite.add("Clear space for RIGHT motor test",
                  "right motor@{}".format(speed),
                  actuate['RIGHT'],
                  [speed, 0], [4, 0], measure['RE'], measure['RE'], 1)

    return suite


def main():
    """Start the program via main entry point."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 "..")))
    import commRaspMain
    import PiBot
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
                      [60, 10], [5, 5], [], [], 1)
            suite.add("Clear gripper space... testing gripper open-close",
                      "gripper open-close", robot.close_grabber,
                      [80, 5], [5, 5], [], [], 1)
    else:
        # Raw mode
        robot = commRaspMain.PiBot()
        while not all(map(lambda fn: fn(), [robot._motors_enable,
                                            robot._encoders_enable,
                                            robot._servo_enable])):
            time.sleep(0.05)
        robot._tof_init()
        robot._gyro_start()
        robot._adc_conf(3)
        suite = get_suite(robot)

        robot._motorL_set(0)
        robot._motorR_set(0)

    suite.execute()


if __name__ == "__main__":
    main()
