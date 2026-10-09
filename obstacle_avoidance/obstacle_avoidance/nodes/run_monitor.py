import argparse
import sys

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class RunMonitor(Node):
    def __init__(self, scan_topic: str):
        super().__init__("run_monitor")
        self.min_range_m = float("inf")
        self.scan_count = 0
        self.create_subscription(LaserScan, scan_topic, self.on_scan, qos_profile_sensor_data)

    def on_scan(self, scan: LaserScan):
        valid = [r for r in scan.ranges if scan.range_min <= r <= scan.range_max]
        self.min_range_m = min([self.min_range_m] + valid)
        self.scan_count += 1


def parse_args():
    parser = argparse.ArgumentParser(description="Pass/fail collision check from the LiDAR scan.")
    parser.add_argument("--duration", type=float, default=120.0)
    parser.add_argument("--collision-m", type=float, default=0.20)
    parser.add_argument("--scan-topic", default="/scan")
    return parser.parse_args()


def main():
    args = parse_args()
    rclpy.init()
    monitor = RunMonitor(args.scan_topic)
    end_ns = monitor.get_clock().now().nanoseconds + int(args.duration * 1e9)
    while rclpy.ok() and monitor.get_clock().now().nanoseconds < end_ns:
        rclpy.spin_once(monitor, timeout_sec=0.1)
    collided = monitor.min_range_m < args.collision_m
    print(f"duration={args.duration:.0f}s scans={monitor.scan_count} "
          f"min_range_m={monitor.min_range_m:.3f} collision_threshold_m={args.collision_m} "
          f"result={'FAIL' if collided else 'PASS'}")
    monitor.destroy_node()
    rclpy.try_shutdown()
    sys.exit(1 if collided else 0)


if __name__ == "__main__":
    main()
