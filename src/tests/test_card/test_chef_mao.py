import unittest

from .common_imports import *

class TestDunyarzad(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            ChefMao: 2,
            NorthernSmokedChicken: 2,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            Liben: 2,  # Companion
            KnightsOfFavoniusLibrary: 2,  # Location
            ParametricTransformer: 2,  # Item
            MondstadtHashBrown: 2,  # Food
            WolfsGravestone: 2,  # Weapon
            LeaveItToMe: 2,  # Event
        }))

        # test first play of food add dice and draw food
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ChefMao,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        self.assertIn(ChefMaoSupport, game_state.player1.supports)

        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        dice_after = game_state.player1.dice

        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({
                ChefMao: 1,
                NorthernSmokedChicken: 1,
                MondstadtHashBrown: 1,
            }),
        )
        dice_diff = dice_after - dice_before
        self.assertEqual(dice_diff.num_dice(), 1)
        self.assertIn(next(iter(dice_diff)), PURE_ELEMENTS)

        # test dice effects are once per round
        dice_before = dice_after
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice.from_empty(),
            ),
        ))
        dice_after = game_state.player1.dice
        self.assertEqual(dice_after, dice_before)

        # test draw effect is once per game
        game_state = next_round(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({NorthernSmokedChicken: 1}))
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({MondstadtHashBrown: 1}))

        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        dice_after = game_state.player1.dice

        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({}),
        )
        dice_diff = dice_after - dice_before
        self.assertEqual(dice_diff.num_dice(), 1)
        self.assertIn(next(iter(dice_diff)), PURE_ELEMENTS)
