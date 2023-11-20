import unittest

from .common_imports import *

class TestWhenTheCraneReturned(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, WhenTheCraneReturned).execute(base_state)
        base_state = grant_all_infinite_revival(base_state)

        game_state = step_action(base_state, Pid.P1, CardAction(
            card=WhenTheCraneReturned,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1})),
        ))
        game_state = step_swap(game_state, Pid.P1, char_id=3)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        self.assertIn(WhenTheCraneReturnedStatus, game_state.get_player1().get_combat_statuses())
        self.assertEqual(game_state.get_player1().just_get_active_character().get_id(), 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.get_player1().just_get_active_character().get_id(), 1)
        self.assertNotIn(WhenTheCraneReturnedStatus, game_state.get_player1().get_combat_statuses())