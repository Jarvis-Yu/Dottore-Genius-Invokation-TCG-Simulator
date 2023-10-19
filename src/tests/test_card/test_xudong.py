import unittest

from src.tests.test_card.common_imports import *


class TestXudong(unittest.TestCase):
    def test_xudong(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({
                    Xudong: 2,
                    MondstadtHashBrown: 2,
                    SweetMadame: 2,
                })
            ).build()
        ).build()

        # test giving wrong num of dice
        card_action = CardAction(
            card=Xudong,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(Pid.P1, card_action)
        )

        # test giving right num of dice
        card_action = CardAction(
            card=Xudong,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1, Element.GEO: 1})),
        )
        game_state = base_game.action_step(Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        xudong_support = buffed_game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 1)

        buffed_game_state = kill_character(buffed_game_state, 1, Pid.P1, 2)
        buffed_game_state = kill_character(buffed_game_state, 2, Pid.P1, 2)
        buffed_game_state = kill_character(buffed_game_state, 3, Pid.P1, 2)

        # test play 0 cost card does not affect Xudong
        card_action = CardAction(
            card=SweetMadame,
            instruction=StaticTargetInstruction(
                dice=ActualDice({}),
                target=StaticTarget(
                    pid=Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = buffed_game_state.action_step(Pid.P1, card_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        xudong_support = game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 1)
        self.assertTrue(
            game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test play card does benefits from Xudong
        card_action = CardAction(
            card=MondstadtHashBrown,
            instruction=StaticTargetInstruction(
                dice=ActualDice({}),
                target=StaticTarget(
                    pid=Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = buffed_game_state.action_step(Pid.P1, card_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        xudong_support = game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 0)
        self.assertTrue(
            game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test Xudong resets next round
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(EndRoundAction())
        a2.inject_action(EndRoundAction())
        gsm.player_step()  # P1 end
        gsm.player_step()  # P2 end
        gsm.auto_step()  # go through end phase
        game_state = gsm.get_game_state()
        xudong_support = game_state.get_player1().get_supports().just_find(XudongSupport, 1)
        assert isinstance(xudong_support, XudongSupport)
        self.assertEqual(xudong_support.usages, 1)
