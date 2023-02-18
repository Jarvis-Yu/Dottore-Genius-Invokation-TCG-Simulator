import unittest
from typing import Tuple, Callable

from dgisim.src.state.game import GameState
from dgisim.src.state.player import PlayerState
from dgisim.src.player_agent import PlayerAgent
from dgisim.src.phase.starting_hand_select import StartingHandSelectPhase

from dgisim.tests.agents import NoneAgent


def keep_running_until(
        state: GameState,
        round: int,
        max_rounds: int,
        agents: Tuple[PlayerAgent, PlayerAgent],
        do_print: bool = False,
        stop_condition: Callable[[GameState], bool] = lambda _: False
) -> GameState:
    if round >= max_rounds or stop_condition(state):
        return state
    if do_print:
        print(f"#### State {round}")
    if do_print:
        print(state)
    pid = state.waiting_for()
    if do_print:
        print(f"#### Waiting for {pid}")
    if pid is not None:
        if do_print:
            print("#### Some Action")
        new_state = state.run_action(pid, None)
    else:
        new_state = state.run()
    return keep_running_until(
        new_state,
        round + 1,
        max_rounds,
        agents,
        do_print=do_print,
        stop_condition=stop_condition,
    )


class TestGameStateMachine(unittest.TestCase):
    _intitialState = GameState.from_default()

    def test_first_step(self):
        state = keep_running_until(
            self._intitialState,
            0,
            4,
            (NoneAgent(), NoneAgent()),
            do_print=False,
            stop_condition=lambda st: isinstance(st.get_phase(), StartingHandSelectPhase)
        )
        self.assertTrue(isinstance(state.get_phase(), StartingHandSelectPhase))
        self.assertIs(state.get_player1().get_phase(), PlayerState.act.WAIT_PHASE)
        self.assertIs(state.get_player2().get_phase(), PlayerState.act.WAIT_PHASE)


if __name__ == "__main__":
    unittest.main()
