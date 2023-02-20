from dgisim.src.state.game_state import GameState
from dgisim.src.player_agent import PlayerAgent


class GameStateMachine:
    def __init__(self, game_state: GameState, player1: PlayerAgent, player2: PlayerAgent):
        self._game_state = game_state
        self._playerAgent1 = player1
        self._playerAgent2 = player2

    @classmethod
    def from_default(cls, player1: PlayerAgent, player2: PlayerAgent):
        return cls(GameState.from_default(), player1, player2)

    def one_step(self):
        pid = self._game_state.waiting_for()
        if pid is None:
            self._game_state = self._game_state.step()
        else:
            self._game_state = self._game_state.action_step(
                pid, self.player(pid).choose_action(self._game_state, pid))

    def run(self):
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

    def player(self, id: GameState.pid) -> PlayerAgent:
        if id is GameState.pid.P1:
            return self._playerAgent1
        elif id is GameState.pid.P2:
            return self._playerAgent2
        else:
            raise Exception("GameStateMachine.player(): Invalid player id")

    def game_end(self) -> bool:
        return self._game_state.game_end()
