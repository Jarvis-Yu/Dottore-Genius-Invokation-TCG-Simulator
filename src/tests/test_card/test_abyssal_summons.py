import unittest

from .common_imports import *

class TestAbyssalSummons(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            AbyssalSummons: 2,
        }))

        game_state = base_state

        # test the use of the card summons a random hilichurl summon
        summon_pool = AbyssalSummons.SUMMONS
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AbyssalSummons,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 2})),
        ))
        summon = game_state.player1.summons.get_summons()[0]
        self.assertIn(type(summon), summon_pool)

        # test no repeating summons are summoned on successive use
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AbyssalSummons,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 2})),
        ))
        summon1, summon2 = game_state.player1.summons.get_summons()
        self.assertIsNot(type(summon1), type(summon2))

        # test card usable even if no room for more summons
        game_state = AddSummonEffect(Pid.P1, OzSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P1, UshiSummon).execute(game_state)
        self.assertTrue(AbyssalSummons.loosely_usable(game_state, Pid.P1))

    def test_deck_validity(self):
        self.assertTrue(AbyssalSummons.valid_in_deck(MutableDeck(
            chars=[RhodeiaOfLoch, JadeplumeTerrorshroom, Eula],
            cards={},
        )))
        self.assertFalse(StoneAndContracts.valid_in_deck(MutableDeck(
            chars=[RhodeiaOfLoch, Nahida, Eula],
            cards={},
        )))
