from __future__ import annotations

from dgisim.src.dices import AbstractDices, ActualDices
# from dgisim.src.event.event import GameEvent

class EventPre:
    # def __init__(
    #     self,
    #     dices: Dices,
    #     event: GameEvent,
    #     energy: int = 0,
    # ):
    #     self._dices = dices
    #     self._event = event
    #     self._energy = energy
    pass

class DiceOnlyPre(EventPre):
    def __init__(self, dices: AbstractDices) -> None:
        self._dices = dices

    def dices(self) -> AbstractDices:
        return self._dices

    def _satisfies(self, dices: ActualDices) -> bool:
        # TODO: check if dices satisfies self._dices
        return True

    def fulfill(self) -> DicesOnlyFulfill:
        return DicesOnlyFulfill(self)

class DicesOnlyFulfill:

    def __init__(self, pre: DiceOnlyPre) -> None:
        self._done = False
        self._pre = pre

    # def next_request(self) -> 

# class DiceAndTarget(EventPre):
#     def __init__(self, dices: AbstractDices) -> None:
#         self._dices = dices
