import unittest

from src.tests.test_card.common_imports import *


class TestVanaranan(unittest.TestCase):
    def test_vanarana(self):
        dice_list = [
            ActualDice({}),
            ActualDice({Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDice({Element.OMNI: 1, Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDice({Element.OMNI: 1, Element.GEO: 3, Element.ELECTRO: 1, Element.CRYO: 2}),
        ]
        for dice in dice_list:
            with self.subTest(dice=dice):
                base_game = ACTION_TEMPLATE.factory().f_player1(
                    lambda p: p.factory().hand_cards(
                        Cards({
                            Vanarana: 2,
                        })
                    ).dice(
                        dice
                    ).build()
                ).build()
                a1, a2 = PuppetAgent(), LazyAgent()
                gsm = GameStateMachine(base_game, a1, a2)
                a1.inject_actions([
                    CardAction(
                        card=Vanarana,
                        instruction=DiceOnlyInstruction(dice=ActualDice({})),
                    ),
                    CardAction(
                        card=Vanarana,
                        instruction=DiceOnlyInstruction(dice=ActualDice({})),
                    ),
                    EndRoundAction(),
                    DiceSelectAction(selected_dice=ActualDice({})),  # roll phase
                ])
                gsm.step_until_next_phase()
                gsm.step_until_phase(base_game.get_mode().action_phase(), observe=False)
                p1_dice_before = gsm.get_game_state().get_player1().get_dice()
                gsm.auto_step()
                p1_dice_after = gsm.get_game_state().get_player1().get_dice()
                if dice.num_dice() <= 4:
                    self.assertEqual(
                        p1_dice_before.num_dice() + dice.num_dice(),
                        p1_dice_after.num_dice()
                    )
                    for elem in dice:
                        self.assertEqual(p1_dice_before[elem] + dice[elem], p1_dice_after[elem])
                else:
                    self.assertEqual(p1_dice_before.num_dice() + 4, p1_dice_after.num_dice())
                    for elem in dice:
                        if elem is Element.GEO:  # hard coded for last case only
                            continue
                        self.assertEqual(p1_dice_before[elem] + dice[elem], p1_dice_after[elem])
