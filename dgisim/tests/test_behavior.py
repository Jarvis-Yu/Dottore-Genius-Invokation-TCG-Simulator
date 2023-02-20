import unittest
from typing import Tuple, Callable

from dgisim.src.state.game_state import GameState
from dgisim.src.state.player_state import PlayerState
from dgisim.src.player_agent import PlayerAgent
from dgisim.src.phase.starting_hand_select_phase import StartingHandSelectPhase
from dgisim.src.card.cards import Cards

from dgisim.tests.agents import NoneAgent, BasicAgent


def keep_running_until(
        state: GameState,
        round: int,
        max_rounds: int,
        agents: Tuple[PlayerAgent, PlayerAgent],
        do_print: bool = False,
        stop_condition: Callable[[GameState], bool] = lambda _: False
) -> GameState:
    if do_print:
        print(f"########## State {round} ##########")
    if do_print:
        print(state)
    if round >= max_rounds or stop_condition(state):
        return state
    pid = state.waiting_for()
    if do_print:
        print(f"#### Waiting for {pid}")
    if pid is not None:
        if do_print:
            print("#### Some Action Submitted")
        if pid is GameState.pid.P1:
            new_state = state.action_step(pid, agents[0].choose_action(state, pid))
        elif pid is GameState.pid.P2:
            new_state = state.action_step(pid, agents[1].choose_action(state, pid))
        else:
            raise Exception("Unknown pid")
    else:
        new_state = state.step()
    return keep_running_until(
        new_state,
        round + 1,
        max_rounds,
        agents,
        do_print=do_print,
        stop_condition=stop_condition,
    )


class TestBehavior(unittest.TestCase):
    _intitialState = GameState.from_default()

    def test_card_select_phase_phase(self):
        state = keep_running_until(
            self._intitialState,
            0,
            4,
            (BasicAgent(), BasicAgent()),
            do_print=False,
            stop_condition=lambda st: isinstance(st.get_phase(), StartingHandSelectPhase)
        )
        self.assertTrue(isinstance(state.get_phase(), StartingHandSelectPhase))
        self.assertIs(state.get_player1().get_phase(), PlayerState.act.PASSIVE_WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.act.PASSIVE_WAIT_PHASE)

    def test_card_select_phase_cards(self):
        p1_deck: Cards = self._intitialState.get_player1().get_deck_cards()
        p2_deck: Cards = self._intitialState.get_player2().get_deck_cards()
        state = keep_running_until(
            self._intitialState,
            0,
            4,
            (BasicAgent(), BasicAgent()),
            do_print=False,
            stop_condition=lambda st: isinstance(st.get_phase(), StartingHandSelectPhase)
        )
        self.assertEqual(p1_deck, state.get_player1().get_deck_cards() + state.get_player1().get_hand_cards())
        self.assertEqual(p2_deck, state.get_player2().get_deck_cards() + state.get_player2().get_hand_cards())


if __name__ == "__main__":
    unittest.main()
