from enum import Enum

from ..event import EventType

__all__ = [
    "CharacterSkill",
]


class CharacterSkill(Enum):
    NORMAL_ATTACK = 0
    ELEMENTAL_BURST = 1
    ELEMENTAL_SKILL1 = 2
    ELEMENTAL_SKILL2 = 3

    def to_event_type(self) -> EventType:
        if self is CharacterSkill.NORMAL_ATTACK:
            return EventType.NORMAL_ATTACK
        elif self is CharacterSkill.ELEMENTAL_SKILL1:
            return EventType.ELEMENTAL_SKILL1
        elif self is CharacterSkill.ELEMENTAL_SKILL2:
            return EventType.ELEMENTAL_SKILL2
        elif self is CharacterSkill.ELEMENTAL_BURST:
            return EventType.ELEMENTAL_BURST
        raise NotImplementedError

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
