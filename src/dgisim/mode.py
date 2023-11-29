from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from typing_extensions import override

from .dice import AbstractDice
from .element import *
from .event import *
from .helper.level_print import level_print_single

if TYPE_CHECKING:
    from .card.card import Card
    from .character.character import Character
    from .deck import Deck
    from .phase.phase import Phase
    from .status.statuses import Statuses

__all__ = [
    "Mode",
    "AllOmniMode",
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
    _CARDS_PER_ROUND = 2
    _DECK_CARDS_REQUIREMENT = 30
    _DECK_CARD_LIMIT_PER_KIND = 2
    _DECK_CHARS_REQUIREMENT = 3
    _DECK_CHAR_LIMIT_PER_KIND = 1
    _DICE_LIMIT = 16
    _DICE_REROLL_CHANCES = 1
    _HAND_CARD_LIMIT = 10
    _INITIAL_CARDS_NUM = 5
    _MAX_CARDS_PER_KIND = 2
    _ROUND_LIMIT = 15
    _SUMMONS_LIMIT = 4
    _SUPPORTS_LIMIT = 4
    _SWAP_COST = AbstractDice({Element.ANY: 1})
    _SWAP_SPEED = EventSpeed.COMBAT_ACTION

    def card_redraw_chances(self) -> int:
        return self._CARD_REDRAW_CHANCES

    def cards_per_round(self) -> int:
        return self._CARDS_PER_ROUND

    def deck_cards_requirement(self) -> int:
        return self._DECK_CARDS_REQUIREMENT

    def deck_card_limit_per_kind(self) -> int:
        return self._DECK_CARD_LIMIT_PER_KIND

    def deck_chars_requirement(self) -> int:
        return self._DECK_CHARS_REQUIREMENT

    def deck_char_limit_per_kind(self) -> int:
        return self._DECK_CHAR_LIMIT_PER_KIND

    def partially_valid_deck(self, deck: Deck) -> bool:
        from collections import Counter
        return (
            len(deck.chars) <= self.deck_chars_requirement()
            and sum(deck.cards.values()) <= self.deck_cards_requirement()
            and Counter(deck.chars).most_common(1)[0][1] <= self.deck_char_limit_per_kind()
            and max(deck.cards.values()) <= self.deck_card_limit_per_kind()
            and all(char in self.all_chars() for char in deck.chars)
            and all(card in self.all_cards() for card in deck.cards)
            and all(card.valid_in_deck(deck) for card in deck.cards)
        )

    def valid_deck(self, deck: Deck) -> bool:
        from collections import Counter
        return (
            len(deck.chars) == self.deck_chars_requirement()
            and sum(deck.cards.values()) == self.deck_cards_requirement()
            and Counter(deck.chars).most_common(1)[0][1] <= self.deck_char_limit_per_kind()
            and max(deck.cards.values()) <= self.deck_card_limit_per_kind()
            and all(char in self.all_chars() for char in deck.chars)
            and all(card in self.all_cards() for card in deck.cards)
            and all(card.valid_in_deck(deck) for card in deck.cards)
        )

    def dice_limit(self) -> int:
        return self._DICE_LIMIT

    def dice_reroll_chances(self) -> int:
        return self._DICE_REROLL_CHANCES

    def round_limit(self) -> int:
        return self._ROUND_LIMIT

    def initial_cards_num(self) -> int:
        return self._INITIAL_CARDS_NUM

    def hand_card_limit(self) -> int:
        return self._HAND_CARD_LIMIT

    def summons_limit(self) -> int:
        return self._SUMMONS_LIMIT

    def supports_limit(self) -> int:
        return self._SUPPORTS_LIMIT

    def swap_cost(self) -> AbstractDice:
        return self._SWAP_COST

    def swap_speed(self) -> EventSpeed:
        return self._SWAP_SPEED

    def player_default_hidden_statuses(self) -> Statuses:
        from .status.statuses import Statuses
        from .status.status import ChargedAttackStatus, PlungeAttackStatus, DeathThisRoundStatus
        return Statuses((ChargedAttackStatus(), PlungeAttackStatus(), DeathThisRoundStatus()))

    @abstractmethod
    def all_cards(self) -> frozenset[type[Card]]:
        pass

    @abstractmethod
    def all_chars(self) -> frozenset[type[Character]]:
        pass

    @property
    @abstractmethod
    def first_phase(self) -> type[Phase]:
        """ :returns: the initial phase of a new game. """
        pass

    @property
    @abstractmethod
    def card_select_phase(self) -> type[Phase]:
        """ :returns: the Card Select Phase. """
        pass

    @property
    @abstractmethod
    def starting_hand_select_phase(self) -> type[Phase]:
        """ :returns: the Starting Hand Select Phase. """
        pass

    @property
    @abstractmethod
    def roll_phase(self) -> type[Phase]:
        """ :returns: the Roll Phase. """
        pass

    @property
    @abstractmethod
    def action_phase(self) -> type[Phase]:
        """ :returns: the Action Phase. """
        pass

    @property
    @abstractmethod
    def end_phase(self) -> type[Phase]:
        """ :returns: the End Phase. """
        pass

    @property
    @abstractmethod
    def game_end_phase(self) -> type[Phase]:
        """ :returns: the Game End Phase. """
        pass

    def phase_code(self, phase: Phase | type[Phase]) -> int:
        """ :returns: the code of the given phase. """
        from .phase.phase import Phase
        if isinstance(phase, Phase):
            phase = type(phase)
        if phase is self.card_select_phase:
            return 1
        elif phase is self.starting_hand_select_phase:
            return 2
        elif phase is self.roll_phase:
            return 3
        elif phase is self.action_phase:
            return 4
        elif phase is self.end_phase:
            return 5
        elif phase is self.game_end_phase:
            return 6
        else:
            raise Exception(f"Unknown phase: {phase}")

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

    @property
    def first_phase(self) -> type[Phase]:
        return self.card_select_phase

    @property
    def card_select_phase(self) -> type[Phase]:
        from .phase.default.card_select_phase import CardSelectPhase
        return CardSelectPhase

    @property
    def starting_hand_select_phase(self) -> type[Phase]:
        from .phase.default.starting_hand_select_phase import StartingHandSelectPhase
        return StartingHandSelectPhase

    @property
    def roll_phase(self) -> type[Phase]:
        from .phase.default.roll_phase import RollPhase
        return RollPhase

    @property
    def action_phase(self) -> type[Phase]:
        from .phase.default.action_phase import ActionPhase
        return ActionPhase

    @property
    def end_phase(self) -> type[Phase]:
        from .phase.default.end_phase import EndPhase
        return EndPhase

    @property
    def game_end_phase(self) -> type[Phase]:
        from .phase.default.game_end_phase import GameEndPhase
        return GameEndPhase


class AllOmniMode(DefaultMode):
    _DICE_REROLL_CHANCES = 0

    @property
    def roll_phase(self) -> type[Phase]:
        from .phase.all_omni.roll_phase import RollPhase
        return RollPhase
