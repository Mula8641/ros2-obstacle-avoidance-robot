import math
from dataclasses import dataclass
from typing import Mapping

from .core.state_machine import Thresholds
from .core.velocity_policy import Speeds


@dataclass(frozen=True)
class Settings:
    thresholds: Thresholds
    speeds: Speeds
    front_half_angle_rad: float
    side_angle_rad: float
    scan_topic: str
    cmd_topic: str
    control_rate_hz: float
    use_stamped_cmd: bool


def _problems(params: Mapping) -> list:
    problems = []
    if not params["backup_enter_m"] < params["backup_exit_m"] < params["turn_enter_m"] < params["turn_exit_m"]:
        problems.append("need backup_enter_m < backup_exit_m < turn_enter_m < turn_exit_m")
    if params["backup_max_s"] <= 0 or params["turn_min_s"] < 0:
        problems.append("need backup_max_s > 0 and turn_min_s >= 0")
    if not (params["cruise_mps"] > 0 and params["turn_radps"] > 0 and params["backup_mps"] < 0):
        problems.append("need cruise_mps > 0, turn_radps > 0 and backup_mps < 0")
    if not 0 < params["front_half_angle_deg"] < params["side_angle_deg"] <= 180:
        problems.append("need 0 < front_half_angle_deg < side_angle_deg <= 180")
    if params["control_rate_hz"] <= 0:
        problems.append("need control_rate_hz > 0")
    return problems


def load_settings(params: Mapping) -> Settings:
    problems = _problems(params)
    if problems:
        raise ValueError("; ".join(problems))
    return Settings(
        thresholds=Thresholds(
            turn_enter_m=params["turn_enter_m"],
            turn_exit_m=params["turn_exit_m"],
            backup_enter_m=params["backup_enter_m"],
            backup_exit_m=params["backup_exit_m"],
            backup_max_s=params["backup_max_s"],
            turn_min_s=params["turn_min_s"],
        ),
        speeds=Speeds(
            cruise_mps=params["cruise_mps"],
            turn_radps=params["turn_radps"],
            backup_mps=params["backup_mps"],
        ),
        front_half_angle_rad=math.radians(params["front_half_angle_deg"]),
        side_angle_rad=math.radians(params["side_angle_deg"]),
        scan_topic=params["scan_topic"],
        cmd_topic=params["cmd_topic"],
        control_rate_hz=params["control_rate_hz"],
        use_stamped_cmd=params["use_stamped_cmd"],
    )
