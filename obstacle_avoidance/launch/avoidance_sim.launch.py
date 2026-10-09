import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    sim_launch = os.path.join(
        get_package_share_directory("turtlebot3_gazebo"), "launch", "turtlebot3_world.launch.py")
    params_file = os.path.join(
        get_package_share_directory("obstacle_avoidance"), "config", "params.yaml")
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(sim_launch)),
        Node(
            package="obstacle_avoidance",
            executable="avoidance_node",
            parameters=[params_file, {"use_sim_time": use_sim_time}],
            output="screen",
        ),
    ])
