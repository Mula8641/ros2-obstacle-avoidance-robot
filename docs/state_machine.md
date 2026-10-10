# State machine

```mermaid
stateDiagram-v2
    [*] --> CRUISE
    CRUISE --> TURN_LEFT: front below turn_enter, left side freer
    CRUISE --> TURN_RIGHT: front below turn_enter, right side freer
    TURN_LEFT --> CRUISE: front at or above turn_exit
    TURN_RIGHT --> CRUISE: front at or above turn_exit
    CRUISE --> BACKUP: front below backup_enter
    TURN_LEFT --> BACKUP: front below backup_enter
    TURN_RIGHT --> BACKUP: front below backup_enter
    BACKUP --> TURN_LEFT: clear or timed out, left side freer
    BACKUP --> TURN_RIGHT: clear or timed out, right side freer
```

Rules are evaluated top to bottom; the first match wins.

| From | Condition | To |
|---|---|---|
| any except BACKUP | `front_m < backup_enter_m` | BACKUP |
| BACKUP | `front_m >= turn_exit_m` or `seconds_in_state >= backup_max_s` | TURN_LEFT if `left_m >= right_m` else TURN_RIGHT |
| CRUISE | `front_m < turn_enter_m` | TURN_LEFT if `left_m >= right_m` else TURN_RIGHT |
| TURN_LEFT / TURN_RIGHT | `front_m >= turn_exit_m` | CRUISE |
| otherwise | none | stay |

`turn_exit_m` (0.80) is larger than `turn_enter_m` (0.50): this hysteresis stops the robot from flickering between CRUISE and a turn at the boundary. The turn direction is picked once, on entry, and never flipped mid-turn.
