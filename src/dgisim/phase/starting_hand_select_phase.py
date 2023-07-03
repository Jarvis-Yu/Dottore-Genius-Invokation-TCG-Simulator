from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from ..phase import phase as ph

from ..action.action import PlayerAction, CharacterSelectAction
from ..state.enums import PID, ACT

if TYPE_CHECKING:
    from ..state.game_state import GameState


class StartingHandSelectPhase(ph.Phase):

    def _activate(self, game_state: GameState) -> GameState:
        return game_state.factory().player1(
            game_state.get_player1().factory().phase(ACT.ACTION_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(ACT.ACTION_PHASE).build()
        ).build()

    def _to_roll_phase(self, game_state: GameState) -> GameState:
        return game_state.factory().phase(
            game_state.get_mode().roll_phase()
        ).player1(
            game_state.get_player1().factory().phase(ACT.PASSIVE_WAIT_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(ACT.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step(self, game_state: GameState) -> GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        if p1.get_phase() == ACT.PASSIVE_WAIT_PHASE and p2.get_phase() == ACT.PASSIVE_WAIT_PHASE:
            return self._activate(game_state)
        elif p1.get_phase() is ACT.END_PHASE and p2.get_phase() is ACT.END_PHASE:
            return self._to_roll_phase(game_state)
        else:
            raise Exception("Unknown Game State to process")

    def _handle_picking_starting_hand(self, game_state: GameState, pid: PID, action: CharacterSelectAction) -> GameState:
        swap_action: CharacterSelectAction = action
        char_id = swap_action.char_id
        player = game_state.get_player(pid)
        chars = player.get_characters()
        if not chars.char_id_valid(char_id):
            return game_state
        new_chars = chars.factory().active_character_id(char_id).build()
        return game_state.factory().active_player_id(
            pid.other()
        ).player(
            pid,
            player.factory()
            .characters(new_chars)
            .phase(ACT.END_PHASE)
            .build()
        ).build()

    def step_action(self, game_state: GameState, pid: PID, action: PlayerAction) -> Optional[
        GameState]:
        if isinstance(action, CharacterSelectAction):
            return self._handle_picking_starting_hand(game_state, pid, action)
        else:
            raise Exception("Unknown Game State to process")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StartingHandSelectPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
