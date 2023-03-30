from __future__ import annotations

import dgisim.src.state.game_state as gs
import dgisim.src.phase.phase as ph

class GameEndPhase(ph.Phase):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, GameEndPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)