import unittest

from .common_imports import *

class TestLyresong(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Lyresong: 2,
            TenacityOfTheMillelith: 1,
            GamblersEarrings: 1,
        }))

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_player_active(game_state, Pid.P1),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))

        # test Lyresong takes artifact back as card, with cost reduction on next play
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Lyresong,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_player_active(game_state, Pid.P1),
                dice=ActualDice.from_empty(),
            ),
        ))
        p1ac = p1_active_char(game_state)
        self.assertNotIn(TenacityOfTheMillelithStatus, p1ac.character_statuses)
        self.assertIn(TenacityOfTheMillelith, game_state.player1.hand_cards)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_player_active(game_state, Pid.P1),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        p1ac = p1_active_char(game_state)
        self.assertIn(TenacityOfTheMillelithStatus, p1ac.character_statuses)
        self.assertNotIn(TenacityOfTheMillelith, game_state.player1.hand_cards)
