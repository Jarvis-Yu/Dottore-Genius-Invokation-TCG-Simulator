from __future__ import annotations
from typing import List, Tuple
from enum import Enum

import dgisim.src.state.game_state as gm
import dgisim.src.character.character as Cr
from dgisim.src.event.effect import *


def normal_attack_template(source: StaticEffectTarget, id: int, element: Element, damage: int) -> tuple[Effect, ...]:
    return (
        DamageEffect(
            source=source,
            target=DynamicEffectTarget.OPPO_ACTIVE,
            element=element,
            damage=damage,
        ),
        EnergyRechargeEffect(
            target=source,
            recharge=1,
        ),
    )


# class EventSpeed(Enum):
#     COMBAT = 0
#     FAST = 1


# class EventType(Enum):
#     NORMAL_ATTACK = 0
#     ELEMENTAL_SKILL = 1
#     ELEMENTAL_BURST = 2
#     SKILL = 3


# class GameEvent:
#     def __init__(self, event_speed: EventSpeed, effects: Tuple[Effect, ...]) -> None:
#         self._event_speed = event_speed
#         self._effects = effects


# class CompoundEvent(GameEvent):
#     pass


# class SeperableEvent(GameEvent):
#     pass

# # TODO: check whether this is compound


# class TypicalNormalAttackEvent(CompoundEvent):
#     def __init__(self, damage: int, element: Element, recharge: int) -> None:
#         damage_effect = DamageEffect(EffectTarget.OPPO_ACTIVE, element, damage)
#         recharge_effect = EnergyRechargeEffect(EffectTarget.SELF_SELF, recharge)
#         super().__init__(
#             EventSpeed.COMBAT,
#             (
#                 damage_effect,
#                 recharge_effect,
#             )
#         )


# class TypicalSwapCharacterEvent(CompoundEvent):
#     import dgisim.src.character.characters as chars

#     def __init__(self, index: chars.Characters.CharId) -> None:
#         super().__init__(
#             EventSpeed.COMBAT,
#             (
#                 SwapCharacterEffect(EffectTarget.SELF_ABS, index),
#             )
#         )