import unittest

from .common_imports import *

class TestTossUp(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TossUp: 2,
        }))
        base_state = replace_dice(base_state, Pid.P1, ActualDice.from_empty())

        game_state = base_state
        
        # check that toss up cannot be used when there is no dice to reroll
        self.assertFalse(TossUp.loosely_usable(game_state, Pid.P1))

        # check that toss up can reroll up to 2 times
        game_state = replace_dice(game_state, Pid.P1, ActualDice({
            Element.PYRO: 1, Element.HYDRO: 1, Element.ANEMO: 1,
        }))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TossUp,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_action(game_state, Pid.P1, DiceSelectAction(
            selected_dice=ActualDice({Element.PYRO: 1}),
        ))
        game_state = step_action(game_state, Pid.P1, DiceSelectAction(
            selected_dice=ActualDice({Element.HYDRO: 1}),
        ))
        self.assertRaises(Exception, lambda: step_action(game_state, Pid.P1, DiceSelectAction(
            selected_dice=ActualDice({Element.ANEMO: 1}),
        )))

        # check that toss up allows early stop
        game_state = replace_dice(game_state, Pid.P1, ActualDice({
            Element.PYRO: 1, Element.HYDRO: 1, Element.ANEMO: 1,
        }))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TossUp,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_action(game_state, Pid.P1, DiceSelectAction(
            selected_dice=ActualDice.from_empty(),
        ))
        self.assertRaises(Exception, lambda: step_action(game_state, Pid.P1, DiceSelectAction(
            selected_dice=ActualDice({Element.ANEMO: 1}),
        )))
