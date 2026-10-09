# Environment (Phase 0.6)

Measured on 2026-10-09 in WSL2 with the stock `turtlebot3_world.launch.py` running (`TURTLEBOT3_MODEL=waffle`, `LIBGL_ALWAYS_SOFTWARE=1`).

| Item | Value | Source |
|---|---|---|
| Ubuntu | 24.04 | `lsb_release -rs` |
| ROS | Jazzy (`/opt/ros/jazzy`) | `ros2 pkg prefix` |
| Gazebo | Gazebo Sim 8.15.0 (Harmonic) | `gz sim --version` |
| TurtleBot3 install route | apt: `ros-jazzy-turtlebot3-gazebo` 2.3.7 (no source build needed) | `setup_wsl.sh` |
| Velocity topic | `/cmd_vel` | `ros2 topic list` |
| Velocity type | `geometry_msgs/msg/TwistStamped` (subscriber is `ros_gz_bridge`) | `ros2 topic info -v` |
| Scan topic | `/scan`, `sensor_msgs/msg/LaserScan` | `ros2 topic info` |
| `angle_min` / `angle_max` | 0.0 / 6.28 rad | `topic echo` |
| `angle_increment` | 0.017493 rad (about 1 deg) | `topic echo` |
| `range_min` / `range_max` | 0.12 m / 3.5 m | `topic echo` |
| Sample count | 360 (derived from angle_max / angle_increment; not counted directly) | calculation |
| Scan rate | about 1.4 Hz wall-clock with software rendering | `topic hz` |
| Other topics | `/odom`, `/imu`, `/joint_states`, `/clock`, `/tf`, camera topics | `ros2 topic list` |

## Findings

- The plan's assumed names and `use_stamped_cmd: true` were correct; `params.yaml` needs no change.
- Publishing `TwistStamped` with `linear.x = 0.15` to `/cmd_vel` for 6 s moved the robot (`/odom` x reached 0.17 m), so the command topic works (task 0.7, done with a scripted publish rather than `teleop_keyboard`).
- The Gazebo GUI process started under WSLg, but the window was not looked at, so a visual check of the hexagon world is still open (0.2 / 0.5).
- `LIBGL_ALWAYS_SOFTWARE=1` was used for all runs. One scan-rate check without it (1.2 Hz) showed no improvement, so rendering is not the bottleneck. The scan rate is low (about 1.3 Hz against a nominal 5 Hz) because the sim runs well below real time.
- The scan `range_min` is 0.12 m. With the robot jammed against an obstacle the front reading was about 0.20 m, so `run_monitor` defaults to a 0.20 m collision limit.
