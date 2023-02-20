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


class FoodCard(EventCard):
    pass


class SweetMadame(FoodCard):
    def another(self) -> SweetMadame:
        return SweetMadame()


class MondstadtHashBrown(FoodCard):
    def another(self) -> MondstadtHashBrown:
        return MondstadtHashBrown()


class JueyunGuoba(FoodCard):
    def another(self) -> JueyunGuoba:
        return JueyunGuoba()


class LotusFlowerCrisp(FoodCard):
    def another(self) -> LotusFlowerCrisp:
        return LotusFlowerCrisp()


class MintyMeatRolls(FoodCard):
    def another(self) -> MintyMeatRolls:
        return MintyMeatRolls()


class MushroomPizza(FoodCard):
    def another(self) -> MushroomPizza:
        return MushroomPizza()


class NorthernSmokedChicken(FoodCard):
    def another(self) -> NorthernSmokedChicken:
        return NorthernSmokedChicken()


class Starsigns(EventCard):
    def another(self) -> Starsigns:
        return Starsigns()
