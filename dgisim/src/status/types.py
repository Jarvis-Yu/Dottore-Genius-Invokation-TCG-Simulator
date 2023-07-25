from ..effect import effect as eft

from ..event import ActionPEvent, CardPEvent

__all__ = [
    "Preprocessable",
    # "Informable",
]

Preprocessable = eft.SpecificDamageEffect | ActionPEvent | CardPEvent

# Informable = eft.SpecificDamageEffect | StaticTarget | CharacterSkill
