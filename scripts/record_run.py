"""Record pose, LiDAR scan and commanded motion of a run to a JSON-lines file.

Usage (sim and avoidance_node already running): python3 scripts/record_run.py out.jsonl --duration 300
"""
import argparse
import json
import math

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class Recorder(Node):
    def __init__(self, out_path: str):
        super().__init__("run_recorder")
        self.out = open(out_path, "w")
        self.scan = None
        self.cmd = (0.0, 0.0)
        self.create_subscription(LaserScan, "/scan", lambda m: setattr(self, "scan", m), qos_profile_sensor_data)
        self.create_subscription(TwistStamped, "/cmd_vel", self.on_cmd, 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)

    def on_cmd(self, msg):
        self.cmd = (msg.twist.linear.x, msg.twist.angular.z)

    def on_odom(self, msg):
        if self.scan is not None:
            q = msg.pose.pose.orientation
            yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            ranges = [round(r, 3) if math.isfinite(r) else None for r in self.scan.ranges]
            record = {"x": msg.pose.pose.position.x, "y": msg.pose.pose.position.y, "yaw": yaw,
                      "v": self.cmd[0], "w": self.cmd[1], "ranges": ranges,
                      "angle_min": self.scan.angle_min, "angle_increment": self.scan.angle_increment}
            self.out.write(json.dumps(record) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--duration", type=float, default=300.0)
    args = parser.parse_args()
    rclpy.init()
    recorder = Recorder(args.out)
    end_ns = recorder.get_clock().now().nanoseconds + int(args.duration * 1e9)
    while rclpy.ok() and recorder.get_clock().now().nanoseconds < end_ns:
        rclpy.spin_once(recorder, timeout_sec=0.1)
    recorder.out.close()
    recorder.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
