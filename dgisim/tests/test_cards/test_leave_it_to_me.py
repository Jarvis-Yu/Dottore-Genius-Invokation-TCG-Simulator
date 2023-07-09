import unittest

from dgisim.tests.test_cards.common_imports import *


class TestLeaveItToMe(unittest.TestCase):
    def test_leave_it_to_me(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({LeaveItToMe: 1})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=LeaveItToMe,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(Pid.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=LeaveItToMe,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0})),
        )
        game_state = base_game.action_step(Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertTrue(
            buffed_game_state.get_player1().get_combat_statuses().contains(LeaveItToMeStatus)
        )

        # test swap with no dices fails
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(Pid.P1, swap_action)
        )

        # test swap with no dices
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1}))
        )
        game_state = buffed_game_state.action_step(Pid.P1, swap_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        self.assertFalse(
            game_state.get_player1().get_combat_statuses().contains(LeaveItToMeStatus)
        )
        self.assertEqual(game_state.get_active_player_id(), Pid.P1)

        # test opponent cannot use this
        game_state = buffed_game_state.action_step(Pid.P1, SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        assert game_state is not None
        game_state = auto_step(game_state)
        game_state = game_state.action_step(Pid.P2, swap_action)
        assert game_state is not None
        game_state = auto_step(game_state)
        self.assertEqual(game_state.get_active_player_id(), Pid.P1)