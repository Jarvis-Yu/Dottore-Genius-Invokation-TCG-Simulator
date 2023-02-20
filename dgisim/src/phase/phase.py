from __future__ import annotations
from typing import Optional

import dgisim.src.state.game_state as gm
from dgisim.src.helper.level_print import level_print_single
from dgisim.src.action import Action


class Phase:
    def step(self, game_state: gm.GameState) -> gm.GameState:
        raise Exception("Not Overriden")

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action: Action) -> gm.GameState:
        raise Exception("Not Overriden")

    def waiting_for(self, game_state: gm.GameState) -> Optional[gm.GameState.pid]:
        raise Exception("Not Overriden")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Phase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        return level_print_single(self.__class__.__name__, indent)
