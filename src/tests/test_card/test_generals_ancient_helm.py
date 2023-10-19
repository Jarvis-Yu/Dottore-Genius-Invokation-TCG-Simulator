import unittest

from .common_imports import *


class TestGeneralsAncientHelm(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, GeneralsAncientHelm).execute(base_state)

        game_state = base_state
        for i in range(1, 3):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=GeneralsAncientHelm,
                instruction=StaticTargetInstruction(
                    dice=ActualDice({Element.OMNI: 2}),
                    target=StaticTarget.from_char_id(Pid.P1, i),
                )
            ))

        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 7)

        game_state = next_round(game_state)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1, char_id=2)
        p1c1, p1c2, _ = game_state.get_player1().get_characters().get_characters()
        self.assertEqual(p1c1.get_hp(), 6)
        self.assertEqual(p1c2.get_hp(), 9)