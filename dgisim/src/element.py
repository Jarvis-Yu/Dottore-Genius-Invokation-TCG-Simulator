"""
This file contains the enums and structs of elements and reactions.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, FrozenSet, Optional, Iterator

from .helper.hashable_dict import HashableDict

__all__ = [
    "AURA_ELEMENTS",
    "AURA_ELEMENTS_ORDERED",
    "Element",
    "ElementalAura",
    "Reaction",
    "ReactionDetail",
]


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

    def __repr__(self) -> str:
        return self.name


AURA_ELEMENTS_ORDERED: tuple[Element, ...] = (
    Element.PYRO,
    Element.HYDRO,
    Element.ELECTRO,
    Element.CRYO,
    Element.DENDRO,
)

AURA_ELEMENTS: FrozenSet[Element] = frozenset(AURA_ELEMENTS_ORDERED)


@dataclass(frozen=True)
class _ReactionData:
    reaction_elems: tuple[frozenset[Element], frozenset[Element]]
    damage_boost: int


class Reaction(Enum):
    BLOOM = _ReactionData(
        reaction_elems=(frozenset({Element.DENDRO}), frozenset({Element.HYDRO})),
        damage_boost=1,
    )
    BURNING = _ReactionData(
        reaction_elems=(frozenset({Element.DENDRO}), frozenset({Element.PYRO})),
        damage_boost=1,
    )
    CRYSTALLIZE = _ReactionData(
        reaction_elems=(
            frozenset({
                Element.PYRO,
                Element.HYDRO,
                Element.CRYO,
                Element.ELECTRO,
            }),
            frozenset({
                Element.GEO
            }),
        ),
        damage_boost=1,
    )
    ELECTRO_CHARGED = _ReactionData(
        reaction_elems=(frozenset({Element.HYDRO}), frozenset({Element.ELECTRO})),
        damage_boost=1,
    )
    FROZEN = _ReactionData(
        reaction_elems=(frozenset({Element.HYDRO}), frozenset({Element.CRYO})),
        damage_boost=1,
    )
    MELT = _ReactionData(
        reaction_elems=(frozenset({Element.PYRO}), frozenset({Element.CRYO})),
        damage_boost=2,
    )
    OVERLOADED = _ReactionData(
        reaction_elems=(frozenset({Element.PYRO}), frozenset({Element.ELECTRO})),
        damage_boost=2,
    )
    QUICKEN = _ReactionData(
        reaction_elems=(frozenset({Element.DENDRO}), frozenset({Element.ELECTRO})),
        damage_boost=1,
    )
    SUPERCONDUCT = _ReactionData(
        reaction_elems=(frozenset({Element.CRYO}), frozenset({Element.ELECTRO})),
        damage_boost=1,
    )
    SWIRL = _ReactionData(
        reaction_elems=(
            frozenset({
                Element.PYRO,
                Element.HYDRO,
                Element.CRYO,
                Element.ELECTRO,
            }),
            frozenset({
                Element.ANEMO
            }),
        ),
        damage_boost=0,
    )
    VAPORIZE = _ReactionData(
        reaction_elems=(frozenset({Element.HYDRO}), frozenset({Element.PYRO})),
        damage_boost=2,
    )

    @classmethod
    def consult_reaction(cls, first: Element, second: Element) -> Optional[Reaction]:
        for reaction in cls:
            e1, e2 = reaction.value.reaction_elems
            if (first in e1 and second in e2) or (first in e2 and second in e1):
                return reaction
        return None

    @classmethod
    def consult_reaction_with_aura(
            cls, aura: ElementalAura, second: Element
    ) -> None | ReactionDetail:
        for elem in aura:
            reaction = cls.consult_reaction(elem, second)
            if reaction is not None:
                return ReactionDetail(reaction, elem, second)
        return None

    def damage_boost(self) -> int:
        return self.value.damage_boost


@dataclass(frozen=True)
class ReactionDetail:
    reaction_type: Reaction
    first_elem: Element
    second_elem: Element

    def __post_init__(self):
        if Reaction.consult_reaction(self.first_elem, self.second_elem) != self.reaction_type:
            raise Exception(
                "Trying to init invalid ReactionDetail",
                str([
                    self.reaction_type,
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

    def contains(self, elem: Element) -> bool:
        assert elem in AURA_ELEMENTS
        return self._aura[elem]

    def __contains__(self, elem: Element) -> bool:
        return self.contains(elem)

    def has_aura(self) -> bool:
        return any(self._aura.values())

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

    def __str__(self) -> str:
        return '[' + ','.join(map(
            lambda elem: elem.name, self.elem_auras()
        )) + ']'
