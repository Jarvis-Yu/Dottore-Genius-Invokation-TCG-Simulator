import unittest

from .common_imports import *

class TestStoneAndContracts(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            ButterCrab: 2,
        }))
        base_state = add_dmg_listener(base_state, Pid.P1)

        game_state = base_state

        # test all character gets shield with correct amount of dmg deduction
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ButterCrab,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 2})),
        ))
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1, char_id=3)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(dmgs[0].damage, 1)
        self.assertEqual(dmgs[1].damage, 1)
        self.assertEqual(dmgs[2].damage, 0)

        # test shield takes dmg only once
        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1, char_id=3)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)

        # test shield only lasts one round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ButterCrab,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 1, Element.GEO: 1})),
        ))
        p1ac = p1_active_char(game_state)
        self.assertIn(ButterCrabStatus, p1ac.character_statuses)

        game_state = next_round(game_state)
        p1ac = p1_active_char(game_state)
        self.assertNotIn(ButterCrabStatus, p1ac.character_statuses)
