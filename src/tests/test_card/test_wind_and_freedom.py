import unittest

from .common_imports import *

class TestWindAndFreedom(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, WindAndFreedom).execute(base_state)
        base_state = grant_all_infinite_revival(base_state)

        game_state = step_action(base_state, Pid.P1, CardAction(
            card=WindAndFreedom,
            instruction=DiceOnlyInstruction(dice=ActualDice({})),
        ))
        game_state = step_swap(game_state, Pid.P1, char_id=3)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        self.assertIn(WindAndFreedomStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.just_get_active_character().id, 3)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.just_get_active_character().id, 1)
        self.assertIn(WindAndFreedomStatus, game_state.player1.combat_statuses)

        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.just_get_active_character().id, 2)
        self.assertIn(WindAndFreedomStatus, game_state.player1.combat_statuses)
