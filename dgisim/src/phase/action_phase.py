from __future__ import annotations
from typing import Optional

import dgisim.src.state.game_state as gm
import dgisim.src.phase.phase as ph
from dgisim.src.state.player_state import PlayerState
from dgisim.src.action import Action, EndRoundAction

class ActionPhase(ph.Phase):
    def step(self, game_state: gm.GameState) -> gm.GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        active_player_id = game_state.get_active_player_id()
        if p1.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE and p2.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE:
            # TODO: Handle before action buffs
            return game_state.factory().player(
                active_player_id,
                game_state.get_player(active_player_id).factory().phase(
                    PlayerState.act.ACTION_PHASE
                ).build()
            ).build()
        elif p1.get_phase() is PlayerState.act.END_PHASE and p2.get_phase() is PlayerState.act.END_PHASE:
            return game_state.factory().phase(
                game_state.get_mode().end_phase()
            ).player(
                active_player_id,
                game_state.get_player(active_player_id).factory().phase(
                    PlayerState.act.PASSIVE_WAIT_PHASE
                ).build()
            ).other_player(
                active_player_id,
                game_state.get_other_player(active_player_id).factory().phase(
                    PlayerState.act.PASSIVE_WAIT_PHASE
                ).build()
            ).build()
        raise Exception("Unknown Game State to process")

    def _handle_end_round(self, game_state: gm.GameState, pid: gm.GameState.pid, action: EndRoundAction) -> gm.GameState:
        active_player_id = game_state.get_active_player_id()
        active_player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        if other_player.get_phase() is PlayerState.act.END_PHASE:
            other_player_new_phase = PlayerState.act.END_PHASE
        elif other_player.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE:
            other_player_new_phase = PlayerState.act.ACTION_PHASE
        else:
            raise Exception(f"Unknown Game State to process {other_player.get_phase()}")
        if pid is active_player_id:
            return game_state.factory().active_player(
                active_player_id.other()
            ).player(
                active_player_id,
                active_player.factory().phase(
                    PlayerState.act.END_PHASE
                ).build()
            ).other_player(
                active_player_id,
                other_player.factory().phase(
                    other_player_new_phase
                ).build()
            ).build()
        raise Exception("Unknown Game State to process")

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action: Action) -> gm.GameState:
        """
        TODO: Currently only allows player to end their round
        """
        if isinstance(action, EndRoundAction):
            return self._handle_end_round(game_state, pid, action)
        raise Exception("Unknown Game State to process")

    def waiting_for(self, game_state: gm.GameState) -> Optional[gm.GameState.pid]:
        """
        TODO: override this to handle death swap
        """
        return super().waiting_for(game_state)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ActionPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
