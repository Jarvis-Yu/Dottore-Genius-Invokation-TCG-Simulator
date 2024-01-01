import unittest

from .common_imports import *

class TestJoyousCelebration(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, JoyousCelebration).execute(base_state)

        # cannot be used if active character is GEO
        game_state = replace_character(base_state, Pid.P1, Ningguang, 1)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P1)
        self.assertFalse(JoyousCelebration.loosely_usable(game_state, Pid.P1))

        # cannot be used if active character is ANEMO
        game_state = replace_character(base_state, Pid.P1, Venti, 1)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P1)
        self.assertFalse(JoyousCelebration.loosely_usable(game_state, Pid.P1))

        # can be used if active character is of the other elements
        # and only apply element to characters with aura already
        chars: tuple[type[Character], ...] = (Yoimiya, RhodeiaOfLoch, Keqing, Nahida, Kaeya)
        for char in chars:
            with self.subTest(char=char):
                game_state = replace_character(base_state, Pid.P1, char, 1)
                game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P1, 1)
                game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P1, 3)
                self.assertTrue(JoyousCelebration.loosely_usable(game_state, Pid.P1))

                game_state = step_action(game_state, Pid.P1, CardAction(
                    card=JoyousCelebration,
                    instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
                ))
                c1, c2, c3 = game_state.player1.characters.get_characters()
                self.assertFalse(c2.elemental_aura.has_aura())
                self.assertIs(
                    c1.elemental_aura.has_aura(),
                    c1.ELEMENT() is Element.PYRO,
                )
                self.assertIs(
                    c3.elemental_aura.has_aura(),
                    c1.ELEMENT() is Element.PYRO,
                )
