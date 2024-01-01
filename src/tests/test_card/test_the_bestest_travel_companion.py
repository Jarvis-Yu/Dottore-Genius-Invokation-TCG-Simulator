import unittest

from .common_imports import *


class TestTheBestestTravelCompanion(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TheBestestTravelCompanion: 10,
        }))
        base_state = replace_dice(base_state, Pid.P1, ActualDice({
            Element.OMNI: 1,
            Element.PYRO: 1,
            Element.HYDRO: 1,
            Element.ANEMO: 1,
            Element.ELECTRO: 1,
            Element.DENDRO: 1,
            Element.CRYO: 1,
            Element.GEO: 1,
        }))

        # test behaviour
        game_state = base_state
        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dice=ActualDice(
                {Element.PYRO: 1, Element.HYDRO: 1}
            )),
        ))
        dice_after = game_state.player1.dice
        self.assertEqual(dice_after.num_dice(), dice_before.num_dice())
        self.assertEqual(dice_after[Element.OMNI], dice_before[Element.OMNI] + 2)

        dice_before = dice_after
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dice=ActualDice(
                {Element.OMNI: 1, Element.GEO: 1}
            )),
        ))
        dice_after = game_state.player1.dice
        self.assertEqual(dice_after.num_dice(), dice_before.num_dice())
        self.assertEqual(dice_after[Element.OMNI], dice_before[Element.OMNI] + 1)