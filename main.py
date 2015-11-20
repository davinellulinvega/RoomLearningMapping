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

except KeyboardInterrupt:
    # Shut sphero down
    sphero.shutdown()
    # Exit the program with a little message
    print("Goodbye !!! Hope to see you again soon!!!")
