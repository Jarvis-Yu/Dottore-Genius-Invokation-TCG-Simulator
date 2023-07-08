from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..card.card import Card
    from ..effect.structs import StaticTarget
    from ..dices import AbstractDices
    from ..state.enums import PID

class EventSpeed(Enum):
    FAST_ACTION = "Fast-Action"
    COMBAT_ACTION = "Combat-Action"


class EventType(Enum):
    NORMAL_ATTACK = "Normal-Attack"
    ELEMENTAL_SKILL1 = "Elemental-Skill1"
    ELEMENTAL_SKILL2 = "Elemental-Skill2"
    ELEMENTAL_BURST = "Elemental-Burst"
    SWAP = "Swap"


@dataclass(frozen=True, kw_only=True)
class GameEvent:
    target: StaticTarget
    event_type: EventType
    event_speed: EventSpeed
    dices_cost: AbstractDices

@dataclass(frozen=True, kw_only=True)
class CardEvent:
    pid: PID
    card_type: type[Card]
    dices_cost: AbstractDices
