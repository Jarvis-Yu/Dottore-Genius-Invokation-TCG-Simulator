from __future__ import annotations

from .card import card as card
from .character import character as chr
from .phase import phase as ph

from .dices import AbstractDices
from .element.element import *
from .event.event import *
from .helper.level_print import level_print_single


class Mode:

    _HAND_CARD_LIMIT = 10
    _ROUND_LIMIT = 15
    _SUMMONS_LIMIT = 4
    _SUPPORTS_LIMIT = 4
    _SWAP_COST = AbstractDices({Element.ANY: 1})
    _SWAP_SPEED = EventSpeed.COMBAT_ACTION

    def round_limit(self) -> int:
        return self._ROUND_LIMIT

    def hand_card_limit(self) -> int:
        return self._HAND_CARD_LIMIT

    def summons_limit(self) -> int:
        return self._SUMMONS_LIMIT

    def supports_limit(self) -> int:
        return self._SUPPORTS_LIMIT

    def swap_cost(self) -> AbstractDices:
        return self._SWAP_COST

    def swap_speed(self) -> EventSpeed:
        return self._SWAP_SPEED

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

    def dict_str(self) -> dict | str:
        return self.__class__.__name__


class DefaultMode(Mode):

    def all_cards(self) -> frozenset[type[card.Card]]:
        from .card.cards_set import default_cards
        return default_cards()

    def all_chars(self) -> frozenset[type[chr.Character]]:
        from .character.characters_set import default_characters
        return default_characters()

    # Initial phase of this mode
    def card_select_phase(self) -> ph.Phase:
        from .phase.card_select_phase import CardSelectPhase
        return CardSelectPhase()

    def starting_hand_select_phase(self) -> ph.Phase:
        from .phase.starting_hand_select_phase import StartingHandSelectPhase
        return StartingHandSelectPhase()

    def roll_phase(self) -> ph.Phase:
        from .phase.roll_phase import RollPhase
        return RollPhase()

    def action_phase(self) -> ph.Phase:
        from .phase.action_phase import ActionPhase
        return ActionPhase()

    def end_phase(self) -> ph.Phase:
        from .phase.end_phase import EndPhase
        return EndPhase()

    def game_end_phase(self) -> ph.Phase:
        from .phase.game_end_phase import GameEndPhase
        return GameEndPhase()

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
