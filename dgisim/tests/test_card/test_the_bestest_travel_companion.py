import unittest

from .common_imports import *


class TestTheBestestTravelCompanion(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TheBestestTravelCompanion: 10,
        }))
        base_state = replace_dices(base_state, Pid.P1, ActualDices({
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
        dices_before = game_state.get_player1().get_dices()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dices=ActualDices(
                {Element.PYRO: 1, Element.HYDRO: 1}
            )),
        ))
        dices_after = game_state.get_player1().get_dices()
        self.assertEqual(dices_after.num_dices(), dices_before.num_dices())
        self.assertEqual(dices_after[Element.OMNI], dices_before[Element.OMNI] + 2)

        dices_before = dices_after
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dices=ActualDices(
                {Element.OMNI: 1, Element.GEO: 1}
            )),
        ))
        dices_after = game_state.get_player1().get_dices()
        self.assertEqual(dices_after.num_dices(), dices_before.num_dices())
        self.assertEqual(dices_after[Element.OMNI], dices_before[Element.OMNI] + 1)