#!/usr/bin/pyhton
# -*- coding: UTF-8 -*-
__author__ = 'davinellulinvega'

import Network
from sphero_driver import sphero_driver

class Sphero(sphero_driver):
    """Define a child class Sphero extending the capabilities of the sphero_driver and
     initializing the instance for our purpose"""

    def __init__(self):
        """Initialize the parent class, extend the object with members and
         configure the data steaming and collision detection"""

        # Initialize the parent class
        sphero_driver.Sphero.__init__(self)
        # Members
        self._x = 0
        self._y = 0
        self._speed_x = 0
        self._speed_y = 0
        self._power = 2
        self._collided = False
        self._collision_pos = set()

        # Define the actor and critic
        self._actor = Network.Network(3, [10, 10], 2)
        self._critic = Network.Network(3, [10, 10], 1)

        # Configure the collision detection and data streaming
        self.config_collision_detect(0x01, (0xff / 7), 0x00, (0xff / 7), 0x00, 0x01, False)
        self.set_data_strm(15, 1, 0, 0, sphero_driver.STRM_MASK2['VELOCITY_X'] | sphero_driver.STRM_MASK2['VELOCITY_Y'] | sphero_driver.STRM_MASK2['ODOM_X'] | sphero_driver.STRM_MASK2['ODOM_Y'], False)

        # Set power notification as well (0x00: disable, 0x01: enable)
        self.set_power_notify(0x01, False)

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
