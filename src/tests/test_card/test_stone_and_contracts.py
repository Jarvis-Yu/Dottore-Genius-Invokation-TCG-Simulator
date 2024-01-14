import unittest

from .common_imports import *

class TestStoneAndContracts(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            StoneAndContracts: 1,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({}))

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=StoneAndContracts,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))

        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_phase(game_state.mode.end_phase)
        gsm.step_until_phase(game_state.mode.action_phase)
        game_state = gsm.get_game_state()
        game_state = replace_dice(game_state, Pid.P1, ActualDice.from_empty())

        # check that Stone and Contracts creates 3 OMNI and draws one card
        self.assertIn(StoneAndContractsStatus, game_state.player1.combat_statuses)
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({Paimon: 2}))
        game_state = auto_step(game_state)
        self.assertNotIn(StoneAndContractsStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 3}))
        self.assertEqual(game_state.player1.hand_cards, Cards({Paimon: 1}))

    def test_deck_validity(self):
        self.assertTrue(StoneAndContracts.valid_in_deck(MutableDeck(
            chars=[Keqing, Ningguang, Eula],
            cards={},
        )))
        self.assertFalse(StoneAndContracts.valid_in_deck(MutableDeck(
            chars=[Xingqiu, Nahida, Eula],
            cards={},
        )))
