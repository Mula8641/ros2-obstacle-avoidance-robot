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


def _valid_range(sample: float, range_max: float) -> float:
    # LiDAR reports inf/nan for "nothing seen"
    return sample if math.isfinite(sample) and sample >= 0 else range_max


def compute_sectors(ranges: Sequence[float], angle_min: float, angle_increment: float,
                    range_max: float, front_half_angle: float, side_angle: float) -> Sectors:
    front_m = left_m = right_m = range_max
    for index, sample in enumerate(ranges):
        angle = _normalize_angle(angle_min + index * angle_increment)
        distance_m = _valid_range(sample, range_max)
        if abs(angle) <= front_half_angle:
            front_m = min(front_m, distance_m)
        elif front_half_angle < angle <= side_angle:
            left_m = min(left_m, distance_m)
        elif -side_angle <= angle < -front_half_angle:
            right_m = min(right_m, distance_m)
    return Sectors(front_m=front_m, left_m=left_m, right_m=right_m)
