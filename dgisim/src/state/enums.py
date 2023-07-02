from __future__ import annotations
from enum import Enum

class PID(Enum):
    P1 = 1
    P2 = 2

    def is_player1(self) -> bool:
        return self is PID.P1

    def is_player2(self) -> bool:
        return self is PID.P2

    def other(self) -> PID:
        if self is PID.P1:
            return PID.P2
        elif self is PID.P2:
            return PID.P1
        else:
            raise Exception("Unknown situation of pid")