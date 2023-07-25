from ..effect import effect as eft

from ..event import ActionEvent, CardEvent

__all__ = [
    "Preprocessable",
    # "Informable",
]

Preprocessable = eft.SpecificDamageEffect | ActionEvent | CardEvent

# Informable = eft.SpecificDamageEffect | StaticTarget | CharacterSkill
