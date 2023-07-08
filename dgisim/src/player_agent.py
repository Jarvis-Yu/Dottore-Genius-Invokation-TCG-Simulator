from __future__ import annotations
from typing import TYPE_CHECKING

from .action.action import PlayerAction

if TYPE_CHECKING:
    from .state.enums import PID
    from .state.game_state import GameState

__all__ = [
    "PlayerAgent",
]


class PlayerAgent:
    """
    The "interface" for all player agents.

    A player agent is what that is accepted by GameStateMachine as a player to
    interact with the game.
    """
    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        return PlayerAction()
