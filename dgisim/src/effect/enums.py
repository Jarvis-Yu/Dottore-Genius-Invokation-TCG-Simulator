from __future__ import annotations
from enum import Enum
from typing import ClassVar, TYPE_CHECKING

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
    HIDDEN_STATUSES = "Hidden-Statuses"
    COMBAT_STATUSES = "Combat-Statuses"


class TriggeringSignal(Enum):
    ACT_PRE_SKILL = "ActPreSkill"  # trigger prepare skill
    COMBAT_ACTION = "CombatAction"
    DEATH_EVENT = "DeathEvent"
    END_ROUND_CHECK_OUT = "EndRoundCheckOut"  # summons etc.
    FAST_ACTION = "FastAction"
    GAME_START = "GameStart"  # on triggered once at the start of the first round
    OPPO_DECLARE_END_ROUND = "OppoDeclareEndRound"
    POST_CARD = "PostCard"
    POST_DMG = "PostDmg"  # triggering after each summon effect
    POST_REACTION = "PostReaction"
    PRE_ACTION = "PreAction"
    ROUND_END = "RoundEnd"  # remove frozen etc.
    ROUND_START = "RoundStart"
    SELF_DECLARE_END_ROUND = "SelfDeclareEndRound"
    SWAP_EVENT_1 = "SwapEvent1"  # P1's swap; TODO: make it relative
    SWAP_EVENT_2 = "SwapEvent2"  # P2's swap; TODO: make it relative
    TRIGGER_REVIVAL = "TriggerRevival"

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
