# RoomLearningMapping
A very simple python program that uses the Sphero 2.0 robot, via the sphero_driver (https://github.com/mmwise/sphero_ros).
At the moment the goal of this project is to have the robot learn how to navigate in a room, thanks to an actor - critic architecture.
Because for each collision, the position of the robot is recorded, a second part of the program will analyze the data gathered and build a layout of the room.
