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
    HAND_CARD = 6


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
    #: triggers when "when the battle begins" for the first time
    INIT_GAME_START = 6
    #: triggers when "when your opponent declare the end of their round"
    OPPO_DECLARE_END_ROUND = 7
    #: triggers when "when ... play a ... card"
    POST_CARD = 8
    #: triggers when "when ... character takes DMG"
    POST_DMG = 9
    #: triggers when "after ... character takes Elemental Reaction DMG"
    POST_REACTION = 10
    #: triggers when "after any ..."
    POST_ANY = 11
    #: triggers when "before ... choose their action"
    PRE_ACTION = 12
    #: triggers when "End Phase"
    ROUND_END = 13  # remove frozen etc.
    #: triggers when "when the Action Phase starts"
    ROUND_START = 14
    #: triggers when "when you declare the end of your round"
    SELF_DECLARE_END_ROUND = 15
    #: ABOUT TO BE DEPRECATED: triggers when this player switch a character
    SELF_SWAP = 16  # swap of this player
    #: ABOUT TO BE DEPRECATED: triggers when the opponent switch a character
    OPPO_SWAP = 17  # swap of the opposing playing
    #: triggers when "when the character ... would be defeated"
    TRIGGER_REVIVAL = 18
    #: triggers when "when the character to which this is attached is defeated"
    # only triggers the character which is about to be defeated
    DEATH_DECLARATION = 19
    #: triggers when "when the battle begins" character is being revived
    REVIVAL_GAME_START = 20


class DynamicCharacterTarget(Enum):
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_NEXT = 4
    SELF_PREV = 5
    SELF_NEXT_OFF = 6
    SELF_PREV_OFF = 7

    OPPO_ACTIVE = 11
    OPPO_OFF_FIELD = 12
    OPPO_ALL = 13
    OPPO_NEXT = 14
    OPPO_PREV = 15
    OPPO_NEXT_OFF = 16
    OPPO_PREV_OFF = 17

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
                ).characters
                if ref_char_id is None:
                    avoided_char_id = game_state.get_player(
                        pid.other()
                    ).just_get_active_character().id
                else:
                    avoided_char_id = ref_char_id
                targets.extend([
                    StaticTarget.from_char_id(pid.other(), char.id)
                    for char in oppo_chars
                    if char.id != avoided_char_id
                ])
            case DynamicCharacterTarget.OPPO_NEXT:
                selected_char = game_state.get_player(
                    pid.other()
                ).characters.get_nth_next_alive_character_in_activity_order(1)
                targets.append(StaticTarget.from_char_id(pid.other(), selected_char.id))
            case DynamicCharacterTarget.OPPO_NEXT_OFF:
                off_field_chars = game_state.get_player(
                    pid.other()
                ).characters.get_alive_character_in_activity_order()[1:]
                if len(off_field_chars) != 0:
                    targets.append(StaticTarget.from_char_id(pid.other(), off_field_chars[0].id))
            case DynamicCharacterTarget.SELF_ACTIVE:
                targets.append(StaticTarget.from_player_active(game_state, pid))
            case DynamicCharacterTarget.SELF_NEXT_OFF:
                off_field_chars = game_state.get_player(
                    pid
                ).characters.get_alive_character_in_activity_order()[1:]
                if len(off_field_chars) != 0:
                    targets.append(StaticTarget.from_char_id(pid, off_field_chars[0].id))
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
                ).characters
                if ref_char_id is None:
                    avoided_char_id = game_state.get_player(
                        pid.other()
                    ).just_get_active_character().id
                else:
                    avoided_char_id = ref_char_id
                targets.extend([
                    char
                    for char in oppo_chars
                    if char.id != avoided_char_id
                ])
            case DynamicCharacterTarget.OPPO_NEXT:
                selected_char = game_state.get_player(
                    pid.other()
                ).characters.get_nth_next_alive_character_in_activity_order(1)
                targets.append(selected_char)
            case DynamicCharacterTarget.OPPO_NEXT_OFF:
                off_field_chars = game_state.get_player(
                    pid.other()
                ).characters.get_alive_character_in_activity_order()[1:]
                if len(off_field_chars) != 0:
                    targets.append(off_field_chars[0])
            case DynamicCharacterTarget.SELF_ACTIVE:
                targets.append(game_state.get_player(pid).just_get_active_character())
            case DynamicCharacterTarget.SELF_NEXT_OFF:
                off_field_chars = game_state.get_player(
                    pid
                ).characters.get_alive_character_in_activity_order()[1:]
                if len(off_field_chars) != 0:
                    targets.append(off_field_chars[0])
            case _:
                raise NotImplementedError(f"get_target_chars for {self} is not implemented")
        return targets
