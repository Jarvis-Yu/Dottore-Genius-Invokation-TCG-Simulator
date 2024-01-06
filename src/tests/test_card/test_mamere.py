import unittest

from .common_imports import *

class TestMamere(unittest.TestCase):
    def test_behaviour(self):
        base_state = replace_hand_cards(
            ONE_ACTION_TEMPLATE,
            Pid.P1,
            Cards({
                Mamere: 2,
                ChangTheNinth: 2,
            }),
        )

        # check playing support triggers Mamere
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Mamere,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ChangTheNinth,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        mamere1 = game_state.player1.supports.find_by_sid(1)
        assert isinstance(mamere1, MamereSupport)
        self.assertEqual(mamere1.usages, 2)
        hand_cards = game_state.player1.hand_cards
        generated_card = next(iter(hand_cards - Cards({Mamere: 1, ChangTheNinth: 1})))
        self.assertTrue(issubclass(generated_card, MamereSupport._card_categories))
        self.assertIsNot(generated_card, Mamere)

        # add second Mamere and double check the previous Mamere is not triggered
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Mamere,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            hand_cards - Cards({Mamere: 1}),
        )

        # checks both Mamere can be triggered the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({NorthernSmokedChicken: 1}))
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        hand_cards = game_state.player1.hand_cards
        self.assertEqual(hand_cards.num_cards(), 2)
        for card in hand_cards:
            self.assertTrue(issubclass(card, MamereSupport._card_categories))
            self.assertIsNot(card, Mamere)
        mamere1 = game_state.player1.supports.find_by_sid(1)
        mamere3 = game_state.player1.supports.find_by_sid(3)
        assert isinstance(mamere1, MamereSupport)
        assert isinstance(mamere3, MamereSupport)
        self.assertEqual(mamere1.usages, 1)
        self.assertEqual(mamere3.usages, 2)

        # checks Mamere can be triggered only once per round
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({NorthernSmokedChicken: 1}))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice.from_empty(),
            ),
        ))
        hand_cards = game_state.player1.hand_cards
        self.assertEqual(hand_cards.num_cards(), 0)

        # check playing Mamere doesn't trigger Mamere
        game_state = next_round_with_great_omni(game_state)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Mamere: 1}))
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Mamere,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        hand_cards = game_state.player1.hand_cards
        self.assertEqual(hand_cards.num_cards(), 0)
