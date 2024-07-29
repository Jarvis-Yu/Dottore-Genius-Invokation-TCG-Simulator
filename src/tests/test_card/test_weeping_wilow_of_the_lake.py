import unittest

from .common_imports import *

SUPPORT = WeepingWillowOfTheLake
SUPPORT_STATUS = WeepingWillowOfTheLakeSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestWeepingWillowOfTheLake(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards.from_dict_ordered({Paimon: 30}))
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({SUPPORT: 4}))

        # check end round with > 2 cards does not trigger willow
        game_state = base_state
        game_state = play_support_card(game_state, Pid.P1, SUPPORT, cost=1)
        assert game_state.player1.hand_cards.num_cards() == 3

        def after_END_ROUND_CHECK_OUT(gs: GameState) -> bool:
            if gs.effect_stack.is_empty():
                return False
            effect = gs.effect_stack.peek()
            return isinstance(effect, AllStatusTriggererEffect) and effect.signal is TriggeringSignal.ROUND_END

        game_state = step_until(game_state, after_END_ROUND_CHECK_OUT)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), 3 + game_state.mode.cards_per_round())
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        
        # check end round with == 2 cards triggers willow
        game_state = next_round(game_state)
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Liben: 2}))
        game_state = step_until(game_state, after_END_ROUND_CHECK_OUT)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 2 + game_state.mode.cards_per_round())
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)

        # check end round with < 2 cards triggers willow
        game_state = next_round(game_state)
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Liben: 1}))
        game_state = step_until(game_state, after_END_ROUND_CHECK_OUT)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 2 + game_state.mode.cards_per_round())
        self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)
