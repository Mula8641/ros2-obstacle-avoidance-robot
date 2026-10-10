import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Sectors:
    front_m: float
    left_m: float
    right_m: float


def _normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def clamp_range(sample: float, range_min: float, range_max: float) -> float:
    """Usable distance for one LiDAR sample.

    inf, nan, negative and beyond-range readings mean "nothing seen" and count as range_max.
    A reading closer than range_min is real but unmeasurable, so it counts as range_min
    (the nearest possible obstacle) instead of being dropped.
    """
    if not math.isfinite(sample) or sample < 0 or sample > range_max:
        usable = range_max
    elif sample < range_min:
        usable = range_min
    else:
        usable = sample
    return usable


def compute_sectors(ranges: Sequence[float], angle_min: float, angle_increment: float,
                    range_max: float, front_half_angle: float, side_angle: float,
                    range_min: float = 0.0) -> Sectors:
    front_m = left_m = right_m = range_max
    for index, sample in enumerate(ranges):
        angle = _normalize_angle(angle_min + index * angle_increment)
        distance_m = clamp_range(sample, range_min, range_max)
        if abs(angle) <= front_half_angle:
            front_m = min(front_m, distance_m)
        elif front_half_angle < angle <= side_angle:
            left_m = min(left_m, distance_m)
        elif -side_angle <= angle < -front_half_angle:
            right_m = min(right_m, distance_m)
    return Sectors(front_m=front_m, left_m=left_m, right_m=right_m)
