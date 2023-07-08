from __future__ import annotations
from enum import Enum

class ZONE(Enum):
    CHARACTERS = "Characters"
    SUMMONS = "Summons"
    SUPPORTS = "Supports"
    COMBAT_STATUSES = "Combat-Statuses"


class TRIGGERING_SIGNAL(Enum):
    FAST_ACTION = 0
    COMBAT_ACTION = 1
    DEATH_EVENT = 2
    SWAP_EVENT_1 = 3  # P1's swap
    SWAP_EVENT_2 = 4  # P2's swap
    ROUND_START = 5
    END_ROUND_CHECK_OUT = 6  # summons etc.
    ROUND_END = 7  # remove frozen etc.


class DYNAMIC_CHARACTER_TARGET(Enum):
    SELF_SELF = 0
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6