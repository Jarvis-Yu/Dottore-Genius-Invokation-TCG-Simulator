from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state.enums import Pid

__all__ = [
    "DynamicCharacterTarget",
    "TriggeringSignal",
    "Zone",
]


class Zone(Enum):
    CHARACTERS = "Characters"
    SUMMONS = "Summons"
    SUPPORTS = "Supports"
    COMBAT_STATUSES = "Combat-Statuses"


class TriggeringSignal(Enum):
    FAST_ACTION = 0
    COMBAT_ACTION = 1
    DEATH_EVENT = 2
    SWAP_EVENT_1 = 3  # P1's swap
    SWAP_EVENT_2 = 4  # P2's swap
    POST_DMG = 5  # triggering after each summon effect
    ROUND_START = 6
    PRE_ACTION = 7
    ACT_PRE_SKILL = 8  # trigger prepare skill
    END_ROUND_CHECK_OUT = 9  # summons etc.
    ROUND_END = 10  # remove frozen etc.

    @classmethod
    def swap_event(cls, pid: Pid) -> TriggeringSignal:
        if pid.is_player1():
            return TriggeringSignal.SWAP_EVENT_1
        elif pid.is_player2():
            return TriggeringSignal.SWAP_EVENT_2
        raise Exception("Not Reached!")


class DynamicCharacterTarget(Enum):
    SELF_SELF = 0
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6
