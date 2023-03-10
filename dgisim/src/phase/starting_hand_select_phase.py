from __future__ import annotations
from typing import Optional

import dgisim.src.state.game_state as gm
import dgisim.src.phase.phase as ph
from dgisim.src.action import Action, CharacterSelectAction
from dgisim.src.state.player_state import PlayerState


class StartingHandSelectPhase(ph.Phase):

    def _activate(self, game_state: gm.GameState) -> gm.GameState:
        return game_state.factory().player1(
            game_state.get_player1().factory().phase(PlayerState.act.ACTION_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(PlayerState.act.ACTION_PHASE).build()
        ).build()

    def _to_roll_phase(self, game_state: gm.GameState) -> gm.GameState:
        return game_state.factory().phase(
            game_state.get_mode().roll_phase()
        ).player1(
            game_state.get_player1().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step(self, game_state: gm.GameState) -> gm.GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        if p1.get_phase() == PlayerState.act.PASSIVE_WAIT_PHASE and p2.get_phase() == PlayerState.act.PASSIVE_WAIT_PHASE:
            return self._activate(game_state)
        elif p1.get_phase() is PlayerState.act.END_PHASE and p2.get_phase() is PlayerState.act.END_PHASE:
            return self._to_roll_phase(game_state)
        else:
            raise Exception("Unknown Game State to process")

    def _handle_picking_starting_hand(self, game_state: gm.GameState, pid: gm.GameState.pid, action: CharacterSelectAction) -> gm.GameState:
        swap_action: CharacterSelectAction = action
        char_id = swap_action.get_selected_character_id()
        player: PlayerState = game_state.get_player(pid)
        chars = player.get_characters()
        if not chars.char_id_valid(char_id):
            return game_state
        new_chars = chars.factory().active_character_id(char_id).build()
        return game_state.factory().player(
            pid,
            player.factory()
            .characters(new_chars)
            .phase(PlayerState.act.END_PHASE)
            .build()
        ).build()

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action: Action) -> gm.GameState:
        if isinstance(action, CharacterSelectAction):
            return self._handle_picking_starting_hand(game_state, pid, action)
        else:
            raise Exception("Unknown Game State to process")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StartingHandSelectPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
