from __future__ import annotations
from typing import TYPE_CHECKING

from ..effect import effect as eft
from ..status import status as stt

from ..effect.enums import TriggeringSignal, Zone
from ..effect.structs import StaticTarget
from .enums import DynamicCharacterTarget
from .structs import DamageType

if TYPE_CHECKING:
    from ..state.enums import Pid
    from ..state.game_state import GameState
    from .structs import StaticTarget

__all__ = [
    "normal_attack_template",
    "standard_post_effects",
]


def normal_attack_template(
        game_state: GameState,
        source: StaticTarget,
        element: eft.Element,
        damage: int,
) -> tuple[eft.Effect, ...]:
    player = game_state.get_player(source.pid)
    assert stt.ChargedAttackStatus in player.get_hidden_statuses()
    charged_status = player.get_hidden_statuses().just_find(stt.ChargedAttackStatus)
    assert stt.PlungeAttackStatus in player.get_hidden_statuses()
    plunge_status = player.get_hidden_statuses().just_find(stt.PlungeAttackStatus)
    effects: list[eft.Effect] = []
    effects.append(eft.ReferredDamageEffect(
        source=source,
        target=DynamicCharacterTarget.OPPO_ACTIVE,
        element=element,
        damage=damage,
        damage_type=DamageType(
            normal_attack=True,
            charged_attack=charged_status.can_charge,
            plunge_attack=plunge_status.can_plunge,
        ),
    ))
    return tuple(effects)


def standard_post_effects(
        game_state: GameState,
        priorized_pid: Pid,
        has_damage: bool = True,
        has_swap: bool = True,
) -> list[eft.Effect]:
    es: list[eft.Effect] = []
    if has_damage:
        es.append(eft.AliveMarkCheckerEffect())
        es.append(eft.DefeatedCheckerEffect())
    if has_swap or has_damage:
        es.append(
            eft.SwapCharacterCheckerEffect(
                my_active=StaticTarget(
                    pid=priorized_pid,
                    zone=Zone.CHARACTERS,
                    id=game_state.get_player(priorized_pid).just_get_active_character().get_id(),
                ),
                oppo_active=StaticTarget(
                    pid=priorized_pid.other(),
                    zone=Zone.CHARACTERS,
                    id=game_state.get_player(
                        priorized_pid.other()).just_get_active_character().get_id(),
                ),
            )
        )
    if has_damage:
        es.append(eft.AllStatusTriggererEffect(
            pid=priorized_pid,
            signal=TriggeringSignal.POST_REACTION,
        ))
        es.append(eft.DefeatedMarkCheckerEffect())
        es.append(eft.AllStatusTriggererEffect(
            pid=priorized_pid,
            signal=TriggeringSignal.DEATH_EVENT,
        ))
        es.append(eft.DeathCheckCheckerEffect())
        es.append(eft.AllStatusTriggererEffect(
            pid=priorized_pid,
            signal=TriggeringSignal.POST_DMG,
        ))
    return es
