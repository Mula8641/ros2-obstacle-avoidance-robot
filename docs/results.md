# Results

All runs: `turtlebot3_world`, TurtleBot3 waffle, parameters from `obstacle_avoidance/config/params.yaml` (unchanged defaults), software rendering (`LIBGL_ALWAYS_SOFTWARE=1`), launched with `ros2 launch obstacle_avoidance avoidance_sim.launch.py`. The simulation ran at roughly a quarter of real time, so 360 s of wall-clock time is about 90 s of robot time and the scan rate was about 1.1 Hz.

## Three consecutive 360 s runs

Output of `ros2 run obstacle_avoidance run_monitor --duration 360` and the node's transition log, copied unedited:

```
RUN 1
duration=360s scans=400 min_range_m=0.305 collision_threshold_m=0.2 result=PASS
exit=0
state changes: 4
CRUISE -> TURN_RIGHT (front=0.50 m)
TURN_RIGHT -> CRUISE (front=0.84 m)
CRUISE -> TURN_RIGHT (front=0.49 m)
TURN_RIGHT -> CRUISE (front=1.13 m)
stop: 1 zero-velocity message, 0 tracebacks
RUN 2
duration=360s scans=414 min_range_m=0.284 collision_threshold_m=0.2 result=PASS
exit=0
state changes: 4
CRUISE -> TURN_RIGHT (front=0.49 m)
TURN_RIGHT -> CRUISE (front=0.80 m)
CRUISE -> TURN_RIGHT (front=0.48 m)
TURN_RIGHT -> CRUISE (front=1.12 m)
stop: 1 zero-velocity message, 0 tracebacks
RUN 3
duration=360s scans=401 min_range_m=0.317 collision_threshold_m=0.2 result=PASS
exit=0
state changes: 4
CRUISE -> TURN_RIGHT (front=0.49 m)
TURN_RIGHT -> CRUISE (front=0.88 m)
CRUISE -> TURN_LEFT (front=0.49 m)
TURN_LEFT -> CRUISE (front=0.81 m)
stop: 1 zero-velocity message, 0 tracebacks
```

Run 1 was recorded with `scripts/record_run.py`; `assets/demo_run.jsonl` is a 124-sample subset of that recording and `assets/demo.gif` is rendered from it.

## BACKUP in the simulator

No avoidance run above reaches BACKUP: the robot turns at 0.50 m and never gets close enough. To exercise it, the robot was teleported with `gz service /world/default/set_pose` to 0.20 m from a wall, facing it, while the controller was running (world coordinates; the odometry frame starts at the robot's spawn point, which is offset from the world frame). Transition log:

```
CRUISE -> TURN_LEFT (front=0.22 m)
TURN_LEFT -> BACKUP (front=0.21 m)
BACKUP -> TURN_LEFT (front=0.30 m)
TURN_LEFT -> CRUISE (front=0.98 m)
CRUISE -> TURN_RIGHT (front=0.28 m)
TURN_RIGHT -> CRUISE (front=0.81 m)
```

The first four lines are the recovery from the top wall. `TURN_LEFT -> BACKUP` happens after the turn has lasted `turn_min_s`, and `BACKUP -> TURN_LEFT` happens at 0.30 m, which is `backup_exit_m`: BACKUP ended on distance, not on the timeout. The last two lines followed the second placement, at the bottom wall: the front reading was 0.28 m, above the BACKUP threshold, and a plain turn was enough.

## Negative check for the monitor

With no controller running, the robot was driven straight into obstacles at 0.25 m/s for 240 s. With the original 0.12 m limit the monitor reported PASS (minimum 0.123 m), which showed that limit could never trigger; the limit became 0.20 m. Re-running the same scenario gave:

```
duration=240s scans=315 min_range_m=0.120 collision_threshold_m=0.2 result=FAIL
```

with exit code 1.

## Earlier measurements (before the BACKUP change)

Before BACKUP and the settings were revised, three 360 s runs gave minimum ranges of 0.306, 0.253 and 0.256 m with 6 state changes each, and a 120 s run produced no state changes at all. They are not the shipped behaviour and are not used in the README.
