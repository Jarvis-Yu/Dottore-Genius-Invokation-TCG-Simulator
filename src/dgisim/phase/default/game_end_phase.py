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

    def waiting_for(self, game_state: ph.GameState) -> None | ph.Pid:
        return None

    def step_action(self, game_state: GameState, pid: Pid, action: PlayerAction) -> None | GameState:
        raise Exception("Not Reached")

    def action_generator(self, game_state: GameState, pid: Pid) -> None | ActionGenerator:
        raise Exception("Not Reached")
