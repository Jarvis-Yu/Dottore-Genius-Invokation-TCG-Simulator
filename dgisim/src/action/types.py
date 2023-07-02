from __future__ import annotations

import dgisim.src.card.card as cd
from dgisim.src.card.cards import Cards
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.dices import ActualDices, AbstractDices
from dgisim.src.effect.structs import StaticTarget
from dgisim.src.element.element import Element

_SingleChoiceType = StaticTarget | int | ActualDices | CharacterSkill | type["cd.Card"] | Element

GivenChoiceType = tuple[_SingleChoiceType, ...] | AbstractDices | Cards

DecidedChoiceType = _SingleChoiceType | ActualDices | Cards
