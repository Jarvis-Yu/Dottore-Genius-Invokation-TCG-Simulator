import unittest

from .common_imports import *


class TestCalxsArts(unittest.TestCase):
    def test_calxs_arts(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_characters(
                    lambda chrs: tuple(
                        chr.factory().energy(1).build()
                        for chr in chrs
                    )
                ).build()
            ).hand_cards(
                Cards({CalxsArts: 10})
            ).build()
        ).build()
        assert base_game.get_player1().just_get_active_character().get_id() == 1

        # every character has energy
        game_state = just(base_game.action_step(
            Pid.P1,
            CardAction(
                card=CalxsArts,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
            )
        ))
        game_state = auto_step(game_state)
        p1cs = game_state.get_player1().get_characters()
        self.assertEqual(p1cs.just_get_character(1).get_energy(), 3)
        self.assertEqual(p1cs.just_get_character(2).get_energy(), 0)
        self.assertEqual(p1cs.just_get_character(3).get_energy(), 0)

        # only one teammate has energy
        game_state = base_game.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().energy(0).build()
                ).build()
            ).build()
        ).build()
        game_state = just(game_state.action_step(
            Pid.P1,
            CardAction(
                card=CalxsArts,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
            )
        ))
        game_state = auto_step(game_state)
        p1cs = game_state.get_player1().get_characters()
        self.assertEqual(p1cs.just_get_character(1).get_energy(), 2)
        self.assertEqual(p1cs.just_get_character(2).get_energy(), 0)
        self.assertEqual(p1cs.just_get_character(3).get_energy(), 0)

        # no teammate has energy
        game_state = base_game.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().energy(0).build()
                ).f_character(
                    3,
                    lambda c: c.factory().energy(0).build()
                ).build()
            ).build()
        ).build()
        self.assertRaises(Exception, lambda: game_state.action_step(
            Pid.P1,
            CardAction(
                card=CalxsArts,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
            )
        ))

        # active character full energy
        game_state = base_game.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    1,
                    lambda c: c.factory().energy(c.get_max_energy()).build()
                ).build()
            ).build()
        ).build()
        self.assertRaises(Exception, lambda: game_state.action_step(
            Pid.P1,
            CardAction(
                card=CalxsArts,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
            )
        ))
