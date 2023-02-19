from __future__ import annotations
from enum import Enum
from typing_extensions import override

from dgisim.src.cost import Cost


class Card:
    cost: Cost

    def another(self) -> Card:
        raise Exception("Not implemented")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Card)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)

    def __str__(self) -> str:
        return self.__class__.__name__


# for test only
class OmniCard(Card):
    pass


class EventCard(Card):
    pass


class SweetMadame(EventCard):
    def another(self) -> SweetMadame:
        return SweetMadame()


class MondstadtHashBrown(EventCard):
    def another(self) -> MondstadtHashBrown:
        return MondstadtHashBrown()


class Starsigns(EventCard):
    def another(self) -> Starsigns:
        return Starsigns()
