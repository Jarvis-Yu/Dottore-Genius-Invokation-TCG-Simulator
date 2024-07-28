import unittest

from .common_imports import *

EVENT_CARD = PlungingStrike

class TestPlungingStrike(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EVENT_CARD: 2}))
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_aura_remover(base_state, Pid.P2)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = replace_character(base_state, Pid.P1, Ningguang, char_id=3)

        """ check plunging strike triggers swap effects before normal attack """
        game_state = base_state
        game_state = AddCombatStatusEffect(Pid.P1, IcicleStatus).execute(game_state)
        game_state = play_char_target_card(game_state, Pid.P1, EVENT_CARD, char_id=3, cost=3)
        assert_last_dmg(self, game_state, Pid.P1, last_index=1, status=True)  # Kaeya Burst Status
        assert_last_dmg(self, game_state, Pid.P1, last_index=0, normal_attack=True)
        self.assertEqual(p1_active_char(game_state).id, 3)
        self.assertIs(game_state.waiting_for(), Pid.P2)  # check is combat action
