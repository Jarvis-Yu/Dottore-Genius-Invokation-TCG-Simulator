from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

from .action.action import PlayerAction

if TYPE_CHECKING:
    from .state.enums import Pid
    from .state.game_state import GameState

__all__ = [
    "PlayerAgent",
]


class PlayerAgent(ABC):
    """
    The "interface" for all player agents.

    A player agent is what that is accepted by GameStateMachine as a player to
    interact with the game.
    """
    @abstractmethod
    def choose_action(self, history: list[GameState], pid: Pid) -> PlayerAction:
        """
        `history` contains all game-states of the current game in chronological order.

        `pid` represents the player the agent if choosing action for.
        """
        pass
