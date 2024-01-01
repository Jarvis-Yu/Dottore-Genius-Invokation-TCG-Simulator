import unittest

from .common_imports import *


class TestElementalSoothingWater(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceSoothingWater,
    ).execute(ACTION_TEMPLATE)

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceSoothingWater.valid_in_deck(
                MutableDeck(chars=[Venti, Xingqiu, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceSoothingWater.valid_in_deck(
                MutableDeck(chars=[Xingqiu, Venti, Mona], cards={})
            )
        )

    def test_status_behaviour(self):
        base_state = self.BASE_GAME
        for i in range(3):
            base_state = PublicAddCardEffect(
                Pid.P1, ElementalResonanceSoothingWater
            ).execute(base_state)

        self.assertFalse(ElementalResonanceSoothingWater.strictly_usable(base_state, Pid.P1))

        active_char_id = 1
        for i in range(1, 4):
            with self.subTest(not_full_char_id=i):
                game_state = kill_character(base_state, character_id=i, pid=Pid.P1, hp=8)
                self.assertTrue(ElementalResonanceSoothingWater.strictly_usable(game_state, Pid.P1))
                game_state = step_action(game_state, Pid.P1, CardAction(
                    card=ElementalResonanceSoothingWater,
                    instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 1}))
                ))
                expected_hp: int
                if i == active_char_id:
                    expected_hp = 10
                else:
                    expected_hp = 9
                self.assertEqual(
                    game_state.player1.characters.just_get_character(i).hp,
                    expected_hp
                )

        game_state = base_state
        for i in range(1, 4):
            game_state = kill_character(game_state, character_id=i, pid=Pid.P1, hp=8)
        self.assertTrue(ElementalResonanceSoothingWater.strictly_usable(game_state, Pid.P1))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceSoothingWater,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 1}))
        ))
        p1cs = game_state.player1.characters
        self.assertEqual(p1cs.just_get_character(1).hp, 10)
        self.assertEqual(p1cs.just_get_character(2).hp, 9)
        self.assertEqual(p1cs.just_get_character(3).hp, 9)
