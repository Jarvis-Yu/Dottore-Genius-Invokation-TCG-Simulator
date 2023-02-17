from typing import Optional
from dgisim.src.state.game import GameState


class Phase:
    def run(self, game_state: GameState) -> GameState:
        raise Exception("Not Overriden")

    def run_action(self, game_state: GameState, pid: GameState.pid, action) -> GameState:
        raise Exception("Not Overriden")

    def waiting_for(self, game_state: GameState) -> Optional[GameState.pid]:
        raise Exception("Not Overriden")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Phase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
