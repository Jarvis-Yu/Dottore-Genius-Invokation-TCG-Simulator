from __future__ import annotations
from enum import Enum
from typing_extensions import override

from dgisim.src.cost import Cost


class Card:
    cost: Cost

    def another(self) -> Card:
        raise Exception("Not implemented")

    # def __eq__(self, other: object) -> bool:
    #     return isinstance(other, Card)

    # def __hash__(self) -> int:
    #     return hash(self.__class__.__name__)

    def __str__(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def name() -> str:
        return "card"


# for test only
class OmniCard(Card):
    pass


class EventCard(Card):
    pass


class FoodCard(EventCard):
    pass


class SweetMadame(FoodCard):
    _name = "SweetMadame"

    def another(self) -> SweetMadame:
        return SweetMadame()

    @staticmethod
    def name() -> str:
        return "SweetMadame"


class MondstadtHashBrown(FoodCard):
    def another(self) -> MondstadtHashBrown:
        return MondstadtHashBrown()

    @staticmethod
    def name() -> str:
        return "MondstadtHashBrown"


class JueyunGuoba(FoodCard):
    def another(self) -> JueyunGuoba:
        return JueyunGuoba()

    @staticmethod
    def name() -> str:
        return "JueyunGuoba"


class LotusFlowerCrisp(FoodCard):
    def another(self) -> LotusFlowerCrisp:
        return LotusFlowerCrisp()

    @staticmethod
    def name() -> str:
        return "LotusFlowerCrisp"


class MintyMeatRolls(FoodCard):
    def another(self) -> MintyMeatRolls:
        return MintyMeatRolls()

    @staticmethod
    def name() -> str:
        return "MintyMeatRolls"


class MushroomPizza(FoodCard):
    def another(self) -> MushroomPizza:
        return MushroomPizza()

    @staticmethod
    def name() -> str:
        return "MushroomPizza"


class NorthernSmokedChicken(FoodCard):
    def another(self) -> NorthernSmokedChicken:
        return NorthernSmokedChicken()

    @staticmethod
    def name() -> str:
        return "NorthernSmokedChicken"


class Starsigns(EventCard):
    def another(self) -> Starsigns:
        return Starsigns()

    @staticmethod
    def name() -> str:
        return "Starsigns"
