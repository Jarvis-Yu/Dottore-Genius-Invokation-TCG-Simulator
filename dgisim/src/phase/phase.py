from __future__ import annotations
from typing import Optional

import dgisim.src.state.game_state as gm
from dgisim.src.helper.level_print import level_print_single
from dgisim.src.action import PlayerAction
from dgisim.src.event.event_pre import EventPre


class Phase:
    def step(self, game_state: gm.GameState) -> gm.GameState:
        raise Exception("Not Overriden")

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.Pid, action: PlayerAction) -> gm.GameState:
        raise Exception("Not Overriden")

    def waiting_for(self, game_state: gm.GameState) -> Optional[gm.GameState.Pid]:
        players = [game_state.get_player1(), game_state.get_player2()]
        for player in players:
            from dgisim.src.state.player_state import PlayerState
            if player.get_phase() is PlayerState.Act.ACTION_PHASE:
                return game_state.get_pid(player)
        return None

    def possible_actions(self, game_state: gm.GameState) -> dict[int, EventPre]:
        return {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Phase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        return level_print_single(self.__class__.__name__, indent)
