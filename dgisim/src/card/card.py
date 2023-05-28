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

    @classmethod
    def name(cls) -> str:
        return cls.__name__


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
    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1


class MondstadtHashBrown(FoodCard):
    pass


class JueyunGuoba(FoodCard):
    pass


class LotusFlowerCrisp(FoodCard):
    pass


class MintyMeatRolls(FoodCard):
    pass


class MushroomPizza(FoodCard):
    pass


class NorthernSmokedChicken(FoodCard):
    pass


class Starsigns(EventCard):
    pass

# TODO: change to the correct parent class
class LightningStiletto(Card):
    pass
