from __future__ import annotations
from typing import FrozenSet, Optional
from enum import Enum
from dataclasses import dataclass

from dgisim.src.element.element import Element
import dgisim.src.state.game_state as gm


class Zone(Enum):
    CHARACTER = 0
    SUMMONS = 1
    SUPPORT = 2
    HAND = 3


class DynamicEffectTarget(Enum):
    SELF_SELF = 0
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6


@dataclass(frozen=True)
class StaticEffectTarget:
    pid: gm.GameState.Pid
    zone: Zone
    id: int


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

    def __init__(self, target: DynamicEffectTarget, index: Optional[chars.Characters.CharId] = None):
        assert target != DynamicEffectTarget.SELF_ABS or index is not None
        self._target = target
        self._index = index


@dataclass(frozen=True)
class DamageEffect(Effect):
    source: StaticEffectTarget
    target: DynamicEffectTarget
    element: Element
    damage: int

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

    def legal(self) -> bool:
        return self.element in DamageEffect.DAMAGE_ELEMENTS


@dataclass(frozen=True)
class EnergyRechargeEffect(Effect):
    target: StaticEffectTarget
    recharge: int
