import math

from commRaspMain import PiBot as PiBotBase
from abc import ABC as AbstractBaseClass
from abc import abstractmethod
import time


def pv(**kwargs):
    for key in kwargs:
        print(str(key) + ":", kwargs[key])


class SensorConverter(AbstractBaseClass):
    @abstractmethod
    def get(self, x: int) -> float:
        pass

    @staticmethod
    def make_converters(file_path: str) -> list:
        """
            2
        1      3

        4      9
         5    8
          6  7
        :param file_path:
        :return: [SharpSensorConverter] + [IRSensorConverter]
        """
        converters = []

        with open(file_path, 'r') as file:
            for _ in range(3):
                line = file.readline()
                a, b, c, d, e = map(float, line.split())
                converters.append(SharpSensorConverter(a, b, c, d, e))
            for _ in range(6):
                line = file.readline()
                a, b = map(float, line.split())
                converters.append(IRSensorConverter(a, b))

        return converters


class SharpSensorConverter(SensorConverter):
    def __init__(self, a, b, c, d, e):
        self.e = e
        self.d = d
        self.c = c
        self.b = b
        self.a = a

    def get(self, x: int) -> float:
        value = self.a + (self.b - self.a) / ((1 + (x / self.c) ** self.d) ** self.e)
        return value / 100


class IRSensorConverter(SensorConverter):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, x: int) -> float:
        value = (self.a * x) / (self.b + x)
        return value / 100


def validate_speed_percentage_arg(i: int):
    def validate_speed_percentage(speed_function):
        def validate_percentage(*args):
            percentage = args[i]
            if not -99 <= percentage <= 99:
                raise ValueError("Speed percentage must be in range -99 .. 99")
            return speed_function(*args)

        return validate_percentage

    return validate_speed_percentage


def validate_speed_percentage(speed_function):
    return validate_speed_percentage_arg(1)(speed_function)


class PiBot(PiBotBase):
    def __init__(self, robot_nr):
        super().__init__()

        # Converters
        self.converters = SensorConverter.make_converters("converters{}.txt".format(robot_nr))
        self.front_left_ir_converter, \
        self.front_middle_ir_converter, \
        self.front_right_ir_converter, \
        self.rear_left_straight_ir_converter, \
        self.rear_left_diagonal_ir_converter, \
        self.rear_left_side_ir_converter, \
        self.rear_right_straight_ir_converter, \
        self.rear_right_diagonal_ir_converter, \
        self.rear_right_side_ir_converter = self.converters

        # Initialize robot
        self._motors_enable()
        self._encoders_enable()
        self._servo_enable()
        self.set_grabber_height(100)
        self.close_grabber(100)
        self._adc_conf(3)

        # Initialize timestamps
        self.first_block_last_update = 0
        self.second_block_last_update = 0
        self.sensors_last_update = 0

        # Constants
        self.UPDATE_TIME = 0.005
        self.SENSOR_LIMITS = [(100, 1000)] * 6 + [(50, 800)] * 2 + [(0, 1023)] * 6 + [(50, 800)]
        self.WHEEL_DIAMETER = 0.025
        self.TICK_PER_DEGREE = 1

    def set_update_time(self, update_time):
        self.UPDATE_TIME = update_time

    def _sensor_values_correct(self, start: int = 0, end: int = 15) -> bool:
        for i, value in enumerate(self.sensor[start:end]):
            if value is None:  # or value not in range(self.SENSOR_LIMITS[i][0], self.SENSOR_LIMITS[i][1] + 1):
                return False
        return True

    def _update_first_sensor_block(self):
        timestamp = time.time()
        if timestamp - self.first_block_last_update >= self.UPDATE_TIME:
            self._adc_read(1)
            while not self._sensor_values_correct(0, 8):
                self._adc_read(1)
            self.first_block_last_update = timestamp

    def _update_second_sensor_block(self):
        timestamp = time.time()
        if timestamp - self.second_block_last_update >= self.UPDATE_TIME:
            self._adc_read(2)
            while not self._sensor_values_correct(8, 15):
                self._adc_read(2)
            self.second_block_last_update = timestamp

    def _update_sensors(self):
        timestamp = time.time()
        if timestamp - self.sensors_last_update >= self.UPDATE_TIME:
            self._adc_read()
            while not self._sensor_values_correct():
                self._adc_read()
            self.sensors_last_update = timestamp

    def _update_sensor_block(self, block_nr):
        if block_nr == 1:
            self._update_first_sensor_block()
        elif block_nr == 2:
            self._update_second_sensor_block()
        else:
            self._update_sensors()

    def get_value_or_none_from_converter(self, converter, sensor_value, sensor_block_nr):
        try:
            value = converter.get(sensor_value)
        except OverflowError:
            value = None
            self._adc_read(sensor_block_nr)
        return value

    def get_value_from_converter(self, converter, sensor_index, sensor_block_nr):
        value = None
        self._update_sensor_block(sensor_block_nr)
        while value is None:
            value = self.get_value_or_none_from_converter(converter, self.sensor[sensor_index], sensor_block_nr)
        return value

    def get_front_left_ir(self) -> float:
        return self.get_value_from_converter(self.front_left_ir_converter, 14, 2)

    def get_front_middle_ir(self) -> float:
        return self.get_value_from_converter(self.front_middle_ir_converter, 7, 1)

    def get_front_right_ir(self) -> float:
        return self.get_value_from_converter(self.front_right_ir_converter, 6, 1)

    def get_front_irs(self) -> [float]:
        return [self.get_front_left_ir(), self.get_front_middle_ir(), self.get_front_right_ir()]

    def get_rear_left_straight_ir(self) -> float:
        return self.get_value_from_converter(self.rear_left_straight_ir_converter, 2, 1)

    def get_rear_left_diagonal_ir(self) -> float:
        return self.get_value_from_converter(self.rear_left_diagonal_ir_converter, 1, 1)

    def get_rear_left_side_ir(self) -> float:
        return self.get_value_from_converter(self.rear_left_side_ir_converter, 0, 1)

    def get_rear_right_straight_ir(self) -> float:
        return self.get_value_from_converter(self.rear_right_straight_ir_converter, 3, 1)

    def get_rear_right_diagonal_ir(self) -> float:
        return self.get_value_from_converter(self.rear_right_diagonal_ir_converter, 4, 1)

    def get_rear_right_side_ir(self) -> float:
        return self.get_value_from_converter(self.rear_right_side_ir_converter, 5, 1)

    def get_rear_irs(self) -> [float]:
        return [
            self.get_rear_left_side_ir(), self.get_rear_left_diagonal_ir(), self.get_rear_left_straight_ir(),
            self.get_rear_right_straight_ir(), self.get_rear_right_diagonal_ir(), self.get_rear_right_side_ir()
        ]

    def get_irs(self) -> [float]:
        return self.get_front_irs() + self.get_rear_irs()

    def get_leftmost_line_sensor(self) -> int:
        self._update_second_sensor_block()
        return self.sensor[8]

    def get_second_line_sensor_from_left(self) -> int:
        self._update_second_sensor_block()
        return self.sensor[9]

    def get_third_line_sensor_from_left(self) -> int:
        self._update_second_sensor_block()
        return self.sensor[10]

    def get_rightmost_line_sensor(self) -> int:
        self._update_second_sensor_block()
        return self.sensor[13]

    def get_second_line_sensor_from_right(self) -> int:
        self._update_second_sensor_block()
        return self.sensor[12]

    def get_third_line_sensor_from_right(self) -> int:
        self._update_second_sensor_block()
        return self.sensor[11]

    @validate_speed_percentage
    def set_left_wheel_speed(self, percentage: int):
        """
        :param percentage: -99 .. 99
        """
        self._motorR_set(-percentage)

    @validate_speed_percentage
    def set_right_wheel_speed(self, percentage: int):
        """
        :param percentage: -99 .. 99
        """
        self._motorL_set(-percentage)

    @validate_speed_percentage
    def set_wheels_speed(self, percentage: int):
        """
        :param percentage: -99 .. 99
        """
        self._motorB_set(-percentage)

    def _update_encoders(self):
        while not self._encoders_get() or any(map(lambda encoder: encoder is None, self.encoder)):
            pass

    def get_right_wheel_encoder(self) -> int:
        self._update_encoders()
        return -int(self.encoder[0])

    def get_left_wheel_encoder(self) -> int:
        self._update_encoders()
        return -int(self.encoder[1])

    def _get_encoders_mean(self):
        return (self.get_right_wheel_encoder() + self.get_left_wheel_encoder()) / 2

    @staticmethod
    def limit_speed(speed):
        """
        :param speed: speed percentage
        :return: speed percentage limited to range -99 .. 99
        """
        return max(-99, min(99, speed))

    @validate_speed_percentage
    def move(self, speed_percentage: int, distance: float):
        """
        Move forward by distance
        :param speed_percentage: -99 .. 99
        :param distance: meters
        """
        DIFFERENCE_LIMIT = 10

        wheel_circumference = math.pi * self.WHEEL_DIAMETER
        right_wheel_speed = left_wheel_speed = speed_percentage

        right_wheel_encoder_start = self.get_right_wheel_encoder()
        left_wheel_encoder_start = self.get_left_wheel_encoder()

        distance_in_degrees = ((distance / wheel_circumference) * 360 * self.TICK_PER_DEGREE) / 3

        right_wheel_encoder_goal = right_wheel_encoder_start + distance_in_degrees
        left_wheel_encoder_goal = left_wheel_encoder_start + distance_in_degrees

        initial_difference = self.get_right_wheel_encoder() - self.get_left_wheel_encoder()

        self.set_wheels_speed(speed_percentage)

        change = 0.5

        while self.get_right_wheel_encoder() < right_wheel_encoder_goal \
                and self.get_left_wheel_encoder() < left_wheel_encoder_goal:

            right_left_difference = self.get_right_wheel_encoder() - self.get_left_wheel_encoder() - initial_difference
            left_right_difference = -right_left_difference

            if right_left_difference > DIFFERENCE_LIMIT:
                right_wheel_speed -= change
                left_wheel_speed += change
            elif left_right_difference > DIFFERENCE_LIMIT:
                left_wheel_speed -= change
                right_wheel_speed += change
            else:
                right_wheel_speed = left_wheel_speed = speed_percentage

            right_wheel_speed = PiBot.limit_speed(right_wheel_speed)
            left_wheel_speed = PiBot.limit_speed(left_wheel_speed)
            self.set_right_wheel_speed(right_wheel_speed)
            self.set_left_wheel_speed(left_wheel_speed)

        self.set_wheels_speed(0)

    def set_grabber_height(self, height_percentage):
        """
        :param height: 0 .. 100
        :return:
        """
        y = -0.12 * height_percentage + 42
        self._servo_two_set(y)

    def close_grabber(self, percentage):
        """
        :param percentage: 0 .. 100
        :return:
        """
        y = -0.11 * percentage + 36
        self._servo_one_set(y)
