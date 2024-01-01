import unittest

from .common_imports import *

class TestInEveryHouseAStove(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, InEveryHouseAStove).execute(base_state)

        hand_before = base_state.player1.hand_cards

        for n in range(1, 6):
            with self.subTest(round=n):
                game_state = base_state.factory().round(n).build()
                game_state = step_action(game_state, Pid.P1, CardAction(
                    card=InEveryHouseAStove,
                    instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
                ))
                hand_after = game_state.player1.hand_cards
                self.assertEqual(
                    hand_after.num_cards() - (hand_before.num_cards() - 1),  # -1 for card played
                    min(n, 4),
                )