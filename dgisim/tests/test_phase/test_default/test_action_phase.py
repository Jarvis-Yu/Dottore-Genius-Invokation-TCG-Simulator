import unittest

from dgisim.src.action.action import *
from dgisim.src.agents import PuppetAgent
from dgisim.src.card.card import Card
from dgisim.src.element import Element
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.phase.default.action_phase import ActionPhase
from dgisim.src.state.enums import Pid
from dgisim.tests.helpers.game_state_templates import ACTION_TEMPLATE
from dgisim.tests.helpers.quality_of_life import *


class TestActionPhase(unittest.TestCase):
    def test_handle_elemental_tuning_action(self):
        action_phase = ActionPhase()
        import os, sys
        sys.stdout = open(os.devnull, 'w')
        self.assertRaises(
            Exception,
            lambda: action_phase._handle_elemental_tuning_action(
                ACTION_TEMPLATE,
                Pid.P1,
                ElementalTuningAction(card=Card, dice_elem=Element.ANY),
            ),
        )
        sys.stdout.close()
        sys.stdout = sys.__stdout__

    def test_handle_death_swap_action(self):
        action_phase = ActionPhase()
        game_state = kill_character(ACTION_TEMPLATE, 3, pid=Pid.P1)
        self.assertRaises(
            Exception,
            lambda: action_phase._handle_death_swap_action(
                game_state,
                Pid.P1,
                DeathSwapAction(char_id=3),
            ),
        )

    def test_step_action(self):
        game_state = ACTION_TEMPLATE
        game_state = add_damage_effect(ACTION_TEMPLATE, 46, Element.PIERCING, pid=Pid.P2)
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        gsm.auto_step()
        game_state = gsm.get_game_state()
        self.assertRaises(Exception, lambda: game_state.action_step(Pid.P1, EndRoundAction()))
        self.assertRaises(Exception, lambda: game_state.action_step(Pid.P2, EndRoundAction()))

    def test_action_generator(self):
        self.assertIsNotNone(ActionPhase().action_generator(ACTION_TEMPLATE, Pid.P1))
        self.assertIsNone(ActionPhase().action_generator(ACTION_TEMPLATE, Pid.P2))
