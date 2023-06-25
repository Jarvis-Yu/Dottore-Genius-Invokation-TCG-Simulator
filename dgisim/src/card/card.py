from __future__ import annotations
from typing_extensions import override

import dgisim.src.state.game_state as gs
import dgisim.src.effect.effect as eft
import dgisim.src.action as act
import dgisim.src.status.status as stt
import dgisim.src.character.character as chr
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.dices import AbstractDices
from dgisim.src.element.element import Element
from dgisim.src.helper.quality_of_life import BIG_INT
from dgisim.src.event.event import CardEvent
from dgisim.src.status.status_processing import StatusProcessing


class Card:
    _DICE_COST = AbstractDices({Element.OMNI: BIG_INT})

    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        raise NotImplementedError

    @classmethod
    def base_dice_cost(cls) -> AbstractDices:
        return cls._DICE_COST

    @classmethod
    def preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid
    ) -> tuple[gs.GameState, AbstractDices]:
        """
        Return a tuple of GameState and AbstractDices:
        - returned game-state is the game-state after preprocessing the usage of the card
        - returned abstract-dices are the actual cost of using the card at the provided game_state
        """
        game_state, card_event = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            item=CardEvent(
                card_type=cls,
                dices_cost=cls._DICE_COST,
            ),
            pp_type=stt.Status.PPType.CARD
        )
        assert isinstance(card_event, CardEvent)
        return game_state, card_event.dices_cost

    @classmethod
    def just_preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid
    ) -> AbstractDices:
        return cls.preprocessed_dice_cost(game_state, pid)[1]

    # TODO add a post effect adding inform() to all status

    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """ doesn't check if player has the card in hand """
        return game_state.get_active_player_id() is pid

    @classmethod
    def loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """
        doesn't check if player has the card in hand

        don't override this unless you know what you are doing
        """
        return cls._loosely_usable(game_state, pid)

    @classmethod
    def usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """
        checks if card can be used (but neglect if player have enough dices for this)

        don't override this unless you know what you are doing
        """
        return game_state.get_player(pid).get_hand_cards().contains(cls) \
            and cls.loosely_usable(game_state, pid)

    @classmethod
    def strictly_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """
        checks if card can be used

        don't override this unless you know what you are doing
        """
        dices_satisfy = game_state.get_player(pid).get_dices().loosely_satisfy(
            cls.just_preprocessed_dice_cost(game_state, pid)
        )
        return dices_satisfy and cls.usable(game_state, pid)

    @classmethod
    def valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> None | gs.GameState:
        """ Return the preprocessed game-state if instruction is valid, otherwise return None """
        if not game_state.get_player(pid).get_hand_cards().contains(cls) \
                or not game_state.get_active_player_id() is pid \
                or not cls._valid_instruction(game_state, pid, instruction):
            return None
        game_state, dices_cost = cls.preprocessed_dice_cost(game_state, pid)
        if instruction.dices.just_satisfy(dices_cost):
            return game_state
        else:
            return None

    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return True

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


class _UsableFuncs:
    @staticmethod
    def active_combat_talent_skill_card_usable(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            char: type[chr.Character]
    ):
        """ Check if active character is the character type and can cast skill """
        ac = game_state.get_player(pid).get_active_character()
        if ac is None:
            return False
        if type(ac) is not char or not ac.can_cast_skill():
            return False
        return True

    @staticmethod
    def active_combat_talent_burst_card_usable(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            char: type[chr.Character]
    ):
        """
        Check if active character is the character type, can cast skill and have
        enough energy
        """
        active_character = game_state.get_player(pid).get_active_character()
        if active_character is None:
            return False
        return _UsableFuncs.active_combat_talent_skill_card_usable(game_state, pid, char) \
            and active_character.get_energy() == active_character.get_max_energy()


class _ValidInstructionFuncs:
    @staticmethod
    def target_is_active_character(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.CharacterTargetInstruction,
    ) -> bool:
        return instruction.target.pid == pid \
            and instruction.target.zone is eft.Zone.CHARACTER \
            and instruction.target.id == game_state.get_player(pid).get_characters().get_active_character_id()


class OmniCard(Card):
    """ the card used to hide opponent's cards """
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
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        characters = game_state.get_player(pid).get_characters()
        if all(char.satiated() for char in characters):
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        """ This only applies to food with a single target, override if needed """
        if not isinstance(instruction, act.CharacterTargetInstruction):
            return False

        target = game_state.get_target(instruction.target)
        return isinstance(target, chr.Character) and not target.satiated()

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
        return cls.food_effects(instruction) + (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.SatiatedStatus,
            ),
        )

    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
        return ()


class _DirectHealCard(FoodCard):
    @classmethod
    def heal_amount(cls) -> int:
        return 0

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
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
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
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
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
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

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.NorthernSmokedChickenStatus,
            ),
        )


class Starsigns(EventCard):
    _DICE_COST = AbstractDices({Element.ANY: 2})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """ Check active character doesn't have full energy """
        active_character = game_state.get_player(pid).get_active_character()
        if active_character is None or active_character.get_energy() >= active_character.get_max_energy():
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        """ Check target is active character and .loosely_usable() """
        if not isinstance(instruction, act.DiceOnlyInstruction):
            return False

        return cls.loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyRechargeEffect(
                eft.StaticTarget(
                    pid=pid,
                    zone=eft.Zone.CHARACTER,
                    id=game_state.get_player(pid).just_get_active_character().get_id(),
                ),
                1
            ),
        )


class CalxsArts(EventCard):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        """ Check active character doesn't have full energy and teammates have energy """
        ac = game_state.get_player(pid).get_active_character()
        cs = game_state.get_player(pid).get_characters()
        if ac is None or ac.get_energy() >= ac.get_max_energy():
            return False
        has_teammate_with_energy = any(
            char.get_energy() > 0
            for char in cs.get_none_active_characters()
        )
        if not has_teammate_with_energy:
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls.loosely_usable(game_state, pid)


class ChangingShifts(EventCard):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction)

    
    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.ChangingShiftsStatus,
            ),
        )


class LeaveItToMe(EventCard):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.LeaveItToMeStatus,
            ),
        )

# TODO: change to the correct parent class

#### Keqing ####


class LightningStiletto(EventCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        cs = game_state.get_player(pid).get_characters()
        keqings = [char for char in cs if type(char) is chr.Keqing]
        if not keqings:
            return False
        if all(not keqing.can_cast_skill() for keqing in keqings):
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        if not isinstance(instruction, act.CharacterTargetInstruction):
            return False
        target = game_state.get_target(instruction.target)
        return isinstance(target, chr.Keqing) and target.can_cast_skill()

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.CharacterTargetInstruction)
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
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        return _UsableFuncs.active_combat_talent_skill_card_usable(game_state, pid, chr.Keqing) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = eft.StaticTarget(
            pid=pid,
            zone=eft.Zone.CHARACTER,
            id=game_state.get_player(pid).just_get_active_character().get_id(),
        )
        return (
            eft.AddCharacterStatusEffect(
                target=target,
                status=stt.ThunderingPenanceStatus,
            ),
            eft.CastSkillEffect(
                target=target,
                skill=CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )

#### Kaeya ####


class ColdBloodedStrike(EquipmentCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.CRYO: 4})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        return _UsableFuncs.active_combat_talent_skill_card_usable(game_state, pid, chr.Kaeya) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = eft.StaticTarget(
            pid=pid,
            zone=eft.Zone.CHARACTER,
            id=game_state.get_player(pid).just_get_active_character().get_id(),
        )
        return (
            eft.AddCharacterStatusEffect(
                target=target,
                status=stt.ColdBloodedStrikeStatus,
            ),
            eft.CastSkillEffect(
                target=target,
                skill=CharacterSkill.ELEMENTAL_SKILL1,
            ),
        )


#### Rhodeia of Loch ####

class StreamingSurge(EquipmentCard, _CombatActionCard):
    _DICE_COST = AbstractDices({Element.HYDRO: 4})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: gs.GameState.Pid) -> bool:
        return _UsableFuncs.active_combat_talent_burst_card_usable(game_state, pid, chr.RhodeiaOfLoch) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = eft.StaticTarget(
            pid=pid,
            zone=eft.Zone.CHARACTER,
            id=game_state.get_player(pid).just_get_active_character().get_id(),
        )
        return (
            eft.AddCharacterStatusEffect(
                target=target,
                status=stt.StreamingSurgeStatus,
            ),
            eft.CastSkillEffect(
                target=target,
                skill=CharacterSkill.ELEMENTAL_BURST,
            ),
        )
