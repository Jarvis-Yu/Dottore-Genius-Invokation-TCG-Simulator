import unittest

from .common_imports import *


class TestElementalResonanceHighVoltage(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceHighVoltage,
    ).execute(ACTION_TEMPLATE).factory().f_player1(
        lambda p1: p1.factory().f_characters(
            lambda cs: cs.factory().f_characters(
                lambda chars: tuple(
                    char.factory().energy(char.get_max_energy() - 1).build()
                    for char in chars
                )
            ).active_character_id(
                2
            ).build()
        ).build()
    ).build()

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceHighVoltage.valid_in_deck(
                MutableDeck(chars=[Klee, Bennett, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceHighVoltage.valid_in_deck(
                MutableDeck(chars=[Bennett, YaeMiko, Keqing], cards={})
            )
        )

    def test_status_behaviour(self):
        base_state = self.BASE_GAME
        for i in range(3):
            base_state = PublicAddCardEffect(
                Pid.P1, ElementalResonanceHighVoltage
            ).execute(base_state)

        self.assertTrue(ElementalResonanceHighVoltage.strictly_usable(base_state, Pid.P1))
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=ElementalResonanceHighVoltage,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 1}))
        ))
        p1c1, p1c2, p1c3 = tuple(char for char in game_state.get_player1().get_characters())
        self.assertEqual(p1c1.get_energy(), p1c1.get_max_energy() - 1)
        self.assertEqual(p1c2.get_energy(), p1c2.get_max_energy())
        self.assertEqual(p1c3.get_energy(), p1c3.get_max_energy() - 1)

        self.assertTrue(ElementalResonanceHighVoltage.strictly_usable(game_state, Pid.P1))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceHighVoltage,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 1}))
        ))
        p1c1, p1c2, p1c3 = tuple(char for char in game_state.get_player1().get_characters())
        self.assertEqual(p1c1.get_energy(), p1c1.get_max_energy() - 1)
        self.assertEqual(p1c2.get_energy(), p1c2.get_max_energy())
        self.assertEqual(p1c3.get_energy(), p1c3.get_max_energy())

        self.assertTrue(ElementalResonanceHighVoltage.strictly_usable(game_state, Pid.P1))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceHighVoltage,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 1}))
        ))
        p1c1, p1c2, p1c3 = tuple(char for char in game_state.get_player1().get_characters())
        self.assertEqual(p1c1.get_energy(), p1c1.get_max_energy())
        self.assertEqual(p1c2.get_energy(), p1c2.get_max_energy())
        self.assertEqual(p1c3.get_energy(), p1c3.get_max_energy())

        self.assertFalse(ElementalResonanceHighVoltage.strictly_usable(game_state, Pid.P1))

        game_state = game_state.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    1,
                    lambda c: c.factory().hp(0).alive(False).build()
                ).build()
            ).build()
        ).build()

        self.assertFalse(ElementalResonanceHighVoltage.strictly_usable(game_state, Pid.P1))
