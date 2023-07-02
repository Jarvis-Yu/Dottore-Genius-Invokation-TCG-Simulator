import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.card.cards import *
from dgisim.src.card.card import *
from dgisim.src.status.status import *
from dgisim.src.support.support import *
from dgisim.src.agents import *
from dgisim.src.state.enums import PID


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