import pytest

from obstacle_avoidance.settings import load_settings

PARAMS = {
    "turn_enter_m": 0.5, "turn_exit_m": 0.8, "backup_enter_m": 0.22, "backup_exit_m": 0.30,
    "backup_max_s": 1.5, "turn_min_s": 1.0,
    "cruise_mps": 0.15, "turn_radps": 0.8, "backup_mps": -0.08,
    "front_half_angle_deg": 30.0, "side_angle_deg": 90.0,
    "scan_topic": "/scan", "cmd_topic": "/cmd_vel", "control_rate_hz": 10.0, "use_stamped_cmd": False,
}


def test_builds_from_dict():
    s = load_settings(PARAMS)
    assert s.thresholds.turn_exit_m == 0.8 and s.speeds.backup_mps == -0.08
    assert s.thresholds.backup_exit_m == 0.30 and s.thresholds.turn_min_s == 1.0
    assert s.cmd_topic == "/cmd_vel"


def test_missing_key_raises():
    with pytest.raises(KeyError):
        load_settings({k: v for k, v in PARAMS.items() if k != "scan_topic"})


@pytest.mark.parametrize("override", [
    {"turn_exit_m": 0.4},                      # exit below enter removes the hysteresis
    {"turn_enter_m": 0.25},                    # enter at or below backup_exit
    {"backup_exit_m": 0.2},                    # exit not above backup_enter
    {"backup_max_s": 0},
    {"turn_min_s": -1},
    {"cruise_mps": 0},
    {"turn_radps": -0.8},
    {"backup_mps": 0.08},                      # backup must reverse
    {"front_half_angle_deg": 0},
    {"front_half_angle_deg": 95},              # front wider than the side sector
    {"side_angle_deg": 200},
    {"control_rate_hz": 0},
])
def test_invalid_values_are_rejected(override):
    with pytest.raises(ValueError):
        load_settings({**PARAMS, **override})
