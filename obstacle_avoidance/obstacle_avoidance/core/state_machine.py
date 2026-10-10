from dataclasses import dataclass
from enum import Enum, auto

from .scan_sectors import Sectors


class State(Enum):
    CRUISE = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    BACKUP = auto()


@dataclass(frozen=True)
class Thresholds:
    turn_enter_m: float = 0.50
    turn_exit_m: float = 0.80
    backup_enter_m: float = 0.22
    backup_exit_m: float = 0.30
    backup_max_s: float = 1.5
    turn_min_s: float = 1.0


def _freer_turn(sectors: Sectors) -> State:
    return State.TURN_LEFT if sectors.left_m >= sectors.right_m else State.TURN_RIGHT


def next_state(current: State, sectors: Sectors, seconds_in_state: float, t: Thresholds) -> State:
    front_m = sectors.front_m
    in_turn = current in (State.TURN_LEFT, State.TURN_RIGHT)
    # a fresh turn is exempt, otherwise a wedged robot flips BACKUP -> TURN -> BACKUP every tick
    backup_allowed = current is State.CRUISE or (in_turn and seconds_in_state >= t.turn_min_s)
    if backup_allowed and front_m < t.backup_enter_m:
        result = State.BACKUP
    elif current is State.BACKUP and (front_m >= t.backup_exit_m or seconds_in_state >= t.backup_max_s):
        result = _freer_turn(sectors)
    elif current is State.CRUISE and front_m < t.turn_enter_m:
        result = _freer_turn(sectors)
    elif in_turn and front_m >= t.turn_exit_m:
        result = State.CRUISE
    else:
        result = current
    return result
