# Environment

Measured with the stock `turtlebot3_world.launch.py` running in WSL2 (`TURTLEBOT3_MODEL=waffle`, `LIBGL_ALWAYS_SOFTWARE=1`).

| Item | Value |
|---|---|
| Ubuntu | 24.04 |
| ROS | Jazzy (`/opt/ros/jazzy`) |
| Gazebo | Gazebo Sim 8.15.0 (Harmonic) |
| TurtleBot3 install | apt: `ros-jazzy-turtlebot3-gazebo` 2.3.7 |
| Velocity topic | `/cmd_vel`, `geometry_msgs/msg/TwistStamped` (subscriber is `ros_gz_bridge`) |
| Scan topic | `/scan`, `sensor_msgs/msg/LaserScan` |
| `angle_min` / `angle_max` | 0.0 / 6.28 rad |
| `angle_increment` | 0.017493 rad (about 1 deg) |
| `range_min` / `range_max` | 0.12 m / 3.5 m |
| Samples per scan | 360 |
| Scan rate | about 1.1 to 1.3 Hz wall-clock (nominal 5 Hz) |
| Other topics | `/odom`, `/imu`, `/joint_states`, `/clock`, `/tf`, camera topics |

## Notes

- `use_stamped_cmd: true` in `params.yaml` matches the measured `/cmd_vel` type.
- Publishing `TwistStamped` with `linear.x = 0.15` to `/cmd_vel` for 6 s moved the robot (`/odom` x reached 0.17 m).
- `LIBGL_ALWAYS_SOFTWARE=1` was used for all runs. A scan-rate check without it (1.2 Hz) showed no improvement, so rendering is not the bottleneck. The simulation runs well below real time, which is why the scan rate is low.
- With the robot pressed against an obstacle the front reading was about 0.20 m, so `run_monitor` defaults to a 0.20 m collision limit (the sensor minimum is 0.12 m).
