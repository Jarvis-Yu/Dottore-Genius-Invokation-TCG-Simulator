import unittest

from dgisim.src.agents import *
from dgisim.src.card.cards import Cards
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.phase.default.action_phase import ActionPhase
from dgisim.src.phase.default.card_select_phase import CardSelectPhase
from dgisim.src.phase.default.end_phase import EndPhase
from dgisim.src.phase.default.game_end_phase import GameEndPhase
from dgisim.src.phase.default.roll_phase import RollPhase
from dgisim.src.phase.default.starting_hand_select_phase import StartingHandSelectPhase
from dgisim.src.state.enums import Act, Pid
from dgisim.src.state.game_state import GameState


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
        self.assertIs(state.get_player1().get_phase(), Act.END_PHASE)
        self.assertIs(state.get_player2().get_phase(), Act.END_PHASE)

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
        self.assertEqual(p1_deck, state.get_player1().get_deck_cards() +
                         state.get_player1().get_hand_cards())
        self.assertEqual(p2_deck, state.get_player2().get_deck_cards() +
                         state.get_player2().get_hand_cards())

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
        state_machine.auto_step()
        state_machine.one_step()  # other player choose starting character
        state_machine.auto_step()
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
        state_machine.step_until_phase(EndPhase)
        state = state_machine.get_game_state()
        self.assertIs(state.get_player1().get_phase(), Act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), Act.PASSIVE_WAIT_PHASE)

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
        self.assertEqual(p1.get_hand_cards().num_cards() +
                         p1.get_deck_cards().num_cards(), p1_deck.num_cards())
        self.assertEqual(p2.get_hand_cards().num_cards() +
                         p2.get_deck_cards().num_cards(), p2_deck.num_cards())
        self.assertIs(state.get_player1().get_phase(), Act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), Act.PASSIVE_WAIT_PHASE)
        state_machine.step_until_phase(EndPhase)
        state_machine.step_until_phase(RollPhase)
        state = state_machine.get_game_state()
        p1 = state.get_player1()
        p2 = state.get_player2()
        self.assertEqual(p1.get_hand_cards().num_cards(), 9)
        self.assertEqual(p2.get_hand_cards().num_cards(), 9)
        self.assertEqual(p1.get_hand_cards().num_cards() +
                         p1.get_deck_cards().num_cards(), p1_deck.num_cards())
        self.assertEqual(p2.get_hand_cards().num_cards() +
                         p2.get_deck_cards().num_cards(), p2_deck.num_cards())
        self.assertIs(state.get_player1().get_phase(), Act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), Act.PASSIVE_WAIT_PHASE)

    def test_game_end_phase_basic_behavior(self):
        state_machine = GameStateMachine(
            self._initial_state,
            LazyAgent(),
            LazyAgent(),
        )
        state_machine.step_until_phase(GameEndPhase)
        self.assertTrue(state_machine.game_end())
        self.assertIsNone(state_machine.get_winner())

    def test_random_agents_not_break_game(self):
        from dgisim.src.mode import AllOmniMode
        mode = AllOmniMode()
        base_game = self._initial_state.factory().mode(
            mode
        ).phase(
            mode.card_select_phase()
        ).build()

        import os, sys, time
        optional_repeats = os.getenv("RNG_PLAYS")
        optional_show_progress = os.getenv("SHOW_PROGRESS")
        repeats: int
        show_progress: bool
        try:
            repeats = int(optional_repeats) if optional_repeats is not None else 5
            show_progress = (
                int(optional_show_progress) != 0
                if optional_show_progress is not None
                else False
            )
        except:
            repeats = 5
            show_progress = False
        from collections import defaultdict
        wins: dict[None | Pid, int] = defaultdict(int)
        prev_progress = ""
        times: list[float] = []
        num_transitions = 0
        for i in range(repeats):
            if show_progress:
                print(end='\b' * len(prev_progress))
                prev_progress = f"[{i}/{repeats}]"
                print(end=prev_progress)
                sys.stdout.flush()
            start = time.time()
            if i % 3 == 0:
                state_machine = GameStateMachine(
                    self._initial_state,
                    RandomAgent(),
                    RandomAgent(),
                )
            else:
                state_machine = GameStateMachine(
                    base_game,
                    RandomAgent(),
                    RandomAgent(),
                )
            game_end_phase = state_machine.get_game_state().get_mode().game_end_phase()
            try:
                state_machine.step_until_phase(game_end_phase)
                end = time.time()
                times.append(end - start)
                num_transitions += len(state_machine.get_history())
                wins[state_machine.get_winner()] += 1
            except Exception:
                all_state = state_machine.get_history()
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("AN EXCEPTION IS THROWN WHEN EXECUTING THE GAME")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                for i, game_state in enumerate(all_state[-5:]):
                    print(f"<<<{i+1}>>>")
                    print(game_state)
                raise Exception("Test failed because random agent triggers an excpetion")
        if show_progress:
            print(end='\b' * len(prev_progress))
            sys.stdout.flush()
        average_time_in_ms = sum(times) / len(times) * 1000
        average_state_time_in_μs = average_time_in_ms / (num_transitions / len(times)) * 1000
        print(end=f"[[A random game takes {round(average_time_in_ms, 1)} ms on average, "
              + f"{round(average_state_time_in_μs)} μs per state]]")
