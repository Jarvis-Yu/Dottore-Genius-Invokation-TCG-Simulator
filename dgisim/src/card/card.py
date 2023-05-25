from __future__ import annotations
from enum import Enum
from typing import TypeVar
from typing_extensions import override


import dgisim.src.state.game_state as gs
from dgisim.src.event.effect import *
import dgisim.src.action as ac


class Card:
    # def __eq__(self, other: object) -> bool:
    #     return isinstance(other, Card)

    # def __hash__(self) -> int:
    #     return hash(self.__class__.__name__)

    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[Effect, ...]:
        raise NotImplementedError

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
    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        es = (
            StuffedBuffEffect(
                instruction.target()
            ),
        )
        return es
    pass


class _DirectHealCard(FoodCard):
    @classmethod
    def heal_amount(cls) -> int:
        return 0

    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[Effect, ...]:
        es = super().effects(instruction)
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        es = (
            RecoverHPEffect(
                instruction.target(),
                cls.heal_amount()
            ),
        ) + es
        return es


class SweetMadame(_DirectHealCard):
    _name = "SweetMadame"

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1

    @staticmethod
    def name() -> str:
        return "SweetMadame"


class MondstadtHashBrown(FoodCard):
    @staticmethod
    def name() -> str:
        return "MondstadtHashBrown"


class JueyunGuoba(FoodCard):
    @staticmethod
    def name() -> str:
        return "JueyunGuoba"


class LotusFlowerCrisp(FoodCard):
    @staticmethod
    def name() -> str:
        return "LotusFlowerCrisp"


class MintyMeatRolls(FoodCard):
    @staticmethod
    def name() -> str:
        return "MintyMeatRolls"


class MushroomPizza(FoodCard):
    @staticmethod
    def name() -> str:
        return "MushroomPizza"


class NorthernSmokedChicken(FoodCard):
    @staticmethod
    def name() -> str:
        return "NorthernSmokedChicken"


class Starsigns(EventCard):
    @staticmethod
    def name() -> str:
        return "Starsigns"
