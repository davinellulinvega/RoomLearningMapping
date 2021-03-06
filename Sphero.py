#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'davinellulinvega'

import Network
import sphero_driver
import ast
import math
from pickle import Pickler
from pickle import Unpickler
import threading


class Sphero(sphero_driver.Sphero):
    """Define a child class Sphero extending the capabilities of the sphero_driver.Sphero"""

    def __init__(self, reload_brain=False, hid_act=[1], hid_crit=[1]):
        """
        Extend the parent Class with some members, initialize them and return an instance of the Sphero class
        :param reload_brain: Whether to reload the actor and critic from the configuration files or not.
        True: reload, False: forget it (default)
        :param hid_act: A list describing the number of neurons to implement for each hidden layer in the actor
        Defaults to one hidden layer with one neuron.
        :param hid_crit: A list describing the number of neurons to implement for each hidden layer in the critic
        Defaults to one hidden layer with one neuron.
        :return: An initialized instance of the class Sphero
        """

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
        self._path_length = 0

        # Initialize the set of collision positions
        self.load_collision_pos()

        # Initialize the actor and critic
        self._actor = None
        self._critic = None
        loaded = True
        # If required from the configuration files
        if reload_brain:
            loaded = self.load_brain()

        # If not required or if reading the configuration files failed
        if not (reload_brain and loaded):
            self._actor = Network.Network(2, hid_act, 2)
            self._critic = Network.Network(2, hid_crit, 1)

    def initialize(self):
        """
        Configure the the data streaming, collision detection and power notification
        :return: Nothing
        """

        # Check that the robot is connected before anything
        if self.is_connected:
            # Configure the collision detection and data streaming
            self.config_collision()
            self.set_data_strm(40, 1, 0, 0,
                               sphero_driver.STRM_MASK2['VELOCITY_X'] | sphero_driver.STRM_MASK2['VELOCITY_Y'] |
                               sphero_driver.STRM_MASK2['ODOM_X'] | sphero_driver.STRM_MASK2['ODOM_Y'], False)

            # Set power notification as well (0x00: disable, 0x01: enable)
            self.set_power_notify(0x01, False)

            # Add the different callbacks to the processing of their respective data
            self.add_async_callback(sphero_driver.IDCODE['DATA_STRM'], self.on_position_speed)
            self.add_async_callback(sphero_driver.IDCODE['COLLISION'], self.on_collision)
            self.add_async_callback(sphero_driver.IDCODE['PWR_NOTIFY'], self.on_power_notify)

            # Switch the back led on
            self.set_back_led(255, False)

    def config_collision(self):
        """
        A function to dynamically adapt the configuration of the collision detection
        :return: Nothing
        """

        # If the robot is bellow a speed of 10
        if self._speed_x < 30:
            # Assign some fix values that should not trigger a collision just by moving around
            amp_x = 10
            speed_x = 20
        else:
            # If the speed is high enough we assign dynamic values based on the speed
            speed_x = int(self._speed_x * 0.3)
            amp_x = int(self._speed_x * 0.2)

        # The same processing applies on the Y axis
        if self._speed_y < 30:
            # Assign some fix values that should not trigger a collision just by moving around
            amp_y = 10
            speed_y = 20
        else:
            # If the speed is high enough we assign dynamic values based on the speed
            speed_y = int(self._speed_y * 0.3)
            amp_y = int(self._speed_y * 0.2)

        # Finally send the configuration to the robot
        self.config_collision_detect(0x01, amp_x, speed_x, amp_y, speed_y, 0x01, False)

    def on_collision(self, data):
        """
        This function is a callback for the collision detected event. It changes the value of the collided member
        and the speed on both axis. And record the position of the collision for mapping purposes
        :param data: Information on the magnitude and speed of the collision on each axis
        :return: Nothing
        """

        # Simply set the collided member to True
        self._collided = True
        # Set the speed on both the x and y axis to 0
        self._speed_x = 0
        self._speed_y = 0
        # And record the position
        self._collision_pos.add((data['X'], data['Y'], data['Z']))

    def reset_collision(self, speed_x=30, speed_y=30):
        """
        Check if the robot is still in contact with the object through speed measurements and reset the collision state
        accordingly
        :return: Nothing
        """

        # Check the speed of the robot on both axis
        if abs(self._speed_x) > speed_x and abs(self._speed_y) > speed_y:
            # Assign False to the _collided member
            self._collided = False

    def on_position_speed(self, data):
        """
        This function is a callback for the streaming of position and speed information.
        :param data: A dictionary containing all the requested information
        :return: Nothing
        """

        # Simply assign the values to the corresponding members
        self._x = data['ODOM_X'] / 100
        self._y = data['ODOM_Y'] / 100
        self._speed_x = data['VELOCITY_X']
        self._speed_y = data['VELOCITY_Y']

    def on_power_notify(self, data):
        """
        This function is a callback for the power notification and simply assign the requested data to the power member
        :param data: A dictionary containing the power information
        :return: Nothing
        """

        # Assign the data to the power member
        self._power = data

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

    def load_brain(self):
        """
        Load the actor and critic's configurations from the corresponding files.
        :return: True if configuration loaded, False otherwise
        """

        try:
            # Open the file
            with open("Config/actor.cfg", "rb") as cfg_file:
                # Instantiate an Unpickler
                unpickle = Unpickler(cfg_file)
                # Load the object
                self._actor = unpickle.load()

            # Repeat the operation for the actor
            with open("Config/critic.cfg", "rb") as cfg_file:
                unpickle = Unpickler(cfg_file)
                self._critic = unpickle.load()

            # Return True because everything up to this point went well
            return True

        except IOError as error:
            # Display a message detailing the error
            print("No prevously recorded actor and/or critic configuration")
            # Return False to warn that something bad happened, leaving the actor and critic in an unknown state
            return False

    def unload(self, timeout=None):
        """
        A simple method that will disconnect from the robot, record the brain's configuration, dumps the collision data
         and wait for all thread to terminate
        :param timeout: the time to wait for all thread to terminate. Defaults to None, meaning wait forever
        :return: Nothing
        """

        # Switch the back led off
        self.set_back_led(0, False)
        # Disconnect from the robot
        self.disconnect()
        # Record the brain's configuration
        self.dump_brain()
        # Record the collision positions
        self.dump_collision_pos()
        # Check that more than one thread is running to avoid a runtimeError
        if threading.activeCount() > 0:
            # Wait for all threads to terminate
            self.join(timeout)

    def get_power_status(self):
        """
        A getter for the power status
        :return: An int representing the power status. 1: charging, 2: Ok, 3: Low, 4: Critical
        """
        return self._power

    def get_state_value(self):
        """
        Activate the critic and return its output as the value for the state.
        :return: A float in the range [-1, 1]
        """

        # Activate the critic
        self._critic.activate([self._x, self._y])
        # Get the output
        output = self._critic.get_output()
        # Finally return the state's value
        return output[0]

    def learn(self, state_n, state_o, discount, learn_rate):
        """
        Compute the error depending on the collision status and have the actor and critic learn
        :param state_n: the value of the new state
        :param state_o: the value of the old state
        :param discount: the discount rate
        :return: Nothing
        """

        # Compute the punishment
        if self._collided:
            punishment = -1
        else:
            punishment = 0

        # Compute the error
        error = punishment + discount * state_n - state_o

        # Have the actor and critic learn
        self._actor.learn([error, error], learn_rate)
        self._critic.learn([error], learn_rate)

    def get_roll_params(self, max_speed=255):
        """
        Activate the actor and return the speed and heading for the next roll
        :param max_speed: The maximal speed at which sphero can roll
        :return: A tuple: (speed, heading)
        """

        # Activate the actor
        self._actor.activate([self._x, self._y])

        # Get the parameters for the roll
        outputs = self._actor.get_output()  # outputs are in the range [0; 1]
        speed = outputs[0] * max_speed  # With output=1 -> max_speed, with output=0 -> 0
        heading = outputs[1] * 359  # 359 is the maximum heading possible

        # Return the formatted parameters
        return int(speed), int(heading)


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
