import unittest

from src.tests.test_card.common_imports import *


class TestLiben(unittest.TestCase):
    BASE_STATE = ACTION_TEMPLATE
    BASE_STATE = PublicAddCardEffect(Pid.P1, Liben).execute(BASE_STATE)
    BASE_STATE = replace_character(BASE_STATE, Pid.P1, Collei, 1)
    BASE_STATE = replace_character(BASE_STATE, Pid.P1, Nahida, 2)
    BASE_STATE = replace_character(BASE_STATE, Pid.P1, Tighnari, 3)

    def test_liben(self):
        dice_list = [
            ActualDice({}),
            ActualDice({Element.ELECTRO: 2, Element.CRYO: 1}),
            ActualDice({Element.OMNI: 1, Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDice({Element.OMNI: 2, Element.ELECTRO: 2, Element.CRYO: 1}),
            ActualDice({Element.OMNI: 1, Element.GEO: 3, Element.ELECTRO: 1, Element.CRYO: 2}),
        ]
        expected_list = [
            ActualDice({}),
            ActualDice({Element.ELECTRO: 1}),
            ActualDice({}),
            ActualDice({Element.OMNI: 1, Element.ELECTRO: 1}),
            ActualDice({Element.OMNI: 1, Element.GEO: 2, Element.CRYO: 1}),
        ]
        for dice, expected_dice in zip(dice_list, expected_list):
            with self.subTest(dice=dice):
                base_state = self.BASE_STATE.factory().f_player1(
                    lambda p: p.factory().dice(
                        dice
                    ).build()
                ).build()
                game_state = step_action(base_state, Pid.P1, CardAction(
                    card=Liben,
                    instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
                ))
                gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
                gsm.step_until_holds(
                    lambda gs: (
                            gs.effect_stack.is_not_empty()
                            and gs.effect_stack.peek() == AllStatusTriggererEffect(
                            pid=Pid.P1,
                            signal=TriggeringSignal.ROUND_END,
                        )
                    )
                )
                game_state = gsm.get_game_state()
                post_liben_dice = game_state.player1.dice
                self.assertEqual(post_liben_dice, expected_dice)
                liben = game_state.player1.supports.just_find(LibenSupport, sid=1)
                assert isinstance(liben, LibenSupport)
                expected_fill = min(3, dice.num_dice()-expected_dice.num_dice())
                self.assertEqual(liben.usages, expected_fill)

                gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
                gsm.step_until_phase(game_state.mode.action_phase)
                game_state = gsm.get_game_state()
                pre_dice = game_state.player1.dice
                pre_deck_cards = game_state.player1.deck_cards
                pre_hand_cards = game_state.player1.hand_cards
                game_state = auto_step(game_state)
                post_dice = game_state.player1.dice
                post_deck_cards = game_state.player1.deck_cards
                post_hand_cards = game_state.player1.hand_cards

                if expected_fill == 3:
                    self.assertNotIn(LibenSupport, game_state.player1.supports)
                    self.assertEqual(post_dice, pre_dice + {Element.OMNI: 2})
                    self.assertEqual(pre_deck_cards + pre_hand_cards, post_deck_cards + post_hand_cards)
                    self.assertEqual(post_hand_cards.num_cards(), pre_hand_cards.num_cards() + 2)
                else:
                    self.assertIn(LibenSupport, game_state.player1.supports)
                    self.assertEqual(post_dice, pre_dice)
                    self.assertEqual(pre_deck_cards + pre_hand_cards, post_deck_cards + post_hand_cards)
                    self.assertEqual(post_hand_cards.num_cards(), pre_hand_cards.num_cards())
