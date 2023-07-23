from typing import Callable, Optional

from .action.action import PlayerAction
from .helper.level_print import GamePrinter
from .phase.phase import Phase
from .player_agent import PlayerAgent
from .state.enums import Pid
from .state.game_state import GameState

__all__ = [
    "GameStateMachine",
]


class GameStateMachine:
    def __init__(self, game_state: GameState, agent1: PlayerAgent, agent2: PlayerAgent):
        self._history = [game_state]
        self._perspective_history: dict[Pid, list[GameState]] = {
            Pid.P1: [game_state.prespective_view(Pid.P1)],
            Pid.P2: [game_state.prespective_view(Pid.P2)],
        }
        self._action_history: list[int] = []
        self._actions: dict[int, PlayerAction] = {}
        self._game_state = game_state
        self._player_agent1 = agent1
        self._player_agent2 = agent2

    @classmethod
    def from_default(cls, agent1: PlayerAgent, agent2: PlayerAgent):
        return cls(GameState.from_default(), agent1, agent2)

    def get_history(self) -> tuple[GameState, ...]:
        return tuple(self._history)

    def get_action_history(self) -> tuple[GameState, ...]:
        return tuple([self._history[i] for i in self._action_history])

    def get_last_action(self) -> Optional[PlayerAction]:
        if self._action_history:
            return self._actions[self._action_history[-1]]
        return None

    def get_last_action_idx(self) -> Optional[int]:
        if self._action_history:
            return self._action_history[-1]
        return None

    def get_game_state(self) -> GameState:
        return self._game_state

    def curr_index(self) -> int:
        return len(self._history) - 1

    def is_latest_index(self, index: int) -> bool:
        return index == self.latest_index()

    def latest_index(self) -> int:
        return len(self._history) - 1

    def prev_action_index(self, index: int) -> int:
        if not self._action_history:
            return 0
        if index <= self._action_history[0]:
            return self._action_history[0]
        for i in reversed(self._action_history):
            if i < index:
                return i
        raise Exception("Not Reached")

    def next_action_index(self, index: int) -> int:
        if not self._action_history:
            return 0
        if index >= self._action_history[-1]:
            return self._action_history[-1]
        for i in reversed(self._action_history):
            if i > index:
                return i
        raise Exception("Not Reached")

    def action_at(self, index: int) -> Optional[PlayerAction]:
        return self._actions.get(index, None)

    def prev_index(self, index: int) -> int:
        return max(0, index - 1)

    def next_index(self, index: int) -> int:
        return min(self.latest_index(), index + 1)

    def get_game_state_at(self, index: int) -> GameState:
        return self._history[index]

    def _append_history(self, game_state: GameState) -> None:
        self._history.append(self._game_state)
        self._perspective_history[Pid.P1].append(self._game_state.prespective_view(Pid.P1))
        self._perspective_history[Pid.P2].append(self._game_state.prespective_view(Pid.P2))

    def _step(self, observe=False) -> None:
        self._game_state = self._game_state.step()
        if observe:
            print(GamePrinter.dict_game_printer(self._game_state.dict_str()))
            input(":> ")
        self._append_history(self._game_state)

    def _action_step(self, pid: Pid, action: PlayerAction, observe=False) -> bool:
        next_state = self._game_state.action_step(pid, action)
        if next_state is None:
            return False
        action_idx = len(self._history) - 1
        self._action_history.append(action_idx)
        self._actions[action_idx] = action
        self._game_state = next_state
        if observe:
            print(GamePrinter.dict_game_printer(self._game_state.dict_str()))
            input(":> ")
        self._append_history(self._game_state)
        return True

    def step_until_phase(self, phase: type[Phase] | Phase, observe=False) -> None:
        if isinstance(phase, Phase):
            phase = type(phase)
        while isinstance(self._game_state.get_phase(), phase):
            self.one_step(observe=observe)
        while not isinstance(self._game_state.get_phase(), phase):
            self.one_step(observe=observe)

    def step_until_next_phase(self, observe=False) -> None:
        phase = self._game_state.get_phase()
        while self._game_state.get_phase() == phase:
            self.one_step(observe=observe)

    def step_until_holds(self, predicate: Callable[[GameState], bool], observe=False) -> None:
        while not predicate(self._game_state):
            self.one_step(observe=observe)

    def one_step(self, observe=False) -> None:
        """
        transition the game to its next state, if the transition requires a player action,
        ask for it and then make the step
        """
        if self.game_end():
            return
        pid = self._game_state.waiting_for()
        if pid is None:
            self._step(observe=observe)
        else:
            patience = 5
            while patience > 0 \
                    and not self._action_step(
                        pid,
                        self.player_agent(pid).choose_action(self._perspective_history[pid], pid),
                        observe=observe,
                    ):
                patience -= 1

    def changing_step(self, observe=False) -> None:
        game_state = self._game_state
        self.one_step(observe=observe)
        while not self.game_end() and game_state is self._game_state:
            self.one_step(observe=observe)

    def auto_step(self, observe=False) -> None:
        """
        fast-forward to the game state where a player action is required
        """
        pid = self._game_state.waiting_for()
        while not self.game_end() and pid is None:
            self._step(observe=observe)
            pid = self._game_state.waiting_for()

    def player_step(self, observe=False) -> None:
        """
        fast-forward to the game state where a player action is required,
        and then make one step taking the player's action
        """
        self.auto_step(observe=observe)
        self.one_step(observe=observe)

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

    def player_agent(self, id: Pid) -> PlayerAgent:
        if id is Pid.P1:
            return self._player_agent1
        elif id is Pid.P2:
            return self._player_agent2
        else:
            raise Exception("GameStateMachine.player(): Invalid player id")

    def game_end(self) -> bool:
        return self._game_state.game_end()

    def get_winner(self) -> None | Pid:
        return self._game_state.get_winner()
