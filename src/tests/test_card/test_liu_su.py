import unittest

from .common_imports import *

class TestLiuSu(unittest.TestCase):
    def test_behaviour(self):
        base_state = replace_hand_cards(
            ONE_ACTION_TEMPLATE,
            Pid.P1,
            Cards({LiuSu: 2}),
        )

        game_state = base_state
        for _ in range(2):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=LiuSu,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
            ))

        # swap to no energy gives energy
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P1, 2)
        ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(ac.get_energy(), 1)
        sups = game_state.get_player1().get_supports()
        liu1, liu2 = sups.just_find(LiuSuSupport, 1), sups.just_find(LiuSuSupport, 2)
        assert isinstance(liu1, LiuSuSupport) and isinstance(liu2, LiuSuSupport)
        self.assertEqual(liu1.usages, 1)
        self.assertFalse(liu1.activated)
        self.assertEqual(liu2.usages, 2)
        self.assertTrue(liu2.activated)

        # swapping to character with energy doesn't charage
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P1, 2)
        ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(ac.get_energy(), 1)
        sups = game_state.get_player1().get_supports()
        liu1, liu2 = sups.just_find(LiuSuSupport, 1), sups.just_find(LiuSuSupport, 2)
        assert isinstance(liu1, LiuSuSupport) and isinstance(liu2, LiuSuSupport)
        self.assertEqual(liu1.usages, 1)
        self.assertFalse(liu1.activated)
        self.assertEqual(liu2.usages, 2)
        self.assertTrue(liu2.activated)

        # LiuSu can only be triggered once per round
        game_state = step_swap(game_state, Pid.P1, 3)
        ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(ac.get_energy(), 1)
        sups = game_state.get_player1().get_supports()
        liu1, liu2 = sups.just_find(LiuSuSupport, 1), sups.just_find(LiuSuSupport, 2)
        assert isinstance(liu1, LiuSuSupport) and isinstance(liu2, LiuSuSupport)
        self.assertEqual(liu1.usages, 1)
        self.assertFalse(liu1.activated)
        self.assertEqual(liu2.usages, 1)
        self.assertFalse(liu2.activated)

        # Liu Su reactivated the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_swap(game_state, Pid.P1, 1)
        ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(ac.get_energy(), 1)
        sups = game_state.get_player1().get_supports()
        liu1, liu2 = sups.find(LiuSuSupport, 1), sups.just_find(LiuSuSupport, 2)  # type: ignore
        assert isinstance(liu2, LiuSuSupport)
        self.assertIsNone(liu1)
        self.assertEqual(liu2.usages, 1)
        self.assertTrue(liu2.activated)
