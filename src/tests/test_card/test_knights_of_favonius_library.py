import unittest

from src.tests.test_card.common_imports import *


class TestKnightsOfFavoniusLibrary(unittest.TestCase):
    def test_knights_of_favonius_library(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({
                    KnightsOfFavoniusLibrary: 2,
                })
            ).build()
        ).f_player2(
            lambda p: p.factory().hand_cards(
                Cards({
                    KnightsOfFavoniusLibrary: 2,
                })
            ).build()
        ).build()

        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            CardAction(
                card=KnightsOfFavoniusLibrary,
                instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
            ),
            DiceSelectAction(
                selected_dice=ActualDice({}),
            ),
            EndRoundAction(),
        ])
        a2.inject_actions([
            CardAction(
                card=KnightsOfFavoniusLibrary,
                instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
            ),
            DiceSelectAction(
                selected_dice=ActualDice({}),
            ),
            CardAction(
                card=KnightsOfFavoniusLibrary,
                instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
            ),
            DiceSelectAction(
                selected_dice=ActualDice({Element.GEO: 2}),
            ),
            EndRoundAction(),
        ])
        gsm.step_until_phase(base_game.mode.roll_phase())
        gsm.auto_step()
        game_state = gsm.get_game_state()
        p1, p2 = game_state.player1, game_state.player2
        self.assertEqual(p1.dice_reroll_chances, 2)
        self.assertEqual(p2.dice_reroll_chances, 3)
        self.assertIn(KnightsOfFavoniusLibrarySupport, p1.supports)
        self.assertIn(KnightsOfFavoniusLibrarySupport, p2.supports)