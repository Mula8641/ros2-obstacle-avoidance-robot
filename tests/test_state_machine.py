import pytest

from obstacle_avoidance.core.scan_sectors import Sectors
from obstacle_avoidance.core.state_machine import State, Thresholds, next_state

T = Thresholds()
FAR = 3.5


def sec(front=FAR, left=FAR, right=FAR):
    return Sectors(front_m=front, left_m=left, right_m=right)


@pytest.mark.parametrize("current", [State.CRUISE, State.TURN_LEFT, State.TURN_RIGHT])
def test_close_front_triggers_backup(current):
    assert next_state(current, sec(front=0.2), 0.0, T) is State.BACKUP


def test_backup_cannot_reenter_itself_and_holds_while_blocked():
    assert next_state(State.BACKUP, sec(front=0.2), 0.5, T) is State.BACKUP


def test_backup_exits_when_front_clear():
    assert next_state(State.BACKUP, sec(front=0.9, left=2, right=1), 0.5, T) is State.TURN_LEFT


def test_backup_exits_on_timeout_even_if_blocked():
    assert next_state(State.BACKUP, sec(front=0.2, left=1, right=2), 1.5, T) is State.TURN_RIGHT


def test_cruise_turns_toward_freer_side():
    assert next_state(State.CRUISE, sec(front=0.4, left=2, right=1), 0, T) is State.TURN_LEFT
    assert next_state(State.CRUISE, sec(front=0.4, left=1, right=2), 0, T) is State.TURN_RIGHT


def test_tie_goes_left():
    assert next_state(State.CRUISE, sec(front=0.4, left=1, right=1), 0, T) is State.TURN_LEFT


@pytest.mark.parametrize("turn", [State.TURN_LEFT, State.TURN_RIGHT])
def test_turn_ends_when_front_clear(turn):
    assert next_state(turn, sec(front=0.8), 0, T) is State.CRUISE


@pytest.mark.parametrize("turn", [State.TURN_LEFT, State.TURN_RIGHT])
def test_hysteresis_keeps_turning_at_0_6(turn):
    assert next_state(turn, sec(front=0.6), 0, T) is turn


def test_hysteresis_keeps_cruising_at_0_6():
    assert next_state(State.CRUISE, sec(front=0.6), 0, T) is State.CRUISE


def test_turn_direction_never_flips_mid_turn():
    s = sec(front=0.4, left=0.5, right=3)
    assert next_state(State.TURN_LEFT, s, 0, T) is State.TURN_LEFT
