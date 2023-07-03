from __future__ import annotations
import random
from collections import Counter
from typing import Union, Iterator, TYPE_CHECKING

from ..helper.hashable_dict import HashableDict
from ..helper.level_print import level_print

if TYPE_CHECKING:
    from .card import Card


class Cards:
    def __init__(self, mapping: dict[type[Card], int]) -> None:
        self._cards = HashableDict(mapping)

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

    def empty(self) -> bool:
        return all(value == 0 for value in self._cards.values())

    def not_empty(self) -> bool:
        return any(value > 0 for value in self._cards.values())

    def contains(self, card: type[Card]) -> bool:
        for c in self._cards:
            if c == card and self._cards[c] >= 1:
                return True
        return False

    def __contains__(self, card: type[Card]) -> bool:
        return self.contains(card)

    def add(self, card: type[Card]) -> Cards:
        return self + {card: 1}

    def remove(self, card: type[Card]) -> Cards:
        assert card in self._cards
        assert self._cards[card] >= 1
        return self - {card: 1}

    def remove_all(self, card: type[Card]) -> Cards:
        assert card in self._cards
        assert self._cards[card] >= 1
        return self - {card: self._cards[card]}

    def __getitem__(self, card: type[Card]) -> int:
        assert card in self._cards
        return self._cards[card]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cards):
            return False
        return self._cards == other._cards

    def __hash__(self) -> int:
        return hash(self._cards)

    def __str__(self) -> str:
        return self.to_string(0)

    def __iter__(self) -> Iterator[type[Card]]:
        return (  # type: ignore
            card
            for card in self._cards.keys()
            if self[card] > 0
        )

    def to_string(self, indent: int = 0) -> str:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return level_print(existing_cards, indent)

    def dict_str(self) -> Union[dict, str]:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return existing_cards
