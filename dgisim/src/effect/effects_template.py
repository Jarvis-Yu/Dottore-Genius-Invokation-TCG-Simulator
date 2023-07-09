from __future__ import annotations
from typing import TYPE_CHECKING

from ..effect import effect as eft

from .enums import DynamicCharacterTarget
from .structs import DamageType

if TYPE_CHECKING:
    from .structs import StaticTarget

__all__ = [
    "normal_attack_template",
]


def normal_attack_template(
        source: StaticTarget,
        element: eft.Element,
        damage: int,
        dices_num: int,
) -> tuple[eft.Effect, ...]:
    effects: list[eft.Effect] = []
    effects.append(eft.ReferredDamageEffect(
        source=source,
        target=DynamicCharacterTarget.OPPO_ACTIVE,
        element=element,
        damage=damage,
        damage_type=DamageType(
            normal_attack=True,
            charged_attack=dices_num % 2 == 0,
        ),
    ))
    return tuple(effects)
