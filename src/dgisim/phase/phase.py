from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

from ..helper.level_print import level_print_single

if TYPE_CHECKING:
    from ..state.game_state import GameState
    from ..action.action import PlayerAction
    from ..action.action_generator import ActionGenerator
    from ..state.enums import Pid

__all__ = [
    "Phase",
]


class Phase(ABC):
    """
    Phase defines how `GameState` make state transitions under this phase.

    This class doesn't store any data, so all instances of `Phase` (of the same class)
    are considered equal and have the same hash.
    """

    @abstractmethod
    def step(self, game_state: GameState) -> GameState:
        """
        :returns: the next game state after one state transition from `game_state`.

        This method defines how state transition is performed. (transtion without player action)
        """
        raise NotImplementedError

    @abstractmethod
    def step_action(
        self,
        game_state: GameState,
        pid: Pid,
        action: PlayerAction
    ) -> None | GameState:
        """
        :param game_state: current game state.
        :param pid: player of action.
        :param action: the action of player.

        :returns: the next game state after one state transition from `game_state`.

        This method defines how state transition is performed. (transtion with player action)
        """
        raise NotImplementedError

    def waiting_for(self, game_state: GameState) -> None | Pid:
        """
        :returns: which player's action is required to perform the next state transition.
                  `None` is returned if no player action is required.
        """
        players = [game_state.get_player1(), game_state.get_player2()]
        for player in players:
            if player.get_phase().is_action_phase():
                return game_state.get_pid(player)
        return None

    @abstractmethod
    def action_generator(self, game_state: GameState, pid: Pid) -> None | ActionGenerator:
        """
        :returns: an action generator for player `pid` under `game_state`.
                  `None` is returned if the player is not allowed to make a move.
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other)

    def __hash__(self) -> int:
        return hash(type(self))

    def dict_str(self) -> dict | str:
        return self.__class__.__name__
