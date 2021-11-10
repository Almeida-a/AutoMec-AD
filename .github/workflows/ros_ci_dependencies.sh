#!/bin/bash

# Ackerman dependencies
sudo apt-get install ros-noetic-ros-controllers ros-noetic-ackermann-msgs

# Camera dependencies
sudo apt-get install git-core cmake freeglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev ros-noetic-rgbd-launch
git clone git://github.com/OpenKinect/libfreenect.git
cd libfreenect
mkdir build
cd build
cmake -L ..
make
sudo make install
sudo ldconfig /usr/local/lib64/
freenect-glview
cd ~/catkin_ws/src
git clone https://github.com/ros-drivers/freenect_stack.git
cd ..
catkin_make
source devel/setup.sh
##roslaunch freenect_launch freenect.launch depth_registration:=true

