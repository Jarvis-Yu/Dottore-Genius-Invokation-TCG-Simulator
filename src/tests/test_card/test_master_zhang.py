import unittest

from .common_imports import *

class TestMasterZhang(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            MasterZhang: 2,
            AquilaFavonia: 3,
        }))
        base_state = replace_character(base_state, Pid.P1, Keqing, 1)
        base_state = replace_character(base_state, Pid.P1, Keqing, 2)
        base_state = replace_character(base_state, Pid.P1, Keqing, 3)

        # test Master Zhang has cost discount on first play
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=MasterZhang,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AquilaFavonia,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AquilaFavonia,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))

        # test Master Zhang's discount refreshes every round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AquilaFavonia,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice({Element.OMNI: 0}),
            ),
        ))
