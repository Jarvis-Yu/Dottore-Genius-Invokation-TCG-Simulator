from __future__ import annotations
from typing import Dict, Optional
from enum import Enum
import random

from dgisim.src.helper.hashable_dict import HashableDict
from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
from dgisim.src.element.element import Element

class Dices:

    def __init__(self, dices: Dict[Element, int]) -> None:
        self._dices = HashableDict(dices)

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
            (dice.name, str(num))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return level_print(existing_dices, indent)

class ActualDices(Dices):
    """
    Used for the actual dices a player can have.
    """
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

    @classmethod
    def from_empty(cls) -> Dices:
        return Dices(dict([
            (elem, 0)
            for elem in ActualDices._LEGAL_ELEMS
        ]))

    @classmethod
    def from_random(cls, size: int) -> Dices:
        dices = ActualDices.from_empty()
        for i in range(size):
            elem = random.choice(tuple(ActualDices._LEGAL_ELEMS))
            dices._dices[elem] += 1
        return dices

    @classmethod
    def from_all(cls, size: int, elem: Element) -> Dices:
        dices = ActualDices.from_empty()
        dices._dices[Element.OMNI] = size
        return dices

class AbstractDices(Dices):
    """
    Used for the dice cost of cards and other actions
    """
    _PRE_ELEMS = frozenset({
        Element.OMNI,
        Element.PYRO,
        Element.HYDRO,
        Element.ANEMO,
        Element.ELECTRO,
        Element.DENDRO,
        Element.CRYO,
        Element.GEO,
        Element.ANY,
    })

    @classmethod
    def from_pre(cls, omni: int, any: int, element: Optional[Element] = None, num: Optional[int] = None) -> Dices:
        assert element is None or element in AbstractDices._PRE_ELEMS
        dices = { Element.OMNI: omni, Element.ANY: any, }
        if element is not None and num is not None:
            dices[element] = num
        return Dices(dices)
