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
from abc import abstractmethod
from typing import TYPE_CHECKING, cast
from dataclasses import replace
from typing_extensions import override

from ..action import action as act
from ..action import action_generator as acg
from ..character import character as chr
from ..effect import effect as eft
from ..status import status as stt
from ..summon import summon as sm
from ..support import support as sp

from ..character.enums import CharacterSkill, Faction, WeaponType
from ..dice import AbstractDice, ActualDice
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
    "ItemCard",
    "LocationCard",
    "ArcaneLegendCard",
    "FoodCard",

    # Weapon Card
    ## Bow ##
    "AmosBow",
    "KingsSquire",
    "RavenBow",
    "SacrificialBow",
    ## Catalyst ##
    "AThousandFloatingDreams",
    "FruitOfFulfillment",
    "MagicGuide",
    "SacrificialFragments",
    ## Claymore ##
    "SacrificialGreatsword",
    "TheBell",
    "WhiteIronGreatsword",
    "WolfsGravestone",
    ## Polearm ##
    "LithicSpear",
    "VortexVanquisher",
    "WhiteTassel",
    ## Sword ##
    "AquilaFavonia",
    "SacrificialSword",
    "TravelersHandySword",

    # Artifact Card
    "GamblersEarrings",
    "GeneralsAncientHelm",
    "InstructorsCap",
    "TenacityOfTheMillelith",

    # Event Card
    ## Food Card ##
    "JueyunGuoba",
    "LotusFlowerCrisp",
    "MintyMeatRolls",
    "MondstadtHashBrown",
    "MushroomPizza",
    "NorthernSmokedChicken",
    "SweetMadame",
    "TandooriRoastChicken",
    "TeyvatFriedEgg",
    ## Other ##
    "CalxsArts",
    "ChangingShifts",
    "ElementalResonanceEnduringRock",
    "ElementalResonanceFerventFlames",
    "ElementalResonanceHighVoltage",
    "ElementalResonanceImpetuousWinds",
    "ElementalResonanceShatteringIce",
    "ElementalResonanceSoothingWater",
    "ElementalResonanceSprawlingGreenery",
    "ElementalResonanceWovenFlames",
    "ElementalResonanceWovenIce",
    "ElementalResonanceWovenStone",
    "ElementalResonanceWovenThunder",
    "ElementalResonanceWovenWaters",
    "ElementalResonanceWovenWeeds",
    "ElementalResonanceWovenWinds",
    "FreshWindOfFreedom",
    "IHaventLostYet",
    "LeaveItToMe",
    "QuickKnit",
    "SendOff",
    "Starsigns",
    "TheBestestTravelCompanion",
    "WhenTheCraneReturned",
    "WhereIsTheUnseenRazor",
    "WindAndFreedom",

    # Support Card
    ## Companion ##
    "ChangTheNinth",
    "Liben",
    "Paimon",
    "Xudong",
    ## Item ##
    "NRE",
    "ParametricTransformer",
    ## Location ##
    "KnightsOfFavoniusLibrary",
    "LiyueHarborWharf",
    "SumeruCity",
    "Tenshukaku",
    "Vanarana",

    # Character Specific
    ## Albedo ##
    "DescentOfDivinity",
    ## Arataki Itto ##
    "AratakiIchiban",
    ## Bennett ##
    "GrandExpectation",
    ## Collei ##
    "FloralSidewinder",
    ## Dehya ##
    "StalwartAndTrue",
    ## Electro Hypostasis ##
    "AbsorbingPrism",
    ## Fatui Pyro Agent ##
    "PaidInFull",
    ## Fischl ##
    "StellarPredator",
    ## Ganyu ##
    "UndividedHeart",
    ## Hu Tao ##
    "SanguineRouge",
    ## Jadeplume Terrorshroom ##
    "ProliferatingSpores",
    ## Jean ##
    "LandsOfDandelion",
    ## Kaedehara Kazuha ##
    "PoeticsOfFuubutsu",
    ## Kaeya ##
    "ColdBloodedStrike",
    ## Keqing ##
    "LightningStiletto",
    "ThunderingPenance",
    ## Klee ##
    "PoundingSurprise",
    ## Maguu Kenki ##
    "TranscendentAutomaton",
    ## Mona ##
    "ProphecyOfSubmersion",
    ## Nahida ##
    "TheSeedOfStoredKnowledge",
    ## Ningguang ##
    "StrategicReserve",
    ## Noelle ##
    "IGotYourBack",
    ## Qiqi ##
    "RiteOfResurrection",
    ## Rhodeia of Loch ##
    "StreamingSurge",
    ## Sangonomiya Kokomi ##
    "TamakushiCasket",
    ## Shenhe ##
    "MysticalAbandon",
    ## Tighnari ##
    "KeenSight",
    ## Venti ##
    "EmbraceOfWinds",
    ## Xingqiu ##
    "TheScentRemained",
    ## Yae Miko ##
    "TheShrinesSacredShade",
    ## Yoimiya ##
    "NaganoharaMeteorSwarm",
]

############################## base ##############################


class Card:
    _DICE_COST = AbstractDice({Element.OMNI: BIG_INT})

    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        """
        :param game_state: the state of the game when the card is played.
        :param pid: the card-player's pid.
        :param instruction: additional information on how card should be played.

        Returns the effects of the card when played.
        """
        raise NotImplementedError

    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        """
        :returns: if this card can be added to the `deck`.
        """
        return True

    @classmethod
    def base_dice_cost(cls) -> AbstractDice:  # pragma: no cover
        """
        :returns: the basic cost of the card without any discount.
        """
        return cls._DICE_COST

    @classmethod
    def preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: Pid
    ) -> tuple[gs.GameState, AbstractDice]:
        """
        :returns: a tuple of `GameState` and `AbstractDice`.

        The returned game_state is the game_state after preprocessing the usage of the card.

        The returned abstract_dice are the actual cost of using the card at the provided game_state.
        """
        game_state, card_event = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            pp_type=Preprocessables.CARD,
            item=CardPEvent(
                pid=pid,
                card_type=cls,
                dice_cost=cls._DICE_COST,
            ),
        )
        assert isinstance(card_event, CardPEvent)
        return game_state, card_event.dice_cost

    @classmethod
    def just_preprocessed_dice_cost(
            cls,
            game_state: gs.GameState,
            pid: Pid
    ) -> AbstractDice:
        """
        :returns: the actual cost of the card for `pid` at `game_state`.
        """
        return cls.preprocessed_dice_cost(game_state, pid)[1]

    # TODO add a post effect adding inform() to all status

    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """ doesn't check if player has the card in hand """
        return game_state.get_active_player_id() is pid

    @classmethod
    def loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """
        :returns: `True` if the card can be played by the player `pid` provided they
                  have the card.
        """
        return cls._loosely_usable(game_state, pid) and game_state.get_effect_stack().is_empty()

    @classmethod
    def usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """
        :returns: `True` if the card can be played by the player `pid` and they
                  have the card.
        """
        return game_state.get_player(pid).get_hand_cards().contains(cls) \
            and cls.loosely_usable(game_state, pid)

    @classmethod
    def strictly_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """
        :returns: `True` if the card can be played by the player `pid`, and they
                  have the card and they have the dice to pay for the card.
        """
        dice_satisfy = game_state.get_player(pid).get_dice().loosely_satisfy(
            cls.just_preprocessed_dice_cost(game_state, pid)
        )
        return dice_satisfy and cls.usable(game_state, pid)

    @classmethod
    def valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> None | gs.GameState:
        """
        :returns: the preprocessed game-state if instruction is valid,
                  otherwise return None.
        """
        if not game_state.get_player(pid).get_hand_cards().contains(cls) \
                or not game_state.get_active_player_id() is pid \
                or not cls._valid_instruction(game_state, pid, instruction) \
                or not (game_state.get_player(pid).get_dice() - instruction.dice).is_legal():
            return None
        game_state, dice_cost = cls.preprocessed_dice_cost(game_state, pid)
        if instruction.dice.just_satisfy(dice_cost):
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
        """ :returns: the action generator if the card is `strictly_usable` otherwise None. """
        return None  # pragma: no cover

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return type(self) == type(other)

    def __repr__(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def is_combat_action() -> bool:
        """ :returns: if playing the card is a combat action. """
        return False

    @classmethod
    def name(cls) -> str:
        """ :returns: the name of the card without space. """
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
    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        if not isinstance(instruction, act.DiceOnlyInstruction):  # pragma: no cover
            return False

        return cls.loosely_usable(game_state, pid)

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
        if instruction.dice is None:
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
        if instruction.dice is None:
            assert isinstance(player_choice, ActualDice)
            return replace(
                action_generator,
                instruction=replace(instruction, dice=player_choice),
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
    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return any(
            cls._valid_char(game_state, pid, char)
            for char in game_state.get_player(pid).get_characters()
        ) and super()._loosely_usable(game_state, pid)

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
        char = game_state.get_character_target(instruction.target)
        if char is None:  # pragma: no cover
            return False
        return (
            cls._valid_char(game_state, pid, char)
            and super()._valid_instruction(game_state, pid, instruction)
        )

    @classmethod
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:  # pragma: no cover
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
            chars = [char for char in chars if cls._valid_char(
                game_state, pid, char)]
            return tuple(
                StaticTarget(
                    pid=pid,
                    zone=Zone.CHARACTERS,
                    id=char.get_id(),
                )
                for char in chars
            )

        elif instruction.dice is None:
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

        elif instruction.dice is None:
            assert isinstance(player_choice, ActualDice)
            return replace(
                action_generator,
                instruction=replace(instruction, dice=player_choice),
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

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return (
            (
                not cls._MY_SIDE
                or (
                    not (summons := game_state.get_player(
                        pid).get_summons()).empty()
                    and any(
                        cls._valid_summon(summon)
                        for summon in summons
                    )
                )
            ) and (
                not cls._OPPO_SIDE
                or (
                    not (summons := game_state.get_other_player(
                        pid).get_summons()).empty()
                    and any(
                        cls._valid_summon(summon)
                        for summon in summons
                    )
                )
            )
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
            isinstance(instruction, act.StaticTargetInstruction)
            and (
                (not cls._MY_SIDE or instruction.target.pid is pid)
                and (not cls._OPPO_SIDE or instruction.target.pid is pid.other())
            )
            and isinstance(summon := game_state.get_target(instruction.target), sm.Summon)
            and cls._valid_summon(summon)
            and cls.loosely_usable(game_state, pid)
        )

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

        elif instruction.dice is None:
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

        elif instruction.dice is None:
            assert isinstance(player_choice, ActualDice)
            return replace(
                action_generator,
                instruction=replace(instruction, dice=player_choice),
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
            ret_val = ret_val and isinstance(
                instruction, act.DiceOnlyInstruction)
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
                    CharacterSkill.SKILL1,
                    CharacterSkill.SKILL2,
                    CharacterSkill.SKILL3,
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
            ret_val = ret_val and isinstance(
                instruction, act.DiceOnlyInstruction)
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
        chars = game_state.get_player(
            pid).get_characters().get_alive_characters()
        return any(cls._valid_char(game_state, pid, char) for char in chars) \
            and super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
        return char.WEAPON_TYPE() is cls.WEAPON_TYPE

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
        ) + cls.on_enter_effects(game_state, pid, instruction)

    @classmethod
    def on_enter_effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.StaticTargetInstruction
    ) -> tuple[eft.Effect, ...]:
        return ()


class ArtifactEquipmentCard(EquipmentCard, _CharTargetChoiceProvider):
    ARTIFACT_STATUS: type[stt.ArtifactEquipmentStatus]

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        chars = game_state.get_player(
            pid).get_characters().get_alive_characters()
        return any(cls._valid_char(game_state, pid, char) for char in chars) \
            and super()._loosely_usable(game_state, pid)

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

        # only dice unfilled here
        assert type(instruction) is act.DiceOnlyInstruction \
            or type(instruction) is act.StaticTargetInstruction
        if instruction.dice is None:
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
        if instruction.dice is None:
            assert isinstance(player_choice, ActualDice)
            return replace(
                action_generator,
                instruction=replace(instruction, dice=player_choice),
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


class ItemCard(SupportCard):
    pass


class LocationCard(SupportCard):
    pass


class ArcaneLegendCard(Card):
    @override
    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return cls not in deck.cards or deck.cards[cls] == 0

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return stt.ArcaneLegendUsedStatus not in game_state.get_player(pid).get_hidden_statuses()

    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        return cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddHiddenStatusEffect(
                pid,
                stt.ArcaneLegendUsedStatus,
            ),
        )


class FoodCard(EventCard):
    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        characters = game_state.get_player(pid).get_characters()
        if all(not cls._valid_char(game_state, pid, char) for char in characters):
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
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
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


class _RangedFoodCard(FoodCard, _DiceOnlyChoiceProvider):
    @override
    @classmethod
    def _valid_instruction(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction
    ) -> bool:
        """ This only applies to food with a single target, override if needed """
        if not isinstance(instruction, act.DiceOnlyInstruction):
            return False  # pragma: no cover
        return cls._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.DiceOnlyInstruction)
        targets = [
            StaticTarget.from_char_id(pid, char.get_id())
            for char in game_state.get_player(pid).get_characters()
            if cls._valid_char(game_state, pid, char)
        ]
        return sum([
            cls.ranged_food_effects(instruction, target)
            for target in targets
        ], ()) + tuple([
            eft.AddCharacterStatusEffect(
                target,
                stt.SatiatedStatus
            )
            for target in targets
        ])

    @classmethod
    @abstractmethod
    def ranged_food_effects(
            cls,
            instruction: act.DiceOnlyInstruction,
            target: StaticTarget,
    ) -> tuple[eft.Effect, ...]:
        pass


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
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
        return char.get_hp() < char.get_max_hp() \
            and super()._valid_char(game_state, pid, char)

# <<<<<<<<<<<<<<<<<<<< Equipment Cards <<<<<<<<<<<<<<<<<<<<
########## Weapon Card ##########
#### Bow ####


class AmosBow(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.BOW
    WEAPON_STATUS = stt.AmosBowStatus


class KingsSquire(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.BOW
    WEAPON_STATUS = stt.KingsSquireStatus

    @override
    @classmethod
    def on_enter_effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.StaticTargetInstruction
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCharacterStatusEffect(
                target=instruction.target,
                status=stt.KingsSquireEffectStatus,
            ),
        )


class RavenBow(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.BOW
    WEAPON_STATUS = stt.RavenBowStatus


class SacrificialBow(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.BOW
    WEAPON_STATUS = stt.SacrificialBowStatus

#### Catalyst ####


class AThousandFloatingDreams(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.CATALYST
    WEAPON_STATUS = stt.AThousandFloatingDreamsStatus


class FruitOfFulfillment(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.ANY: 3})
    WEAPON_TYPE = WeaponType.CATALYST
    WEAPON_STATUS = stt.FruitOfFulfillmentStatus

    @override
    @classmethod
    def on_enter_effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.StaticTargetInstruction
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.DrawRandomCardEffect(
                pid=pid,
                num=2,
            ),
        )


class MagicGuide(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.CATALYST
    WEAPON_STATUS = stt.MagicGuideStatus


class SacrificialFragments(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.CATALYST
    WEAPON_STATUS = stt.SacrificialFragmentsStatus

#### Claymore ####


class SacrificialGreatsword(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.CLAYMORE
    WEAPON_STATUS = stt.SacrificialGreatswordStatus


class TheBell(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.CLAYMORE
    WEAPON_STATUS = stt.TheBellStatus


class WhiteIronGreatsword(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.CLAYMORE
    WEAPON_STATUS = stt.WhiteIronGreatswordStatus


class WolfsGravestone(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.CLAYMORE
    WEAPON_STATUS = stt.WolfsGravestoneStatus


#### Polearm ####

class LithicSpear(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.POLEARM
    WEAPON_STATUS = stt.LithicSpearStatus

    @override
    @classmethod
    def on_enter_effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.StaticTargetInstruction
    ) -> tuple[eft.Effect, ...]:
        stacks = len([
            None
            for char in game_state.get_player(pid).get_characters()
            if char.of_faction(Faction.LIYUE)
        ])
        if stacks == 0:
            return ()
        return (
            eft.UpdateCharacterStatusEffect(
                target=instruction.target,
                status=stt.LithicGuardStatus(usages=stacks),
            ),
        )


class VortexVanquisher(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.POLEARM
    WEAPON_STATUS = stt.VortexVanquisherStatus


class WhiteTassel(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.POLEARM
    WEAPON_STATUS = stt.WhiteTasselStatus

#### Sword ####


class AquilaFavonia(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.SWORD
    WEAPON_STATUS = stt.AquilaFavoniaStatus


class SacrificialSword(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    WEAPON_TYPE = WeaponType.SWORD
    WEAPON_STATUS = stt.SacrificialSwordStatus


class TravelersHandySword(WeaponEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    WEAPON_TYPE = WeaponType.SWORD
    WEAPON_STATUS = stt.TravelersHandySwordStatus

########## Artifact Card ##########


class GamblersEarrings(ArtifactEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 1})
    ARTIFACT_STATUS = stt.GamblersEarringsStatus


class GeneralsAncientHelm(ArtifactEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    ARTIFACT_STATUS = stt.GeneralsAncientHelmStatus


class InstructorsCap(ArtifactEquipmentCard):
    _DICE_COST = AbstractDice({Element.ANY: 2})
    ARTIFACT_STATUS = stt.InstructorsCapStatus


class TenacityOfTheMillelith(ArtifactEquipmentCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    ARTIFACT_STATUS = stt.TenacityOfTheMillelithStatus

# <<<<<<<<<<<<<<<<<<<< Event Cards <<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<< Event Cards / Food Cards <<<<<<<<<<<<<<<<<<<<


class JueyunGuoba(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDice({})

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
    _DICE_COST = AbstractDice({Element.OMNI: 1})

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
    _DICE_COST = AbstractDice({Element.OMNI: 1})

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
    _DICE_COST = AbstractDice({Element.OMNI: 1})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 2


class MushroomPizza(FoodCard, _CharTargetChoiceProvider):
    """
    Heal first then the status
    """

    _DICE_COST = AbstractDice({Element.OMNI: 1})

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
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
        return _DirectHealCard._valid_char(game_state, pid, char)


class NorthernSmokedChicken(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDice({})

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
    _DICE_COST = AbstractDice({})

    @override
    @classmethod
    def heal_amount(cls) -> int:
        return 1


class TandooriRoastChicken(_RangedFoodCard):
    _DICE_COST = AbstractDice({Element.ANY: 2})

    @override
    @classmethod
    def ranged_food_effects(
            cls,
            instruction: act.DiceOnlyInstruction,
            target: StaticTarget,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCharacterStatusEffect(
                target=target,
                status=stt.TandooriRoastChickenStatus,
            ),
        )


class TeyvatFriedEgg(FoodCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: 2})

    @classmethod
    def revive_on_cooldown(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return stt.ReviveOnCooldownStatus in game_state.get_player(pid).get_combat_statuses()

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
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
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
                stt.ReviveOnCooldownStatus,
            )
        )

    @override
    @classmethod
    def food_effects(cls, instruction: act.Instruction) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        return (
            eft.ReviveRecoverHPEffect(
                target=instruction.target,
                recovery=1,
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Event Cards / Food Cards >>>>>>>>>>>>>>>>>>>>


class CalxsArts(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: 1})

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
                recharge=sum(
                    1 for char in none_active_chars if char.get_energy() > 0),
            )
        )
        return tuple(effects)


class ChangingShifts(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        chars = game_state.get_player(
            pid).get_characters().get_none_active_characters()
        return any(
            char.alive()
            for char in chars
        ) and super()._loosely_usable(game_state, pid)

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


class _ElementalResonanceCard(EventCard):
    _ELEMENT: Element

    @override
    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return 2 <= sum(
            1
            for char in deck.chars
            if char.ELEMENT() is cls._ELEMENT
        )


class ElementalResonanceEnduringRock(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.GEO: 1})
    _ELEMENT = Element.GEO

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
                status=stt.ElementalResonanceEnduringRockStatus,
            ),
        )


class ElementalResonanceFerventFlames(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.PYRO: 1})
    _ELEMENT = Element.PYRO

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
                status=stt.ElementalResonanceFerventFlamesStatus,
            ),
        )


class ElementalResonanceHighVoltage(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.ELECTRO: 1})
    _ELEMENT = Element.ELECTRO

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        """ Check active character doesn't have full energy """
        characters = game_state.get_player(
            pid).get_characters().get_alive_character_in_activity_order()
        if not any(char.get_energy() < char.get_max_energy() for char in characters):
            return False
        return super()._loosely_usable(game_state, pid)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        characters = \
            game_state.get_player(pid).get_characters(
            ).get_alive_character_in_activity_order()
        char_id = next(
            char.get_id()
            for char in characters
            if char.get_energy() < char.get_max_energy()
        )
        return (
            eft.EnergyRechargeEffect(
                StaticTarget.from_char_id(pid, char_id),
                1
            ),
        )


class ElementalResonanceImpetuousWinds(_ElementalResonanceCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDice({Element.ANEMO: 1})
    _ELEMENT = Element.ANEMO

    @override
    @classmethod
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
        return (
            char.alive()
            and char.get_id() != game_state.get_player(pid).just_get_active_character().get_id()
        )

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        cs = game_state.get_player(pid).get_characters()
        return any(char.alive() for char in cs.get_none_active_characters())

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
            eft.SwapCharacterEffect(target=instruction.target),
            eft.AddDiceEffect(pid=pid, element=Element.OMNI, num=1),
        )


class ElementalResonanceShatteringIce(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.CRYO: 1})
    _ELEMENT = Element.CRYO

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
                status=stt.ElementalResonanceShatteringIceStatus,
            ),
        )


class ElementalResonanceSoothingWater(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.HYDRO: 1})
    _ELEMENT = Element.HYDRO

    _MAIN_RECOVERY = 2
    _SUB_RECOVERY = 1

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        chars = game_state.get_player(pid).get_characters()
        return any(char.get_hp() < char.get_max_hp() for char in chars)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        chars = game_state.get_player(pid).get_characters(
        ).get_alive_character_in_activity_order()
        effects: list[eft.Effect] = [eft.RecoverHPEffect(
            target=StaticTarget.from_char_id(pid, chars[0].get_id()),
            recovery=cls._MAIN_RECOVERY,
        )]
        for char in chars[1:]:
            effects.append(eft.RecoverHPEffect(
                target=StaticTarget.from_char_id(pid, char.get_id()),
                recovery=cls._SUB_RECOVERY,
            ))
        return tuple(effects)


class ElementalResonanceSprawlingGreenery(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.DENDRO: 1})
    _ELEMENT = Element.DENDRO

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [eft.AddCombatStatusEffect(
            target_pid=pid,
            status=stt.ElementalResonanceSprawlingGreeneryStatus,
        )]

        this_player = game_state.get_player(pid)
        burning_flame_summon = this_player.get_summons().find(sm.BurningFlameSummon)
        if burning_flame_summon is not None:
            effects.append(eft.OverrideSummonEffect(
                target_pid=pid,
                summon=replace(burning_flame_summon,
                               usages=burning_flame_summon.usages + 1),
            ))

        combat_statuses = this_player.get_combat_statuses()
        catalyzing_field_status = combat_statuses.find(
            stt.CatalyzingFieldStatus)
        if catalyzing_field_status is not None:
            assert isinstance(catalyzing_field_status,
                              stt.CatalyzingFieldStatus)
            effects.append(eft.OverrideCombatStatusEffect(
                target_pid=pid,
                status=replace(catalyzing_field_status,
                               usages=catalyzing_field_status.usages + 1),
            ))

        dendro_core_status = combat_statuses.find(stt.DendroCoreStatus)
        if dendro_core_status is not None:
            assert isinstance(dendro_core_status, stt.DendroCoreStatus)
            effects.append(eft.OverrideCombatStatusEffect(
                target_pid=pid,
                status=replace(dendro_core_status,
                               usages=dendro_core_status.usages + 1),
            ))

        return tuple(effects)


class _ElementalResonanceDie(_ElementalResonanceCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({})
    _DICE_NUM = 1

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddDiceEffect(
                pid=pid,
                element=cls._ELEMENT,
                num=cls._DICE_NUM,
            ),
        )


class ElementalResonanceWovenFlames(_ElementalResonanceDie):
    _ELEMENT = Element.PYRO


class ElementalResonanceWovenIce(_ElementalResonanceDie):
    _ELEMENT = Element.CRYO


class ElementalResonanceWovenStone(_ElementalResonanceDie):
    _ELEMENT = Element.GEO


class ElementalResonanceWovenThunder(_ElementalResonanceDie):
    _ELEMENT = Element.ELECTRO


class ElementalResonanceWovenWaters(_ElementalResonanceDie):
    _ELEMENT = Element.HYDRO


class ElementalResonanceWovenWeeds(_ElementalResonanceDie):
    _ELEMENT = Element.DENDRO


class ElementalResonanceWovenWinds(_ElementalResonanceDie):
    _ELEMENT = Element.ANEMO


class FreshWindOfFreedom(EventCard, _DiceOnlyChoiceProvider, ArcaneLegendCard):
    _DICE_COST = AbstractDice({Element.OMNI: 0})

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return super().effects(
            game_state,
            pid,
            instruction,
        ) + (
            eft.AddCombatStatusEffect(
                target_pid=pid,
                status=stt.FreshWindOfFreedomStatus,
            ),
        )


class IHaventLostYet(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        return (
            (
                game_state.get_player(pid)
                .get_hidden_statuses()
                .just_find(stt.DeathThisRoundStatus).activated
            ) and (
                stt.IHaventLostYetOnCooldownStatus not in
                game_state.get_player(pid).get_combat_statuses()
            )
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
                element=Element.OMNI,
                num=1,
            ),
            eft.EnergyRechargeEffect(
                target=target,
                recharge=1,
            ),
            eft.AddCombatStatusEffect(
                target_pid=target.pid,
                status=stt.IHaventLostYetOnCooldownStatus,
            ),
        )


class LeaveItToMe(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({})

    @override
    @classmethod
    def _loosely_usable(cls, game_state: gs.GameState, pid: Pid) -> bool:
        chars = game_state.get_player(
            pid).get_characters().get_none_active_characters()
        return any(
            char.alive()
            for char in chars
        ) and super()._loosely_usable(game_state, pid)

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
    _DICE_COST = AbstractDice({Element.OMNI: 1})
    _MY_SIDE = True

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
            eft.OneSummonIncreaseUsageEffect(
                target=instruction.target,
                d_usages=1,
            ),
        )


class SendOff(EventCard, _SummonTargetChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    _OPPO_SIDE = True

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
            eft.OneSummonDecreaseUsageEffect(
                target=instruction.target,
                d_usages=2,
            ),
        )


class Starsigns(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.ANY: 2})

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
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyRechargeEffect(
                StaticTarget.from_player_active(game_state, pid),
                1
            ),
        )


class TheBestestTravelCompanion(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.ANY: 2})

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.AddDiceEffect(
                pid=pid,
                element=Element.OMNI,
                num=2,
            ),
        )


class WhenTheCraneReturned(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: 1})

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
                pid,
                stt.WhenTheCraneReturnedStatus,
            ),
        )

class WhereIsTheUnseenRazor(EventCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: 0})

    @override
    @classmethod
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
        return any(
            isinstance(status, stt.WeaponEquipmentStatus)
            for status in char.get_equipment_statuses()
        ) and super()._valid_char(game_state, pid, char)

    @override
    @classmethod
    def effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
            instruction: act.Instruction,
    ) -> tuple[eft.Effect, ...]:
        assert isinstance(instruction, act.StaticTargetInstruction)
        char_target = game_state.get_character_target(instruction.target)
        assert char_target is not None
        weapon = char_target.get_equipment_statuses(
        ).just_find_type(stt.WeaponEquipmentStatus)
        card = weapon.WEAPON_CARD
        return (
            eft.RemoveCharacterStatusEffect(
                target=instruction.target,
                status=type(weapon),
            ),
            eft.PublicAddCardEffect(
                pid=instruction.target.pid,
                card=card,
            ),
            eft.AddCombatStatusEffect(
                target_pid=instruction.target.pid,
                status=stt.WhereIsTheUnseenRazorStatus,
            ),
        )


class WindAndFreedom(EventCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.OMNI: 1})

    @override
    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return 2 <= sum(
            1
            for char in deck.chars
            if char.of_faction(Faction.MONDSTADT)
        )

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
                status=stt.WindAndFreedomStatus,
            ),
        )

# >>>>>>>>>>>>>>>>>>>> Event Cards >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Support Cards <<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<< Support Cards / Companion Cards <<<<<<<<<<<<<<<<<<<<


class ChangTheNinth(CompanionCard):
    _DICE_COST = AbstractDice.from_empty()
    _SUPPORT_STATUS = sp.ChangTheNinthSupport


class Liben(CompanionCard):
    _DICE_COST = AbstractDice.from_empty()
    _SUPPORT_STATUS = sp.LibenSupport


class Paimon(CompanionCard):
    _DICE_COST = AbstractDice({Element.OMNI: 3})
    _SUPPORT_STATUS = sp.PaimonSupport


class Xudong(CompanionCard):
    _DICE_COST = AbstractDice({Element.ANY: 2})
    _SUPPORT_STATUS = sp.XudongSupport

# >>>>>>>>>>>>>>>>>>>> Support Cards / Companion Cards >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Support Cards / Item Cards <<<<<<<<<<<<<<<<<<<<


class NRE(ItemCard):
    _DICE_COST = AbstractDice({Element.ANY: 1})
    _SUPPORT_STATUS = sp.NRESupport

    @classmethod
    def _effects(
            cls,
            game_state: gs.GameState,
            pid: Pid,
    ) -> tuple[eft.Effect, ...]:
        return (
            eft.DrawRandomCardOfTypeEffect(
                pid=pid,
                num=1,
                card_type=FoodCard,
            ),
        )


class ParametricTransformer(ItemCard):
    _DICE_COST = AbstractDice({Element.ANY: 2})
    _SUPPORT_STATUS = sp.ParametricTransformerSupport

# >>>>>>>>>>>>>>>>>>>> Support Cards / Item Cards >>>>>>>>>>>>>>>>>>>>

# <<<<<<<<<<<<<<<<<<<< Support Cards / Location Cards <<<<<<<<<<<<<<<<<<<<


class KnightsOfFavoniusLibrary(LocationCard):
    _DICE_COST = AbstractDice({Element.OMNI: 1})
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


class LiyueHarborWharf(LocationCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    _SUPPORT_STATUS = sp.LiyueHarborWharfSupport


class SumeruCity(LocationCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    _SUPPORT_STATUS = sp.SumeruCitySupport


class Tenshukaku(LocationCard):
    _DICE_COST = AbstractDice({Element.OMNI: 2})
    _SUPPORT_STATUS = sp.TenshukakuSupport


class Vanarana(LocationCard):
    _DICE_COST = AbstractDice.from_empty()
    _SUPPORT_STATUS = sp.VanaranaSupport

# >>>>>>>>>>>>>>>>>>>> Support Cards / Location Cards >>>>>>>>>>>>>>>>>>>>

# >>>>>>>>>>>>>>>>>>>> Support Cards >>>>>>>>>>>>>>>>>>>>

#### Albedo ####


class DescentOfDivinity(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.GEO: 3})
    _CHARACTER = chr.Albedo
    _EQUIPMENT_STATUS = stt.DescentOfDivinityStatus
    _SKILL = CharacterSkill.SKILL2


#### Arataki Itto ####


class AratakiIchiban(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.GEO: 1, Element.ANY: 2})
    _CHARACTER = chr.AratakiItto
    _EQUIPMENT_STATUS = stt.AratakiIchibanStatus
    _SKILL = CharacterSkill.SKILL1

#### Bennett ####


class GrandExpectation(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.PYRO: 4})
    _CHARACTER = chr.Bennett
    _EQUIPMENT_STATUS = stt.GrandExpectationStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Collei ####

class FloralSidewinder(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.DENDRO: 4})
    _CHARACTER = chr.Collei
    _EQUIPMENT_STATUS = stt.FloralSidewinderStatus
    _SKILL = CharacterSkill.SKILL2


#### Dehya ####

class StalwartAndTrue(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.PYRO: 4})
    _CHARACTER = chr.Dehya
    _EQUIPMENT_STATUS = stt.StalwartAndTrueStatus
    _SKILL = CharacterSkill.SKILL2


#### Electro Hypostasis ####

class AbsorbingPrism(TalentEventCard, _CombatActionCard, _DiceOnlyChoiceProvider):
    _DICE_COST = AbstractDice({Element.ELECTRO: 2})
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


#### Fatui Pyro Agent ####

class PaidInFull(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.PYRO: 3})
    _CHARACTER = chr.FatuiPyroAgent
    _EQUIPMENT_STATUS = stt.PaidInFullStatus
    _SKILL = CharacterSkill.SKILL2


#### Fischl ####

class StellarPredator(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ELECTRO: 3})
    _CHARACTER = chr.Fischl
    _EQUIPMENT_STATUS = stt.StellarPredatorStatus
    _SKILL = CharacterSkill.SKILL2


#### Ganyu ####

class UndividedHeart(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.CRYO: 5})
    _CHARACTER = chr.Ganyu
    _EQUIPMENT_STATUS = stt.UndividedHeartStatus
    _SKILL = CharacterSkill.SKILL3


#### Hu Tao ####


class SanguineRouge(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.PYRO: 2})
    _CHARACTER = chr.HuTao
    _EQUIPMENT_STATUS = stt.SanguineRougeStatus
    _SKILL = CharacterSkill.SKILL2


#### Jadeplume Terrorshroom ####

class ProliferatingSpores(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.DENDRO: 3})
    _CHARACTER = chr.JadeplumeTerrorshroom
    _EQUIPMENT_STATUS = stt.ProliferatingSporesStatus
    _SKILL = CharacterSkill.SKILL2


#### Jean ####

class LandsOfDandelion(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ANEMO: 4})
    _CHARACTER = chr.Jean
    _EQUIPMENT_STATUS = stt.LandsOfDandelionStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Kaedehara Kazuha ####


class PoeticsOfFuubutsu(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ANEMO: 3})
    _CHARACTER = chr.KaedeharaKazuha
    _EQUIPMENT_STATUS = stt.PoeticsOfFuubutsuStatus
    _SKILL = CharacterSkill.SKILL2

#### Kaeya ####


class ColdBloodedStrike(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.CRYO: 4})
    _CHARACTER = chr.Kaeya
    _EQUIPMENT_STATUS = stt.ColdBloodedStrikeStatus
    _SKILL = CharacterSkill.SKILL2

#### Keqing ####


class LightningStiletto(TalentEventCard, _CombatActionCard, _CharTargetChoiceProvider):
    _DICE_COST = AbstractDice({Element.ELECTRO: 3})

    @override
    @classmethod
    def valid_in_deck(cls, deck: Deck) -> bool:
        return False

    @override
    @classmethod
    def _valid_char(cls, game_state: gs.GameState, pid: Pid, char: chr.Character) -> bool:
        return isinstance(char, chr.Keqing) \
            and super()._valid_char(game_state, pid, char)

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
                skill=CharacterSkill.SKILL2,
            ),
        )


class ThunderingPenance(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ELECTRO: 3})
    _CHARACTER = chr.Keqing
    _EQUIPMENT_STATUS = stt.ThunderingPenanceStatus
    _SKILL = CharacterSkill.SKILL2

#### Klee ####


class PoundingSurprise(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.PYRO: 3})
    _CHARACTER = chr.Klee
    _EQUIPMENT_STATUS = stt.PoundingSurpriseStatus
    _SKILL = CharacterSkill.SKILL2


#### Maguu Kenki ####

class TranscendentAutomaton(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ANEMO: 3})
    _CHARACTER = chr.MaguuKenki
    _EQUIPMENT_STATUS = stt.TranscendentAutomatonStatus
    _SKILL = CharacterSkill.SKILL2

#### Mona ####


class ProphecyOfSubmersion(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.HYDRO: 3})
    _CHARACTER = chr.Mona
    _EQUIPMENT_STATUS = stt.ProphecyOfSubmersionStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST

#### Nahida ####


class TheSeedOfStoredKnowledge(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.DENDRO: 3})
    _CHARACTER = chr.Nahida
    _EQUIPMENT_STATUS = stt.TheSeedOfStoredKnowledgeStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Ningguang ####

class StrategicReserve(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.GEO: 4})
    _CHARACTER = chr.Ningguang
    _EQUIPMENT_STATUS = stt.StrategicReserveStatus
    _SKILL = CharacterSkill.SKILL2


#### Noelle ####


class IGotYourBack(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.GEO: 3})
    _CHARACTER = chr.Noelle
    _EQUIPMENT_STATUS = stt.IGotYourBackStatus
    _SKILL = CharacterSkill.SKILL2


#### Qiqi ####

class RiteOfResurrection(_TalentEquipmentSkillCard):
    """
    - Tested, second equipment doesn't refresh rivial limit per game.
    - Tested, revival of Qiqi resets revival chances per game.
    """
    _DICE_COST = AbstractDice({Element.CRYO: 5})
    _CHARACTER = chr.Qiqi
    _EQUIPMENT_STATUS = stt.RiteOfResurrectionStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Rhodeia of Loch ####


class StreamingSurge(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.HYDRO: 4})
    _CHARACTER = chr.RhodeiaOfLoch
    _EQUIPMENT_STATUS = stt.StreamingSurgeStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Sangonomiya Kokomi ####
class TamakushiCasket(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.HYDRO: 3})
    _CHARACTER = chr.SangonomiyaKokomi
    _EQUIPMENT_STATUS = stt.TamakushiCasketStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Shenhe ####

class MysticalAbandon(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.CRYO: 3})
    _CHARACTER = chr.Shenhe
    _EQUIPMENT_STATUS = stt.MysticalAbandonStatus
    _SKILL = CharacterSkill.SKILL2


#### Tighnari ####


class KeenSight(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.DENDRO: 4})
    _CHARACTER = chr.Tighnari
    _EQUIPMENT_STATUS = stt.KeenSightStatus
    _SKILL = CharacterSkill.SKILL2


#### Venti ####

class EmbraceOfWinds(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ANEMO: 3})
    _CHARACTER = chr.Venti
    _EQUIPMENT_STATUS = stt.EmbraceOfWindsStatus
    _SKILL = CharacterSkill.SKILL2

#### Xingqiu ####


class TheScentRemained(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.HYDRO: 3})
    _CHARACTER = chr.Xingqiu
    _EQUIPMENT_STATUS = stt.TheScentRemainedStatus
    _SKILL = CharacterSkill.SKILL2

#### Yae Miko ####


class TheShrinesSacredShade(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.ELECTRO: 3})
    _CHARACTER = chr.YaeMiko
    _EQUIPMENT_STATUS = stt.TheShrinesSacredShadeStatus
    _SKILL = CharacterSkill.ELEMENTAL_BURST


#### Yoimiya ####

class NaganoharaMeteorSwarm(_TalentEquipmentSkillCard):
    _DICE_COST = AbstractDice({Element.PYRO: 2})
    _CHARACTER = chr.Yoimiya
    _EQUIPMENT_STATUS = stt.NaganoharaMeteorSwarmStatus
    _SKILL = CharacterSkill.SKILL2
