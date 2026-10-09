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
    backup_max_s: float = 1.5


def _freer_turn(sectors: Sectors) -> State:
    return State.TURN_LEFT if sectors.left_m >= sectors.right_m else State.TURN_RIGHT


def next_state(current: State, sectors: Sectors, seconds_in_state: float, t: Thresholds) -> State:
    front_m = sectors.front_m
    if current is not State.BACKUP and front_m < t.backup_enter_m:
        result = State.BACKUP
    elif current is State.BACKUP and (front_m >= t.turn_exit_m or seconds_in_state >= t.backup_max_s):
        result = _freer_turn(sectors)
    elif current is State.CRUISE and front_m < t.turn_enter_m:
        result = _freer_turn(sectors)
    elif current in (State.TURN_LEFT, State.TURN_RIGHT) and front_m >= t.turn_exit_m:
        result = State.CRUISE
    else:
        result = current
    return result
