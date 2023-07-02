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

class ACT(Enum):
    ACTION_PHASE = "Action Phase"
    PASSIVE_WAIT_PHASE = "Passive Wait Phase"
    ACTIVE_WAIT_PHASE = "Aggressive Wait Phase"
    END_PHASE = "End Phase"

    def is_action_phase(self) -> bool:
        return self is ACT.ACTION_PHASE

    def is_passive_wait_phase(self) -> bool:
        return self is ACT.PASSIVE_WAIT_PHASE

    def is_active_wait_phase(self) -> bool:
        return self is ACT.ACTIVE_WAIT_PHASE
    
    def is_end_phase(self) -> bool:
        return self is ACT.END_PHASE