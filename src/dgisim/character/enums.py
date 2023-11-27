from enum import Enum

from ..event import EventType

__all__ = [
    "CharacterSkill",
    "CharacterSkillType",
    "Faction",
    "WeaponType",
]


class CharacterSkill(Enum):
    SKILL1 = 1  # typically the normal attack
    SKILL2 = 2  # typically the 1st elemental skill
    SKILL3 = 3  # typically the 2nd elemental skill
    ELEMENTAL_BURST = 4

    def to_event_type(self) -> EventType:
        if self is CharacterSkill.SKILL1:
            return EventType.SKILL1
        elif self is CharacterSkill.SKILL2:
            return EventType.SKILL2
        elif self is CharacterSkill.SKILL3:
            return EventType.SKILL3
        elif self is CharacterSkill.ELEMENTAL_BURST:
            return EventType.ELEMENTAL_BURST
        raise NotImplementedError

    # TODO: remove
    def is_elemental_skill(self) -> bool:
        return self is CharacterSkill.SKILL2 or self is CharacterSkill.SKILL3

    def is_elemental_burst(self) -> bool:
        return self is CharacterSkill.ELEMENTAL_BURST

class CharacterSkillType(Enum):
    NORMAL_ATTACK = "Normal-Attack"
    ELEMENTAL_SKILL = "Elemental-Skill"
    ELEMENTAL_BURST = "Elemental-Burst"

class WeaponType(Enum):
    BOW = 1
    CATALYST = 2
    CLAYMORE = 3
    POLEARM = 4
    SWORD = 5
    NONE = 6

class Faction(Enum):
    MONDSTADT = 1
    LIYUE = 2
    INAZUMA = 3
    SUMERU = 4
    FONTAINE = 5
    NATLAN = 6
    SNEZHNAYA = 7
    FATUI = 8
    MONSTER = 9
    HILICHURL = 10
