from __future__ import annotations
from typing import TYPE_CHECKING

from .. import phase as ph

if TYPE_CHECKING:
    from ...action.action import PlayerAction
    from ...action.action_generator import ActionGenerator
    from ...state.game_state import GameState
    from ...state.enums import Pid

__all__ = [
    "GameEndPhase",
]


class GameEndPhase(ph.Phase):
    def step(self, game_state: GameState) -> GameState:
        raise Exception("Not Reached")

    def step_action(self, game_state: GameState, pid: Pid, action: PlayerAction) -> None | GameState:
        raise Exception("Not Reached")

    def action_generator(self, game_state: GameState, pid: Pid) -> None | ActionGenerator:
        raise Exception("Not Reached")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GameEndPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
