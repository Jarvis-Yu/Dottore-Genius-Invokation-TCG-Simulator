import unittest

from .common_imports import *


class TestElementalResonanceDieCard(unittest.TestCase):
    """
    As all elemental resonance die cards are literally the same except for its element.
    We only test the pyro one.
    """
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceWovenFlames,
    ).execute(ACTION_TEMPLATE)

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceWovenFlames.valid_in_deck(
                MutableDeck(chars=[AratakiItto, Nahida, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceWovenFlames.valid_in_deck(
                MutableDeck(chars=[Bennett, Nahida, Klee], cards={})
            )
        )

    def test_card_adds_status(self):
        game_state = self.BASE_GAME
        old_pyro_dices = game_state.get_player1().get_dices()[Element.PYRO]
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceWovenFlames,
            instruction=DiceOnlyInstruction(dices=ActualDices({}))
        ))
        new_pyro_dices = game_state.get_player1().get_dices()[Element.PYRO]
        self.assertEqual(new_pyro_dices, old_pyro_dices + 1)
