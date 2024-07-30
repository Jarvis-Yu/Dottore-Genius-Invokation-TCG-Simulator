import unittest

from .common_imports import *

ARCANE_LEGEND = ViciousAncientBattle

class TestVicioutAncientBattle(unittest.TestCase):
    def test_behaviour(self):
        self.assertTrue(issubclass(ARCANE_LEGEND, ArcaneLegendCard))

        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARCANE_LEGEND: 1}))

        assert base_state.player2.just_get_active_character().id == 1
        assert base_state.player2.just_get_active_character().energy == 0

        """ check cannot be played when opponent active has no energy """
        game_state = base_state
        self.assertRaises(Exception, lambda: play_dice_only_card(game_state, Pid.P1, ARCANE_LEGEND, cost=0))

        # set opponent non-active energy to be non-zero, but still cannot be played
        game_state = recharge_energy_for(game_state, Pid.P2, char_id=2, amount=2)
        self.assertRaises(Exception, lambda: play_dice_only_card(game_state, Pid.P1, ARCANE_LEGEND, cost=0))

        # set opponent active energy to be non-zero, and can be played
        game_state = recharge_energy_for(game_state, Pid.P2, amount=2)
        game_state = play_dice_only_card(game_state, Pid.P1, ARCANE_LEGEND, cost=0)
        self.assertEqual(game_state.player2.just_get_active_character().energy, 1)

    def test_only_only_can_be_played(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARCANE_LEGEND: 2}))
        base_state = recharge_energy_for_all(base_state)

        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, ARCANE_LEGEND, cost=0)
        self.assertRaises(Exception, lambda: play_dice_only_card(game_state, Pid.P1, ARCANE_LEGEND, cost=0))