import math

from obstacle_avoidance.core.scan_sectors import compute_sectors

RANGE_MAX = 3.5
FRONT = math.radians(30)
SIDE = math.radians(90)
STEP = math.radians(1)


def scan(blocked_deg=None, blocked_m=None, count=360, angle_min=0.0):
    ranges = [RANGE_MAX] * count
    for deg, dist in zip(blocked_deg or [], blocked_m or []):
        ranges[deg % count] = dist
    return compute_sectors(ranges, angle_min, STEP, RANGE_MAX, FRONT, SIDE)


def test_wall_ahead_sets_front():
    assert scan([0], [0.4]).front_m == 0.4


def test_obstacle_left_only():
    s = scan([60], [0.5])
    assert (s.left_m, s.front_m, s.right_m) == (0.5, RANGE_MAX, RANGE_MAX)


def test_obstacle_right_only():
    s = scan([-60], [0.5])
    assert (s.right_m, s.front_m, s.left_m) == (0.5, RANGE_MAX, RANGE_MAX)


def test_inf_and_nan_count_as_range_max():
    ranges = [float("inf"), float("nan"), -1.0] + [RANGE_MAX] * 357
    s = compute_sectors(ranges, 0.0, STEP, RANGE_MAX, FRONT, SIDE)
    assert (s.front_m, s.left_m, s.right_m) == (RANGE_MAX,) * 3


def test_samples_near_two_pi_map_to_right():
    s = scan([350], [0.3])
    assert s.front_m == 0.3 and s.right_m == RANGE_MAX


def test_empty_sector_returns_range_max():
    s = compute_sectors([0.2] * 10, 0.0, STEP, RANGE_MAX, FRONT, SIDE)
    assert (s.left_m, s.right_m) == (RANGE_MAX, RANGE_MAX)
