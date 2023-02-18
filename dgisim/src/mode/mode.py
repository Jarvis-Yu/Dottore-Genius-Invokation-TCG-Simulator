from __future__ import annotations

import dgisim.src.phase.phase as ph
import  dgisim.src.phase.card_select as cs
import  dgisim.src.phase.starting_hand_select as shs
from dgisim.src.helper.level_print import level_print_single


class Mode:
    def card_select_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def starting_hand_select_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Mode)

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, indent: int = 0) -> str:
        return level_print_single(self.__class__.__name__, indent)


class DefaultMode(Mode):
    # Initial phase of this mode
    def card_select_phase(self) -> ph.Phase:
        return cs.CardSelectPhase()

    def starting_hand_select_phase(self) -> ph.Phase:
        return shs.StartingHandSelectPhase()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DefaultMode)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
