# ros2-obstacle-avoidance-robot

ROS 2 Jazzy obstacle avoidance for a TurtleBot3 in Gazebo, built as a tested finite state machine.

![tests](https://github.com/Mula8641/ros2-obstacle-avoidance-robot/actions/workflows/tests.yml/badge.svg)

![demo](assets/demo.gif)

*Replay of one recorded simulation run (not a screen capture): grey dots are the robot's own LiDAR hits, the path is coloured by commanded state.*

## Why I built it this way

This is the ROS 2 version of the state-machine safety logic I built on a Lego robot in Stateflow. I wanted the behaviour to be a handful of named states with written transition rules, so I can test every rule and explain each one in a sentence. I kept the decision logic free of ROS so it runs in CI in milliseconds, and I kept the scope small (LiDAR only, no map, no goal) so the project is finished and its limits are known. The reasoning behind each choice, and what I rejected, is in [docs/decisions.md](docs/decisions.md).

## How it works

Each 360-sample LiDAR scan is reduced to three numbers: the closest valid reading in the front (within 30 degrees of straight ahead), left (30 to 90 degrees) and right (-90 to -30 degrees) sectors. Readings that are `inf`, `nan` or out of range count as "nothing seen"; a reading closer than the sensor can measure counts as the nearest possible obstacle.

A four-state machine turns those numbers into a mode: CRUISE, TURN_LEFT, TURN_RIGHT or BACKUP. A turn starts at 0.50 m and ends at 0.80 m, so the robot does not flicker at the boundary, and the direction is chosen once, toward the freer side. BACKUP is the safety net for being closer than 0.22 m. The full rules are in [docs/state_machine.md](docs/state_machine.md).

Each state maps to a fixed velocity (0.15 m/s forward, 0.8 rad/s turning in place, 0.08 m/s reverse), published at 10 Hz. The node in `nodes/avoidance_node.py` only connects `/scan` and `/cmd_vel` to the pure functions in `core/`. If no scan arrives for a second it publishes zero velocity, and on shutdown it publishes zero velocity once.

## Quick start

Requires WSL2 with Ubuntu 24.04. Clone into the Linux filesystem (for example `~/ros_ws/src`), not `/mnt/c` or `/mnt/d`: the Windows drive is slow enough that ROS logging stalls for seconds.

```bash
./scripts/setup_wsl.sh
source /opt/ros/jazzy/setup.bash
cd ~/ros_ws && colcon build --symlink-install --packages-select obstacle_avoidance
source install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch obstacle_avoidance avoidance_sim.launch.py
```

On the machine used for the results below (Intel integrated graphics, software rendering), the simulation ran at roughly a quarter of real time and scans arrived at about 1.1 Hz instead of the nominal 5 Hz. Expect slower robot progress than wall-clock time suggests.

## Run the tests

```bash
pytest -q                                                  # 53 tests, no ROS needed
ros2 run obstacle_avoidance run_monitor --duration 120     # needs the simulation running
```

`run_monitor` listens to `/scan` and exits 0 if the closest reading stayed at or above `--collision-m` (default 0.20 m), otherwise 1. The default is 0.20 m, not the sensor's 0.12 m minimum, because a robot pressed against an obstacle reads about 0.20 m on its LiDAR; a 0.12 m limit can never trigger.

CI runs `ruff`, `pytest` and a `colcon build` inside a `ros:jazzy` container on every push.

## Tuning

All values live in `obstacle_avoidance/config/params.yaml`. Loading fails if the thresholds are not in the order `backup_enter_m < backup_exit_m < turn_enter_m < turn_exit_m`, or if a speed has the wrong sign.

| Parameter | Default | Effect |
|---|---|---|
| `turn_enter_m` | 0.50 | front distance that starts a turn |
| `turn_exit_m` | 0.80 | front distance that ends a turn |
| `backup_enter_m` | 0.22 | front distance that triggers a backup |
| `backup_exit_m` | 0.30 | front distance at which a backup ends |
| `backup_max_s` | 1.5 | longest backup |
| `turn_min_s` | 1.0 | a new turn cannot go back to BACKUP before this |
| `cruise_mps` | 0.15 | forward speed |
| `turn_radps` | 0.8 | turn rate |
| `backup_mps` | -0.08 | reverse speed |
| `front_half_angle_deg` / `side_angle_deg` | 30 / 90 | sector widths |
| `use_stamped_cmd` | true | Jazzy's TurtleBot3 bridge takes `TwistStamped` on `/cmd_vel` |

The defaults were not changed to make any run pass.

## Results

Three consecutive runs of 360 s wall-clock each (about 90 s of robot time), `turtlebot3_world`, waffle, default parameters. Raw output is in [docs/results.md](docs/results.md).

| Run | Closest LiDAR reading | State changes | `run_monitor` | Shutdown |
|---|---|---|---|---|
| 1 | 0.305 m | 4 | exit 0 | zero velocity published |
| 2 | 0.284 m | 4 | exit 0 | zero velocity published |
| 3 | 0.317 m | 4 | exit 0 | zero velocity published |

Each run was two turns, each followed by a return to CRUISE. The robot never got closer than 0.28 m, so these runs do not reach BACKUP. To exercise it, the robot was teleported to 0.20 m from a wall while the controller ran: it turned, backed up, left BACKUP at 0.30 m (on distance, not on the timeout), turned and resumed cruising. A deliberate crash with no controller was reported as FAIL, exit 1.

## Problems found and fixed

- **The collision monitor could not fail.** Its limit equalled the sensor's minimum range, so no reading could be below it, and a crash scenario passed. The limit is now 0.20 m, taken from the reading measured when the robot is pressed against an obstacle, and the crash scenario now fails as it should.
- **BACKUP could only leave by timeout.** At 0.08 m/s, 1.5 s of reversing covers about 0.12 m, far short of the 0.80 m exit distance. It now leaves at 0.30 m or after 1.5 s, and a new turn cannot flip straight back into BACKUP, so a wedged robot alternates slowly instead of every tick.
- **Shutdown crashed or hung.** There were three causes: the default signal handling closed ROS before the final stop command, a second interrupt arrived during cleanup, and when the launch stops Gazebo first the simulation clock stops, which froze `spin()` so it never saw the signal. The node now handles the signals itself, uses a short-timeout spin loop and publishes zero velocity before anything else.
- **Startup stalled for seconds on a Windows drive.** Running from the Linux filesystem fixed it.
- **The controller and the monitor disagreed on what a valid reading is.** They now share one function.
- **120 s runs showed no avoidance at all.** The simulation runs at about a quarter of real time here, so 120 s was about 30 s of robot time. The runs above are 360 s.
- **Settings were unchecked.** `turn_exit_m` below `turn_enter_m` silently removed the hysteresis. Loading now rejects impossible combinations.

## Limitations

- Reactive only: no map and no goal, so it can loop in symmetric spaces.
- Simulation only; nothing here was run on real hardware.
- BACKUP is blind: there is no rear sensing, so reversing assumes clear space behind. A turn has no timeout, so in an enclosed space where every direction stays under 0.80 m the robot keeps rotating.
- Three runs in one small world with nine pillars show the logic works, not how it generalises. The closest approach (0.28 m) is only 8 cm above the collision limit.
- The demo is a replay built from recorded odometry and scans, so wall outlines look doubled where odometry drifted.

## Next steps

Nav2 integration with this as a safety layer, SLAM, a median filter on the scan, speed scaling with distance, and a real TurtleBot3.

## Layout

`obstacle_avoidance/` is the ROS 2 package: `core/` is pure logic (sectors, state machine, velocity policy, watchdog), `settings.py` loads and validates parameters, and `nodes/` holds the ROS wiring. `scripts/` has the WSL setup script, a run recorder and the demo renderer (`python scripts/make_demo_gif.py assets/demo_run.jsonl assets/demo.gif`). Measured environment: [docs/environment.md](docs/environment.md).

## License

MIT
