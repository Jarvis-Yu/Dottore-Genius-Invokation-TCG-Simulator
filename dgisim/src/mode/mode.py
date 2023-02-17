from __future__ import annotations

from dgisim.src.phase.card_select import CardSelectPhase
from dgisim.src.phase.starting_hand_select import StartingHandSelectPhase
from dgisim.src.phase.phase import Phase


class Mode:
    def card_select_phase(self) -> Phase:
        raise Exception("Not Overridden")

    def starting_hand_select_phase(self) -> Phase:
        raise Exception("Not Overridden")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Mode)


class DefaultMode(Mode):
    def card_select_phase(self) -> Phase:
        return CardSelectPhase()

    def starting_hand_select_phase(self) -> Phase:
        return StartingHandSelectPhase()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DefaultMode)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
