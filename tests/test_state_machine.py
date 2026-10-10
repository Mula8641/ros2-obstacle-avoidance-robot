import pytest

from obstacle_avoidance.core.scan_sectors import Sectors
from obstacle_avoidance.core.state_machine import State, Thresholds, next_state

T = Thresholds()
FAR = 3.5


def sec(front=FAR, left=FAR, right=FAR):
    return Sectors(front_m=front, left_m=left, right_m=right)


@pytest.mark.parametrize("current", [State.CRUISE, State.TURN_LEFT, State.TURN_RIGHT])
def test_close_front_triggers_backup(current):
    assert next_state(current, sec(front=0.2), T.turn_min_s, T) is State.BACKUP


def test_backup_cannot_reenter_itself_and_holds_while_blocked():
    assert next_state(State.BACKUP, sec(front=0.2), 0.5, T) is State.BACKUP


def test_backup_exits_when_front_clear():
    assert next_state(State.BACKUP, sec(front=0.9, left=2, right=1), 0.5, T) is State.TURN_LEFT


def test_backup_exits_at_backup_exit_distance_without_waiting_for_timeout():
    assert next_state(State.BACKUP, sec(front=T.backup_exit_m, left=1, right=2), 0.3, T) is State.TURN_RIGHT


def test_backup_holds_just_below_backup_exit_distance():
    assert next_state(State.BACKUP, sec(front=T.backup_exit_m - 0.01), 0.3, T) is State.BACKUP


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


@pytest.mark.parametrize("turn", [State.TURN_LEFT, State.TURN_RIGHT])
def test_fresh_turn_does_not_bounce_back_into_backup(turn):
    assert next_state(turn, sec(front=0.1), T.turn_min_s - 0.1, T) is turn


@pytest.mark.parametrize("turn", [State.TURN_LEFT, State.TURN_RIGHT])
def test_settled_turn_can_enter_backup(turn):
    assert next_state(turn, sec(front=0.1), T.turn_min_s, T) is State.BACKUP


def test_wedged_robot_alternates_slowly_not_every_tick():
    state, seconds, visited = State.CRUISE, 0.0, []
    blocked = sec(front=0.1, left=1, right=1)
    for _ in range(40):
        new = next_state(state, blocked, seconds, T)
        seconds = 0.0 if new is not state else seconds + 0.1
        state = new
        visited.append(state)
    changes = sum(1 for a, b in zip(visited, visited[1:]) if a is not b)
    assert changes <= 4
