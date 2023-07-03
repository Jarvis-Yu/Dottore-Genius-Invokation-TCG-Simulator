from ..effect import effect as eft
from ..event import event as evt

Preprocessable = eft.SpecificDamageEffect | evt.GameEvent | evt.CardEvent
