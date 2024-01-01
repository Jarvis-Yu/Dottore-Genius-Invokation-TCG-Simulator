import unittest

from .common_imports import *


class TestLiyueHarborWharf(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, LiyueHarborWharf).execute(base_state)

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LiyueHarborWharf,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 2})),
        ))

        # test 2 more card is drawn for the first round
        game_state = step_until_phase(game_state, game_state.mode.end_phase)
        old_deck_cards = game_state.player1.deck_cards
        old_hand_cards = game_state.player1.hand_cards
        game_state = step_until_signal(game_state, TriggeringSignal.ROUND_END)
        new_deck_cards = game_state.player1.deck_cards
        new_hand_cards = game_state.player1.hand_cards
        self.assertEqual(new_deck_cards + new_hand_cards, old_deck_cards + old_hand_cards)
        self.assertEqual(new_hand_cards.num_cards(), old_hand_cards.num_cards() + 2)

        # test 2 more card is drawn for the second round, and support disappears
        game_state = step_until_phase(game_state, game_state.mode.end_phase)
        old_deck_cards = game_state.player1.deck_cards
        old_hand_cards = game_state.player1.hand_cards
        game_state = step_until_signal(game_state, TriggeringSignal.ROUND_END)
        new_deck_cards = game_state.player1.deck_cards
        new_hand_cards = game_state.player1.hand_cards
        self.assertNotIn(LiyueHarborWharfSupport, game_state.player1.supports)
        self.assertEqual(new_deck_cards + new_hand_cards, old_deck_cards + old_hand_cards)
        self.assertEqual(new_hand_cards.num_cards(), old_hand_cards.num_cards() + 2)