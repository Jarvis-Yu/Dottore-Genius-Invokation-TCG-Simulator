"""
The definition of an *Event* in this project is, something that can be
preprocessed by statuses according to the description of each status.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import TYPE_CHECKING

from typing_extensions import Self

if TYPE_CHECKING:
    from .card.card import Card
    from .character.character import Character
    from .character.enums import CharacterSkill, CharacterSkillType
    from .effect.effect import SpecificDamageEffect
    from .effect.structs import DamageType, StaticTarget
    from .element import Element, Reaction
    from .dice import AbstractDice
    from .state.game_state import GameState
    from .state.enums import Pid

__all__ = [
    # enums
    "EventSpeed",
    "EventSubType",
    "EventType",

    "InformableEvent",
    "DmgIEvent",
    "CharacterDeathIEvent",
    "ReactionIEvent",
    "SkillIEvent",

    "PreprocessableEvent",
    "ActionPEvent",
    "CardPEvent",
    "DmgPEvent",
    "RollChancePEvent",
]


class EventSpeed(Enum):
    FAST_ACTION = "Fast-Action"
    COMBAT_ACTION = "Combat-Action"


class EventSubType(Enum):
    pass


class EventType(Enum):
    SKILL1 = "Normal-Attack1"
    SKILL2 = "Elemental-Skill1"
    SKILL3 = "Elemental-Skill2"
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
class ReactionIEvent(InformableEvent):
    source: StaticTarget
    target: StaticTarget
    source_type: DamageType
    reaction: Reaction



@dataclass(frozen=True, kw_only=True)
class SkillIEvent(InformableEvent):
    source: StaticTarget
    skill_type: CharacterSkill
    skill_true_type: CharacterSkillType

    def is_skill_from_character(
            self,
            game_state: GameState,
            pid_to_check: Pid,
            skill_type: None | CharacterSkill = None,
            char_type: None | type[Character] = None,
    ) -> bool:
        return (
            self.source.pid is pid_to_check
            and (
                skill_type is None
                or self.skill_type is skill_type
            )
            and (
                char_type is None
                or isinstance(game_state.get_character_target(self.source), char_type)
            )
        )


@dataclass(frozen=True, kw_only=True)
class PreprocessableEvent:
    pass


@dataclass(frozen=True, kw_only=True)
class ActionPEvent(PreprocessableEvent):
    source: StaticTarget       # this source is who caused the GameEvent
    target: None | StaticTarget = None
    event_type: EventType
    event_sub_type: None | EventSubType | CharacterSkillType = None
    event_speed: EventSpeed
    dice_cost: AbstractDice

    def with_new_cost(self, new_cost: AbstractDice) -> Self:
        return replace(self, dice_cost=new_cost)


@dataclass(frozen=True, kw_only=True)
class CardPEvent(PreprocessableEvent):
    pid: Pid
    card_type: type[Card]
    dice_cost: AbstractDice

    def with_new_cost(self, new_cost: AbstractDice) -> Self:
        return replace(self, dice_cost=new_cost)


@dataclass(frozen=True, kw_only=True)
class DmgPEvent(PreprocessableEvent):
    dmg: SpecificDamageEffect

    def delta_damage(self, d_damage: int) -> Self:
        new_damage = max(0, self.dmg.damage + d_damage)
        return replace(self, dmg=replace(self.dmg, damage=new_damage))

    def convert_element(self, element: Element) -> Self:
        return replace(self, dmg=replace(self.dmg, element=element))


@dataclass(frozen=True, kw_only=True)
class RollChancePEvent(PreprocessableEvent):
    pid: Pid
    chances: int
