from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dgisim.src.summon.summon import *

if TYPE_CHECKING:
    from dgisim.src.effect.enums import TRIGGERING_SIGNAL
    from dgisim.src.effect.structs import StaticTarget


@dataclass(frozen=True, kw_only=True)
class TestSummon(Summon):
    usages: int = -1

    def _react_to_signal(
            self,
            source: StaticTarget,
            signal: TRIGGERING_SIGNAL
    ) -> tuple[list[eft.Effect], Optional[TestSummon]]:
        return [], self