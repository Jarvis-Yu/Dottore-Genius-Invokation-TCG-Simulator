import unittest

from .common_imports import *

class TestLyresong(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            YayoiNanatsuki: 2,
            TenacityOfTheMillelith: 3,
            GamblersEarrings: 1,
        }))

        # test Yayoi Nanatsuki has cost discount on first play
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=YayoiNanatsuki,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))

        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice({Element.OMNI: 0}),
            ),
        ))
