import unittest

from .common_imports import *

class TestInEveryHouseAStove(unittest.TestCase):
    def test_first_round_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = AddCardEffect(Pid.P1, InEveryHouseAStove).execute(base_state)

        # round 1 with 1 kind of 2 talent cards should not trigger
        game_state = replace_entire_deck(base_state, Pid.P1, Cards({
            InEveryHouseAStove: 1,
            ThunderingPenance: 2,
        }))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=InEveryHouseAStove,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertNotIn(ThunderingPenance, game_state.player1.hand_cards)

        # round 1 with 2 kinds of 1 talent cards should trigger
        game_state = replace_entire_deck(base_state, Pid.P1, Cards({
            InEveryHouseAStove: 1,
            ThunderingPenance: 1,
            ColdBloodedStrike: 1,
            Paimon: 10000,
        }))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=InEveryHouseAStove,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertTrue(
            ThunderingPenance in game_state.player1.hand_cards or
            ColdBloodedStrike in game_state.player1.hand_cards
        )

        # round 2 with 2 kinds of talent cards should not trigger
        game_state = replace_entire_deck(base_state, Pid.P1, OrderedCards((
            InEveryHouseAStove,
            ThunderingPenance,
            ColdBloodedStrike,
            Paimon, Paimon, Paimon,
        ))).factory().round(2).build()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=InEveryHouseAStove,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertFalse(  # this may fail when things are correct [2 / (0x7fffffff + 3)] of the times
            ThunderingPenance in game_state.player1.hand_cards or
            ColdBloodedStrike in game_state.player1.hand_cards
        )

    def test_2plus_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = AddCardEffect(Pid.P1, InEveryHouseAStove).execute(base_state)
        base_state = replace_entire_deck(base_state, Pid.P1, Cards({
            InEveryHouseAStove: 1,
            Paimon: 255,
        }))

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
                    min((max(0, n - 1)), 4),
                )