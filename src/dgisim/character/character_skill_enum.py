from enum import Enum

from ..event.event import EventType

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