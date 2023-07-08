from __future__ import annotations

from ..card import card as cd

from ..card.cards import Cards
from ..character.enums import CharacterSkill
from ..dices import ActualDices, AbstractDices
from ..effect.structs import StaticTarget
from ..element import Element
from .enums import ActionType

__all__ = [
    "DecidedChoiceType",
    "GivenChoiceType",
]

_SingleChoiceType = (
    StaticTarget
    | int
    | ActualDices
    | CharacterSkill
    | type["cd.Card"]
    | Element
    | ActionType
)

GivenChoiceType = tuple[_SingleChoiceType, ...] | ActualDices | AbstractDices | Cards

DecidedChoiceType = _SingleChoiceType | ActualDices | Cards
