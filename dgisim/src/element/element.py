from __future__ import annotations
from typing import FrozenSet, Optional, Iterator
from enum import Enum
from dataclasses import dataclass

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
    BLOOM = ({Element.DENDRO}, {Element.HYDRO})
    BURNING = ({Element.DENDRO}, {Element.PYRO})
    CRYSTALLIZE = ({
        Element.PYRO,
        Element.HYDRO,
        Element.CRYO,
        Element.ELECTRO,
    }, {
        Element.GEO
    })
    ELECTRO_CHARGED = ({Element.HYDRO}, {Element.ELECTRO})
    FROZEN = ({Element.HYDRO}, {Element.CRYO})
    MELT = ({Element.PYRO}, {Element.CRYO})
    OVERLOADED = ({Element.PYRO}, {Element.ELECTRO})
    QUICKEN = ({Element.DENDRO}, {Element.ELECTRO})
    SUPERCONDUCT = ({Element.CRYO}, {Element.ELECTRO})
    SWIRL = ({
        Element.PYRO,
        Element.HYDRO,
        Element.CRYO,
        Element.ELECTRO,
    }, {
        Element.ANEMO
    })
    VAPORIZE = ({Element.HYDRO}, {Element.PYRO})

    @classmethod
    def consult_reaction(cls, first: Element, second: Element) -> Optional[Reaction]:
        for reaction in cls:
            e1, e2 = reaction.value
            if (first in e1 and second in e2) or (first in e2 and second in e1):
                return reaction
        return None


@dataclass(frozen=True)
class ReactionDetail:
    reaction: Reaction
    first_elem: Element
    second_elem: Element

    def __post_init__(self):
        if Reaction.consult_reaction(self.first_elem, self.second_elem) != self.reaction:
            raise Exception(
                "Trying to init invalid ReactionDetail",
                str([
                    self.reaction,
                    self.first_elem,
                    self.second_elem,
                ])
            )


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

    @staticmethod
    def aurable(elem: Element) -> bool:
        return elem in AURA_ELEMENTS

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

    def add(self, elem: Element) -> ElementalAura:
        assert elem in AURA_ELEMENTS
        if elem in self._aura and self._aura[elem]:
            return self
        return ElementalAura(HashableDict(
            (e, aura if e != elem else True)
            for e, aura in self._aura.items()
        ))

    def has(self, elem: Element) -> ElementalAura:
        assert elem in AURA_ELEMENTS
        return self._aura[elem]

    def elem_auras(self) -> tuple[Element, ...]:
        return tuple(iter(self))

    def __iter__(self) -> Iterator[Element]:
        return (
            elem
            for elem, aura in self._aura.items()
            if aura
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ElementalAura):
            return False
        return self._aura == other._aura

    def __hash__(self) -> int:
        return hash(self._aura)
