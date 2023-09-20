import unittest

from dgisim.tests.test_card.common_imports import *


class TestLiben(unittest.TestCase):
    BASE_STATE = ACTION_TEMPLATE
    BASE_STATE = PublicAddCardEffect(Pid.P1, Liben).execute(BASE_STATE)
    BASE_STATE = replace_character(BASE_STATE, Pid.P1, Collei, 1)
    BASE_STATE = replace_character(BASE_STATE, Pid.P1, Nahida, 2)
    BASE_STATE = replace_character(BASE_STATE, Pid.P1, Tighnari, 3)

    def test_liben(self):
        dices_list = [
            ActualDices({}),
            ActualDices({Element.ELECTRO: 2, Element.CRYO: 1}),
            ActualDices({Element.OMNI: 1, Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDices({Element.OMNI: 2, Element.ELECTRO: 2, Element.CRYO: 1}),
            ActualDices({Element.OMNI: 1, Element.GEO: 3, Element.ELECTRO: 1, Element.CRYO: 2}),
        ]
        expected_list = [
            ActualDices({}),
            ActualDices({Element.ELECTRO: 1}),
            ActualDices({}),
            ActualDices({Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDices({Element.GEO: 2, Element.ELECTRO: 1, Element.CRYO: 1}),
        ]
        for dices, expected_dices in zip(dices_list, expected_list):
            with self.subTest(dices=dices):
                base_state = self.BASE_STATE.factory().f_player1(
                    lambda p: p.factory().dices(
                        dices
                    ).build()
                ).build()
                game_state = step_action(base_state, Pid.P1, CardAction(
                    card=Liben,
                    instruction=DiceOnlyInstruction(dices=ActualDices.from_empty()),
                ))
                gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
                gsm.step_until_holds(
                    lambda gs: (
                        gs.get_effect_stack().is_not_empty()
                        and gs.get_effect_stack().peek() == AllStatusTriggererEffect(
                            pid=Pid.P1,
                            signal=TriggeringSignal.ROUND_END,
                        )
                    )
                )
                game_state = gsm.get_game_state()
                post_liben_dices = game_state.get_player1().get_dices()
                self.assertEqual(post_liben_dices, expected_dices)
                liben = game_state.get_player1().get_supports().just_find(LibenSupport, sid=1)
                assert isinstance(liben, LibenSupport)
                expected_fill = min(3, dices.num_dices()-expected_dices.num_dices())
                self.assertEqual(liben.usages, expected_fill)

                gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
                gsm.step_until_phase(game_state.get_mode().action_phase)
                game_state = gsm.get_game_state()
                pre_dices = game_state.get_player1().get_dices()
                pre_deck_cards = game_state.get_player1().get_deck_cards()
                pre_hand_cards = game_state.get_player1().get_hand_cards()
                game_state = auto_step(game_state)
                post_dices = game_state.get_player1().get_dices()
                post_deck_cards = game_state.get_player1().get_deck_cards()
                post_hand_cards = game_state.get_player1().get_hand_cards()

                if expected_fill == 3:
                    self.assertNotIn(LibenSupport, game_state.get_player1().get_supports())
                    self.assertEqual(post_dices, pre_dices + {Element.OMNI: 2})
                    self.assertEqual(pre_deck_cards + pre_hand_cards, post_deck_cards + post_hand_cards)
                    self.assertEqual(post_hand_cards.num_cards(), pre_hand_cards.num_cards() + 2)
                else:
                    self.assertIn(LibenSupport, game_state.get_player1().get_supports())
                    self.assertEqual(post_dices, pre_dices)
                    self.assertEqual(pre_deck_cards + pre_hand_cards, post_deck_cards + post_hand_cards)
                    self.assertEqual(post_hand_cards.num_cards(), pre_hand_cards.num_cards())
