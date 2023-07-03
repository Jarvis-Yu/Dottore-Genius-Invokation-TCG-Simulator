from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.dgisim.summon.summon import *

if TYPE_CHECKING:
    from src.dgisim.effect.enums import TRIGGERING_SIGNAL
    from src.dgisim.effect.structs import StaticTarget


@dataclass(frozen=True, kw_only=True)
class TestSummon(Summon):
    usages: int = -1

    def _react_to_signal(
            self,
            source: StaticTarget,
            signal: TRIGGERING_SIGNAL
    ) -> tuple[list[eft.Effect], Optional[TestSummon]]:
        return [], self