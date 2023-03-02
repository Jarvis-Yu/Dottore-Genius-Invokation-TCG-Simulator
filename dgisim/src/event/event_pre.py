from enum import Enum

from dgisim.src.dices import Dices
from dgisim.src.event.event import GameEvent

class EventPre:
    def __init__(
        self,
        dices: Dices,
        event: GameEvent,
        energy: int = 0,
    ):
        self._dices = dices
        self._energy = energy
