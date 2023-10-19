import unittest

from .common_imports import *


class TestPaimon(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, Paimon).execute(base_state)

        def skip_round(game_state: GameState) -> GameState:
            gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
            gsm.step_until_phase(game_state.get_mode().end_phase)
            gsm.step_until_phase(game_state.get_mode().action_phase)
            return gsm.get_game_state()

        old_dice = base_state.get_player1().get_dice()
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 3})),
        ))
        new_dice = game_state.get_player1().get_dice()
        self.assertEqual(new_dice, old_dice - {Element.HYDRO: 3})

        # first trigger time
        game_state = skip_round(game_state)
        old_dice = game_state.get_player1().get_dice()
        game_state = auto_step(game_state)
        new_dice = game_state.get_player1().get_dice()
        self.assertEqual(new_dice, old_dice + {Element.OMNI: 2})
        self.assertIn(PaimonSupport, game_state.get_player1().get_supports())

        # second trigger time
        game_state = skip_round(game_state)
        old_dice = game_state.get_player1().get_dice()
        game_state = auto_step(game_state)
        new_dice = game_state.get_player1().get_dice()
        self.assertEqual(new_dice, old_dice + {Element.OMNI: 2})
        self.assertNotIn(PaimonSupport, game_state.get_player1().get_supports())