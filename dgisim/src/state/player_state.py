from __future__ import annotations
from enum import Enum


class PlayerState:
    class act(Enum):
        ACTION_PHASE = "Action Phase"
        WAIT_PHASE = "Wait Phase"
        END_PHASE = "End Phase"

    def __init__(self, phase: act, card_redraw_chances: int):
        self._phase = phase
        self._card_redraw_chances = card_redraw_chances

    def factory(self) -> PlayerStateFactory:
        return PlayerStateFactory(self)

    def get_phase(self) -> act:
        return self._phase

    def get_card_redraw_chances(self) -> int:
        return self._card_redraw_chances

    def isEndPhase(self):
        return self._phase is self.act.END_PHASE

    @staticmethod
    def examplePlayer():
        return PlayerState(
            phase=PlayerState.act.WAIT_PHASE,
            card_redraw_chances=0
        )


class PlayerStateFactory:
    def __init__(self, player_state: PlayerState) -> None:
        self._phase = player_state.get_phase()
        self._card_redraw_chances = player_state.get_card_redraw_chances()

    def phase(self, phase: PlayerState.act) -> PlayerStateFactory:
        self._phase = phase
        return self

    def card_redraw_chances(self, chances: int) -> PlayerStateFactory:
        self._card_redraw_chances = chances
        return self

    def build(self) -> PlayerState:
        return PlayerState(
            phase=self._phase,
            card_redraw_chances=self._card_redraw_chances
        )
