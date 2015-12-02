#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'davinellulinvega'

import Sphero

# Instantiate a Sphero object
sphero = Sphero.Sphero(False, [10], [10])

# Connect to the robot
sphero.connect()

# Configure the robot
sphero.initialize()

# Start a second thread for processing async data
sphero.start()

try:
    # Initialize the power status
    power = sphero.get_power_status()

    # While the sphero robot does not need to be plugged in
    while power < 4:
        # Get the value of the present state
        state_o = sphero.get_state_value()

        # Get the parameters for the next roll
        speed, heading = sphero.get_roll_params(0xff)

        # Roll according to the parameters
        sphero.roll(speed, heading, 0x01, False)  # The third parameter is the state: 0x00->breaking, 0x01->driving

        # Get the value of the new state
        state_n = sphero.get_state_value()

        # Have the actor and the critic learn
        sphero.learn(state_n, state_o, 0.7, 0.001)

        # Reset the collision status
        sphero.reset_collision()

        # Query the power status
        power = sphero.get_power_status()

    # Shut the robot down
    print("Sphero feels a bit tired.\nShutting down ...")
    sphero.unload()

except KeyboardInterrupt:
    print("\nThe user has requested the program to stop.\nStopping the program ...")
    # Shut sphero down
    sphero.unload()

# Exit the program with a little message
print("Goodbye !!! Hope to see you again soon!!!")
