from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

from dgisim.src.state.enums import PID
import dgisim.src.effect.effect as eft
import dgisim.src.card.card as cd
from dgisim.src.dices import AbstractDices


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
    target: eft.StaticTarget
    event_type: EventType
    event_speed: EventSpeed
    dices_cost: AbstractDices

@dataclass(frozen=True, kw_only=True)
class CardEvent:
    pid: PID
    card_type: type[cd.Card]
    dices_cost: AbstractDices
