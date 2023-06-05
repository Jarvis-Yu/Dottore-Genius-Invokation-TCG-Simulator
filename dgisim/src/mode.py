from __future__ import annotations
from typing import Union

import dgisim.src.phase.phase as ph
import dgisim.src.card.card as card
import dgisim.src.character.character as chr
from dgisim.src.helper.level_print import level_print_single


class Mode:

    _HAND_CARD_LIMIT = 10
    _ROUND_LIMIT = 15

    def get_round_limit(self) -> int:
        return self._ROUND_LIMIT

    def get_hand_card_limit(self) -> int:
        return self._HAND_CARD_LIMIT

    def all_cards(self) -> frozenset[type[card.Card]]:
        raise Exception("Not Overridden")

    def all_chars(self) -> frozenset[type[chr.Character]]:
        raise Exception("Not Overridden")

    def card_select_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def starting_hand_select_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def roll_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def action_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def end_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def game_end_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other)

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, indent: int = 0) -> str:
        return level_print_single(self.__class__.__name__, indent)

    def dict_str(self) -> Union[dict, str]:
        return self.__class__.__name__


class DefaultMode(Mode):

    def all_cards(self) -> frozenset[type[card.Card]]:
        from dgisim.src.card.cards_set import default_cards
        return default_cards()

    def all_chars(self) -> frozenset[type[chr.Character]]:
        from dgisim.src.character.characters_set import default_characters
        return default_characters()

    # Initial phase of this mode
    def card_select_phase(self) -> ph.Phase:
        from dgisim.src.phase.card_select_phase import CardSelectPhase
        return CardSelectPhase()

    def starting_hand_select_phase(self) -> ph.Phase:
        from dgisim.src.phase.starting_hand_select_phase import StartingHandSelectPhase
        return StartingHandSelectPhase()

    def roll_phase(self) -> ph.Phase:
        from dgisim.src.phase.roll_phase import RollPhase
        return RollPhase()

    def action_phase(self) -> ph.Phase:
        from dgisim.src.phase.action_phase import ActionPhase
        return ActionPhase()

    def end_phase(self) -> ph.Phase:
        from dgisim.src.phase.end_phase import EndPhase
        return EndPhase()

    def game_end_phase(self) -> ph.Phase:
        from dgisim.src.phase.game_end_phase import GameEndPhase
        return GameEndPhase()

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
