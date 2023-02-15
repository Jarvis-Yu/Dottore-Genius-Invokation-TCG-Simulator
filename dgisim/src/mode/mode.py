from __future__ import annotations

from dgisim.src.phase.card_select_phase import CardSelectPhase
from dgisim.src.phase.phase import Phase


class Mode:
    def card_select_phase(self) -> Phase:
        raise Exception("Not Overridden")

    def starting_hand_select_phase(self) -> Phase:
        raise Exception("Not Overridden")


class DefaultMode(Mode):
    def card_select_phase(self) -> Phase:
        return super().card_select_phase()

    def starting_hand_select_phase(self) -> Phase:
        return super().starting_hand_select_phase()
