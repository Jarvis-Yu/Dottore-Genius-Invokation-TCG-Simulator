from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import replace
from typing_extensions import override

from ..action import action as act
from ..action import action_generator as acg
from ..character import character as chr
from ..effect import effect as eft
from ..status import status as stt
from ..support import support as sp

from ..character.character_skill_enum import CharacterSkill
from ..dices import AbstractDices, ActualDices
from ..effect.enums import ZONE
from ..effect.structs import StaticTarget
from ..element.element import Element
from ..event.event import CardEvent
from ..helper.quality_of_life import BIG_INT
from ..state.enums import PID
from ..status.enums import PREPROCESSABLES
from ..status.status_processing import StatusProcessing

if TYPE_CHECKING:
    from ..state import game_state as gs

    from ..action.types import DecidedChoiceType, GivenChoiceType


class Card:
    _DICE_COST = AbstractDices({Element.OMNI: BIG_INT})

    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
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
            pid: PID
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
                pid=pid,
                card_type=cls,
                dices_cost=cls._DICE_COST,
            ),
            pp_type=PREPROCESSABLES.CARD
        )
        assert isinstance(card_event, CardEvent)
        return game_state, card_event.dices_cost

    @classmethod
    def just_preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: PID
    ) -> AbstractDices:
        return cls.preprocessed_dice_cost(game_state, pid)[1]

    # TODO add a post effect adding inform() to all status

    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        """ doesn't check if player has the card in hand """
        return game_state.get_active_player_id() is pid

    @classmethod
    def loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        """
        doesn't check if player has the card in hand

        don't override this unless you know what you are doing
        """
        return cls._loosely_usable(game_state, pid) and game_state.get_effect_stack().is_empty()

    @classmethod
    def usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        """
        checks if card can be used (but neglect if player have enough dices for this)

        don't override this unless you know what you are doing
        """
        return game_state.get_player(pid).get_hand_cards().contains(cls) \
            and cls.loosely_usable(game_state, pid)

    @classmethod
    def strictly_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
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
            pid: PID,
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
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return True

    @classmethod
    def action_generator(
            cls,
            game_state: gs.GameState,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        return None

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
            pid: PID,
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
            pid: PID,
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
            pid: PID,
            instruction: act.StaticTargetInstruction,
    ) -> bool:
        return instruction.target.pid == pid \
            and instruction.target.zone is ZONE.CHARACTERS \
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


class SupportCard(Card):
    # TODO: The effects are currently not handling support zone overflow

    @override
    @classmethod
    def valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> None | gs.GameState:
        supports = game_state.get_player(pid).get_supports()
        if supports.is_full():
            if not isinstance(instruction, act.StaticTargetInstruction):
                return None
            target = game_state.get_target(instruction.target)
            if target is None or not isinstance(target, sp.Support):
                return None
        else:
            if not isinstance(instruction, act.DiceOnlyInstruction):
                return None
        return super().valid_instruction(game_state, pid, instruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        es: list[eft.Effect] = []
        if type(instruction) is act.StaticTargetInstruction:
            es.append(eft.RemoveSupportEffect(
                target_pid=pid,
                sid=instruction.target.id,
            ))
        return tuple(es) + cls._effects(game_state, pid)

    @classmethod
    def _effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
    ) -> tuple[eft.Effect, ...]:
        raise

    @classmethod
    def _choices_helper(
            cls,
            action_generator: acg.ActionGenerator,
    ) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid

        assert action_generator._action_filled()
        instruction = action_generator.instruction
        if type(instruction) is act.StaticTargetInstruction \
                and instruction.target is None:
            supports = game_state.get_player(pid).get_supports()
            return tuple(
                StaticTarget(
                    pid=pid,
                    zone=ZONE.SUPPORTS,
                    id=support.sid,
                )
                for support in supports
            )

        # only dices unfilled here
        assert type(instruction) is act.DiceOnlyInstruction \
            or type(instruction) is act.StaticTargetInstruction
        if instruction.dices is None:
            return cls.preprocessed_dice_cost(game_state, pid)[1]

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        assert action_generator._action_filled()

        instruction = action_generator.instruction

        if type(instruction) is act.StaticTargetInstruction \
                and instruction.target is None:
            assert isinstance(player_choice, StaticTarget)
            return replace(
                action_generator,
                instruction=replace(instruction, target=player_choice),
            )

        assert type(instruction) is act.DiceOnlyInstruction \
            or type(instruction) is act.StaticTargetInstruction
        if instruction.dices is None:
            assert isinstance(player_choice, ActualDices)
            return replace(
                action_generator,
                instruction=replace(instruction, dices=player_choice),
            )

        raise Exception("Not Reached!")

    @override
    @classmethod
    def action_generator(
            cls,
            game_state: gs.GameState,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        if not cls.strictly_usable(game_state, pid):
            return None
        if game_state.get_player(pid).get_supports().is_full():
            return acg.ActionGenerator(
                game_state=game_state,
                pid=pid,
                action=replace(act.CardAction._all_none(), card=cls),
                instruction=act.StaticTargetInstruction._all_none(),
                _choices_helper=cls._choices_helper,
                _fill_helper=cls._fill_helper,
            )
        else:
            return acg.ActionGenerator(
                game_state=game_state,
                pid=pid,
                action=replace(act.CardAction._all_none(), card=cls),
                instruction=act.DiceOnlyInstruction._all_none(),
                _choices_helper=cls._choices_helper,
                _fill_helper=cls._fill_helper,
            )


class CompanionCard(SupportCard):
    pass


class LocationCard(SupportCard):
    pass


# <<<<<<<<<<<<<<<<<<<< Helpers <<<<<<<<<<<<<<<<<<<<
class _DiceOnlyChoiceProvider(Card):
    @classmethod
    def _choices_helper(
            cls,
            action_generator: acg.ActionGenerator,
    ) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid

        assert action_generator._action_filled()

        instruction = action_generator.instruction
        assert type(instruction) is act.DiceOnlyInstruction
        if instruction.dices is None:
            return cls.preprocessed_dice_cost(game_state, pid)[1]

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        assert action_generator._action_filled()

        instruction = action_generator.instruction
        assert type(instruction) is act.DiceOnlyInstruction
        if instruction.dices is None:
            assert isinstance(player_choice, ActualDices)
            return replace(
                action_generator,
                instruction=replace(instruction, dices=player_choice),
            )

        raise Exception("Not Reached!")

    @override
    @classmethod
    def action_generator(
            cls,
            game_state: gs.GameState,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        if not cls.strictly_usable(game_state, pid):
            return None
        return acg.ActionGenerator(
            game_state=game_state,
            pid=pid,
            action=replace(act.CardAction._all_none(), card=cls),
            instruction=act.DiceOnlyInstruction._all_none(),
            _choices_helper=cls._choices_helper,
            _fill_helper=cls._fill_helper,
        )


class _CharTargetChoiceProvider(Card):
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return not char.defeated()

    @classmethod
    def _choices_helper(
            cls,
            action_generator: acg.ActionGenerator,
    ) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid

        assert action_generator._action_filled()

        instruction = action_generator.instruction
        assert type(instruction) is act.StaticTargetInstruction
        if instruction.target is None:
            chars = game_state.get_player(pid).get_characters()
            chars = [char for char in chars if cls._valid_char(char)]
            return tuple(
                StaticTarget(
                    pid=pid,
                    zone=ZONE.CHARACTERS,
                    id=char.get_id(),
                )
                for char in chars
            )

        elif instruction.dices is None:
            return cls.preprocessed_dice_cost(game_state, pid)[1]

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        assert action_generator._action_filled()

        instruction = action_generator.instruction
        assert isinstance(instruction, act.StaticTargetInstruction)
        if instruction.target is None:
            assert isinstance(player_choice, StaticTarget)
            return replace(
                action_generator,
                instruction=replace(instruction, target=player_choice),
            )

        elif instruction.dices is None:
            assert isinstance(player_choice, ActualDices)
            return replace(
                action_generator,
                instruction=replace(instruction, dices=player_choice),
            )

        raise Exception("Not Reached!")

    @override
    @classmethod
    def action_generator(
            cls,
            game_state: gs.GameState,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        if not cls.strictly_usable(game_state, pid):
            return None
        return acg.ActionGenerator(
            game_state=game_state,
            pid=pid,
            action=replace(act.CardAction._all_none(), card=cls),
            instruction=act.StaticTargetInstruction._all_none(),
            _choices_helper=cls._choices_helper,
            _fill_helper=cls._fill_helper,
        )
# >>>>>>>>>>>>>>>>>>>> Helpers >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Event Cards <<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<< Event Cards / Food Cards <<<<<<<<<<<<<<<<<<<<


class FoodCard(EventCard):
    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        characters = game_state.get_player(pid).get_characters()
        if all(not cls._valid_char(char) for char in characters):
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        """ This only applies to food with a single target, override if needed """
        if not isinstance(instruction, act.StaticTargetInstruction):
            return False

        target = game_state.get_target(instruction.target)
        return isinstance(target, chr.Character) and not target.satiated()

    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return not char.satiated() and not char.defeated()

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return cls.food_effects(instruction) + (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.SatiatedStatus,
            ),
        )

    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return ()


class _DirectHealCard(FoodCard):
    @classmethod
    def heal_amount(cls) -> int:
        return 0

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.RecoverHPEffect(
                instruction.target,
                cls.heal_amount()
            ),
        )

    @override
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return char.get_hp() < char.get_max_hp() \
            and super()._valid_char(char)


class SweetMadame(_DirectHealCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1


class MondstadtHashBrown(_DirectHealCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 2


class JueyunGuoba(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.JueyunGuobaStatus,
            ),
        )


class LotusFlowerCrisp(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=stt.LotusFlowerCrispStatus,
            ),
        )


class MintyMeatRolls(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=stt.MintyMeatRollsStatus,
            ),
        )


class MushroomPizza(FoodCard, _CharTargetChoiceProvider):
    """
    Heal first then the status
    """

    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
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

    @override
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return _DirectHealCard._valid_char(char)


class NorthernSmokedChicken(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.NorthernSmokedChickenStatus,
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Event Cards / Food Cards >>>>>>>>>>>>>>>>>>>>


class Starsigns(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.ANY: 2})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
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
            pid: PID,
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
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyRechargeEffect(
                StaticTarget(
                    pid=pid,
                    zone=ZONE.CHARACTERS,
                    id=game_state.get_player(pid).just_get_active_character().get_id(),
                ),
                1
            ),
        )


class CalxsArts(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
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
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls.loosely_usable(game_state, pid)


class ChangingShifts(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.ChangingShiftsStatus,
            ),
        )


class LeaveItToMe(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.LeaveItToMeStatus,
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Event Cards >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Support Cards <<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<< Support Cards / Companion Cards <<<<<<<<<<<<<<<<<<<<


class Xudong(CompanionCard):
    _DICE_COST = AbstractDices({Element.ANY: 2})

    @override
    @classmethod
    def _effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddSupportEffect(
                target_pid=pid,
                support=sp.XudongSupport,
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Support Cards / Companion Cards >>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>> Support Cards >>>>>>>>>>>>>>>>>>>>

#### Keqing ####


class LightningStiletto(EventCard, _CombatActionCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})

    @override
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return isinstance(char, chr.Keqing) \
            and super()._valid_char(char)

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
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
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        if not isinstance(instruction, act.StaticTargetInstruction):
            return False
        target = game_state.get_target(instruction.target)
        return isinstance(target, chr.Keqing) and target.can_cast_skill()

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
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


class ThunderingPenance(EquipmentCard, _CombatActionCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        return _UsableFuncs.active_combat_talent_skill_card_usable(game_state, pid, chr.Keqing) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = StaticTarget(
            pid=pid,
            zone=ZONE.CHARACTERS,
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


class ColdBloodedStrike(EquipmentCard, _CombatActionCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.CRYO: 4})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        return _UsableFuncs.active_combat_talent_skill_card_usable(game_state, pid, chr.Kaeya) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = StaticTarget(
            pid=pid,
            zone=ZONE.CHARACTERS,
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

class StreamingSurge(EquipmentCard, _CombatActionCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.HYDRO: 4})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: PID) -> bool:
        return _UsableFuncs.active_combat_talent_burst_card_usable(game_state, pid, chr.RhodeiaOfLoch) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: PID,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = StaticTarget(
            pid=pid,
            zone=ZONE.CHARACTERS,
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


########### type ##########
