from ..effect import effect as eft
from ..event import event as evt

__all__ = [
    "Preprocessable",
]

Preprocessable = eft.SpecificDamageEffect | evt.GameEvent | evt.CardEvent
