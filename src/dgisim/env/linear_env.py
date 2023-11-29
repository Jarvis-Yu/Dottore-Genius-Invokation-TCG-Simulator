from ..state.game_state import GameState

class LinearEnv:
    def __init__(self, initial_state: GameState):
        self._curr_state = initial_state

    def reset(self):
        pass

    def step(self):
        pass
