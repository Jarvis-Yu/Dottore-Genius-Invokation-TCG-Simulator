import unittest

from .common_imports import *

class TestStrategize(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Strategize: 1,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            Paimon: 4,
        }))

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Strategize,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({Paimon: 2}),
        )
