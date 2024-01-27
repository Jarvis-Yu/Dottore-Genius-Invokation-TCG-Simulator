import unittest

from .common_imports import *

class TestVourukashasGlow(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            VourukashasGlow: 3,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            Paimon: 10,
        }))
        base_state = grant_all_infinite_revival(base_state)

        game_state = base_state

        # equip and take damage as non-active doesn't trigger
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=VourukashasGlow,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice({Element.HYDRO: 1}),
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

        # check heals at the end phase
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=VourukashasGlow,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 1}),
            ),
        ))
        p1c1_bfr, p1c2_bfr, p1c3_bfr = game_state.player1.characters.get_characters()

        game_state = next_round(game_state)
        p1c1_aft, p1c2_aft, p1c3_aft = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1_aft.hp, p1c1_bfr.hp)  # as the other effect was not triggered
        self.assertEqual(p1c2_aft.hp, p1c2_bfr.hp)  # as artifact is not equipped
        self.assertEqual(p1c3_aft.hp, p1c3_bfr.hp + 1)

        # test usages resets the next round
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({}))
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=3)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 1)
