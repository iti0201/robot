# coding=utf-8

"""Drive with encoder and magnetometer data."""

from commRaspMain import PiBot

import time, math



# One encoder does 155 signals per rotation, encoders are reversed

class Robot:



    def __init__(self):

        self.robot = PiBot()

        self.robot._motors_enable()

        self.robot._encoders_enable()

        self.WHEEL_DIAMETER = 0.03 #meters

        self.CIRCUMFERENCE = self.WHEEL_DIAMETER * math.pi

        self.SIGNALS_PER_ROTATION = 155

        self.AXIS_LENGTH = 0.132



    def go_straight(self, speed):

        self.robot._motorB_set(speed)



    """

    Controller for more predictabilit

    goal: Distance to goal

    error: Error between the goal and reference value

    """

    def controller(self):

        pass



    def turn_right_by_degrees(self, degrees, speed, turn_right):

        # Üks ratas peab liikuma 90-kraadise pööramise jaoks 0.101265 m, kui üks täisring on ühel rattal 0.40506m 360-kraadise pöörde jaoks

        # Kui turn_right on True, siis pöörab paremale, else vasakule

        full_circle = 0.40506

        self.robot._encoders_enable()

        self.robot._encoders_get()

        final_distance = (degrees / 360) * full_circle

        average_encoder = abs(float(self.robot.encoder[0]))

        encoder_distance = (average_encoder * self.CIRCUMFERENCE) / self.SIGNALS_PER_ROTATION

        while abs(encoder_distance) < final_distance:

            print("Final distance is: " + str(final_distance))

            print("Encoder distance is: " + str(encoder_distance))

            if turn_right:

                self.adjust_to_right(speed)

            else:

                self.adjust_to_left(speed)

            self.robot._encoders_get()

            two_encoders = abs(float(self.robot.encoder[0])) + abs(float(self.robot.encoder[1]))

            average_encoder = two_encoders / 2

            encoder_distance = (average_encoder * self.CIRCUMFERENCE) / self.SIGNALS_PER_ROTATION

            time.sleep(0.05)

        print("Encoders have travelled: " + str(encoder_distance))

        self.robot._motorB_set(0)





    """Drive straight with a certain speed for a certain distance"""

    def drive_straight_by_distance(self, speed, distance): # Distance in meters

        total_distance = 0.0

        self.robot._encoders_enable()

        self.robot._encoders_get()

        while total_distance < distance:

            while True:

                if -float(self.robot.encoder[0]) < -float(self.robot.encoder[1]) - 1.0 or -float(self.robot.encoder[0]) > -float(self.robot.encoder[1]):

                    break

                print("Total distance is: " + str(total_distance))

                print("Going straight")

                self.robot._motorB_set(speed)

                encoder_clicks = (-float(self.robot.encoder[0]) + (-float(self.robot.encoder[1]))) / 2

                total_distance = (encoder_clicks * self.CIRCUMFERENCE) / self.SIGNALS_PER_ROTATION

                self.robot._encoders_get()

                time.sleep(0.1)

            if -float(self.robot.encoder[1]) - 1.0 > -float(self.robot.encoder[0]):

                self.robot._encoders_get()

                while -float(self.robot.encoder[1]) > -float(self.robot.encoder[0]):

                    print("Adjusting left")

                    self.adjust_to_left(11)

                    time.sleep(0.05)

                    self.robot._encoders_get()

            else:

                self.robot._encoders_get()

                while -float(self.robot.encoder[0]) > -float(self.robot.encoder[1]):

                    print("Adjusting right")

                    self.adjust_to_right(11)

                    time.sleep(0.05)

                    self.robot._encoders_get()

        self.robot._motorB_set(0)



    def adjust_to_left(self, speed):

        self.robot._motorL_set(-speed)

        self.robot._motorR_set(speed)



    def adjust_to_right(self, speed):

        self.robot._motorR_set(-speed)

        self.robot._motorL_set(speed)



    def main(self):

        self.drive_straight_by_distance(12, 0.39)

        print("Left encoder is: " + str(self.robot.encoder[0]))

        print("Right encoder is: " + str(self.robot.encoder[1]))

        time.sleep(0.5)



        self.turn_right_by_degrees(90, 11, True)

        print("Left encoder is: " + str(self.robot.encoder[0]))

        print("Right encoder is: " + str(self.robot.encoder[1]))

        time.sleep(0.5)



        self.drive_straight_by_distance(11, 0.525)

        time.sleep(0.5)



        self.turn_right_by_degrees(46, 11, False)

        time.sleep(0.5)



        self.drive_straight_by_distance(11, 0.19)

        time.sleep(0.5)



        self.turn_right_by_degrees(92, 11, False)

        time.sleep(0.5)



        self.drive_straight_by_distance(11, 0.2)

        time.sleep(0.5)

        self.robot._motorB_set(0)

        print("GG EZ")





if __name__ == '__main__':

    robot = Robot()

    robot.main()
