import pytest

from obstacle_avoidance.core.state_machine import State
from obstacle_avoidance.core.velocity_policy import Speeds, Velocity, velocity_for

S = Speeds()


@pytest.mark.parametrize("state, expected", [
    (State.CRUISE, Velocity(0.15, 0.0)),
    (State.TURN_LEFT, Velocity(0.0, 0.8)),
    (State.TURN_RIGHT, Velocity(0.0, -0.8)),
    (State.BACKUP, Velocity(-0.08, 0.0)),
])
def test_velocity_for_each_state(state, expected):
    assert velocity_for(state, S) == expected
