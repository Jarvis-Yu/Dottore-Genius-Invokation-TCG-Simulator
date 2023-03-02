from __future__ import annotations
from typing import FrozenSet
from enum import Enum

from dgisim.src.element.element import Element


class EffectTarget(Enum):
    SELF_SELF      = 0
    SELF_ACTIVE    = 1
    SELF_OFF_FIELD = 2
    SELF_ALL       = 3
    OPPO_ACTIVE    = 4
    OPPO_OFF_FIELD = 5


class Effect:
    pass

class DamageEffect(Effect):

    DAMAGE_ELEMENTS: FrozenSet[Element] = frozenset({
        Element.PYRO,
        Element.HYDRO,
        Element.ANEMO,
        Element.ELECTRO,
        Element.DENDRO,
        Element.CRYO,
        Element.GEO,
        Element.PHYSICAL,
        Element.PIERCING,
    })

    def __init__(self, element: Element, damage: int, target: EffectTarget):
        assert element in DamageEffect.DAMAGE_ELEMENTS
        self._element = element
        self._damage = damage
        self._target = target

class EnergyRechargeEffect(Effect):

    def __init__(self, recharge: int, target: EffectTarget):
        self._recharge = recharge
        self._target = target