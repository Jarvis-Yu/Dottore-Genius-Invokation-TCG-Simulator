import unittest

from .common_imports import *


class TestDawnWinery(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = AddCardEffect(Pid.P1, DawnWinery).execute(base_state)

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=DawnWinery,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 2})),
        ))
        dawn_winery = game_state.player1.supports.just_find(DawnWinerySupport, 1)
        self.assertEqual(dawn_winery.usages, 2)

        # check swap have cost deduction
        game_state = step_swap(game_state, Pid.P1, 3, 0)
        dawn_winery = game_state.player1.supports.just_find(DawnWinerySupport, 1)
        self.assertEqual(dawn_winery.usages, 1)

        # check 0-cost doesn't get more deduction
        game_state = AddCombatStatusEffect(Pid.P1, ChangingShiftsStatus).execute(game_state)
        game_state = step_swap(game_state, Pid.P1, 2, 0)
        dawn_winery = game_state.player1.supports.just_find(DawnWinerySupport, 1)
        self.assertEqual(dawn_winery.usages, 1)

        game_state = step_swap(game_state, Pid.P1, 3, 0)
        dawn_winery = game_state.player1.supports.just_find(DawnWinerySupport, 1)
        self.assertEqual(dawn_winery.usages, 0)

        # check usages reset the next round
        game_state = next_round(game_state)
        dawn_winery = game_state.player1.supports.just_find(DawnWinerySupport, 1)
        self.assertEqual(dawn_winery.usages, 2)
