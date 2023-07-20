from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dgisim.src.summon.summon import Summon

if TYPE_CHECKING:
    from dgisim.src.effect.effect import Effect
    from dgisim.src.effect.enums import TriggeringSignal
    from dgisim.src.effect.structs import StaticTarget
    from dgisim.src.state.game_state import GameState


@dataclass(frozen=True, kw_only=True)
class TestSummon(Summon):
    usages: int = -1

    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[Effect], None | TestSummon]:
        return [], self