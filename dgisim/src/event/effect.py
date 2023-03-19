from __future__ import annotations
from typing import FrozenSet, Optional
from enum import Enum

from dgisim.src.element.element import Element
import dgisim.src.state.game_state as gm


class EffectTarget(Enum):
    SELF_SELF = 0
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6


class Effect:
    def execute(self, game_state: gm.GameState) -> gm.GameState:
        raise Exception("Not Overriden or Implemented")


class TrigerrbleEffect(Effect):
    pass


class DirectEffect(Effect):
    pass


class CheckerEffect(Effect):
    pass


class PhaseEffect(Effect):
    pass


class SwapCharacterCheckerEffect(CheckerEffect):
    pass


class DeathCheckCheckerEffect(CheckerEffect):
    pass


class DeathSwapPhaseEffect(PhaseEffect):
    pass


class SwapCharacterEffect(DirectEffect):

    import dgisim.src.character.characters as chars

    def __init__(self, target: EffectTarget, index: Optional[chars.Characters.CharId] = None):
        assert target != EffectTarget.SELF_ABS or index is not None
        self._target = target
        self._index = index


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

    def __init__(self, target: EffectTarget, element: Element, damage: int):
        assert element in DamageEffect.DAMAGE_ELEMENTS
        self._element = element
        self._damage = damage
        self._target = target


class EnergyRechargeEffect(Effect):

    def __init__(self, target: EffectTarget, recharge: int):
        self._recharge = recharge
        self._target = target
