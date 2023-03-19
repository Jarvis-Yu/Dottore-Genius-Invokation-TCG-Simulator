from __future__ import annotations
from typing import FrozenSet
from enum import Enum


class Element(Enum):
    OMNI     = 0
    PYRO     = 1
    HYDRO    = 2
    ANEMO    = 3
    ELECTRO  = 4
    DENDRO   = 5
    CRYO     = 6
    GEO      = 7
    PHYSICAL = 8
    PIERCING = 9
    ANY      = 10


AURA_ELEMENTS: FrozenSet[Element] = frozenset({
    Element.PYRO,
    Element.HYDRO,
    # Element.ANEMO,
    Element.ELECTRO,
    Element.DENDRO,
    Element.CRYO,
    # Element.GEO,
    # Element.PHYSICAL,
})


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
    pass
