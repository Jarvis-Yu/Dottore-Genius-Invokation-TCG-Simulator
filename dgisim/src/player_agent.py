from typing import List

from dgisim.src.state.game_state import GameState
from dgisim.src.action.action import PlayerAction



class PlayerAgent:
    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        return PlayerAction()


class PlayerProxyAgent(PlayerAgent):
    pass

class ProxyAgent(PlayerProxyAgent):
    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        return super().choose_action(history, pid)
