from __future__ import annotations
from typing import Dict
from enum import Enum
import random

from dgisim.src.helper.hashable_dict import HashableDict
from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
from dgisim.src.element.element import Element

class Dices:
    _LEGAL_ELEMS = frozenset({
        Element.OMNI,
        Element.PYRO,
        Element.HYDRO,
        Element.ANEMO,
        Element.ELECTRO,
        Element.DENDRO,
        Element.CRYO,
        Element.GEO,
    })

    def __init__(self, dices: Dict[Element, int]) -> None:
        self._dices = HashableDict(dices)

    @classmethod
    def from_empty(cls) -> Dices:
        return Dices(dict([
            (elem, 0)
            for elem in Dices._LEGAL_ELEMS
        ]))

    @classmethod
    def from_random(cls, size: int) -> Dices:
        dices = Dices.from_empty()
        for i in range(size):
            elem = random.choice(tuple(Dices._LEGAL_ELEMS))
            dices._dices[elem] += 1
        return dices

    @classmethod
    def from_all(cls, size: int, elem: Element) -> Dices:
        dices = Dices.from_empty()
        dices._dices[Element.OMNI] = size
        return dices

    def __add__(self, other: Dices) -> Dices:
        return Dices(self._dices + other._dices)

    def __sub__(self, other: Dices) -> Dices:
        return Dices(self._dices - other._dices)

    def num_dices(self) -> int:
        return sum(self._dices.values())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dices):
            return False
        return self._dices == other._dices

    def __hash__(self) -> int:
        return hash(self._dices)

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        existing_dices = dict([
            (dice.name, level_print_single(str(num), indent + INDENT))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return level_print(existing_dices, indent)

"""
class Cards:
    def __init__(self, mapping: Dict[Type[Card], int]) -> None:
        self._cards = HashableDict(mapping)

    @classmethod
    def empty(cls) -> Cards:
        return Cards({})

    def __add__(self, other: Cards) -> Cards:
        return Cards(self._cards + other._cards)

    def __sub__(self, other: Cards) -> Cards:
        return Cards(self._cards - other._cards)

    def pick_random_cards(self, num: int) -> Tuple[Cards, Cards]:
        import random
        picked_cards = dict(Counter(
            random.sample(list(self._cards.keys()), counts=self._cards.values(), k=num)
        ))
        return Cards(self._cards - picked_cards), Cards(picked_cards)

    def num_cards(self) -> int:
        return sum(self._cards.values())

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
            (card.name(), level_print_single(str(num), indent + INDENT))
            for card, num in self._cards.items()
            if num != 0
        ])
        return level_print(existing_cards, indent)
"""