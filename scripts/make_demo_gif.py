"""Render a recorded run (from record_run.py) as an animated replay GIF.

The map is built from the robot's own LiDAR hits; colours show the commanded state.
Usage: python scripts/make_demo_gif.py assets/run.jsonl assets/demo.gif
"""
import argparse
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

STATE_COLORS = {"CRUISE": "tab:green", "TURN_LEFT": "tab:orange", "TURN_RIGHT": "tab:red", "BACKUP": "tab:purple"}


def state_of(record):
    if record["v"] < 0:
        state = "BACKUP"
    elif record["w"] > 0:
        state = "TURN_LEFT"
    elif record["w"] < 0:
        state = "TURN_RIGHT"
    else:
        state = "CRUISE"
    return state


def lidar_points(record):
    points = []
    for i, r in enumerate(record["ranges"]):
        if r is not None:
            a = record["yaw"] + record["angle_min"] + i * record["angle_increment"]
            points.append((record["x"] + r * math.cos(a), record["y"] + r * math.sin(a)))
    return points


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("gif")
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()

    records = [json.loads(line) for line in open(args.run)]
    step = max(1, len(records) // args.frames)
    records = records[::step]
    states = [state_of(r) for r in records]
    hits = [lidar_points(r) for r in records]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=70)
    xs = [r["x"] for r in records]
    ys = [r["y"] for r in records]
    all_hits = [p for frame in hits for p in frame]
    pad = 0.5
    ax.set_xlim(min(p[0] for p in all_hits) - pad, max(p[0] for p in all_hits) + pad)
    ax.set_ylim(min(p[1] for p in all_hits) - pad, max(p[1] for p in all_hits) + pad)
    ax.set_aspect("equal")
    ax.set_title("ROS 2 obstacle avoidance (replay of a recorded run)", fontsize=8)
    scan_dots = ax.scatter([], [], s=1, c="0.4")
    path_dots = ax.scatter([], [], s=6)
    robot, = ax.plot([], [], "ko", ms=8)
    label = ax.text(0.02, 0.96, "", transform=ax.transAxes, fontsize=9, va="top")
    seen = []

    def draw(i):
        seen.extend(hits[i])
        scan_dots.set_offsets(seen)
        path_dots.set_offsets(list(zip(xs[: i + 1], ys[: i + 1])))
        path_dots.set_color([STATE_COLORS[s] for s in states[: i + 1]])
        robot.set_data([xs[i]], [ys[i]])
        label.set_text(states[i])
        label.set_color(STATE_COLORS[states[i]])
        return scan_dots, path_dots, robot, label

    FuncAnimation(fig, draw, frames=len(records)).save(args.gif, writer=PillowWriter(fps=args.fps))


if __name__ == "__main__":
    main()
