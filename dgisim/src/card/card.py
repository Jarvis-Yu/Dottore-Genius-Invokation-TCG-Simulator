from __future__ import annotations
from enum import Enum
from typing import TypeVar
from typing_extensions import override
from dgisim.src.effect.effect import Effect


import dgisim.src.state.game_state as gs
from dgisim.src.effect.effect import *
import dgisim.src.action as ac
import dgisim.src.status.status as stt


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
        return cls.food_effects(instruction) + (
            AddStatusEffect(
                instruction.target(),
                stt.SatiatedStatus,
            ),
        )

    @classmethod
    def food_effects(cls, instruction: ac.Instruction) -> tuple[Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return ()


class _DirectHealCard(FoodCard):
    @classmethod
    def heal_amount(cls) -> int:
        return 0

    @override
    @classmethod
    def food_effects(cls, instruction: ac.Instruction) -> tuple[Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            RecoverHPEffect(
                instruction.target(),
                cls.heal_amount()
            ),
        )


class SweetMadame(_DirectHealCard):
    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1


class MondstadtHashBrown(_DirectHealCard):
    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 2


class JueyunGuoba(FoodCard):
    pass


class LotusFlowerCrisp(FoodCard):
    pass


class MintyMeatRolls(FoodCard):
    pass


class MushroomPizza(FoodCard):
    """
    Heal first then the status
    """
    @override
    @classmethod
    def food_effects(cls, instruction: ac.Instruction) -> tuple[Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            RecoverHPEffect(
                instruction.target(),
                1
            ),
            AddStatusEffect(
                instruction.target(),
                stt.MushroomPizzaStatus,
            )
        )


class NorthernSmokedChicken(FoodCard):
    pass


class Starsigns(EventCard):
    pass

# TODO: change to the correct parent class


class LightningStiletto(Card):
    pass
