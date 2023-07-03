import unittest

from src.tests.test_cards.common_imports import *

class TestChangingShifts(unittest.TestCase):
    def test_changing_shifts(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({ChangingShifts: 1})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=ChangingShifts,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(PID.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=ChangingShifts,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0})),
        )
        game_state = base_game.action_step(PID.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertTrue(
            buffed_game_state.get_player1().get_combat_statuses().contains(ChangingShiftsStatus)
        )

        # test swap with dices fails
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(PID.P1, swap_action)
        )

        # test swap with no dices
        swap_action = SwapAction(
            char_id=3,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 0}))
        )
        game_state = buffed_game_state.action_step(PID.P1, swap_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        self.assertFalse(
            game_state.get_player1().get_combat_statuses().contains(ChangingShiftsStatus)
        )

        # test opponent cannot use this
        game_state = buffed_game_state.action_step(PID.P1, EndRoundAction())
        assert game_state is not None
        game_state = auto_step(game_state)
        self.assertRaises(
            Exception,
            lambda: game_state.action_step(PID.P2, swap_action)
        )