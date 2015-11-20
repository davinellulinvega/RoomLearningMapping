#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'davinellulinvega'

import Network
from sphero_driver import sphero_driver
import ast
import math
from pickle import Pickler


class Sphero(sphero_driver.Sphero):
    """Define a child class Sphero extending the capabilities of the sphero_driver.Sphero"""

    def __init__(self):
        """Initialize the parent class and extend the object with members"""

        # Initialize the parent class
        sphero_driver.Sphero.__init__(self, target_addr="68:86:E7:06:30:CB")
        # Members
        self._x = 0
        self._y = 0
        self._speed_x = 0
        self._speed_y = 0
        self._power = 2
        self._collided = False
        self._collision_pos = set()

        # Initialize the set of collision positions
        self.load_collision_pos()

        # Define the actor and critic
        self._actor = Network.Network(3, [10, 10], 2)
        self._critic = Network.Network(3, [10, 10], 1)

    def configure(self):
        """
        Configure the the data streaming, collision detection and power notification
        :return: Nothing
        """

        # Check that the robot is connected before anything
        if self.is_connected:
            # Configure the collision detection and data streaming
            self.config_collision_detect(0x01, (0xff / 7), 0x00, (0xff / 7), 0x00, 0x01, False)
            self.set_data_strm(15, 1, 0, 0,
                               sphero_driver.STRM_MASK2['VELOCITY_X'] | sphero_driver.STRM_MASK2['VELOCITY_Y'] |
                               sphero_driver.STRM_MASK2['ODOM_X'] | sphero_driver.STRM_MASK2['ODOM_Y'], False)

            # Set power notification as well (0x00: disable, 0x01: enable)
            self.set_power_notify(0x01, False)

            # Add the different callbacks to the processing of their respective data
            self.add_async_callback(sphero_driver.IDCODE['DATA_STRM'], self.on_position_speed)
            self.add_async_callback(sphero_driver.IDCODE['COLLISION'], self.on_collision)
            self.add_async_callback(sphero_driver.IDCODE['PWR_NOTIFY'], self.on_power_notify)

    def on_collision(self, data):
        """
        This function is a callback for the collision detected event and only changes the value of the collided member
        And record the position of the collision for mapping purposes
        :param data: Information on the magnitude and speed of the collision on each axis
        :return: Nothing
        """

        # Simply set the collided member to True
        self._collided = True
        # And record the position
        self._collision_pos.add((data['X'], data['Y'], data['Z']))

    def check_collision_status(self, speed_thres):
        """
        If the robot collided with an object of large proportions, this function checks that the robot is not in contact
        with the object any more, relying on the speed of the robot.
        :param speed_thres: an integer between 0 and 255. If the overall speed of the robot is greater than this
        threshold, it is considered not in contact with an object any more.
        :return: Nothing
        """

        # Compute the overall speed of the robot
        speed = math.sqrt((self._speed_x**2 + self._speed_y**2))

        # Check if the robot previously collided with something and has a speed over the threshold
        if self._collided and speed > speed_thres:
            self._collided = False

    def on_position_speed(self, data):
        """
        This function is a callback for the streaming of position and speed information.
        :param data: A dictionary containing all the requested information
        :return: Nothing
        """

        # Simply assign the values to the corresponding members
        self._x = data['ODOM_X']
        self._y = data['ODOM_Y']
        self._speed_x = data['VELOCITY_X']
        self._speed_y = data['VELOCITY_Y']

    def on_power_notify(self, data):
        """
        This function is a callback for the power notification and simply assign the requested data to the power member
        :param data: A dictionary containing the power information
        :return: Nothing
        """

        # Assign the data to the power member
        self._power = data['STATE']

    def dump_collision_pos(self):
        """
        A simple function that writes the positions of the collisions in a file
        :return: Nothing
        """

        # Just open a file in write mode and dump all the data
        with open("Data/collision_position.dat", "w") as dat_file:
            for elem in self._collision_pos:
                dat_file.write(str(elem) + "\n")

    def load_collision_pos(self):
        """
        A Simple function that loads the positions of the previously recorded collision
        :return: Nothing
        """

        try:
            # Open the pre-defined file
            with open("Data/collision_position.dat", "r") as dat_file:
                # Read a line
                lines = dat_file.readlines()
                # Convert each line into a tuple and insert it into the set
                for str_line in lines:
                    line = ast.literal_eval(str_line)
                    self._collision_pos.add(line)
        except IOError:
            print("No previously recorded data on positions for collision")

    def dump_brain(self):
        """
        Record the configuration of the actor and critic into a binary file.
        :return: Nothing
        """

        # Open the file for writing in binary mode
        with open("Config/actor.cfg", "wb") as cfg_file:
            # Instantiate a pickler
            pickle = Pickler(cfg_file)
            # Dump the configuration
            pickle.dump(self._actor)

        # Repeat the operation for the critic
        with open("Config/critic.cfg", "wb") as cfg_file:
            pickle = Pickler(cfg_file)
            pickle.dump(self._critic)


if __name__ == "__main__":
    # Create an instance of the Sphero class
    sphero = Sphero()
    # Connect to the robot
    sphero.connect()
    # Configure the robot
    sphero.configure()
    # Start a new thread for processing asynchronous data
    sphero.start()

    # Your tests here

    # Disconnect from the robot (aka close the bluetooth socket)
    sphero.disconnect()
    # Wait for all processes to finish
    sphero.join()
