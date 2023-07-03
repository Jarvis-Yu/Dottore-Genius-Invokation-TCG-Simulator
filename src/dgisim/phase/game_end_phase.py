from __future__ import annotations

from ..phase import phase as ph

class GameEndPhase(ph.Phase):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, GameEndPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)