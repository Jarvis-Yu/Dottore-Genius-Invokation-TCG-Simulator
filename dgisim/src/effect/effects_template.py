from __future__ import annotations
from typing import TYPE_CHECKING

from ..effect import effect as eft
from ..status import status as stt

from .enums import DynamicCharacterTarget
from .structs import DamageType

if TYPE_CHECKING:
    from ..state.game_state import GameState
    from .structs import StaticTarget

__all__ = [
    "normal_attack_template",
]


def normal_attack_template(
        game_state: GameState,
        source: StaticTarget,
        element: eft.Element,
        damage: int,
) -> tuple[eft.Effect, ...]:
    dices_num = game_state.get_player(source.pid).get_dices().num_dices()
    character = game_state.get_character_target(source)
    assert character is not None
    assert stt.PlungeAttackStatus in character.get_hidden_statuses()
    plunge_status = character.get_hidden_statuses().just_find(stt.PlungeAttackStatus)
    effects: list[eft.Effect] = []
    effects.append(eft.ReferredDamageEffect(
        source=source,
        target=DynamicCharacterTarget.OPPO_ACTIVE,
        element=element,
        damage=damage,
        damage_type=DamageType(
            normal_attack=True,
            charged_attack=dices_num % 2 == 0,
            plunge_attack=plunge_status.can_plunge,
        ),
    ))
    return tuple(effects)
