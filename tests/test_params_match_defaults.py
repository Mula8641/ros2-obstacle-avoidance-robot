from pathlib import Path

import yaml

from obstacle_avoidance.core.state_machine import Thresholds
from obstacle_avoidance.core.velocity_policy import Speeds
from obstacle_avoidance.settings import load_settings

PARAMS_FILE = Path(__file__).resolve().parent.parent / "obstacle_avoidance" / "config" / "params.yaml"


def test_params_yaml_matches_dataclass_defaults():
    params = yaml.safe_load(PARAMS_FILE.read_text())["avoidance_node"]["ros__parameters"]
    settings = load_settings(params)
    assert settings.thresholds == Thresholds()
    assert settings.speeds == Speeds()
