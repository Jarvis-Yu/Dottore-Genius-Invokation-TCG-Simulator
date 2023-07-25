"""
The definition of an *Event* in this project is, something that can be
preprocessed by statuses according to the description of each status.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .card.card import Card
    from .character.enums import CharacterSkill
    from .effect.effect import SpecificDamageEffect
    from .effect.structs import StaticTarget
    from .dices import AbstractDices
    from .state.enums import Pid

__all__ = [
    # enums
    "EventSpeed",
    "EventType",

    "InformableEvent",
    "DmgIEvent",
    "CharacterDeathIEvent",
    "SkillIEvent",

    "PreprocessableEvent",
    "ActionPEvent",
    "CardPEvent",
    "DmgPEvent",
]


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
class InformableEvent:
    pass


@dataclass(frozen=True, kw_only=True)
class DmgIEvent(InformableEvent):
    dmg: SpecificDamageEffect


@dataclass(frozen=True, kw_only=True)
class CharacterDeathIEvent(InformableEvent):
    target: StaticTarget


@dataclass(frozen=True, kw_only=True)
class SkillIEvent(InformableEvent):
    source: StaticTarget
    skill_type: CharacterSkill


@dataclass(frozen=True, kw_only=True)
class PreprocessableEvent:
    pass


@dataclass(frozen=True, kw_only=True)
class DmgPEvent(PreprocessableEvent):
    dmg: SpecificDamageEffect


@dataclass(frozen=True, kw_only=True)
class ActionPEvent(PreprocessableEvent):
    source: StaticTarget       # this source is who caused the GameEvent
    event_type: EventType
    event_speed: EventSpeed
    dices_cost: AbstractDices


@dataclass(frozen=True, kw_only=True)
class CardPEvent(PreprocessableEvent):
    pid: Pid
    card_type: type[Card]
    dices_cost: AbstractDices
