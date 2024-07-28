import unittest

from .common_imports import *

EVENT_CARD = Pankration
EVENT_STATUS = PankrationStatus

class TestFatuiConspiracy(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EVENT_CARD: 2}))
        base_state = replace_hand_cards(base_state, Pid.P2, Cards({}))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({Paimon: 30}))
        base_state = replace_deck_cards(base_state, Pid.P2, Cards({Paimon: 30}))

        """ check only playable when num of dice (self) >= 8 """
        game_state = base_state
        assert game_state.player2.dice.num_dice() >= 8
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 7}))
        self.assertFalse(EVENT_CARD.loosely_usable(game_state, Pid.P1))
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 8}))
        self.assertTrue(EVENT_CARD.loosely_usable(game_state, Pid.P1))
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 9}))
        self.assertTrue(EVENT_CARD.loosely_usable(game_state, Pid.P1))
        game_state = replace_dice(game_state, Pid.P2, ActualDice({Element.OMNI: 4}))
        self.assertTrue(EVENT_CARD.loosely_usable(game_state, Pid.P1))

        """ check only playable when opponent hasn't ended """
        game_state = base_state
        assert game_state.player1.dice.num_dice() >= 8
        self.assertTrue(EVENT_CARD.loosely_usable(game_state, Pid.P1))
        game_state = end_round(game_state, Pid.P2)
        self.assertFalse(EVENT_CARD.loosely_usable(game_state, Pid.P1))

        """ check whoever ends first girts their opponent two draws """
        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=0)
        self.assertIn(EVENT_STATUS, game_state.player1.combat_statuses)
        played_state = game_state

        # self-end first
        game_state = end_round(played_state, Pid.P1)
        self.assertNotIn(EVENT_STATUS, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 0)
        self.assertEqual(game_state.player2.hand_cards[Paimon], 2)

        # oppo-end first
        game_state = end_round(played_state, Pid.P2)
        self.assertNotIn(EVENT_STATUS, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 2)
        self.assertEqual(game_state.player2.hand_cards[Paimon], 0)
