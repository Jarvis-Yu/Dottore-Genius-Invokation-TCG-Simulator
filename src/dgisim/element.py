"""
This file contains the enums and structs of elements and reactions.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from itertools import chain
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
    OMNI = 1
    PYRO = 2
    HYDRO = 3
    ANEMO = 4
    ELECTRO = 5
    DENDRO = 6
    CRYO = 7
    GEO = 8
    PHYSICAL = 9
    PIERCING = 10
    ANY = 11

    def __repr__(self) -> str:
        return self.name

    def is_pure_element(self) -> bool:
        """ :returns: `True` if the element is a pure element. """
        return self in PURE_ELEMENTS

    def is_aurable_element(self) -> bool:
        """ :returns: `True` if the element is an aurable element. """
        return self in AURA_ELEMENTS


#: Elements of the seven.
PURE_ELEMENTS: set[Element] = {
    Element.PYRO,
    Element.HYDRO,
    Element.ANEMO,
    Element.ELECTRO,
    Element.DENDRO,
    Element.CRYO,
    Element.GEO,
}


#: Aurable elements ordered by reaction priority.
AURA_ELEMENTS_ORDERED: tuple[Element, ...] = (
    Element.PYRO,
    Element.HYDRO,
    Element.ELECTRO,
    Element.CRYO,
    Element.DENDRO,
)

#: Elements that can be applied to characters.
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

    def encoding(self) -> int:
        """
        :returns: the encoding of the reaction.
        """
        for i, reaction in enumerate(Reaction):
            if reaction is self:
                return i + 1
        raise Exception("Invalid reaction")

    @classmethod
    def consult_reaction(cls, first: Element, second: Element) -> Optional[Reaction]:
        """
        :returns: a Reaction if the `first` element can react with the `second` element.
        """
        for reaction in cls:
            e1, e2 = reaction.value.reaction_elems
            if (first in e1 and second in e2) or (first in e2 and second in e1):
                return reaction
        return None

    @classmethod
    def consult_reaction_with_aura(
            cls, aura: ElementalAura, second: Element
    ) -> None | ReactionDetail:
        """
        :returns: the ReactionDetail if the incoming element has a reaction
                  with any aura elements.
        """
        for elem in aura:
            reaction = cls.consult_reaction(elem, second)
            if reaction is not None:
                return ReactionDetail(reaction, elem, second)
        return None

    def damage_boost(self) -> int:
        """
        :returns: the direct damage boost of the reaction.
        """
        return self.value.damage_boost


@dataclass(frozen=True)
class ReactionDetail:
    reaction_type: Reaction
    first_elem: Element
    second_elem: Element

    def elem_reaction(self, elem: Element) -> bool:
        """ :returns: `True` if this reaction is an `elem` reaction. """
        return self.first_elem is elem or self.second_elem is elem

    def encoding(self) -> list[int]:
        return [
            self.reaction_type.encoding(),
            self.first_elem.value,
            self.second_elem.value,
        ]

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
    """
    Stores the aura elements (element applications) of a character.

    This class must initialized by calling `.from_default()` for correct
    aura element ordering.
    """
    def __init__(self, aura: dict[Element, bool] = {}) -> None:
        assert aura.keys() <= AURA_ELEMENTS
        self._aura = HashableDict.from_dict(aura)

    @classmethod
    def from_default(cls) -> ElementalAura:
        """
        :returns: an ElementalAura object that respects aura orders.
                  (namely, Cryo reacts prior to Dendro)
        """
        return cls(HashableDict(
            (elem, False)
            for elem in AURA_ELEMENTS_ORDERED
        ))

    @staticmethod
    def aurable(elem: Element) -> bool:
        """ :returnx: `True` if `elem` is an aura element. """
        return elem in AURA_ELEMENTS

    def peek(self) -> Optional[Element]:
        """ :returns: the element that has the highest priority to be reacted. """
        for elem, aura in self._aura.items():
            if aura:
                return elem
        return None

    def remove(self, elem: Element) -> ElementalAura:
        """
        :returns: a new ElementalAura without `elem`.

        This should only be called if `elem` is contained.
        """
        assert elem in AURA_ELEMENTS
        return ElementalAura(HashableDict(
            (e, aura if e != elem else False)
            for e, aura in self._aura.items()
        ))

    def add(self, elem: Element) -> ElementalAura:
        """
        :returns: a new ElementalAura with `elem`.

        This should only be called if `elem` is aurable.
        """
        assert elem in AURA_ELEMENTS
        if elem in self._aura and self._aura[elem]:
            return self
        return ElementalAura(HashableDict(
            (e, aura if e != elem else True)
            for e, aura in self._aura.items()
        ))

    def contains(self, elem: Element) -> bool:
        """ :returns: `True` if `elem` is applied to the character. """
        assert elem in AURA_ELEMENTS
        return self._aura[elem]

    def __contains__(self, elem: Element) -> bool:
        return self.contains(elem)

    def has_aura(self) -> bool:
        """ :returns: `True` if any element is applied. """
        return any(self._aura.values())

    def elem_auras(self) -> tuple[Element, ...]:
        """ :returns: a tuple of applied elements from highest priority to the lowest. """
        return tuple(iter(self))

    def consult_reaction(self, incoming_elem: Element) -> None | ReactionDetail:
        """
        :returns: ReactionDetail if `incoming_elem` triggers a reaction with
                  the current elements.
        """
        return Reaction.consult_reaction_with_aura(self, incoming_elem)

    def encoding(self) -> list[int]:
        return list(chain.from_iterable([
            (elem.value, 1 if self._aura[elem] else 0)
            for elem in AURA_ELEMENTS
        ]))

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
