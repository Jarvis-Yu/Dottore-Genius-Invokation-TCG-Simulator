from dgisim.src.state.game_state import GameState
from dgisim.src.phase.phase import Phase
from dgisim.src.mode.mode import Mode

class CardSelectPhase(Phase):
    def __init__(self) -> None:
        super().__init__()

    def run(self, game_state: GameState) -> GameState:
        """
        Pre: CardSelectPhase can only drive itself when leaving this phase
        """
        return GameState.defaultStart(Phase())

    def run_action(self, game_state: GameState, pid: GameState.pid, action) -> GameState:
        # TODO
        return GameState.defaultStart(Phase())
