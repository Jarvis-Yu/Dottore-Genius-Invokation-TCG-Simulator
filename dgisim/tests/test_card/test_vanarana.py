import unittest

from dgisim.tests.test_card.common_imports import *


class TestVanaranan(unittest.TestCase):
    def test_vanarana(self):
        dices_list = [
            ActualDices({}),
            ActualDices({Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDices({Element.OMNI: 1, Element.ELECTRO: 1, Element.CRYO: 1}),
            ActualDices({Element.OMNI: 1, Element.GEO: 3, Element.ELECTRO: 1, Element.CRYO: 2}),
        ]
        for dices in dices_list:
            with self.subTest(dices=dices):
                base_game = ACTION_TEMPLATE.factory().f_player1(
                    lambda p: p.factory().hand_cards(
                        Cards({
                            Vanarana: 2,
                        })
                    ).dices(
                        dices
                    ).build()
                ).build()
                a1, a2 = PuppetAgent(), LazyAgent()
                gsm = GameStateMachine(base_game, a1, a2)
                a1.inject_actions([
                    CardAction(
                        card=Vanarana,
                        instruction=DiceOnlyInstruction(dices=ActualDices({})),
                    ),
                    CardAction(
                        card=Vanarana,
                        instruction=DiceOnlyInstruction(dices=ActualDices({})),
                    ),
                    EndRoundAction(),
                    EndRoundAction(),  # roll phase
                ])
                gsm.step_until_next_phase()
                gsm.step_until_phase(base_game.get_mode().action_phase(), observe=False)
                p1_dices_before = gsm.get_game_state().get_player1().get_dices()
                gsm.auto_step()
                p1_dices_after = gsm.get_game_state().get_player1().get_dices()
                if dices.num_dices() <= 4:
                    self.assertEqual(
                        p1_dices_before.num_dices() + dices.num_dices(),
                        p1_dices_after.num_dices()
                    )
                    for elem in dices:
                        self.assertEqual(p1_dices_before[elem] + dices[elem], p1_dices_after[elem])
                else:
                    self.assertEqual(p1_dices_before.num_dices() + 4, p1_dices_after.num_dices())
                    for elem in dices:
                        if elem is Element.GEO:  # hard coded for last case only
                            continue
                        self.assertEqual(p1_dices_before[elem] + dices[elem], p1_dices_after[elem])
