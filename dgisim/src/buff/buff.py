from __future__ import annotations
from enum import Enum

import dgisim.src.state.game_state as gs


class TrigerringEvent(Enum):
    pass


class Buffable:
    def preprocess(self):
        raise Exception("TODO")

    def react_to_signal(self, game_state: gs.GameState, signal: TrigerringEvent) -> gs.GameState:
        raise Exception("TODO")


class CharacterBuff(Buffable):
    pass


class Stuffed(CharacterBuff):
    pass
