import unittest

from dgisim.src.state.game_state import GameState
from dgisim.src.state.player_state import PlayerState
from dgisim.src.event.effect_stack import EffectStack
from dgisim.src.event.effect import *


class TestEffect(unittest.TestCase):
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

    def testDeathCheckCheckerEffect(self):
        game_state = self.OPPO_DEATH_WAIT
        assert game_state.waiting_for() is None
        game_state = game_state.step()
        self.assertEqual(game_state.get_player1().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)
        self.assertEqual(game_state.get_player2().get_phase(), PlayerState.Act.ACTION_PHASE)
        self.assertEqual(
            game_state.get_effect_stack(),
            EffectStack((
                DeathSwapPhaseEndEffect(GameState.Pid.P2, PlayerState.Act.PASSIVE_WAIT_PHASE, PlayerState.Act.ACTION_PHASE),
                DeathSwapPhaseStartEffect(),
            ))
        )

    def testDeathSwapPhaseStartEffect(self):
        game_state = self.OPPO_DEATH_WAIT.step()
        self.assertEqual(game_state.waiting_for(), GameState.Pid.P2)

    def testDeathSwapPhaseEndEffect1(self):
        game_state = self.OPPO_DEATH_WAIT.step()
        game_state = game_state.factory().f_effect_stack(
            # removes DeathSwapPhaseStartEffect which is just for information
            lambda es: es.pop()[0]
        ).build()
        game_state = game_state.step()
        self.assertEqual(game_state.get_player1().get_phase(), PlayerState.Act.ACTION_PHASE)
        self.assertEqual(game_state.get_player2().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)

    def testDeathSwapPhaseEndEffect2(self):
        game_state = self.OPPO_DEATH_END.step()
        game_state = game_state.factory().f_effect_stack(
            # removes DeathSwapPhaseStartEffect which is just for information
            lambda es: es.pop()[0]
        ).build()
        game_state = game_state.step()
        self.assertEqual(game_state.get_player1().get_phase(), PlayerState.Act.ACTION_PHASE)
        self.assertEqual(game_state.get_player2().get_phase(), PlayerState.Act.END_PHASE)
