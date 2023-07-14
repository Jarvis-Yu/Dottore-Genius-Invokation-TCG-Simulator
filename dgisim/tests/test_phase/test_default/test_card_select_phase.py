import unittest

from dgisim.src.action.action import *
from dgisim.src.card.cards import Cards
from dgisim.src.phase.default.card_select_phase import CardSelectPhase
from dgisim.src.state.enums import Act, Pid
from dgisim.tests.helpers.game_state_templates import ACTION_TEMPLATE

class TestCardSelectPhase(unittest.TestCase):
    BASE_GAME_STATE = ACTION_TEMPLATE.factory().phase(
        ACTION_TEMPLATE.get_mode().card_select_phase()
    ).f_player1(
        lambda p1: p1.factory().phase(Act.ACTION_PHASE).build()
    ).f_player2(
        lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
    ).build()

    def test_step_failure(self):
        game_state = self.BASE_GAME_STATE
        self.assertRaises(Exception, lambda: game_state.step())

    def test_handle_card_drawing(self):
        game_state = self.BASE_GAME_STATE.factory().f_player1(
            lambda p1: p1.factory().card_redraw_chances(2).build()
        ).build()
        game_state.action_step(
            Pid.P1,
            CardsSelectAction(selected_cards=Cards({}))
        )
        self.assertIs(game_state.get_player1().get_phase(), Act.ACTION_PHASE)

        self.assertRaises(
            Exception,
            lambda: game_state.action_step(Pid.P1, CharacterSelectAction(char_id=2))
        )

        self.assertIsNone(
            game_state.get_phase().action_generator(game_state, Pid.P2)
        )
