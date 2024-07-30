import unittest

from .common_imports import *

ARCANE_LEGEND = DayOfResistanceMomentOfShatteredDreams
ARCANE_STATUS = DayOfResistanceMomentOfShatteredDreamsStatus

def p1_arcane_status(game_state: GameState, char_id: int = 1) -> ARCANE_STATUS:
    return game_state.player1.characters.just_get_character(char_id).character_statuses.just_find(ARCANE_STATUS)

class TestDayOfResistanceMomentOfShatteredDreams(unittest.TestCase):
    def test_behaviour(self):
        self.assertTrue(issubclass(ARCANE_LEGEND, ArcaneLegendCard))

        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARCANE_LEGEND: 1}))
        base_state = play_char_target_card(base_state, Pid.P1, ARCANE_LEGEND, 1, cost=0)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = add_aura_remover(base_state, Pid.P1)

        self.assertIn(ARCANE_STATUS, base_state.player1.characters.just_get_character(1).character_statuses)

        """ check status can -1 damage 4 times """
        game_state = base_state
        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1, char_id=1)
        assert_last_dmg(self, game_state, Pid.P1, amount=0)
        self.assertEqual(p1_arcane_status(game_state, 1).usages, 3)
        game_state = simulate_status_dmg(game_state, 2, Element.PYRO, Pid.P1, char_id=1)
        assert_last_dmg(self, game_state, Pid.P1, amount=1)
        self.assertEqual(p1_arcane_status(game_state, 1).usages, 2)
        # check dmg to other char is not reduced
        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1, char_id=2)
        assert_last_dmg(self, game_state, Pid.P1, amount=1)
        game_state = simulate_status_dmg(game_state, 2, Element.PYRO, Pid.P1, char_id=3)
        assert_last_dmg(self, game_state, Pid.P1, amount=2)
        self.assertEqual(p1_arcane_status(game_state, 1).usages, 2)
        # back to 4-times test
        game_state = simulate_status_dmg(game_state, 3, Element.HYDRO, Pid.P1, char_id=1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2)
        self.assertEqual(p1_arcane_status(game_state, 1).usages, 1)
        game_state = simulate_status_dmg(game_state, 4, Element.ANEMO, Pid.P1, char_id=1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3)
        self.assertNotIn(ARCANE_STATUS, game_state.player1.characters.just_get_character(1).character_statuses)

        """ check it lasts one round only """
        game_state = base_state
        game_state = next_round(game_state)
        self.assertNotIn(ARCANE_STATUS, game_state.player1.characters.just_get_character(1).character_statuses)


    def test_only_only_can_be_played(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARCANE_LEGEND: 2}))

        game_state = base_state
        game_state = play_char_target_card(game_state, Pid.P1, ARCANE_LEGEND, 1)
        self.assertRaises(Exception, lambda: play_char_target_card(game_state, Pid.P1, ARCANE_LEGEND, 2))
