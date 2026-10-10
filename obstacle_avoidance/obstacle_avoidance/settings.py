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


def load_settings(params: Mapping) -> Settings:
    return Settings(
        thresholds=Thresholds(
            turn_enter_m=params["turn_enter_m"],
            turn_exit_m=params["turn_exit_m"],
            backup_enter_m=params["backup_enter_m"],
            backup_max_s=params["backup_max_s"],
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
