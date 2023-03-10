from __future__ import annotations

import dgisim.src.phase.phase as ph
import dgisim.src.phase.card_select_phase as cs
import dgisim.src.phase.starting_hand_select_phase as shs
import dgisim.src.phase.roll_phase as rp
import dgisim.src.phase.action_phase as ap
import dgisim.src.phase.end_phase as ep
import dgisim.src.phase.game_end_phase as gep
from dgisim.src.helper.level_print import level_print_single


class Mode:

    _ROUND_LIMIT = 15

    def get_round_limit(self) -> int:
        return self._ROUND_LIMIT

    def card_select_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def starting_hand_select_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def roll_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def action_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def end_phase(self) -> ph.Phase:
        raise Exception("Not Overridden")

    def game_end_phase(self) -> ph.Phase:
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

    def roll_phase(self) -> ph.Phase:
        return rp.RollPhase()

    def action_phase(self) -> ph.Phase:
        return ap.ActionPhase()

    def end_phase(self) -> ph.Phase:
        return ep.EndPhase()

    def game_end_phase(self) -> ph.Phase:
        return gep.GameEndPhase()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DefaultMode)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
