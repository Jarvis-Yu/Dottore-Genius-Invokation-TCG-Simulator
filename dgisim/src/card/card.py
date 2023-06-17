from __future__ import annotations
from enum import Enum
from typing import TypeVar
from typing_extensions import override


import dgisim.src.state.game_state as gs
import dgisim.src.effect.effect as eft
import dgisim.src.action as ac
import dgisim.src.status.status as stt
import dgisim.src.character.character as chr


class Card:
    # def __eq__(self, other: object) -> bool:
    #     return isinstance(other, Card)

    # def __hash__(self) -> int:
    #     return hash(self.__class__.__name__)

    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def is_combat_action() -> bool:
        return False

    @classmethod
    def name(cls) -> str:
        return cls.__name__

# for test only


class OmniCard(Card):
    pass


class _CombatActionCard(Card):
    @override
    @staticmethod
    def is_combat_action() -> bool:
        return True


class EventCard(Card):
    pass


class EquipmentCard(Card):
    pass


class FoodCard(EventCard):
    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return cls.food_effects(instruction) + (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.SatiatedStatus,
            ),
        )

    @classmethod
    def food_effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return ()


class _DirectHealCard(FoodCard):
    @classmethod
    def heal_amount(cls) -> int:
        return 0

    @override
    @classmethod
    def food_effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.RecoverHPEffect(
                instruction.target,
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
    @override
    @classmethod
    def food_effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.JueyunGuobaStatus,
            ),
        )


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
    def food_effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.RecoverHPEffect(
                instruction.target,
                1
            ),
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.MushroomPizzaStatus,
            )
        )


class NorthernSmokedChicken(FoodCard):
    pass


class Starsigns(EventCard):
    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.EnergyRechargeEffect(
                instruction.target,
                1
            ),
        )


class CalxsArts(EventCard):
    pass

# TODO: change to the correct parent class

#### Keqing ####


class LightningStiletto(EventCard, _CombatActionCard):
    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.SwapCharacterEffect(
                target=instruction.target,
            ),
            eft.OverrideCharacterStatusEffect(
                target=instruction.target,
                status=stt.KeqingTalentStatus(can_infuse=True),
            ),
            eft.CastSkillEffect(
                target=instruction.target,
                skill=chr.CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )


class ThunderingPenance(EquipmentCard, _CombatActionCard):
    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=stt.ThunderingPenanceStatus,
            ),
            eft.CastSkillEffect(
                target=instruction.target,
                skill=chr.CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )

#### Kaeya ####


class ColdBloodedStrike(EquipmentCard, _CombatActionCard):
    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=stt.ColdBloodedStrikeStatus,
            ),
            eft.CastSkillEffect(
                target=instruction.target,
                skill=chr.CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )
