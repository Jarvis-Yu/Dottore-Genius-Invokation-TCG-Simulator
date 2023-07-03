from __future__ import annotations
from typing import TYPE_CHECKING

from .action.action import PlayerAction

if TYPE_CHECKING:
    from .state.enums import PID
    from .state.game_state import GameState


class PlayerAgent:
    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        return PlayerAction()


class PlayerProxyAgent(PlayerAgent):
    pass


class ProxyAgent(PlayerProxyAgent):
    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        return super().choose_action(history, pid)
