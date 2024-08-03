import unittest

from .common_imports import *


class TestLiyueHarborWharf(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = AddCardEffect(Pid.P1, LiyueHarborWharf).execute(base_state)

        game_state = base_state
        game_state = play_support_card(game_state, Pid.P1, LiyueHarborWharf, cost=2)

        # test 2 more card is drawn for the first round
        old_deck_cards = game_state.player1.deck_cards.to_cards()
        old_hand_cards = game_state.player1.hand_cards
        game_state = next_round(game_state)
        new_deck_cards = game_state.player1.deck_cards.to_cards()
        new_hand_cards = game_state.player1.hand_cards
        self.assertIn(LiyueHarborWharfSupport, game_state.player1.supports)
        self.assertEqual(new_deck_cards + new_hand_cards, old_deck_cards + old_hand_cards)
        self.assertEqual(
            new_hand_cards.num_cards(),
            old_hand_cards.num_cards() + game_state.mode.cards_per_round() + 2,
        )

        # test 2 more card is drawn for the second round, and support disappears
        old_deck_cards = game_state.player1.deck_cards.to_cards()
        old_hand_cards = game_state.player1.hand_cards
        game_state = next_round(game_state)
        new_deck_cards = game_state.player1.deck_cards.to_cards()
        new_hand_cards = game_state.player1.hand_cards
        self.assertNotIn(LiyueHarborWharfSupport, game_state.player1.supports)
        self.assertEqual(new_deck_cards + new_hand_cards, old_deck_cards + old_hand_cards)
        self.assertEqual(
            new_hand_cards.num_cards(),
            old_hand_cards.num_cards() + game_state.mode.cards_per_round() + 2,
        )
