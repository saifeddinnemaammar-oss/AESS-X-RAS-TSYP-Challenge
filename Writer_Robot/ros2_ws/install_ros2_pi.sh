#!/bin/bash
# The Living Map - ROS 2 Humble Installation Script for Raspberry Pi 4 (Ubuntu 22.04)

echo "[SYS] Starting ROS 2 Humble Installation..."

# 1. Setup Locale
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 2. Add ROS 2 Repositories
sudo apt install software-properties-common -y
sudo add-apt-repository universe -y
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3. Install ROS 2 Base and Navigation Dependencies
sudo apt update
sudo apt install ros-humble-ros-base python3-colcon-common-extensions -y
sudo apt install ros-humble-rplidar-ros ros-humble-slam-toolbox ros-humble-navigation2 ros-humble-nav2-bringup -y

echo "[SYS] ROS 2 Installation Complete. Please source your setup.bash."