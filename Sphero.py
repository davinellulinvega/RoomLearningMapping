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

        # Define the actor and critic
        self._actor = Network.Network(3, [10, 10], 2)
        self._critic = Network.Network(3, [10, 10], 1)

        # Configure the collision detection and data streaming
        self.config_collision_detect(0x01, (0xff / 7), 0x00, (0xff / 7), 0x00, 0x01, False)
        self.set_data_strm(15, 1, 0, 0, sphero_driver.STRM_MASK2['VELOCITY_X'] | sphero_driver.STRM_MASK2['VELOCITY_Y'] | sphero_driver.STRM_MASK2['ODOM_X'] | sphero_driver.STRM_MASK2['ODOM_Y'], False)

        # Set power notification as well (0x00: disable, 0x01: enable)
        self.set_power_notify(0x01, False)

    def on_collision(self):

    def on_position(self):

    def on_power_notify(self):
