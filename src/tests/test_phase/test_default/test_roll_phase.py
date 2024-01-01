import unittest

from src.dgisim.action.action import *
from src.dgisim.dice import ActualDice
from src.dgisim.element import Element
from src.dgisim.state.enums import Act, Pid
from src.tests.helpers.game_state_templates import ACTION_TEMPLATE


class TestRollPhase(unittest.TestCase):
    BASE_GAME_STATE = ACTION_TEMPLATE.factory().phase(
        ACTION_TEMPLATE.mode.roll_phase()
    ).f_player1(
        lambda p1: p1.factory().phase(Act.ACTION_PHASE).build()
    ).f_player2(
        lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
    ).build()

    def test_step_failure(self):
        game_state = self.BASE_GAME_STATE
        self.assertRaises(Exception, lambda: game_state.step())

    def test_handle_dice_selection(self):
        game_state = self.BASE_GAME_STATE.factory().f_player1(
            lambda p1: p1.factory().dice_reroll_chances(2).build()
        ).build()
        game_state.action_step(
            Pid.P1,
            DiceSelectAction(selected_dice=ActualDice({Element.OMNI: 2}))
        )
        self.assertIs(game_state.player1.phase, Act.ACTION_PHASE)

        self.assertRaises(
            Exception,
            lambda: game_state.action_step(Pid.P1, CharacterSelectAction(char_id=2))
        )

        self.assertIsNone(
            game_state.phase.action_generator(game_state, Pid.P2)
        )
