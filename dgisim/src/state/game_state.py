from __future__ import annotations
from typing import Optional
from enum import Enum

import dgisim.src.mode.mode as md
import dgisim.src.phase.phase as ph
import dgisim.src.phase.game_end_phase as gep
import dgisim.src.state.player_state as pl
from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
from dgisim.src.action import PlayerAction


class GameState:
    class Pid(Enum):
        P1 = 1
        P2 = 2

        def is_player1(self) -> bool:
            return self == GameState.Pid.P1

        def is_player2(self) -> bool:
            return self is GameState.Pid.P2

        def other(self) -> GameState.Pid:
            if self is GameState.Pid.P1:
                return GameState.Pid.P2
            elif self is GameState.Pid.P2:
                return GameState.Pid.P1
            else:
                raise Exception("Unknown situation of pid")

    def __init__(
        self,
        phase: ph.Phase,
        round: int,
        active_player: GameState.Pid,
        mode: md.Mode,
        player1: pl.PlayerState,
        player2: pl.PlayerState,
    ):
        # REMINDER: don't forget to update factory when adding new fields
        self._phase = phase
        self._round = round
        self._active_player = active_player
        self._player1 = player1
        self._player2 = player2
        self._mode = mode

    @classmethod
    def from_default(cls):
        return cls(
            phase=md.DefaultMode().card_select_phase(),
            round=0,
            active_player=GameState.Pid.P1,
            mode=md.DefaultMode(),
            player1=pl.PlayerState.examplePlayer(),
            player2=pl.PlayerState.examplePlayer(),
        )

    def factory(self):
        return GameStateFactory(self)

    def get_phase(self) -> ph.Phase:
        return self._phase

    def get_round(self) -> int:
        return self._round

    def get_active_player_id(self) -> GameState.Pid:
        return self._active_player

    def get_mode(self) -> md.Mode:
        return self._mode

    def get_player1(self) -> pl.PlayerState:
        return self._player1

    def get_player2(self) -> pl.PlayerState:
        return self._player2

    def get_pid(self, player: pl.PlayerState) -> GameState.Pid:
        if player is self._player1:
            return self.Pid.P1
        elif player is self._player2:
            return self.Pid.P2
        else:
            raise Exception("player unknown")

    def get_player(self, player_id: GameState.Pid) -> pl.PlayerState:
        if player_id.is_player1():
            return self._player1
        elif player_id.is_player2():
            return self._player2
        else:
            raise Exception("player_id unknown")

    def get_other_player(self, player_id: GameState.Pid) -> pl.PlayerState:
        if player_id.is_player1():
            return self._player2
        elif player_id.is_player2():
            return self._player1
        else:
            raise Exception("player_id unknown")

    def waiting_for(self) -> Optional[GameState.Pid]:
        return self._phase.waiting_for(self)

    def step(self) -> GameState:
        return self._phase.step(self)

    def action_step(self, pid: GameState.Pid, action: PlayerAction) -> GameState:
        return self._phase.step_action(self, pid, action)

    def get_winner(self) -> Optional[GameState.Pid]:
        assert self.game_end()
        if isinstance(self._phase, gep.GameEndPhase):
            return None
        # TODO: based on player's health
        raise Exception("Not Implemented")

    def game_end(self) -> bool:
        return isinstance(self._phase, gep.GameEndPhase)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameState):
            return False
        return self._phase == other._phase \
            and self._round == other._round \
            and self._active_player == other._active_player \
            and self._player1 == other._player1 \
            and self._player2 == other._player2 \
            and self._mode == other._mode

    def __hash__(self) -> int:
        return hash((
            self._phase,
            self._round,
            self._player1,
            self._player2,
            self._mode,
        ))

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        new_indent = indent + INDENT
        return level_print({
            "Mode": self._mode.to_string(new_indent),
            "Phase": self._phase.to_string(new_indent),
            "Round": level_print_single(str(self._round), new_indent),
            "Active Player": level_print_single(str(self._active_player), new_indent),
            "Player1": self._player1.to_string(new_indent),
            "Player2": self._player2.to_string(new_indent),
        }, indent)


class GameStateFactory:
    def __init__(self, game_state: GameState):
        self._phase = game_state.get_phase()
        self._round = game_state.get_round()
        self._active_player = game_state.get_active_player_id()
        self._player1 = game_state.get_player1()
        self._player2 = game_state.get_player2()
        self._mode = game_state.get_mode()

    def phase(self, new_phase: ph.Phase) -> GameStateFactory:
        self._phase = new_phase
        return self

    def round(self, new_round: int) -> GameStateFactory:
        self._round = new_round
        return self

    def mode(self, new_mode: md.Mode) -> GameStateFactory:
        self._mode = new_mode
        return self

    def active_player(self, pid: GameState.Pid) -> GameStateFactory:
        self._active_player = pid
        return self

    def player1(self, new_player: pl.PlayerState) -> GameStateFactory:
        self._player1 = new_player
        return self

    def player2(self, new_player: pl.PlayerState) -> GameStateFactory:
        self._player2 = new_player
        return self

    def player(self, pid: GameState.Pid, new_player: pl.PlayerState) -> GameStateFactory:
        if pid is GameState.Pid.P1:
            self._player1 = new_player
        elif pid is GameState.Pid.P2:
            self._player2 = new_player
        else:
            raise Exception("player_id unknown")
        return self

    def other_player(self, pid: GameState.Pid, new_player: pl.PlayerState) -> GameStateFactory:
        if pid is GameState.Pid.P1:
            self._player2 = new_player
        elif pid is GameState.Pid.P2:
            self._player1 = new_player
        else:
            raise Exception("player_id unknown")
        return self

    def build(self) -> GameState:
        return GameState(
            phase=self._phase,
            round=self._round,
            active_player=self._active_player,
            mode=self._mode,
            player1=self._player1,
            player2=self._player2
        )


if __name__ == "__main__":
    initial_state = GameState.from_default()
    pid = initial_state.waiting_for()
    assert pid is None
    state = initial_state.step()
    pass
