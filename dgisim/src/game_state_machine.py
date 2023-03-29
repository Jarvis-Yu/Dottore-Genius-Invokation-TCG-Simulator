from typing import List, Type, Tuple, Optional, Callable

from dgisim.src.state.game_state import GameState
from dgisim.src.player_agent import PlayerAgent
from dgisim.src.action import PlayerAction
from dgisim.src.phase.phase import Phase


class GameStateMachine:
    def __init__(self, game_state: GameState, player1: PlayerAgent, player2: PlayerAgent):
        self._history = [game_state]
        self._action_history: list[GameState] = []
        self._game_state = game_state
        self._playerAgent1 = player1
        self._playerAgent2 = player2

    @classmethod
    def from_default(cls, player1: PlayerAgent, player2: PlayerAgent):
        return cls(GameState.from_default(), player1, player2)

    def get_history(self) -> Tuple[GameState, ...]:
        return tuple(self._history)

    def get_action_history(self) -> Tuple[GameState, ...]:
        return tuple(self._action_history)

    def get_game_state(self) -> GameState:
        return self._game_state

    def _step(self) -> None:
        self._game_state = self._game_state.step()
        self._history.append(self._game_state)

    def _action_step(self, pid: GameState.Pid, action: PlayerAction) -> bool:
        next_state = self._game_state.action_step(pid, action)
        if next_state is None:
            return False
        self._action_history.append(self._game_state)
        self._game_state = next_state
        self._history.append(self._game_state)
        return True

    def step_until_phase(self, phase: Type[Phase]) -> None:
        while isinstance(self._game_state.get_phase(), phase):
            self.one_step()
        while not isinstance(self._game_state.get_phase(), phase):
            self.one_step()

    def step_until_holds(self, predicate: Callable[[GameState], bool]) -> None:
        while not predicate(self._game_state):
            self.one_step()

    def one_step(self) -> None:
        if self.game_end():
            return
        pid = self._game_state.waiting_for()
        if pid is None:
            self._step()
        else:
            patience = 5
            while patience > 0 \
                    and not self._action_step(
                        pid,
                        self.player_agent(pid).choose_action(self._history, pid)
                    ):
                patience -= 1

    def changing_step(self) -> None:
        game_state = self._game_state
        self.one_step()
        while not self.game_end() and game_state is self._game_state:
            self.one_step()

    def auto_step(self) -> None:
        pid = self._game_state.waiting_for()
        while not self.game_end() and pid is None:
            self._step()
            pid = self._game_state.waiting_for()

    def player_step(self) -> None:
        self.auto_step()
        self.one_step()

    def run(self) -> None:
        while (not self.game_end()):
            self.one_step()
        winner_id = self._game_state.get_winner()
        if winner_id is None:
            print("DRAW")
            # TODO
            pass
        else:
            print(winner_id, "WINS")
            # TODO
            pass

    def player_agent(self, id: GameState.Pid) -> PlayerAgent:
        if id is GameState.Pid.P1:
            return self._playerAgent1
        elif id is GameState.Pid.P2:
            return self._playerAgent2
        else:
            raise Exception("GameStateMachine.player(): Invalid player id")

    def game_end(self) -> bool:
        return self._game_state.game_end()

    def get_winner(self) -> Optional[GameState.Pid]:
        return self._game_state.get_winner()
