import signal

import rclpy
from geometry_msgs.msg import Twist, TwistStamped
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.signals import SignalHandlerOptions
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

from ..settings import load_settings
from ..core.scan_sectors import compute_sectors
from ..core.state_machine import State, next_state
from ..core.velocity_policy import Velocity, velocity_for
from ..core.watchdog import scan_is_stale

SCAN_TIMEOUT_S = 1.0
PARAM_NAMES = (
    "turn_enter_m", "turn_exit_m", "backup_enter_m", "backup_exit_m", "backup_max_s", "turn_min_s",
    "cruise_mps", "turn_radps", "backup_mps", "front_half_angle_deg", "side_angle_deg",
    "scan_topic", "cmd_topic", "control_rate_hz", "use_stamped_cmd",
)


class AvoidanceNode(Node):
    def __init__(self):
        super().__init__("avoidance_node")
        for name in PARAM_NAMES:
            self.declare_parameter(name, descriptor=ParameterDescriptor(dynamic_typing=True))
        self.settings = load_settings({n: self.get_parameter(n).value for n in PARAM_NAMES})
        self.sectors = None
        self.last_scan_time = None
        self.state = State.CRUISE
        self.state_since = self.get_clock().now()
        self.timed_out = False
        msg_type = TwistStamped if self.settings.use_stamped_cmd else Twist
        self.cmd_pub = self.create_publisher(msg_type, self.settings.cmd_topic, 10)
        self.create_subscription(LaserScan, self.settings.scan_topic, self.on_scan, qos_profile_sensor_data)
        self.create_timer(1.0 / self.settings.control_rate_hz, self.on_tick)
        self.get_logger().info(f"avoidance_node started, state={self.state.name}")

    def on_scan(self, scan: LaserScan):
        if self.sectors is None:
            self.get_logger().info(f"first scan received ({len(scan.ranges)} samples)")
        self.sectors = compute_sectors(
            scan.ranges, scan.angle_min, scan.angle_increment, scan.range_max,
            self.settings.front_half_angle_rad, self.settings.side_angle_rad, scan.range_min)
        self.last_scan_time = self.get_clock().now()

    def on_tick(self):
        now = self.get_clock().now()
        since_scan = None if self.last_scan_time is None else (now - self.last_scan_time).nanoseconds / 1e9
        stale = scan_is_stale(since_scan, SCAN_TIMEOUT_S)
        if stale:
            if not self.timed_out:
                self.get_logger().warn("no scan received, publishing zero velocity")
            self.publish(Velocity(0.0, 0.0))
        else:
            self.step(now)
        self.timed_out = stale

    def step(self, now):
        seconds_in_state = (now - self.state_since).nanoseconds / 1e9
        new_state = next_state(self.state, self.sectors, seconds_in_state, self.settings.thresholds)
        if new_state is not self.state:
            self.get_logger().info(f"{self.state.name} -> {new_state.name} (front={self.sectors.front_m:.2f} m)")
            self.state, self.state_since = new_state, now
        self.publish(velocity_for(self.state, self.settings.speeds))

    def publish(self, velocity: Velocity):
        stamped = self.settings.use_stamped_cmd
        msg = TwistStamped() if stamped else Twist()
        twist = msg.twist if stamped else msg
        twist.linear.x = velocity.linear_mps
        twist.angular.z = velocity.angular_radps
        if stamped:
            msg.header.stamp = self.get_clock().now().to_msg()
        self.cmd_pub.publish(msg)


def raise_interrupt(signum, frame):
    raise KeyboardInterrupt


def main():
    # keep the context alive on Ctrl+C so the final zero-velocity publish works
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    # a parent that starts us with SIGINT ignored would otherwise make Ctrl+C a no-op
    signal.signal(signal.SIGINT, raise_interrupt)
    signal.signal(signal.SIGTERM, raise_interrupt)
    node = AvoidanceNode()
    try:
        # spin() can block forever once /clock stops, which would swallow the shutdown signal
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # launch may deliver a second SIGINT; don't let it abort the final stop command
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        node.publish(Velocity(0.0, 0.0))
        node.get_logger().info("avoidance_node stopping, zero velocity published")
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
