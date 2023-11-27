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
    CHARACTERS = 1
    SUMMONS = 2
    SUPPORTS = 3
    HIDDEN_STATUSES = 4
    COMBAT_STATUSES = 5


class TriggeringSignal(Enum):
    #: triggers prepare skill statuses
    ACT_PRE_SKILL = 1
    #: triggers when "after a character uses ..." (any skill)
    COMBAT_ACTION = 2
    #: triggers when "after a ... character is defeated"
    DEATH_EVENT = 3
    #: triggers when "at the end phase, ..."
    END_ROUND_CHECK_OUT = 4
    #: triggers when a fast action is performed, unused signal.
    FAST_ACTION = 5
    #: triggers when "when the battle begins"
    GAME_START = 6
    #: triggers when "when your opponent declare the end of their round"
    OPPO_DECLARE_END_ROUND = 7
    #: triggers when "when ... play a ... card"
    POST_CARD = 8
    #: triggers when "when ... character takes DMG"
    POST_DMG = 9
    #: triggers when "after ... character takes Elemental Reaction DMG"
    POST_REACTION = 10
    #: triggers when "before ... choose their action"
    PRE_ACTION = 11
    #: triggers when "End Phase"
    ROUND_END = 12  # remove frozen etc.
    #: triggers when "when the Action Phase starts"
    ROUND_START = 13
    #: triggers when "when you declare the end of your round"
    SELF_DECLARE_END_ROUND = 14
    #: ABOUT TO BE DEPRECATED: triggers when player 1 switch a character
    SWAP_EVENT_1 = 15  # P1's swap; TODO: make it relative
    #: ABOUT TO BE DEPRECATED: triggers when player 2 switch a character
    SWAP_EVENT_2 = 16  # P2's swap; TODO: make it relative
    #: triggers when "when the character ... would be defeated"
    TRIGGER_REVIVAL = 17

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
    SELF_SELF = 1
    SELF_ACTIVE = 2
    SELF_OFF_FIELD = 3
    SELF_ALL = 4
    SELF_ABS = 5
    OPPO_ACTIVE = 6
    OPPO_OFF_FIELD = 7
