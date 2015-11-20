#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'davinellulinvega'

import Sphero

# Instantiate a Sphero object
sphero = Sphero.Sphero(True, [10, 10], [10, 10])

# Connect to the robot
sphero.connect()

# Configure the robot
sphero.configure()

# Start a second thread for processing async data
sphero.start()

try:
    # Initialize the power status
    power = sphero.get_power_status()

    # While the sphero robot does not need to be plugged in
    while power < 4:
        # Get the parameters for the next roll
        speed, heading = sphero.get_roll_params(255 / 4)
        # Roll according to the parameters
        sphero.roll(speed, heading, 0x01, False)  # The third parameter is the state: 0x00->breaking, 0x01->driving
        # Check if the robot is still colliding with an object
        sphero.check_collision_status(10)


        # Query the power status
        power = sphero.get_power_status()

    # Shut the robot down
    print("Sphero feels a bit tired.\nShutting down ...")
    sphero.shutdown()

except KeyboardInterrupt:
    print("The user has requested the program to stop.\nStopping the program ...")
    # Shut sphero down
    sphero.shutdown()

# Exit the program with a little message
print("Goodbye !!! Hope to see you again soon!!!")