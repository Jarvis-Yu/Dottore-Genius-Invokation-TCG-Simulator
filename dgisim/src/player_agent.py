from typing import List

from dgisim.src.state.game_state import GameState
from dgisim.src.action import Action



class PlayerAgent:
    def choose_action(self, history: List[GameState], pid: GameState.pid) -> Action:
        return Action()
