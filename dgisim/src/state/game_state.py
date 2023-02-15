from __future__ import annotations
from typing import Optional
from enum import Enum
from dgisim.src.mode.mode import DefaultMode, Mode

from dgisim.src.phase.phase import Phase
from dgisim.src.state.player_state import PlayerState


class GameState:
    class pid(Enum):
        P1 = 1
        P2 = 2

    ROUND_LIMIT = 15
    # CARD_SELECT_PHASE = "Card Selection Phase"
    # STARTING_HAND_SELECT_PHASE = "Starting Hand Selection Phase"
    # ROLL_PHASE = "Roll Phase"
    # ACTION_PHASE = "Action Phase"
    # END_PHASE = "End Phase"
    # GAME_END_PHASE = "Game End Phase"

    def __init__(self, initial_phase: Phase, round: int, player1: PlayerState, player2: PlayerState, mode: Mode):
        self._phase = initial_phase
        self._round = round
        self._player1 = player1
        self._player2 = player2
        self._mode = mode

    @classmethod
    def defaultStart(cls, initial_phase: Phase):
        return cls(initial_phase, 0, PlayerState.examplePlayer(), PlayerState.examplePlayer(), DefaultMode())

    def get_phase(self) -> Phase:
        return self._phase

    def get_round(self) -> int:
        return self._round

    def get_my_player_state(self, player_id: pid) -> PlayerState:
        if player_id is self.pid.P1:
            return self._player1
        elif player_id is self.pid.P2:
            return self._player2
        else:
            raise Exception("player_id unknown")

    def get_other_player_state(self, player_id: pid) -> PlayerState:
        if player_id is self.pid.P1:
            return self._player2
        elif player_id is self.pid.P2:
            return self._player1
        else:
            raise Exception("player_id unknown")

    def waiting_for(self) -> Optional[pid]:
        # TODO
        # Return any parties that the game is waiting for input
        # Return none if game can drive itself at least one step more
        return self.pid.P1

    def run(self) -> GameState:
        return self._phase.run(self)

    def run_action(self, pid, action) -> GameState:
        return self._phase.run_action(self, pid, action)

    def get_winner(self) -> Optional[pid]:
        if self._round > self.ROUND_LIMIT:
            return None
        # TODO
        # based on player's health
        return self.pid.P1

    def game_end(self) -> bool:
        if self._round > self.ROUND_LIMIT:
            return True
        # TODO
        # check player's health
        return False
