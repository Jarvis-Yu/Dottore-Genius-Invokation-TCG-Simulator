from __future__ import annotations

from dgisim.src.state.game_state import GameState
from dgisim.src.state.player_state import PlayerState
from dgisim.src.effect.effect import *


OPPO_DEATH_WAIT = GameState.from_default().factory().f_phase(
    lambda mode: mode.action_phase()
).active_player(
    GameState.Pid.P1
).f_player1(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(PlayerState.Act.ACTION_PHASE)
    .build()
).f_player2(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory()
        .active_character_id(1)
        .f_character(1, lambda c: c.factory().hp(0).build())
        .build()
    )
    .phase(PlayerState.Act.PASSIVE_WAIT_PHASE)
    .build()
).f_effect_stack(
    lambda es: es.push_one(DeathCheckCheckerEffect())
).build()


OPPO_DEATH_END = OPPO_DEATH_WAIT.factory().f_player2(
    lambda p: p.factory().phase(PlayerState.Act.END_PHASE).build()
).build()


ACTION_TEMPLATE = GameState.from_default().factory().f_phase(
    lambda mode: mode.action_phase()
).active_player(
    GameState.Pid.P1
).f_player1(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(PlayerState.Act.ACTION_PHASE)
    .build()
).f_player2(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(PlayerState.Act.PASSIVE_WAIT_PHASE)
    .build()
).build()


END_TEMPLATE = GameState.from_default().factory().f_phase(
    lambda mode: mode.end_phase()
).active_player(
    GameState.Pid.P1
).f_player1(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(PlayerState.Act.PASSIVE_WAIT_PHASE)
    .build()
).f_player2(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(PlayerState.Act.PASSIVE_WAIT_PHASE)
    .build()
).build()
