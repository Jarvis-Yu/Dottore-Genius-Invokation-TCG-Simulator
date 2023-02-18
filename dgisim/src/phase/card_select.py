from __future__ import annotations
from typing import Optional

import dgisim.src.state.game as gm
from dgisim.src.state.player import PlayerState
import dgisim.src.phase.phase as ph


class CardSelectPhase(ph.Phase):
    def __init__(self) -> None:
        super().__init__()

    def run(self, game_state: gm.GameState) -> gm.GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        # If both players just entered waiting, make them take actions
        if p1.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE and p2.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE:
            return game_state.factory().player1(  # TODO The chances here can be buffed
                p1.factory().phase(PlayerState.act.ACTION_PHASE).card_redraw_chances(1).build()
            ).player2(
                p2.factory().phase(PlayerState.act.ACTION_PHASE).card_redraw_chances(1).build()
            ).build()
        # Otherwise move to the next game phase making both players wait
        return game_state.factory().phase(
            game_state.get_mode().starting_hand_select_phase()
        ).player1(
            game_state.get_player1().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def run_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action) -> gm.GameState:
        # TODO: actually implement something when there is an actually deck
        player: PlayerState = game_state.get_player(pid)
        reducedChances: int = player.get_card_redraw_chances() - 1
        if reducedChances > 0:
            phase: PlayerState.act = player.get_phase()
        else:
            phase: PlayerState.act = PlayerState.act.END_PHASE
        return game_state.factory().player(
            pid,
            player.factory().card_redraw_chances(reducedChances).phase(phase).build()
        ).build()

    def waiting_for(self, game_state: gm.GameState) -> Optional[gm.GameState.pid]:
        players = [game_state.get_player1(), game_state.get_player2()]
        for player in players:
            if player.get_phase() is PlayerState.act.ACTION_PHASE:
                return game_state.get_pid(player)
        return None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CardSelectPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
