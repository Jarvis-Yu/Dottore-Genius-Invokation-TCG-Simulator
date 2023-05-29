from __future__ import annotations
from typing import FrozenSet, Optional
from enum import Enum

from dgisim.src.helper.hashable_dict import HashableDict


class Element(Enum):
    OMNI = 0
    PYRO = 1
    HYDRO = 2
    ANEMO = 3
    ELECTRO = 4
    DENDRO = 5
    CRYO = 6
    GEO = 7
    PHYSICAL = 8
    PIERCING = 9
    ANY = 10


AURA_ELEMENTS_ORDERED: tuple[Element, ...] = (
    Element.PYRO,
    Element.HYDRO,
    Element.ELECTRO,
    Element.CRYO,
    Element.DENDRO,
)

AURA_ELEMENTS: FrozenSet[Element] = frozenset(AURA_ELEMENTS_ORDERED)


class Reaction(Enum):
    BLOOM = 0
    BURNING = 1
    CRYSTALLIZE = 2
    ELECTRO_CHARGED = 3
    FROZEN = 4
    MELT = 5
    OVERLOADED = 6
    QUICKEN = 7
    SUPERCONDUCT = 8
    SWIRL = 9
    VAPORIZE = 10
    SHATTER = 11


class ElementalAura:
    def __init__(self, aura: dict[Element, bool] = {}) -> None:
        assert aura.keys() <= AURA_ELEMENTS
        self._aura = HashableDict.from_dict(aura)

    @classmethod
    def from_default(cls) -> ElementalAura:
        return cls(HashableDict(
            (elem, False)
            for elem in AURA_ELEMENTS_ORDERED
        ))

    def peek(self) -> Optional[Element]:
        for elem, aura in self._aura.items():
            if aura:
                return elem
        return None

    def remove(self, elem: Element) -> ElementalAura:
        assert elem in AURA_ELEMENTS
        return ElementalAura(HashableDict(
            (e, aura if e != elem else False)
            for e, aura in self._aura.items()
        ))

    def has(self, elem: Element) -> ElementalAura:
        assert elem in AURA_ELEMENTS
        return self._aura[elem]

    def elem_auras(self) -> tuple[Element, ...]:
        return tuple(
            elem
            for elem, aura in self._aura.items()
            if aura
        )
