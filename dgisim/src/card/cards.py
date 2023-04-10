from __future__ import annotations
from typing import Dict, Tuple, Type
from collections import Counter
import random

from dgisim.src.card.card import Card
from dgisim.src.helper.hashable_dict import HashableDict
from dgisim.src.helper.level_print import level_print, INDENT, level_print_single


class Cards:
    def __init__(self, mapping: Dict[Type[Card], int]) -> None:
        self._cards = HashableDict(mapping)

    @classmethod
    def from_empty(cls) -> Cards:
        return Cards({})

    def __add__(self, other: Cards) -> Cards:
        return Cards(self._cards + other._cards)

    def __sub__(self, other: Cards) -> Cards:
        return Cards(self._cards - other._cards)

    def pick_random_cards(self, num: int) -> Tuple[Cards, Cards]:
        """
        Returns the left cards and selected cards
        """
        num = min(self.num_cards(), num)
        if num == 0:
            return (self, Cards.from_empty())
        picked_cards = dict(Counter(
            random.sample(list(self._cards.keys()), counts=self._cards.values(), k=num)
        ))
        return Cards(self._cards - picked_cards), Cards(picked_cards)

    def num_cards(self) -> int:
        return sum(self._cards.values())

    def contains(self, card: type[Card]) -> bool:
        for c in self._cards:
            if c == card and self._cards[c] >= 1:
                return True
        return False

    def remove(self, card: type[Card]) -> Cards:
        assert card in self._cards
        assert self._cards[card] >= 1
        return self - Cards({card: 1})

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

    def to_string(self, indent: int = 0) -> str:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return level_print(existing_cards, indent)
