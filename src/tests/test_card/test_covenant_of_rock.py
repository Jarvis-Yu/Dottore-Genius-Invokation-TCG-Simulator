import unittest

from .common_imports import *

class TestCovenantOfRock(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, CovenantOfRock).execute(base_state)

        assert base_state.player1.dice.num_dice() > 0
        self.assertFalse(CovenantOfRock.loosely_usable(base_state, Pid.P1))

        game_state = replace_dice(base_state, Pid.P1, ActualDice.from_empty())
        self.assertTrue(CovenantOfRock.loosely_usable(game_state, Pid.P1))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=CovenantOfRock,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        dice = game_state.player1.dice
        self.assertEqual(dice.num_dice(), 2)
        self.assertTrue(all(
            dice[elem] <= 1
            for elem in dice
        ))
