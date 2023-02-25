import unittest

from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.state.game_state import GameState
from dgisim.tests.agents import BasicAgent
from dgisim.src.phase.card_select_phase import CardSelectPhase
from dgisim.src.phase.phase import Phase
from dgisim.src.phase.starting_hand_select_phase import StartingHandSelectPhase
from dgisim.src.phase.action_phase import ActionPhase
from dgisim.src.state.player_state import PlayerState
from dgisim.src.card.cards import Cards


class TestGameStateMachine(unittest.TestCase):
    _initial_state = GameState.from_default()

    def test_card_select_phase_runs(self):
        state_machine = GameStateMachine(
            self._initial_state,
            BasicAgent(),
            BasicAgent(),
        )
        state_machine.auto_step()  # skip initialization
        state_machine.one_step()  # one player swap cards
        state_machine.one_step()  # other player swap cards
        state = state_machine.get_game_state()
        self.assertTrue(isinstance(state.get_phase(), CardSelectPhase))
        self.assertIs(state.get_player1().get_phase(), PlayerState.act.END_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.act.END_PHASE)

    def test_card_select_phase_behavior(self):
        p1_deck: Cards = self._initial_state.get_player1().get_deck_cards()
        p2_deck: Cards = self._initial_state.get_player2().get_deck_cards()
        state_machine = GameStateMachine(
            self._initial_state,
            BasicAgent(),
            BasicAgent(),
        )
        state_machine.auto_step()  # skip initialization
        state_machine.one_step()  # one player swap cards
        state_machine.one_step()  # other player swap cards
        state = state_machine.get_game_state()
        self.assertEqual(p1_deck, state.get_player1().get_deck_cards() + state.get_player1().get_hand_cards())
        self.assertEqual(p2_deck, state.get_player2().get_deck_cards() + state.get_player2().get_hand_cards())

    def test_entering_starting_hand_select_phase(self):
        state_machine = GameStateMachine(
            self._initial_state,
            BasicAgent(),
            BasicAgent(),
        )
        state_machine.step_until_phase(StartingHandSelectPhase)
        state = state_machine.get_game_state()
        self.assertTrue(isinstance(state.get_phase(), StartingHandSelectPhase))

    def test_starting_hand_select_phase_behavior(self):
        state_machine = GameStateMachine(
            self._initial_state,
            BasicAgent(),
            BasicAgent(),
        )
        state_machine.step_until_phase(StartingHandSelectPhase)
        state_machine.auto_step()
        state_machine.one_step()  # one player choose starting character
        state_machine.one_step()  # other player choose starting character
        state = state_machine.get_game_state()
        self.assertIsNotNone(state.get_player1().get_characters().get_active_character_id())
        self.assertIsNotNone(state.get_player2().get_characters().get_active_character_id())

    def test_roll_phase_behavior(self):
        """ Temporary for the fake roll phase """
        state_machine = GameStateMachine(
            self._initial_state,
            BasicAgent(),
            BasicAgent(),
        )
        state_machine.step_until_phase(ActionPhase)
        state = state_machine.get_game_state()
        self.assertEqual(state.get_player1().get_dices().num_dices(), 8)
        self.assertEqual(state.get_player2().get_dices().num_dices(), 8)

if __name__ == "__main__":
    unittest.main()
