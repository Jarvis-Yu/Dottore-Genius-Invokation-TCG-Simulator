from dataclasses import dataclass
from typing import TYPE_CHECKING

from dgisim.src.state.enums import PID
from dgisim.src.effect.enums import ZONE


@dataclass(frozen=True)
class StaticTarget:
    pid: PID
    zone: ZONE
    id: int
