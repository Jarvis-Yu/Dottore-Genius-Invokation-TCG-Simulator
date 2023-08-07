"""
This file contains the base class "Card" for all cards,
and implementation of all cards.

The classes are divided into 4 sections ordered. Within each section, they are
ordered alphabetically.

- base class, which is Card
- type classes, used to identify what type of card a card is
- template classes, starting with an '_', are templates for other classes
- concrete classes, the implementation of cards that are actually in the game
"""
from __future__ import annotations
from typing import cast, TYPE_CHECKING
from dataclasses import replace
from typing_extensions import override

from ..action import action as act
from ..action import action_generator as acg
from ..character import character as chr
from ..effect import effect as eft
from ..status import status as stt
from ..summon import summon as sm
from ..support import support as sp

from ..character.enums import CharacterSkill, WeaponType
from ..dices import AbstractDices, ActualDices
from ..effect.enums import Zone
from ..effect.structs import StaticTarget
from ..element import Element
from ..event import CardPEvent
from ..helper.quality_of_life import BIG_INT
from ..state.enums import Pid
from ..status.enums import Preprocessables
from ..status.status_processing import StatusProcessing

if TYPE_CHECKING:
    from ..action.types import DecidedChoiceType, GivenChoiceType
    from ..deck import Deck
    from ..state import game_state as gs

__all__ = [
    # base
    "Card",

    # special one
    "OmniCard",

    # type
    "EventCard",
    "EquipmentCard",
    "TalentCard",
    "TalentEventCard",
    "TalentEquipmentCard",
    "WeaponEquipmentCard",
    "ArtifactEquipmentCard",
    "SupportCard",
    "CompanionCard",
    "LocationCard",
    "FoodCard",

    # Weapon Card
    ## Bow ##
    "RavenBow",
    ## Catalyst ##
    "MagicGuide",
    ## Claymore ##
    "WhiteIronGreatsword",
    ## Polearm ##
    "WhiteTassel",
    ## Sword ##
    "TravelersHandySword",

    # Artifact Card
    "GamblersEarrings",

    # Event Card
    ## Food Card ##
    "JueyunGuoba",
    "LotusFlowerCrisp",
    "MintyMeatRolls",
    "MondstadtHashBrown",
    "MushroomPizza",
    "NorthernSmokedChicken",
    "SweetMadame",
    "TeyvatFriedEgg",
    ## Other ##
    "CalxsArts",
    "ChangingShifts",
    "IHaventLostYet",
    "LeaveItToMe",
    "QuickKnit",
    "Starsigns",

    # Support Card
    ## Companion ##
    "Xudong",
    ## Location ##
    "KnightsOfFavoniusLibrary",
    "Vanarana",

    # Character Specific
    ## Arataki Itto ##
    "AratakiIchiban",
    ## Electro Hypostasis ##
    "AbsorbingPrism",
    ## Kaedehara Kazuha ##
    "PoeticsOfFuubutsu",
    ## Kaeya ##
    "ColdBloodedStrike",
    ## Keqing ##
    "LightningStiletto",
    "ThunderingPenance",
    ## Klee ##
    "PoundingSurprise",
    ## Mona ##
    "ProphecyOfSubmersion",
    ## Rhodeia of Loch ##
    "StreamingSurge",
    ## Tighnari ##
    "KeenSight",
    ## Xingqiu ##
    "TheScentRemained",
]

############################## base ##############################


class Card:
    _DICE_COST = AbstractDices({Element.OMNI: BIG_INT})

    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        raise NotImplementedError

    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return True

    @classmethod
    def base_dice_cost(cls) -> AbstractDices:  # pragma: no cover
        return cls._DICE_COST

    @classmethod
    def preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: Pid
    ) -> tuple[gs.GameState, AbstractDices]:
        """
        Return a tuple of GameState and AbstractDices:
        - returned game-state is the game-state after preprocessing the usage of the card
        - returned abstract-dices are the actual cost of using the card at the provided game_state
        """
        game_state, card_event = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            pp_type=Preprocessables.CARD,
            item=CardPEvent(
                pid=pid,
                card_type=cls,
                dices_cost=cls._DICE_COST,
            ),
        )
        assert isinstance(card_event, CardPEvent)
        return game_state, card_event.dices_cost

    @classmethod
    def just_preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: Pid
    ) -> AbstractDices:
        return cls.preprocessed_dice_cost(game_state, pid)[1]

    # TODO add a post effect adding inform() to all status

    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """ doesn't check if player has the card in hand """
        return game_state.get_active_player_id() is pid

    @classmethod
    def loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """
        doesn't check if player has the card in hand

        don't override this unless you know what you are doing
        """
        return cls._loosely_usable(game_state, pid) and game_state.get_effect_stack().is_empty()

    @classmethod
    def usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """
        checks if card can be used (but neglect if player have enough dices for this)

        don't override this unless you know what you are doing
        """
        return game_state.get_player(pid).get_hand_cards().contains(cls) \
            and cls.loosely_usable(game_state, pid)

    @classmethod
    def strictly_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
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
            pid: Pid,
            instruction: act.Instruction
    ) -> None | gs.GameState:
        """ Return the preprocessed game-state if instruction is valid, otherwise return None """
        if not game_state.get_player(pid).get_hand_cards().contains(cls) \
                or not game_state.get_active_player_id() is pid \
                or not cls._valid_instruction(game_state, pid, instruction) \
                or not (game_state.get_player(pid).get_dices() - instruction.dices).is_legal():
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
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        return True

    @classmethod
    def action_generator(
            cls,
            game_state: gs.GameState,
            pid: Pid,
    ) -> None | acg.ActionGenerator:
        return None  # pragma: no cover

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return type(self) == type(other)

    def __repr__(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def is_combat_action() -> bool:
        return False

    @classmethod
    def name(cls) -> str:
        return cls.__name__

############################## helpers functions ##############################


class _UsableFuncs:
    @staticmethod
    def active_combat_talent_card_usable(
            game_state: gs.GameState,
            pid: Pid,
            char: type[chr.Character]
    ):
        """ Check if active character is the character type """
        ac = game_state.get_player(pid).get_active_character()
        if ac is None:  # pragma: no cover
            return False
        return type(ac) is char

    @staticmethod
    def active_combat_talent_skill_card_usable(
            game_state: gs.GameState,
            pid: Pid,
            char: type[chr.Character]
    ):
        """ Check if active character is the character type and can cast skill """
        ac = game_state.get_player(pid).get_active_character()
        if ac is None:  # pragma: no cover
            return False
        if type(ac) is not char or not ac.can_cast_skill():
            return False
        return True

    @staticmethod
    def active_combat_talent_burst_card_usable(
            game_state: gs.GameState,
            pid: Pid,
            char: type[chr.Character]
    ):
        """
        Check if active character is the character type, can cast skill and have
        enough energy
        """
        active_character = game_state.get_player(pid).get_active_character()
        if active_character is None:  # pragma: no cover
            return False
        return _UsableFuncs.active_combat_talent_skill_card_usable(game_state, pid, char) \
            and active_character.get_energy() == active_character.get_max_energy()


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

        raise Exception("Not Reached!"
                        + "Should be called when there is something to fill. action_generator:\n"
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
            pid: Pid,
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
    def _valid_char(cls, char: chr.Character) -> bool:  # pragma: no cover
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
                    zone=Zone.CHARACTERS,
                    id=char.get_id(),
                )
                for char in chars
            )

        elif instruction.dices is None:
            return cls.preprocessed_dice_cost(game_state, pid)[1]

        raise Exception("Not Reached!"
                        + "Should be called when there is something to fill. action_generator:\n"
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
            assert player_choice.zone is Zone.CHARACTERS
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
            pid: Pid,
    ) -> None | acg.ActionGenerator:
        if not cls.strictly_usable(game_state, pid):  # pragma: no cover
            return None
        return acg.ActionGenerator(
            game_state=game_state,
            pid=pid,
            action=replace(act.CardAction._all_none(), card=cls),
            instruction=act.StaticTargetInstruction._all_none(),
            _choices_helper=cls._choices_helper,
            _fill_helper=cls._fill_helper,
        )


class _SummonTargetChoiceProvider(Card):
    """
    If _MY_SIDE is set to true, then all summons on my side can be chosen
    If _OPPO_SIDE is set to true, then all summons on the opponent's side can be chosen
    """
    _MY_SIDE: bool = False
    _OPPO_SIDE: bool = False

    @classmethod
    def _valid_summon(cls, summon: sm.Summon) -> bool:  # pragma: no cover
        return True

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
            pids = []
            if cls._MY_SIDE:
                pids.append(pid)
            if cls._OPPO_SIDE:
                pids.append(pid.other())
            choices = []
            for this_pid in pids:
                summons = game_state.get_player(this_pid).get_summons()
                choices += [
                    StaticTarget(
                        pid=this_pid,
                        zone=Zone.SUMMONS,
                        id=type(summon),
                    )
                    for summon in summons
                    if cls._valid_summon(summon)
                ]
            return tuple(choices)

        elif instruction.dices is None:
            return cls.preprocessed_dice_cost(game_state, pid)[1]

        raise Exception("Not Reached!"
                        + "Should be called when there is something to fill. action_generator:\n"
                        + f"{action_generator}"
                        )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        instruction = action_generator.instruction
        assert isinstance(instruction, act.StaticTargetInstruction)
        if instruction.target is None:
            assert isinstance(player_choice, StaticTarget)
            assert player_choice.zone is Zone.SUMMONS
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
            pid: Pid,
    ) -> None | acg.ActionGenerator:
        if not cls.strictly_usable(game_state, pid):  # pragma: no cover
            return None
        return acg.ActionGenerator(
            game_state=game_state,
            pid=pid,
            action=replace(act.CardAction._all_none(), card=cls),
            instruction=act.StaticTargetInstruction._all_none(),
            _choices_helper=cls._choices_helper,
            _fill_helper=cls._fill_helper,
        )

############################## special card ##############################


class OmniCard(Card):
    """ the card used to hide opponent's cards """
    pass


############################## type card ##############################
class _CombatActionCard(Card):
    @override
    @staticmethod
    def is_combat_action() -> bool:
        return True


class EventCard(Card):
    pass


class EquipmentCard(Card):
    pass


class TalentCard(Card):
    _CHARACTER: type[chr.Character]

    @override
    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return cls._CHARACTER in deck.chars


class TalentEventCard(EventCard, TalentCard):
    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        ret_val = True
        if issubclass(cls, _CombatActionCard):
            ret_val = (
                ret_val
                and _UsableFuncs.active_combat_talent_card_usable(
                    game_state, pid, cls._CHARACTER
                )
            )
        return ret_val and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        ret_val = True
        if issubclass(cls, _DiceOnlyChoiceProvider):
            ret_val = ret_val and isinstance(instruction, act.DiceOnlyInstruction)
        return ret_val and cls._loosely_usable(game_state, pid)


class TalentEquipmentCard(EquipmentCard, TalentCard):
    _IS_SKILL: bool = True
    _SKILL: CharacterSkill

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        ret_val = True
        if issubclass(cls, _CombatActionCard) and cls._IS_SKILL:
            if cls._SKILL in {
                    CharacterSkill.NORMAL_ATTACK,
                    CharacterSkill.ELEMENTAL_SKILL1,
                    CharacterSkill.ELEMENTAL_SKILL2,
            }:
                ret_val = (
                    ret_val
                    and _UsableFuncs.active_combat_talent_skill_card_usable(
                        game_state, pid, cls._CHARACTER
                    )
                )
            elif cls._SKILL is CharacterSkill.ELEMENTAL_BURST:
                ret_val = (
                    ret_val
                    and _UsableFuncs.active_combat_talent_burst_card_usable(
                        game_state, pid, cls._CHARACTER
                    )
                )
        return ret_val and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        ret_val = True
        if issubclass(cls, _DiceOnlyChoiceProvider):
            ret_val = ret_val and isinstance(instruction, act.DiceOnlyInstruction)
        return ret_val and cls._loosely_usable(game_state, pid)


class _TalentEquipmentSkillCard(TalentEquipmentCard, _CombatActionCard, _DiceOnlyChoiceProvider):
    _EQUIPMENT_STATUS: type[stt.EquipmentStatus]

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = StaticTarget(
            pid=pid,
            zone=Zone.CHARACTERS,
            id=game_state.get_player(pid).just_get_active_character().get_id(),
        )
        return (
            eft.AddCharacterStatusEffect(
                target=target,
                status=cls._EQUIPMENT_STATUS,
            ),
            eft.CastSkillEffect(
                target=target,
                skill=cls._SKILL,
            ),
        )


class WeaponEquipmentCard(EquipmentCard, _CharTargetChoiceProvider):
    WEAPON_TYPE: WeaponType
    WEAPON_STATUS: type[stt.WeaponEquipmentStatus]

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        chars = game_state.get_player(pid).get_characters().get_alive_characters()
        return any(cls._valid_char(char) for char in chars) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return char.weapon_type() is cls.WEAPON_TYPE

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        if not isinstance(instruction, act.StaticTargetInstruction) \
                or pid is not instruction.target.pid:
            return False  # pragma: no cover
        char = game_state.get_target(instruction.target)
        if not isinstance(char, chr.Character):  # pragma: no cover
            return False
        return cls._valid_char(char) and super()._valid_instruction(game_state, pid, instruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=cls.WEAPON_STATUS,
            ),
        )


class ArtifactEquipmentCard(EquipmentCard, _CharTargetChoiceProvider):
    ARTIFACT_STATUS: type[stt.ArtifactEquipmentStatus]

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        chars = game_state.get_player(pid).get_characters().get_alive_characters()
        return any(cls._valid_char(char) for char in chars) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        if not isinstance(instruction, act.StaticTargetInstruction) \
                or pid is not instruction.target.pid:
            return False  # pragma: no cover
        char = game_state.get_target(instruction.target)
        if not isinstance(char, chr.Character):  # pragma: no cover
            return False
        return cls._valid_char(char) and super()._valid_instruction(game_state, pid, instruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=cls.ARTIFACT_STATUS,
            ),
        )


class SupportCard(Card):
    _SUPPORT_STATUS: type[sp.Support]

    @override
    @classmethod
    def valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> None | gs.GameState:
        supports = game_state.get_player(pid).get_supports()
        if supports.full():
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
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        es: list[eft.Effect] = []
        if type(instruction) is act.StaticTargetInstruction:
            es.append(eft.RemoveSupportEffect(
                target_pid=pid,
                sid=cast(int, instruction.target.id),
            ))
        return tuple(es) + (
            eft.AddSupportEffect(
                target_pid=pid,
                support=cls._SUPPORT_STATUS,
            ),
        ) + cls._effects(game_state, pid)

    @classmethod
    def _effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
    ) -> tuple[eft.Effect, ...]:
        """ effects that are after the addition of the support """
        return ()  # pragma: no cover

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
                    zone=Zone.SUPPORTS,
                    id=support.sid,
                )
                for support in supports
            )

        # only dices unfilled here
        assert type(instruction) is act.DiceOnlyInstruction \
            or type(instruction) is act.StaticTargetInstruction
        if instruction.dices is None:
            return cls.preprocessed_dice_cost(game_state, pid)[1]

        raise Exception("Not Reached!"
                        + "Should be called when there is something to fill. action_generator:\n"
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
            pid: Pid,
    ) -> None | acg.ActionGenerator:
        if not cls.strictly_usable(game_state, pid):  # pragma: no cover
            return None
        if game_state.get_player(pid).get_supports().full():
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


class FoodCard(EventCard):
    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        characters = game_state.get_player(pid).get_characters()
        if all(not cls._valid_char(char) for char in characters):
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        """ This only applies to food with a single target, override if needed """
        if not isinstance(instruction, act.StaticTargetInstruction) \
                or pid is not instruction.target.pid:
            return False  # pragma: no cover
        target = game_state.get_target(instruction.target)
        return (
            isinstance(target, chr.Character)
            and not target.satiated()
            and target.alive()
        )

    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return not char.satiated() and not char.defeated()

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
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
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:  # pragma: no cover
        assert isinstance(instruction, act.StaticTargetInstruction)
        return ()


class _DirectHealCard(FoodCard):
    @classmethod
    def heal_amount(cls) -> int:  # pragma: no cover
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

# <<<<<<<<<<<<<<<<<<<< Equipment Cards <<<<<<<<<<<<<<<<<<<<
########## Weapon Card ##########
#### Bow ####


class RavenBow(WeaponEquipmentCard):
    _DICE_COST = AbstractDices({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.BOW
    WEAPON_STATUS = stt.RavenBowStatus

#### Catalyst ####


class MagicGuide(WeaponEquipmentCard):
    _DICE_COST = AbstractDices({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.CATALYST
    WEAPON_STATUS = stt.MagicGuideStatus

#### Claymore ####


class WhiteIronGreatsword(WeaponEquipmentCard):
    _DICE_COST = AbstractDices({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.CLAYMORE
    WEAPON_STATUS = stt.WhiteIronGreatswordStatus

#### Polearm ####


class WhiteTassel(WeaponEquipmentCard):
    _DICE_COST = AbstractDices({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.POLEARM
    WEAPON_STATUS = stt.WhiteTasselStatus

#### Sword ####


class TravelersHandySword(WeaponEquipmentCard):
    _DICE_COST = AbstractDices({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.SWORD
    WEAPON_STATUS = stt.TravelersHandySwordStatus

########## Artifact Card ##########


class GamblersEarrings(ArtifactEquipmentCard):
    _DICE_COST = AbstractDices({Element.OMNI: 1})
    ARTIFACT_STATUS = stt.GamblersEarringsStatus

# <<<<<<<<<<<<<<<<<<<< Event Cards <<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<< Event Cards / Food Cards <<<<<<<<<<<<<<<<<<<<


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


class MondstadtHashBrown(_DirectHealCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 2


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


class SweetMadame(_DirectHealCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1


class TeyvatFriedEgg(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 3})

    @classmethod
    def revive_on_cooldown(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return stt.ReviveOnCooldown in game_state.get_player(pid).get_combat_statuses()

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return (
            super()._loosely_usable(game_state, pid)
            and not cls.revive_on_cooldown(game_state, pid)
        )

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        """ This only applies to food with a single target, override if needed """
        if not isinstance(instruction, act.StaticTargetInstruction) \
                or pid is not instruction.target.pid:
            return False  # pragma: no cover
        target = game_state.get_target(instruction.target)
        return (
            isinstance(target, chr.Character)
            and not target.satiated()
            and target.defeated()
            and not cls.revive_on_cooldown(game_state, pid)
        )

    @override
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return not char.satiated() and char.defeated()

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return cls.food_effects(instruction) + (
            eft.AddCharacterStatusEffect(
                instruction.target,
                stt.SatiatedStatus,
            ),
            eft.AddCombatStatusEffect(
                instruction.target.pid,
                stt.ReviveOnCooldown,
            )
        )

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.ReviveRecoverHPEffect(
                target=instruction.target,
                recovery=3,
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Event Cards / Food Cards >>>>>>>>>>>>>>>>>>>>


class CalxsArts(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
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
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction) \
            and cls.loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        player = game_state.get_player(pid)
        none_active_chars = player.get_characters().get_none_active_characters()
        active_char_id = player.just_get_active_character().get_id()
        effects: list[eft.Effect] = [
            eft.EnergyDrainEffect(
                target=StaticTarget(
                    Pid.P1, Zone.CHARACTERS, char.get_id()
                ),
                drain=1,
            )
            for char in none_active_chars
        ]
        effects.append(
            eft.EnergyRechargeEffect(
                target=StaticTarget(
                    Pid.P1, Zone.CHARACTERS, active_char_id
                ),
                recharge=sum(1 for char in none_active_chars if char.get_energy() > 0),
            )
        )
        return tuple(effects)


class ChangingShifts(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.ChangingShiftsStatus,
            ),
        )


class IHaventLostYet(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return (
            game_state.get_player(pid)
            .get_hidden_statuses()
            .just_find(stt.DeathThisRoundStatus).activated
        )

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        return (
            isinstance(instruction, act.DiceOnlyInstruction)
            and cls.loosely_usable(game_state, pid)
        )

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        target = StaticTarget(
            pid,
            Zone.CHARACTERS,
            game_state.get_player(pid).just_get_active_character().get_id(),
        )
        return (
            eft.AddDiceEffect(
                pid=pid,
                dices=ActualDices({Element.OMNI: 1}),
            ),
            eft.EnergyRechargeEffect(
                target=target,
                recharge=1,
            ),
        )


class LeaveItToMe(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({})

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        return isinstance(instruction, act.DiceOnlyInstruction)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.LeaveItToMeStatus,
            ),
        )


class QuickKnit(EventCard, _SummonTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.OMNI: 1})
    _MY_SIDE = True

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return not game_state.get_player(pid).get_summons().empty()

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        if not isinstance(instruction, act.StaticTargetInstruction):  # pragma: no cover
            return False

        return (
            instruction.target.pid is pid
            and isinstance(game_state.get_target(instruction.target), sm.Summon)
            and cls.loosely_usable(game_state, pid)
        )

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.OneSummonIncreaseUsage(
                target=instruction.target,
                d_usages=1,
            ),
        )


class Starsigns(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.ANY: 2})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
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
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        """ Check target is active character and .loosely_usable() """
        if not isinstance(instruction, act.DiceOnlyInstruction):  # pragma: no cover
            return False

        return cls.loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyRechargeEffect(
                StaticTarget(
                    pid=pid,
                    zone=Zone.CHARACTERS,
                    id=game_state.get_player(pid).just_get_active_character().get_id(),
                ),
                1
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Event Cards >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Support Cards <<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<< Support Cards / Companion Cards <<<<<<<<<<<<<<<<<<<<


class Xudong(CompanionCard):
    _DICE_COST = AbstractDices({Element.ANY: 2})
    _SUPPORT_STATUS = sp.XudongSupport

# >>>>>>>>>>>>>>>>>>>> Support Cards / Companion Cards >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Support Cards / Location Cards <<<<<<<<<<<<<<<<<<<<


class KnightsOfFavoniusLibrary(LocationCard):
    _DICE_COST = AbstractDices({Element.OMNI: 1})
    _SUPPORT_STATUS = sp.KnightsOfFavoniusLibrarySupport

    @classmethod
    def _effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.RollPhaseStartEffect(),
        )


class Vanarana(LocationCard):
    _DICE_COST = AbstractDices({})
    _SUPPORT_STATUS = sp.VanaranaSupport

# >>>>>>>>>>>>>>>>>>>> Support Cards / Location Cards >>>>>>>>>>>>>>>>>>>>

# >>>>>>>>>>>>>>>>>>>> Support Cards >>>>>>>>>>>>>>>>>>>>

#### Arataki Itto ####


class AratakiIchiban(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.GEO: 1, Element.ANY: 2})
    _CHARACTER = chr.AratakiItto
    _EQUIPMENT_STATUS = stt.AratakiIchibanStatus
    _SKILL = CharacterSkill.NORMAL_ATTACK

#### Electro Hypostasis ####


class AbsorbingPrism(TalentEventCard, _CombatActionCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})
    _CHARACTER = chr.ElectroHypostasis

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        target = StaticTarget(
            pid=pid,
            zone=Zone.CHARACTERS,
            id=game_state.get_player(pid).just_get_active_character().get_id(),
        )
        return (
            eft.RecoverHPEffect(
                target=target,
                recovery=3,
            ),
            eft.AddCharacterStatusEffect(
                target=target,
                status=stt.ElectroCrystalCoreStatus,
            ),
        )

#### Kaedehara Kazuha ####


class PoeticsOfFuubutsu(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.ANEMO: 3})
    _CHARACTER = chr.KaedeharaKazuha
    _EQUIPMENT_STATUS = stt.PoeticsOfFuubutsuStatus
    _SKILL = CharacterSkill.ELEMENTAL_SKILL1

#### Kaeya ####


class ColdBloodedStrike(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.CRYO: 4})
    _CHARACTER = chr.Kaeya
    _EQUIPMENT_STATUS = stt.ColdBloodedStrikeStatus
    _SKILL = CharacterSkill.ELEMENTAL_SKILL1

#### Keqing ####


class LightningStiletto(TalentEventCard, _CombatActionCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})

    @override
    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return False

    @override
    @classmethod
    def _valid_char(cls, char: chr.Character) -> bool:
        return isinstance(char, chr.Keqing) \
            and super()._valid_char(char)

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        cs = game_state.get_player(pid).get_characters()
        keqings = [char for char in cs if type(char) is chr.Keqing]
        if not keqings:  # pragma: no cover
            return False
        if all(not keqing.can_cast_skill() for keqing in keqings):
            return False
        return Card._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
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
            pid: Pid,
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


class ThunderingPenance(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.ELECTRO: 3})
    _CHARACTER = chr.Keqing
    _EQUIPMENT_STATUS = stt.ThunderingPenanceStatus
    _SKILL = CharacterSkill.ELEMENTAL_SKILL1

#### Klee ####


class PoundingSurprise(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.PYRO: 3})
    _CHARACTER = chr.Klee
    _EQUIPMENT_STATUS = stt.PoundingSurpriseStatus
    _SKILL = CharacterSkill.ELEMENTAL_SKILL1

#### Mona ####


class ProphecyOfSubmersion(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.HYDRO: 3})
    _CHARACTER = chr.Mona
    _EQUIPMENT_STATUS = stt.ProphecyOfSubmersionStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST

#### Rhodeia of Loch ####


class StreamingSurge(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.HYDRO: 4})
    _CHARACTER = chr.RhodeiaOfLoch
    _EQUIPMENT_STATUS = stt.StreamingSurgeStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST

#### Tighnari ####


class KeenSight(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.DENDRO: 4})
    _CHARACTER = chr.Tighnari
    _EQUIPMENT_STATUS = stt.KeenSightStatus
    _SKILL = CharacterSkill.ELEMENTAL_SKILL1

#### Xingqiu ####


class TheScentRemained(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDices({Element.HYDRO: 4})
    _CHARACTER = chr.Xingqiu
    _EQUIPMENT_STATUS = stt.TheScentRemainedStatus
    _SKILL = CharacterSkill.ELEMENTAL_SKILL1
