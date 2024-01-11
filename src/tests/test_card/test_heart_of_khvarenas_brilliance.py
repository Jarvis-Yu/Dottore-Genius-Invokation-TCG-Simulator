import unittest

from .common_imports import *

class TestHeartOfKhvarenasBrilliance(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            HeartOfKhvarenasBrilliance: 3,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            Paimon: 10,
        }))
        base_state = grant_all_infinite_revival(base_state)

        game_state = base_state

        # equip and take damage as non-active doesn't trigger
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=HeartOfKhvarenasBrilliance,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice.from_empty(),
            ),
        ))
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=3)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 0)

        # take damage as active triggers
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=3)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 1)

        # can only trigger once per round
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=3)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 1)

        # test usages resets the next round
        game_state = next_round(game_state)
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({}))
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=3)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 1)
