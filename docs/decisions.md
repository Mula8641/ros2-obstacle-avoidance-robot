# Design decisions

Each entry says what I decided, why, and what I rejected.

## 1. An explicit state machine, not a continuous controller
I wanted every behaviour to be a named state with a written transition rule, so I can unit test each rule and explain it in one sentence. This is the same style I used for safety logic on an earlier Lego robot in Stateflow, and this project is the ROS 2 version of it.
Rejected: potential fields (smooth, but no crisp rules to test), PID on distance (suits wall following, not a go/turn/reverse task), behaviour trees (more machinery than four behaviours need), Nav2 (needs a map and a goal, out of scope).

## 2. Decision logic never imports ROS
`core/` is plain Python. The node converts messages to numbers, calls three functions and publishes. That is what lets 50+ tests run in CI in under a second with no simulator, and it keeps the logic reusable outside ROS.

## 3. Stack
ROS 2 Jazzy, Gazebo Harmonic through `ros_gz`, TurtleBot3 waffle in `turtlebot3_world`, Python 3.12, WSL2 on Ubuntu 24.04. I chose the combination the Jazzy TurtleBot3 packages support, so I would not fight the toolchain.

## 4. Hysteresis: turn at 0.50 m, stop turning at 0.80 m
One threshold makes the robot flip between cruising and turning when the reading sits near it. A wide gap means a turn only ends once the path is clearly open. Both values are parameters, and loading the settings fails if the order is wrong.

## 5. Choose the turn direction once
The freer side wins when a turn starts (ties go left) and it is never reconsidered mid-turn. Re-deciding every tick lets sensor noise reverse the turn.

## 6. Turn in place
Zero forward speed while turning removes arc geometry and keeps the velocity policy a four-row table. The cost is slower, less smooth motion, which does not matter for this goal.

## 7. BACKUP is a safety net, and it was revised
First version: BACKUP left when the front reached 0.80 m or after 1.5 s. A review of that version showed the distance exit could never fire: at 0.08 m/s the robot covers about 0.12 m in 1.5 s, nowhere near 0.80 m from under 0.22 m. So it always left by timeout.
Now: BACKUP leaves at `backup_exit_m` (0.30 m) or after `backup_max_s`, and a new turn is exempt from BACKUP for `turn_min_s` (1.0 s) so a robot wedged against a wall rotates instead of flipping BACKUP, TURN, BACKUP on consecutive ticks. A unit test covers the wedged case, and a staged run in the simulator (see [results.md](results.md)) shows BACKUP leaving on distance.
Still true: there is no rear sensing, so reversing assumes clear space behind. The low speed and short duration limit the risk but do not remove it.

## 8. Parameters in YAML, checked at load
All tunables live in `params.yaml`. `load_settings` raises on an impossible combination (for example `turn_exit_m` below `turn_enter_m`, or a backup speed that is not negative). A test also checks that `params.yaml` matches the dataclass defaults, so the two copies cannot drift apart.

## 9. Success is measured, and the measurement is tested
`run_monitor` exits 1 if the closest LiDAR reading falls below a limit. The first limit was the sensor's own minimum range (0.12 m), which no reading can go below, so it could never fail. A robot pressed against an obstacle reads about 0.20 m on its LiDAR, so the limit is 0.20 m. The monitor was also checked against a run with no controller, driving the robot into obstacles, to confirm it reports a failure.

## 10. One definition of a valid reading
`clamp_range` is used by both the controller and the monitor: inf, nan, negative and beyond-range values mean "nothing seen" and count as the maximum range, and a reading closer than the sensor can measure counts as the minimum range, so a very close obstacle is never mistaken for a clear path.

## 11. Scope
No Nav2, SLAM, camera or extra sensors. I wanted a small project that is finished, tested and honest about its limits, rather than a large one that is half working.

## 12. Results are only what was measured
Every number in the README comes from a recorded run, and the run logs are in [results.md](results.md). The runs are 360 s of wall-clock time because the simulation runs at roughly a quarter of real time here; 120 s runs showed no avoidance events.

## 13. Code style rules
One job per function, one return per function where practical, no bare `except`, errors propagate, log only at boundaries (start, stop, first scan, each state change), frozen dataclasses for values.
