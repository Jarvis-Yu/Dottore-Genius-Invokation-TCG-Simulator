import unittest

from .common_imports import *

EVENT_CARD = FlickeringFourLeafSigil
EVENT_STATUS = FlickeringFourLeafSigilStatus

class TestFatuiConspiracy(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EVENT_CARD: 2}))

        """ check swap to attached character at the end of every round  """
        game_state = base_state
        game_state = play_char_target_card(game_state, Pid.P1, EVENT_CARD, char_id=3, cost=0)
        self.assertIn(EVENT_STATUS, game_state.player1.characters.just_get_character(3).character_statuses)
        assert game_state.player1.just_get_active_character().id != 3

        for _ in range(3):
            game_state = next_round_with_great_omni(game_state)
            self.assertIn(EVENT_STATUS, game_state.player1.characters.just_get_character(3).character_statuses)
            self.assertEqual(game_state.player1.just_get_active_character().id, 3)
