import unittest

from .common_imports import *

class TestThunderAndEternity(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            ThunderAndEternity: 2,
        }))
        base_state = replace_dice(base_state, Pid.P1, ActualDice({
            Element.PYRO: 2,
            Element.HYDRO: 2,
            Element.ANEMO: 2,
            Element.ELECTRO: 2,
            Element.DENDRO: 2,
            Element.CRYO: 2,
            Element.GEO: 2,
            Element.OMNI: 2,
        }))

        # test Thunder and Eternity make all dice OMNI
        game_state = base_state
        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ThunderAndEternity,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        dice_after = game_state.player1.dice
        self.assertEqual(dice_after[Element.OMNI], dice_after.num_dice())
        self.assertEqual(dice_after.num_dice(), dice_before.num_dice())

    def test_deck_validity(self):
        self.assertTrue(ThunderAndEternity.valid_in_deck(MutableDeck(
            chars=[KamisatoAyaka, KaedeharaKazuha, Eula],
            cards={},
        )))
        self.assertFalse(ThunderAndEternity.valid_in_deck(MutableDeck(
            chars=[KamisatoAyaka, Nahida, Eula],
            cards={},
        )))
