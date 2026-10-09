#!/usr/bin/env bash
# UNTESTED: written from PLAN.md steps 0.3/0.4 and not yet run. Verify on a real WSL2 Ubuntu 24.04.
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
sudo apt install -y ros-jazzy-desktop ros-dev-tools python3-pytest

if sudo apt install -y ros-jazzy-turtlebot3-gazebo ros-jazzy-turtlebot3-teleop ros-jazzy-ros-gz; then
  echo "TurtleBot3 installed from apt"
else
  sudo apt install -y python3-vcstool git
  mkdir -p ~/turtlebot3_ws/src
  cd ~/turtlebot3_ws/src
  for repo in turtlebot3_simulations turtlebot3 turtlebot3_msgs; do
    [ -d "$repo" ] || git clone -b jazzy "https://github.com/ROBOTIS-GIT/$repo.git"
  done
  [ -d DynamixelSDK ] || git clone -b jazzy https://github.com/ROBOTIS-GIT/DynamixelSDK.git
  cd ~/turtlebot3_ws
  source /opt/ros/jazzy/setup.bash
  sudo rosdep init 2>/dev/null || true
  rosdep update
  rosdep install --from-paths src -y --ignore-src
  colcon build --symlink-install
fi

grep -qxF "source /opt/ros/jazzy/setup.bash" ~/.bashrc || echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
grep -qxF "export TURTLEBOT3_MODEL=waffle" ~/.bashrc || echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
