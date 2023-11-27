from __future__ import annotations
from enum import Enum

__all__ = [
    "Act",
    "Pid",
]


class Pid(Enum):
    P1 = 1
    P2 = 2

    def is_player1(self) -> bool:
        return self is Pid.P1

    def is_player2(self) -> bool:
        return self is Pid.P2

    def other(self) -> Pid:
        """ :returns: `P2` if this is `P1`, vice versa. """
        if self is Pid.P1:
            return Pid.P2
        elif self is Pid.P2:
            return Pid.P1
        else:  # pragma: no cover
            raise Exception("Unknown situation of pid")


class Act(Enum):
    ACTION_PHASE = 1
    PASSIVE_WAIT_PHASE = 2
    ACTIVE_WAIT_PHASE = 3
    END_PHASE = 4

    def is_action_phase(self) -> bool:  # pragma: no cover
        return self is Act.ACTION_PHASE

    def is_passive_wait_phase(self) -> bool:  # pragma: no cover
        return self is Act.PASSIVE_WAIT_PHASE

    def is_active_wait_phase(self) -> bool:  # pragma: no cover
        return self is Act.ACTIVE_WAIT_PHASE

    def is_end_phase(self) -> bool:  # pragma: no cover
        return self is Act.END_PHASE
