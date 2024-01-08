import unittest

from .common_imports import *

class TestDunyarzad(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Dunyarzad: 2,
            ChangTheNinth: 1,  # 0 cost Companion
            Paimon: 2,  # 3 cost Companion
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            Liben: 2,  # Companion
            KnightsOfFavoniusLibrary: 2,  # Location
            ParametricTransformer: 2,  # Item
            NorthernSmokedChicken: 2,  # Food
            WolfsGravestone: 2,  # Weapon
            LeaveItToMe: 2,  # Event
        }))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=Dunyarzad,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        self.assertIn(DunyarzadSupport, base_state.player1.supports)

        # test 0 cost Companion draws card but keeps discount
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ChangTheNinth,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertEqual(game_state.player1.hand_cards[Liben], 1)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(game_state.player1.hand_cards[Liben], 1)

        # test discount and draw can come together (and discount only once per round)
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(game_state.player1.hand_cards[Liben], 1)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))

        # test discount resets every round, but not draw
        game_state = next_round(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Paimon: 1}))
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({Liben: 1}))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(game_state.player1.hand_cards[Liben], 0)
