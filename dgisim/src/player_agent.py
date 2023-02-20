from dgisim.src.state.game_state import GameState
from dgisim.src.action import Action


class PlayerAgent:
    def choose_action(self, game_state: GameState, pid: GameState.pid) -> Action:
        return Action()
