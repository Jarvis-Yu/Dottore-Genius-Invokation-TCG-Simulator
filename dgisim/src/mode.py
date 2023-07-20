from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .dices import AbstractDices
from .element import *
from .event import *
from .helper.level_print import level_print_single

if TYPE_CHECKING:
    from .card.card import Card
    from .character.character import Character
    from .phase.phase import Phase

__all__ = [
    "Mode",
    "DefaultMode",
]


class Mode(ABC):
    """
    Base Mode for all modes.

    A mode is what that contains all configurations for a 'version' of a game.

    e.g. It contains how many cards a player can have, how many summons can a
    player have...
    """

    _CARD_REDRAW_CHANCES = 1
    _DICE_REROLL_CHANCES = 1
    _HAND_CARD_LIMIT = 10
    _MAX_CARDS_PER_KIND = 2
    _ROUND_LIMIT = 15
    _SUMMONS_LIMIT = 4
    _SUPPORTS_LIMIT = 4
    _SWAP_COST = AbstractDices({Element.ANY: 1})
    _SWAP_SPEED = EventSpeed.COMBAT_ACTION

    def card_redraw_chances(self) -> int:
        return self._CARD_REDRAW_CHANCES

    def dice_reroll_chances(self) -> int:
        return self._DICE_REROLL_CHANCES

    def round_limit(self) -> int:
        return self._ROUND_LIMIT

    def hand_card_limit(self) -> int:
        return self._HAND_CARD_LIMIT

    def max_cards_per_kind(self) -> int:
        return self._MAX_CARDS_PER_KIND

    def summons_limit(self) -> int:
        return self._SUMMONS_LIMIT

    def supports_limit(self) -> int:
        return self._SUPPORTS_LIMIT

    def swap_cost(self) -> AbstractDices:
        return self._SWAP_COST

    def swap_speed(self) -> EventSpeed:
        return self._SWAP_SPEED

    @abstractmethod
    def all_cards(self) -> frozenset[type[Card]]:
        pass

    @abstractmethod
    def all_chars(self) -> frozenset[type[Character]]:
        pass

    @abstractmethod
    def card_select_phase(self) -> Phase:
        pass

    @abstractmethod
    def starting_hand_select_phase(self) -> Phase:
        pass

    @abstractmethod
    def roll_phase(self) -> Phase:
        pass

    @abstractmethod
    def action_phase(self) -> Phase:
        pass

    @abstractmethod
    def end_phase(self) -> Phase:
        pass

    @abstractmethod
    def game_end_phase(self) -> Phase:
        pass

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other)

    def __hash__(self) -> int:
        return hash(type(self))

    def dict_str(self) -> dict | str:
        return self.__class__.__name__


class DefaultMode(Mode):
    """
    The DefaultMode which is what Genius Invokationn TCG in Genshin is like.
    """

    def all_cards(self) -> frozenset[type[Card]]:
        from .card.cards_set import default_cards
        return default_cards()

    def all_chars(self) -> frozenset[type[Character]]:
        from .character.characters_set import default_characters
        return default_characters()

    # Initial phase of this mode
    def card_select_phase(self) -> Phase:
        from .phase.default.card_select_phase import CardSelectPhase
        return CardSelectPhase()

    def starting_hand_select_phase(self) -> Phase:
        from .phase.default.starting_hand_select_phase import StartingHandSelectPhase
        return StartingHandSelectPhase()

    def roll_phase(self) -> Phase:
        from .phase.default.roll_phase import RollPhase
        return RollPhase()

    def action_phase(self) -> Phase:
        from .phase.default.action_phase import ActionPhase
        return ActionPhase()

    def end_phase(self) -> Phase:
        from .phase.default.end_phase import EndPhase
        return EndPhase()

    def game_end_phase(self) -> Phase:
        from .phase.default.game_end_phase import GameEndPhase
        return GameEndPhase()


class AllOmniMode(DefaultMode):
    _DICE_REROLL_CHANCES = 0

    def roll_phase(self) -> Phase:
        from .phase.all_omni.roll_phase import RollPhase
        return RollPhase()
