import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.src.state.game_state import GameState
from dgisim.src.state.player_state import PlayerState
from dgisim.src.effect.effect_stack import EffectStack
from dgisim.src.effect.effect import *


class TestEffect(unittest.TestCase):
    # A game state where P1 just killed the active character of P2

    def testDeathCheckCheckerEffect(self):
        game_state = OPPO_DEATH_WAIT
        assert game_state.waiting_for() is None
        game_state = game_state.step()
        self.assertEqual(game_state.get_player1().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)
        self.assertEqual(game_state.get_player2().get_phase(), PlayerState.Act.ACTION_PHASE)
        self.assertEqual(
            game_state.get_effect_stack(),
            EffectStack((
                DeathSwapPhaseEndEffect(
                    GameState.Pid.P2, PlayerState.Act.PASSIVE_WAIT_PHASE, PlayerState.Act.ACTION_PHASE),
                DeathSwapPhaseStartEffect(),
            ))
        )

    def testDeathSwapPhaseStartEffect(self):
        game_state = OPPO_DEATH_WAIT.step()
        self.assertEqual(game_state.waiting_for(), GameState.Pid.P2)

    def testDeathSwapPhaseEndEffect1(self):
        game_state = OPPO_DEATH_WAIT.step()
        game_state = game_state.factory().f_effect_stack(
            # removes DeathSwapPhaseStartEffect which is just for information
            lambda es: es.pop()[0]
        ).build()
        game_state = game_state.step()
        self.assertEqual(game_state.get_player1().get_phase(), PlayerState.Act.ACTION_PHASE)
        self.assertEqual(game_state.get_player2().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)

    def testDeathSwapPhaseEndEffect2(self):
        game_state = OPPO_DEATH_END.step()
        game_state = game_state.factory().f_effect_stack(
            # removes DeathSwapPhaseStartEffect which is just for information
            lambda es: es.pop()[0]
        ).build()
        game_state = game_state.step()
        self.assertEqual(game_state.get_player1().get_phase(), PlayerState.Act.ACTION_PHASE)
        self.assertEqual(game_state.get_player2().get_phase(), PlayerState.Act.END_PHASE)

    def testRecoverHPEffect(self):
        game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().hp(8).build()
                ).build()
            ).build()
        ).build()

        # Heals normally
        g1 = game_state.factory().f_effect_stack(
            lambda es: es.push_one(RecoverHPEffect(
                StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 2),
                1
            ))
        ).build()
        g1 = g1.step()
        c = g1.get_player1().get_characters().get_character(2)
        assert c is not None
        self.assertEqual(c.get_hp(), 9)

        # No overheal
        g2 = game_state.factory().f_effect_stack(
            lambda es: es.push_one(RecoverHPEffect(
                StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 2),
                3
            ))
        ).build()
        g2 = g2.step()
        c = g2.get_player1().get_characters().get_character(2)
        assert c is not None
        self.assertEqual(c.get_hp(), 10)

    def testEnergyRechargeEffect(self):
        # set up game
        game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    1,
                    lambda c: c.factory().energy(0).build()
                ).build()
            ).build()
        ).build()

        # initial energy
        active_character = game_state.get_player1().get_characters().get_active_character()
        assert active_character is not None, "active character is None"
        initial_energy = active_character.get_energy()

        # apply energy recharge effect [1]
        game_state = game_state.factory().f_effect_stack(
            lambda es: es.push_one(EnergyRechargeEffect(
                StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 1),
                1
            ))
        ).build()

        # move game state up
        game_state = game_state.step()

        # check if energy is 1
        c = game_state.get_player1().get_characters().get_character(1)
        assert c is not None
        self.assertEqual(c.get_energy(), initial_energy + 1)

        # apply energy recharge that exceeds max energy
        game_state = game_state.factory().f_effect_stack(
            lambda es: es.push_one(EnergyRechargeEffect(
                StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 1),
                c.get_max_energy() + 1
            ))
        ).build()
        
        # move game state up
        game_state = game_state.step()

        # check if energy is equal to max energy
        c = game_state.get_player1().get_characters().get_character(1)
        assert c is not None
        self.assertEqual(c.get_energy(), c.get_max_energy())
            

    def testEnergyDrainEffect(self):
        # create game state where char has 3 energy
        game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    1,
                    lambda c: c.factory().energy(3).build()
                ).build()
            ).build()
        ).build()

        # apply energy drain effect [3]
        game_state = game_state.factory().f_effect_stack(
            lambda es: es.push_one(EnergyDrainEffect(
                StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 1),
                3
            ))
        ).build()
        game_state = game_state.step()

        # check if energy is 0
        c = game_state.get_player1().get_characters().get_character(1)
        assert c is not None
        self.assertEqual(c.get_energy(), 0)

        # Apply another energy drain effect to see if goes below zero
        game_state = game_state.factory().f_effect_stack(
            lambda es: es.push_one(EnergyDrainEffect(
                StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 1),
                3,
            ))
        ).build()
        game_state = game_state.step()

        # Check if energy is 0
        c = game_state.get_player1().get_characters().get_character(1)
        assert c is not None
        self.assertEqual(c.get_energy(), 0)
