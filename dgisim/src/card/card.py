from __future__ import annotations
from enum import Enum
from typing import TypeVar
from typing_extensions import override


import dgisim.src.state.game_state as gs
import dgisim.src.effect.effect as eft
import dgisim.src.action as ac
import dgisim.src.status.status as stt
import dgisim.src.character.character as chr
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.dices import AbstractDices
from dgisim.src.element.element import Element
from dgisim.src.helper.quality_of_life import BIG_INT


class Card:
    _DICE_COST = AbstractDices({Element.OMNI: BIG_INT})

    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        raise NotImplementedError

    @classmethod
    def base_dice_cost(cls) -> AbstractDices:
        return cls._DICE_COST

    @classmethod
    def preprocessed_dice_cost(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> AbstractDices:
        # TODO: do the actual preprocessing
        return cls._DICE_COST

    # TODO add a post effect adding inform() to all status

    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """ checks if card can be used (but neglect if player have enough dices for this) """
        return True

    @classmethod
    def strictly_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """ checks if card can be used """
        dices_satisfy = game_state.get_player(pid).get_dices().loosely_satisfy(
            cls.preprocessed_dice_cost(game_state, pid)
        )
        return dices_satisfy and cls.usable(game_state, pid)

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other)

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


def _active_combat_talent_skill_card_usable(
        game_state: gs.GameState,
        pid: gs.GameState.Pid,
        char: type[chr.Character]
):
    ac = game_state.get_player(pid).get_active_character()
    if ac is None:
        return False
    if type(ac) is not char or not ac.can_cast_skill():
        return False
    return True


def _active_combat_talent_burst_card_usable(
        game_state: gs.GameState,
        pid: gs.GameState.Pid,
        char: type[chr.Character]
):
    ac = game_state.get_player(pid).get_active_character()
    if ac is None:
        return False
    return _active_combat_talent_skill_card_usable(game_state, pid, char) \
        and ac.get_energy() == ac.get_max_energy()


class FoodCard(EventCard):
    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        ac = game_state.get_player(pid).get_active_character()
        if ac is None or ac.satiated():
            return False
        return super().usable(game_state, pid)

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
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1


class MondstadtHashBrown(_DirectHealCard):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 2


class JueyunGuoba(FoodCard):
    _DICE_COST = AbstractDices({})

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
    _DICE_COST = AbstractDices({Element.OMNI: 1})


class MintyMeatRolls(FoodCard):
    _DICE_COST = AbstractDices({Element.OMNI: 1})


class MushroomPizza(FoodCard):
    """
    Heal first then the status
    """

    _DICE_COST = AbstractDices({Element.OMNI: 1})

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
    _DICE_COST = AbstractDices({})


class Starsigns(EventCard):
    _DICE_COST = AbstractDices({Element.ANY: 2})

    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        ac = game_state.get_player(pid).get_active_character()
        if ac is None or ac.get_energy() >= ac.get_max_energy():
            return False
        return super().usable(game_state, pid)

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
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        ac = game_state.get_player(pid).get_active_character()
        cs = game_state.get_player(pid).get_characters()
        if ac is None or ac.get_energy() >= ac.get_max_energy():
            return False
        has_teammate_with_energy = any(
            char
            for char in cs.get_none_active_characters()
            if char.get_energy() > 0
        )
        if not has_teammate_with_energy:
            return False
        return super().usable(game_state, pid)

# TODO: change to the correct parent class

#### Keqing ####


class LightningStiletto(EventCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})

    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        from dgisim.src.character.character import Keqing
        cs = game_state.get_player(pid).get_characters()
        keqing = next((c for c in cs if type(c) == Keqing), None)
        if keqing is None:
            return False
        if not keqing.can_cast_skill():
            return False
        return super().usable(game_state, pid)

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
                skill=CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )


class ThunderingPenance(EquipmentCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})

    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        return _active_combat_talent_skill_card_usable(game_state, pid, chr.Keqing) \
            and super().usable(game_state, pid)

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
                skill=CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )

#### Kaeya ####


class ColdBloodedStrike(EquipmentCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.CRYO: 4})

    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        return _active_combat_talent_skill_card_usable(game_state, pid, chr.Kaeya) \
            and super().usable(game_state, pid)

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
                skill=CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )


#### Rhodeia of Loch ####

class StreamingSurge(EquipmentCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.HYDRO: 4})

    @override
    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        return _active_combat_talent_burst_card_usable(game_state, pid, chr.RhodeiaOfLoch) \
            and super().usable(game_state, pid)

    @override
    @classmethod
    def effects(cls, instruction: ac.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, ac.CharacterTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=stt.StreamingSurgeStatus,
            ),
            eft.CastSkillEffect(
                target=instruction.target,
                skill=CharacterSkill.ELEMENTAL_BURST,
            ),
        )
