from __future__ import annotations
from enum import Enum

from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
import dgisim.src.card.card


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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlayerState):
            return False
        return self._phase == other._phase \
            and self._card_redraw_chances == other._card_redraw_chances

    def __hash__(self) -> int:
        return hash((
            self._phase,
            self._card_redraw_chances,
        ))
    
    def __str__(self) -> str:
        return "Player Info To Be Implemented\n"

    def to_string(self, indent: int = 0):
        new_indent = indent + INDENT
        return level_print({
            "Phase": level_print_single(str(self._phase), new_indent),
            "Card Redraw Chances": level_print_single(str(self._card_redraw_chances), new_indent),
        }, indent)


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
