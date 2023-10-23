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
    #: triggers prepare skill statuses
    ACT_PRE_SKILL = "ActPreSkill"
    #: triggers when "after a character uses ..." (any skill)
    COMBAT_ACTION = "CombatAction"
    #: triggers when "after a ... character is defeated"
    DEATH_EVENT = "DeathEvent"
    #: triggers when "at the end phase, ..."
    END_ROUND_CHECK_OUT = "EndRoundCheckOut"
    #: triggers when a fast action is performed, unused signal.
    FAST_ACTION = "FastAction"
    #: triggers when "when the battle begins"
    GAME_START = "GameStart"
    #: triggers when "when your opponent declare the end of their round"
    OPPO_DECLARE_END_ROUND = "OppoDeclareEndRound"
    #: triggers when "when ... play a ... card"
    POST_CARD = "PostCard"
    #: triggers when "when ... character takes DMG"
    POST_DMG = "PostDmg"
    #: triggers when "after ... character takes Elemental Reaction DMG"
    POST_REACTION = "PostReaction"
    #: triggers when "before ... choose their action"
    PRE_ACTION = "PreAction"
    #: triggers when "End Phase"
    ROUND_END = "RoundEnd"  # remove frozen etc.
    #: triggers when "when the Action Phase starts"
    ROUND_START = "RoundStart"
    #: triggers when "when you declare the end of your round"
    SELF_DECLARE_END_ROUND = "SelfDeclareEndRound"
    #: ABOUT TO BE DEPRECATED: triggers when player 1 switch a character
    SWAP_EVENT_1 = "SwapEvent1"  # P1's swap; TODO: make it relative
    #: ABOUT TO BE DEPRECATED: triggers when player 2 switch a character
    SWAP_EVENT_2 = "SwapEvent2"  # P2's swap; TODO: make it relative
    #: triggers when "when the character ... would be defeated"
    TRIGGER_REVIVAL = "TriggerRevival"

    @classmethod
    def swap_event(cls, pid: Pid) -> TriggeringSignal:
        """
        :returns: the corresponding swap event signal for `pid`.

        aBOUT TO BE DEPRECATED.
        """
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
