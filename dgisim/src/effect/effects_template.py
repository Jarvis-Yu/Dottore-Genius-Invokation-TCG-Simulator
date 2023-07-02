from __future__ import annotations
from typing import TYPE_CHECKING

import dgisim.src.effect.effect as eft
from dgisim.src.effect.enums import DYNAMIC_CHARACTER_TARGET

if TYPE_CHECKING:
    from dgisim.src.effect.structs import StaticTarget


def normal_attack_template(
        source: StaticTarget,
        element: eft.Element,
        damage: int,
        dices_num: int,
) -> tuple[eft.Effect, ...]:
    effects: list[eft.Effect] = []
    effects.append(eft.ReferredDamageEffect(
        source=source,
        target=DYNAMIC_CHARACTER_TARGET.OPPO_ACTIVE,
        element=element,
        damage=damage,
        damage_type=eft.DamageType(
            normal_attack=True,
            charged_attack=dices_num % 2 == 0,
        ),
    ))
    return tuple(effects)
