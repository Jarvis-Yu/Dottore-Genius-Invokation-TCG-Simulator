from ..effect import effect as eft
from ..event import GameEvent, CardEvent

__all__ = [
    "Preprocessable",
]

Preprocessable = eft.SpecificDamageEffect | GameEvent | CardEvent
