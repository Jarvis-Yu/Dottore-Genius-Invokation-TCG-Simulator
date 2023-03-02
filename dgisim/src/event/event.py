from typing import List
from enum import Enum

from dgisim.src.event.effect import *


class EventSpeed(Enum):
    COMBAT = 0
    FAST = 1

class EventType(Enum):
    NORMAL_ATTACK   = 0
    ELEMENTAL_SKILL = 1
    ELEMENTAL_BURST = 2
    SKILL           = 3

class GameEvent:
    def __init__(self, effects: List[Effect]) -> None:
        self._effects = effects

class CompoundEvent(GameEvent):
    pass

class SeperableEvent(GameEvent):
    pass

# TODO: check whether this is compound
class TypicalNormalAttackEvent(CompoundEvent):
    def __init__(self, damage: int, element: Element, recharge: int) -> None:
        damage_effect = DamageEffect(element, damage, EffectTarget.OPPO_ACTIVE)
        recharge_effect = EnergyRechargeEffect(recharge, EffectTarget.SELF_SELF)
        super().__init__([
            damage_effect,
            recharge_effect,
        ])
