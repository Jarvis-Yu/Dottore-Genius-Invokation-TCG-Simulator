from __future__ import annotations

from dgisim.src.state.game_state import GameState
from dgisim.src.state.enums import PID
from dgisim.src.state.player_state import PlayerState
from dgisim.src.character.characters import Characters
from dgisim.src.character.character import *
from dgisim.src.effect.effect import *
from dgisim.src.dices import *
from dgisim.src.helper.quality_of_life import BIG_INT


BASE_GAME = GameState.from_default().factory().f_player1(
    lambda p: p.factory().characters(
        Characters((
            RhodeiaOfLoch.from_default(1),
            Kaeya.from_default(2),
            Keqing.from_default(3),
        ), None)
    ).dices(
        ActualDices({
            Element.OMNI: BIG_INT,
            Element.PYRO: BIG_INT,
            Element.HYDRO: BIG_INT,
            Element.ANEMO: BIG_INT,
            Element.ELECTRO: BIG_INT,
            Element.DENDRO: BIG_INT,
            Element.CRYO: BIG_INT,
            Element.GEO: BIG_INT,
        })
    ).build()
).f_player2(
    lambda p: p.factory().characters(
        Characters((
            RhodeiaOfLoch.from_default(1),
            Kaeya.from_default(2),
            Keqing.from_default(3),
        ), None)
    ).dices(
        ActualDices({Element.OMNI: BIG_INT})
    ).build()
).build()


OPPO_DEATH_WAIT = BASE_GAME.factory().f_phase(
    lambda mode: mode.action_phase()
).active_player_id(
    PID.P1
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


ACTION_TEMPLATE = BASE_GAME.factory().f_phase(
    lambda mode: mode.action_phase()
).active_player_id(
    PID.P1
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


END_TEMPLATE = BASE_GAME.factory().f_phase(
    lambda mode: mode.end_phase()
).active_player_id(
    PID.P1
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
