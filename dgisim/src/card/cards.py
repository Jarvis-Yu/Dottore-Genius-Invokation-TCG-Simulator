from __future__ import annotations
from typing import Dict, Tuple

from dgisim.src.card.card import Card
from dgisim.src.helper.hashable_dict import HashableDict

class Cards:
    def __init__(self, mapping: Dict[Card, int]) -> None:
        self._cards = HashableDict(mapping)

    @classmethod
    def empty(cls) -> Cards:
        return Cards({})

    def new_with(self, cards: Dict[Card, int]) -> Cards:
        return Cards(self._cards | cards)

    def pick_random_cards(self, num: int) -> Tuple[Dict[Card, int], Dict[Card, int]]:
        # TODO
        return ({}, {})

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cards):
            return False
        return self._cards == other._cards

    def __hash__(self) -> int:
        return hash(self._cards)
