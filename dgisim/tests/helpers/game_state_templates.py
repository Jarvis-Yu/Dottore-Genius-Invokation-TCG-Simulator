from __future__ import annotations

from dgisim.src.character.character import *
from dgisim.src.character.characters import Characters
from dgisim.src.dice import *
from dgisim.src.effect.effect import *
from dgisim.src.element import Element
from dgisim.src.helper.quality_of_life import BIG_INT
from dgisim.src.mode import DefaultMode
from dgisim.src.state.enums import Pid, Act
from dgisim.src.state.game_state import GameState


class _TestMode(DefaultMode):
    _DICE_LIMIT = 1 << 100


BASE_GAME = GameState.from_default().factory().mode(
    _TestMode()
).f_player1(
    lambda p: p.factory().characters(
        Characters((
            RhodeiaOfLoch.from_default(1),
            Kaeya.from_default(2),
            Keqing.from_default(3),
        ), None)
    ).dice(
        ActualDice({
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
    ).dice(
        ActualDice({
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
).build()


OPPO_DEATH_WAIT = BASE_GAME.factory().f_phase(
    lambda mode: mode.action_phase()
).active_player_id(
    Pid.P1
).f_player1(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(Act.ACTION_PHASE)
    .build()
).f_player2(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory()
        .active_character_id(1)
        .f_character(1, lambda c: c.factory().hp(0).alive(False).build())
        .build()
    )
    .phase(Act.PASSIVE_WAIT_PHASE)
    .build()
).f_effect_stack(
    lambda es: es.push_one(DeathCheckCheckerEffect())
).build()


OPPO_DEATH_END = OPPO_DEATH_WAIT.factory().f_player2(
    lambda p: p.factory().phase(Act.END_PHASE).build()
).build()


ACTION_TEMPLATE = BASE_GAME.factory().f_phase(
    lambda mode: mode.action_phase()
).active_player_id(
    Pid.P1
).f_player1(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(Act.ACTION_PHASE)
    .build()
).f_player2(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(Act.PASSIVE_WAIT_PHASE)
    .build()
).build()

ONE_ACTION_TEMPLATE = ACTION_TEMPLATE.factory().f_player2(
    lambda p: p.factory()
    .phase(Act.END_PHASE)
    .build()
).build()


END_TEMPLATE = BASE_GAME.factory().f_phase(
    lambda mode: mode.end_phase()
).active_player_id(
    Pid.P1
).f_player1(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(Act.PASSIVE_WAIT_PHASE)
    .build()
).f_player2(
    lambda p: p.factory()
    .f_characters(
        lambda cs: cs.factory().active_character_id(1).build()
    )
    .phase(Act.PASSIVE_WAIT_PHASE)
    .build()
).build()
