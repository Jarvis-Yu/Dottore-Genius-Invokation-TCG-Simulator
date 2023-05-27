from __future__ import annotations
from typing import Optional, Union

import dgisim.src.state.game_state as gs
from dgisim.src.helper.level_print import level_print_single
from dgisim.src.action import PlayerAction
from dgisim.src.event.event_pre import EventPre


class Phase:
    def step(self, game_state: gs.GameState) -> gs.GameState:
        raise Exception("Not Overriden")

    def step_action(self, game_state: gs.GameState, pid: gs.GameState.Pid, action: PlayerAction) -> Optional[gs.GameState]:
        raise Exception("Not Overriden")

    def waiting_for(self, game_state: gs.GameState) -> Optional[gs.GameState.Pid]:
        players = [game_state.get_player1(), game_state.get_player2()]
        for player in players:
            from dgisim.src.state.player_state import PlayerState
            if player.get_phase() is PlayerState.Act.ACTION_PHASE:
                return game_state.get_pid(player)
        return None

    def possible_actions(self, game_state: gs.GameState) -> dict[int, EventPre]:
        return {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Phase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        return level_print_single(self.__class__.__name__, indent)

    def dict_str(self) -> Union[dict, str]:
        return self.__class__.__name__
