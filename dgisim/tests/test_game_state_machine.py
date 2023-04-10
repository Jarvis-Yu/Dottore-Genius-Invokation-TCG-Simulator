import unittest

from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.state.game_state import GameState
from dgisim.tests.agents import LazyAgent
from dgisim.src.phase.card_select_phase import CardSelectPhase
from dgisim.src.phase.phase import Phase
from dgisim.src.phase.starting_hand_select_phase import StartingHandSelectPhase
from dgisim.src.phase.roll_phase import RollPhase
from dgisim.src.phase.action_phase import ActionPhase
from dgisim.src.phase.end_phase import EndPhase
from dgisim.src.phase.game_end_phase import GameEndPhase
from dgisim.src.state.player_state import PlayerState
from dgisim.src.card.cards import Cards


class TestGameStateMachine(unittest.TestCase):
    _initial_state = GameState.from_default()

    def test_card_select_phase_runs(self):
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.auto_step()  # skip initialization
        state_machine.one_step()  # one player swap cards
        state_machine.one_step()  # other player swap cards
        state = state_machine.get_game_state()
        self.assertTrue(isinstance(state.get_phase(), CardSelectPhase))
        self.assertIs(state.get_player1().get_phase(), PlayerState.Act.END_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.Act.END_PHASE)

    def test_card_select_phase_behavior(self):
        p1_deck: Cards = self._initial_state.get_player1().get_deck_cards()
        p2_deck: Cards = self._initial_state.get_player2().get_deck_cards()
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
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
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.step_until_phase(StartingHandSelectPhase)
        state = state_machine.get_game_state()
        self.assertTrue(isinstance(state.get_phase(), StartingHandSelectPhase))

    def test_starting_hand_select_phase_behavior(self):
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
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
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.step_until_phase(RollPhase)
        state_machine.step_until_phase(ActionPhase)
        state = state_machine.get_game_state()
        self.assertEqual(state.get_player1().get_dices().num_dices(), 8)
        self.assertEqual(state.get_player2().get_dices().num_dices(), 8)

    def test_action_phase_basic_behavior(self):
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.step_until_phase(ActionPhase)
        # cmd = ""
        # while cmd == "":
        #     print("===========================================")
        #     print(state_machine.get_game_state())
        #     state_machine.one_step()
        #     cd = input()
        state_machine.step_until_phase(EndPhase)
        state = state_machine.get_game_state()
        self.assertIs(state.get_player1().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)

    def test_end_phase_basic_behavior(self):
        p1_deck: Cards = self._initial_state.get_player1().get_deck_cards()
        p2_deck: Cards = self._initial_state.get_player2().get_deck_cards()
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.step_until_phase(EndPhase)
        state_machine.step_until_phase(RollPhase)
        state = state_machine.get_game_state()
        p1 = state.get_player1()
        p2 = state.get_player2()
        self.assertEqual(p1.get_hand_cards().num_cards(), 7)
        self.assertEqual(p2.get_hand_cards().num_cards(), 7)
        self.assertEqual(p1.get_hand_cards().num_cards() + p1.get_deck_cards().num_cards(), p1_deck.num_cards())
        self.assertEqual(p2.get_hand_cards().num_cards() + p2.get_deck_cards().num_cards(), p2_deck.num_cards())
        self.assertIs(state.get_player1().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)
        state_machine.step_until_phase(EndPhase)
        state_machine.step_until_phase(RollPhase)
        state = state_machine.get_game_state()
        p1 = state.get_player1()
        p2 = state.get_player2()
        self.assertEqual(p1.get_hand_cards().num_cards(), 9)
        self.assertEqual(p2.get_hand_cards().num_cards(), 9)
        self.assertEqual(p1.get_hand_cards().num_cards() + p1.get_deck_cards().num_cards(), p1_deck.num_cards())
        self.assertEqual(p2.get_hand_cards().num_cards() + p2.get_deck_cards().num_cards(), p2_deck.num_cards())
        self.assertIs(state.get_player1().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.Act.PASSIVE_WAIT_PHASE)

    def test_game_end_phase_basic_behavior(self):
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.step_until_phase(GameEndPhase)
        self.assertTrue(state_machine.game_end())
        self.assertIsNone(state_machine.get_winner())
        print(state_machine.get_game_state())

    def test_inspect(self):
        """
        Only turned on manually to inspect cases
        """
        from dgisim.tests.agents import HardCodedRandomAgent
        state_machine = GameStateMachine(
            self._initial_state,
            HardCodedRandomAgent(),
            HardCodedRandomAgent(),
        )
        i = 0
        while not state_machine.game_end():
            print(f"########## {i} ##########")
            i += 1
            state_machine.auto_step()
            print(state_machine.get_game_state())
            state_machine.one_step()
            input()

if __name__ == "__main__":
    unittest.main()
