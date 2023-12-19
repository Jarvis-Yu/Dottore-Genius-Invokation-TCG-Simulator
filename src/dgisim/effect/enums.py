from __future__ import annotations
from enum import Enum
from typing import ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from ..character.character import Character
    from ..state.enums import Pid
    from ..state.game_state import GameState

    from .structs import StaticTarget

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
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6

    def get_targets(
            self,
            game_state: GameState,
            pid: Pid,
            ref_char_id: None | int = None,
    ) -> list[StaticTarget]:
        """
        :param game_state: the current game state
        :param pid: pid of this player
        :param ref_char_id: the character id treated as centre if applicable
        :returns: a list of static targets of the targets
        """
        from .structs import StaticTarget

        targets: list[StaticTarget] = []
        match self:
            case DynamicCharacterTarget.OPPO_ACTIVE:
                targets.append(StaticTarget.from_player_active(game_state, pid.other()))
            case DynamicCharacterTarget.OPPO_OFF_FIELD:
                oppo_chars = game_state.get_player(
                    pid.other()
                ).get_characters()
                if ref_char_id is None:
                    avoided_char_id = game_state.get_player(
                        pid.other()
                    ).just_get_active_character().get_id()
                else:
                    avoided_char_id = ref_char_id
                targets.extend([
                    StaticTarget.from_char_id(pid.other(), char.get_id())
                    for char in oppo_chars
                    if char.get_id() != avoided_char_id
                ])
            case DynamicCharacterTarget.SELF_ACTIVE:
                targets.append(StaticTarget.from_player_active(game_state, pid))
            case _:
                raise NotImplementedError(f"get_targets for {self} is not implemented")
        return targets

    def get_target_chars(
            self,
            game_state: GameState,
            pid: Pid,
            ref_char_id: None | int = None,
    ) -> list[Character]:
        """
        :param game_state: the current game state
        :param pid: pid of this player
        :param ref_char_id: the character id treated as centre if applicable
        :returns: a list of characters
        """
        targets: list[Character] = []
        match self:
            case DynamicCharacterTarget.OPPO_ACTIVE:
                targets.append(game_state.get_player(pid.other()).just_get_active_character())
            case DynamicCharacterTarget.OPPO_OFF_FIELD:
                oppo_chars = game_state.get_player(
                    pid.other()
                ).get_characters()
                if ref_char_id is None:
                    avoided_char_id = game_state.get_player(
                        pid.other()
                    ).just_get_active_character().get_id()
                else:
                    avoided_char_id = ref_char_id
                targets.extend([
                    char
                    for char in oppo_chars
                    if char.get_id() != avoided_char_id
                ])
            case DynamicCharacterTarget.SELF_ACTIVE:
                targets.append(game_state.get_player(pid).just_get_active_character())
            case _:
                raise NotImplementedError(f"get_target_chars for {self} is not implemented")
        return targets
