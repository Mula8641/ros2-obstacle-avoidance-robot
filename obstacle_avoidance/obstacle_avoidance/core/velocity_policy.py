from dataclasses import dataclass

from .state_machine import State


@dataclass(frozen=True)
class Velocity:
    linear_mps: float
    angular_radps: float


@dataclass(frozen=True)
class Speeds:
    cruise_mps: float = 0.15
    turn_radps: float = 0.8
    backup_mps: float = -0.08


def velocity_for(state: State, speeds: Speeds) -> Velocity:
    table = {
        State.CRUISE: Velocity(speeds.cruise_mps, 0.0),
        State.TURN_LEFT: Velocity(0.0, speeds.turn_radps),
        State.TURN_RIGHT: Velocity(0.0, -speeds.turn_radps),
        State.BACKUP: Velocity(speeds.backup_mps, 0.0),
    }
    return table[state]
