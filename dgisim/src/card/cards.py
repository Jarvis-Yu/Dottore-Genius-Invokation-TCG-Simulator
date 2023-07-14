from __future__ import annotations
import random
from collections import Counter
from typing import Iterator, TYPE_CHECKING

from ..helper.hashable_dict import HashableDict

if TYPE_CHECKING:
    from .card import Card

__all__ = [
    "Cards",
]


class Cards:
    """
    A container for easy management of cards.
    """
    def __init__(self, cards: dict[type[Card], int]) -> None:
        self._cards = HashableDict.from_dict(cards)

    @classmethod
    def from_empty(cls) -> Cards:
        return Cards({})

    def __add__(self, other: Cards | dict[type[Card], int]) -> Cards:
        other_cards: dict[type[Card], int]
        if isinstance(other, Cards):
            other_cards = other._cards
        else:
            other_cards = other
        return Cards(self._cards + other_cards)

    def __sub__(self, other: Cards | dict[type[Card], int]) -> Cards:
        other_cards: dict[type[Card], int]
        if isinstance(other, Cards):
            other_cards = other._cards
        else:
            other_cards = other
        return Cards(self._cards - other_cards)

    def pick_random_cards(self, num: int) -> tuple[Cards, Cards]:
        """
        Returns the left cards and selected cards
        """
        num = min(self.num_cards(), num)
        if num == 0:
            return (self, Cards.from_empty())
        picked_cards: dict[type[Card], int] = dict(Counter(
            random.sample(list(self._cards.keys()), counts=self._cards.values(), k=num)
        ))
        return Cards(self._cards - picked_cards), Cards(picked_cards)

    def num_cards(self) -> int:
        return sum(self._cards.values())

    def is_legal(self) -> bool:
        return all(val >= 0 for val in self._cards.values())

    def empty(self) -> bool:
        return all(value == 0 for value in self._cards.values())

    def not_empty(self) -> bool:
        return any(value > 0 for value in self._cards.values())

    def contains(self, card: type[Card]) -> bool:
        from .card import OmniCard
        return self[card] > 0 or self[OmniCard] > 0

    def __contains__(self, card: type[Card]) -> bool:
        return self.contains(card)

    def add(self, card: type[Card]) -> Cards:
        return self + {card: 1}

    def remove(self, card: type[Card]) -> Cards:
        from .card import OmniCard
        if self[card] <= 0:
            assert self[OmniCard] > 0
            return self - {OmniCard: 1}  # type: ignore
        return self - {card: 1}

    def remove_all(self, card: type[Card]) -> Cards:
        if self[card] >= 1:
            return self - {card: self._cards[card]}
        else:
            # if the card doesn't exist, even though there might be OmniCards
            # but we don't know how many to remove, so nothing is removed
            return self

    def hide_all(self) -> Cards:
        from .card import OmniCard
        return Cards({OmniCard: self.num_cards()})

    def __getitem__(self, card: type[Card]) -> int:
        return self._cards.get(card, 0)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cards):
            return False
        return self is other or self._cards == other._cards

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._cards)

    def __repr__(self) -> str:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return (
            '{'
            + ", ".join(
                f"{key}: {val}"
                for key, val in existing_cards.items()
            )
            + '}'
        )

    def __iter__(self) -> Iterator[type[Card]]:
        return (  # type: ignore
            card
            for card in self._cards.keys()
            if self[card] > 0
        )

    def to_dict(self) -> dict[type[Card], int]:
        return dict(self._cards.items())

    def dict_str(self) -> dict:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return existing_cards
