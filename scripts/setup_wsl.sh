#!/usr/bin/env bash
# Installs ROS 2 Jazzy desktop, the TurtleBot3 Gazebo simulation and dev tools on Ubuntu 24.04 (WSL2).
# Needs a user with sudo rights. Safe to re-run.
set -euo pipefail

sudo apt update
sudo apt install -y software-properties-common curl
sudo add-apt-repository -y universe

if [ ! -f /etc/apt/sources.list.d/ros2.list ]; then
  ROS_APT_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
  curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_VERSION}/ros2-apt-source_${ROS_APT_VERSION}.$(. /etc/os-release && echo "$VERSION_CODENAME")_all.deb"
  sudo dpkg -i /tmp/ros2-apt-source.deb
fi

sudo apt update
sudo apt install -y ros-jazzy-desktop ros-dev-tools python3-pytest python3-yaml
sudo apt install -y ros-jazzy-turtlebot3-gazebo ros-jazzy-turtlebot3-teleop ros-jazzy-ros-gz

grep -qxF "source /opt/ros/jazzy/setup.bash" ~/.bashrc || echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
grep -qxF "export TURTLEBOT3_MODEL=waffle" ~/.bashrc || echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
