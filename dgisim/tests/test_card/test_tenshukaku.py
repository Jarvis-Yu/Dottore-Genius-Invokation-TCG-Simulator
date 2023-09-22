import unittest

from .common_imports import *


class TestTenshukaku(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Tenshukaku: 1,
        }))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=Tenshukaku,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.CRYO: 2})),
        ))
        base_state = step_until_phase(base_state, phase=base_state.get_mode().action_phase)

        # test triggered when types of dices == 5
        pre_dices = ActualDices({
            Element.PYRO: 1,
            Element.HYDRO: 1,
            Element.ANEMO: 1,
            Element.ELECTRO: 1,
            Element.DENDRO: 1,
        })
        game_state = replace_dices(base_state, Pid.P1, pre_dices)
        game_state = auto_step(game_state)
        self.assertEqual(
            game_state.get_player1().get_dices(),
            pre_dices + {Element.OMNI: 1},
        )

        # test triggered when types of dices > 5
        pre_dices = ActualDices({
            Element.PYRO: 1,
            Element.HYDRO: 1,
            Element.ANEMO: 1,
            Element.ELECTRO: 1,
            Element.DENDRO: 1,
            Element.CRYO: 1,
        })
        game_state = replace_dices(base_state, Pid.P1, pre_dices)
        game_state = auto_step(game_state)
        self.assertEqual(
            game_state.get_player1().get_dices(),
            pre_dices + {Element.OMNI: 1},
        )

        # test not triggered when types of dices < 5
        pre_dices = ActualDices({
            Element.PYRO: 1,
            Element.HYDRO: 1,
            Element.ANEMO: 1,
            Element.ELECTRO: 1,
        })
        game_state = replace_dices(base_state, Pid.P1, pre_dices)
        game_state = auto_step(game_state)
        self.assertEqual(
            game_state.get_player1().get_dices(),
            pre_dices,
        )

        # test omni treated as different kinds of dices
        pre_dices = ActualDices({
            Element.OMNI: 3,
            Element.PYRO: 1,
            Element.HYDRO: 1,
        })
        game_state = replace_dices(base_state, Pid.P1, pre_dices)
        game_state = auto_step(game_state)
        self.assertEqual(
            game_state.get_player1().get_dices(),
            pre_dices + {Element.OMNI: 1},
        )
