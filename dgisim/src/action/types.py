from __future__ import annotations

from ..card import card as cd

from ..card.cards import Cards
from ..character.enums import CharacterSkill
from ..dice import ActualDice, AbstractDice
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
    | ActualDice
    | CharacterSkill
    | type["cd.Card"]
    | Element
    | ActionType
)

GivenChoiceType = tuple[_SingleChoiceType, ...] | ActualDice | AbstractDice | Cards

DecidedChoiceType = _SingleChoiceType | ActualDice | Cards
