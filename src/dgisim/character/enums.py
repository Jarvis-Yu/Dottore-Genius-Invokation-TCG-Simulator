from enum import Enum

from ..event import EventType

__all__ = [
    "CharacterSkill",
    "CharacterSkillType",
    "Faction",
    "WeaponType",
]


class CharacterSkill(Enum):
    SKILL1 = 0  # typically the normal attack
    SKILL2 = 1  # typically the 1st elemental skill
    SKILL3 = 2  # typically the 2nd elemental skill
    ELEMENTAL_BURST = 3

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

class CharacterSkillType(Enum):
    NORMAL_ATTACK = 0
    ELEMENTAL_SKILL = 1
    ELEMENTAL_BURST = 2

    def is_normal_attack(self):
        return self is CharacterSkillType.NORMAL_ATTACK
    
    def is_elemental_skill(self):
        return self is CharacterSkillType.ELEMENTAL_SKILL

    def is_elemental_burst(self):
        return self is CharacterSkillType.ELEMENTAL_BURST

class WeaponType(Enum):
    BOW = 0
    CATALYST = 1
    CLAYMORE = 2
    POLEARM = 3
    SWORD = 4
    NONE = 5

class Faction(Enum):
    MONDSTADT = 0
    LIYUE = 1
    INAZUMA = 2
    SUMERU = 3
    FONTAINE = 4
    NATLAN = 5
    SNEZHNAYA = 6
    FATUI = 7
    MONSTER = 8
    HILICHURL = 9
    THE_EREMITES = 10
