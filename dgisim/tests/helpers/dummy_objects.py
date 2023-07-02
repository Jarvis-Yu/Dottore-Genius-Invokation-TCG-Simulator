from __future__ import annotations
from dataclasses import dataclass

from dgisim.src.summon.summon import *
from dgisim.src.effect.enums import TRIGGERING_SIGNAL


@dataclass(frozen=True, kw_only=True)
class TestSummon(Summon):
    usages: int = -1

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: TRIGGERING_SIGNAL
    ) -> tuple[list[eft.Effect], Optional[TestSummon]]:
        return [], self