from typing import List

from dgisim.src.state.game_state import GameState
from dgisim.src.action import PlayerAction



class PlayerAgent:
    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        return PlayerAction()


class PlayerProxyAgent(PlayerAgent):
    pass
