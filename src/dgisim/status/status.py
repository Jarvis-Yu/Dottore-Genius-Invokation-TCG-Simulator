"""
This file contains the base class "Status" for all statuses,
and implementation of all statuses.

The classes are divided into 4 sections ordered. Within each section, they are
ordered alphabetically.

- base class, which is Status
- type classes, used to identify what type of status a status is
- template classes, starting with an '_', are templates for other classes
- concrete classes, the implementation of statuses that are actually in the game
"""
from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, fields, replace
from enum import Enum
from functools import cached_property
from itertools import chain
from math import ceil
from typing import ClassVar, cast, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft

from ..character.enums import CharacterSkill, CharacterSkillType, WeaponType
from ..dice import ActualDice
from ..effect.effects_template import standard_post_effects
from ..effect.enums import Zone, TriggeringSignal, DynamicCharacterTarget
from ..effect.structs import StaticTarget, DamageType
from ..element import Element, Reaction
from ..event import *
from ..helper.hashable_dict import HashableDict
from ..helper.quality_of_life import BIG_INT, case_val, classproperty
from .enums import Preprocessables, Informables

if TYPE_CHECKING:
    from ..card import card as crd
    from ..card.card import Card
    from ..character.character import Character
    from ..encoding.encoding_plan import EncodingPlan
    from ..state.enums import Pid
    from ..state.game_state import GameState

__all__ = [
    # base
    "Status",

    # type
    "PlayerHiddenStatus",
    "PersonalStatus",
    "HiddenStatus",  # it should be statuses used to record character-talent related data
    "EquipmentStatus",  # talent / weapon / artifact
    "TalentEquipmentStatus",
    "WeaponEquipmentStatus",
    "ArtifactEquipmentStatus",
    "CharacterStatus",  # statues that belongs to one character only
    "CombatStatus",  # statues that buffs the active character

    # templates & types
    "StackedShieldStatus",
    "FixedShieldStatus",
    "PrepareSkillStatus",
    "RevivalStatus",

    # hidden status
    "ArcaneLegendUsedStatus",
    "ChargedAttackStatus",
    "PlungeAttackStatus",
    "DeathThisRoundStatus",

    # equipment status
    ## Weapon ##
    ### bow ###
    "AmosBowStatus",
    "KingsSquireStatus",
    "RavenBowStatus",
    "SacrificialBowStatus",
    ### catalyst ###
    "AThousandFloatingDreamsStatus",
    "FruitOfFulfillmentStatus",
    "MagicGuideStatus",
    "SacrificialFragmentsStatus",
    ### claymore ###
    "SacrificialGreatswordStatus",
    "TheBellStatus",
    "WhiteIronGreatswordStatus",
    "WolfsGravestoneStatus",
    ### polearm ###
    "LithicSpearStatus",
    "VortexVanquisherStatus",
    "WhiteTasselStatus",
    ### sword ###
    "AquilaFavoniaStatus",
    "SacrificialSwordStatus",
    "TravelersHandySwordStatus",
    ## Artifact ##
    "GamblersEarringsStatus",
    "GeneralsAncientHelmStatus",
    "InstructorsCapStatus",
    "TenacityOfTheMillelithStatus",

    # combat status
    "CatalyzingFieldStatus",
    "ChangingShiftsStatus",
    "CrystallizeStatus",
    "DendroCoreStatus",
    "ElementalResonanceEnduringRockStatus",
    "ElementalResonanceFerventFlamesStatus",
    "ElementalResonanceShatteringIceStatus",
    "ElementalResonanceSprawlingGreeneryStatus",
    "FreshWindOfFreedomStatus",
    "KingsSquireEffectStatus",
    "LeaveItToMeStatus",
    "IHaventLostYetOnCooldownStatus",
    "RebelliousShieldStatus",
    "ReviveOnCooldownStatus",
    "WhenTheCraneReturnedStatus",
    "WhereIsTheUnseenRazorStatus",
    "WindAndFreedomStatus",

    # character status
    "FrozenStatus",
    "JueyunGuobaStatus",
    "LithicGuardStatus",
    "LotusFlowerCrispStatus",
    "MintyMeatRollsStatus",
    "MushroomPizzaStatus",
    "NorthernSmokedChickenStatus",
    "SatiatedStatus",
    "TandooriRoastChickenStatus",
    "UnmovableMountainStatus",

    # character specific status
    ## Albedo ##
    "DescentOfDivinityStatus",
    ## Arataki Itto ##
    "AratakiIchibanStatus",
    "RagingOniKingStatus",
    "SuperlativeSuperstrengthStatus",
    ## Bennett ##
    "GrandExpectationStatus",
    "InspirationFieldStatus",
    "InspirationFieldEnhancedStatus",
    ## Chongyun ##
    "ChonghuasFrostFieldStatus",
    ## Collei ##
    "ColleiTalentStatus",
    "FloralSidewinderStatus",
    "SproutStatus",
    ## Dehya ##
    "IncinerationDriveStatus",
    "StalwartAndTrueStatus",
    ## Electro Hypostasis ##
    "ElectroCrystalCoreHiddenStatus",
    "ElectroCrystalCoreStatus",
    "RockPaperScissorsComboPaperStatus",
    "RockPaperScissorsComboScissorsStatus",
    ## Fatui Pyro Agent ##
    "PaidInFullStatus",
    "StealthMasterStatus",
    "StealthStatus",
    ## Fischl ##
    "StellarPredatorStatus",
    ## Ganyu ##
    "GanyuTalentStatus",
    "IceLotusStatus",
    "UndividedHeartStatus",
    ## Hu Tao ##
    "BloodBlossomStatus",
    "ParamitaPapilioStatus",
    "SanguineRougeStatus",
    ## Jadeplume Terrorshroom ##
    "ProliferatingSporesStatus",
    "RadicalVitalityHiddenStatus",
    "RadicalVitalityStatus",
    ## Jean ##
    "LandsOfDandelionStatus",
    ## Kaedehara Kazuha ##
    "MidareRanzanStatus",
    "MidareRanzanCryoStatus",
    "MidareRanzanElectroStatus",
    "MidareRanzanHydroStatus",
    "MidareRanzanPyroStatus",
    "PoeticsOfFuubutsuStatus",
    "PoeticsOfFuubutsuCryoStatus",
    "PoeticsOfFuubutsuElectroStatus",
    "PoeticsOfFuubutsuHydroStatus",
    "PoeticsOfFuubutsuPyroStatus",
    ## Kaeya ##
    "ColdBloodedStrikeStatus",
    "IcicleStatus",
    ## Keqing ##
    "KeqingElectroInfusionStatus",
    "KeqingTalentStatus",
    "ThunderingPenanceStatus",
    ## Klee ##
    "ExplosiveSparkStatus",
    "PoundingSurpriseStatus",
    "SparksnSplashStatus",
    ## Maguu Kenki ##
    "TranscendentAutomatonStatus",
    ## Mona ##
    "IllusoryBubbleStatus",
    "IllusoryTorrentStatus",
    "ProphecyOfSubmersionStatus",
    ## Nahida ##
    "SeedOfSkandhaStatus",
    "ShrineOfMayaStatus",
    "TheSeedOfStoredKnowledgeStatus",
    ## Ningguang ##
    "JadeScreenStatus",
    "StrategicReserveStatus",
    ## Noelle ##
    "FullPlateStatus",
    "IGotYourBackStatus",
    "SweepingTimeStatus",
    ## Qiqi ##
    "FortunePreservingTalismanStatus",
    "QiqiTalentStatus",
    "RiteOfResurrectionStatus",
    ## Rhodeia of Loch ##
    "StreamingSurgeStatus",
    ## Sangonomiya Kokomi ##
    "CeremonialGarmentStatus",
    "TamakushiCasketStatus",
    ## Shenhe ##
    "IcyQuillStatus",
    "MysticalAbandonStatus",
    ## Tighnari ##
    "KeenSightStatus",
    "VijnanaSuffusionStatus",
    ## Venti ##
    "EmbraceOfWindsStatus",
    "StormzoneStatus",
    "WindsOfHarmonyStatus",
    ## Xingqiu ##
    "RainSwordStatus",
    "RainbowBladeworkStatus",
    "TheScentRemainedStatus",
    ## Yae Miko ##
    "RiteOfDispatchStatus",
    "TenkoThunderboltsStatus",
    "TheShrinesSacredShadeStatus",
    ## Yoimiya ##
    "AurousBlazeStatus",
    "NaganoharaMeteorSwarmStatus",
    "NiwabiEnshouStatus",
]


############################## base ##############################
@dataclass(frozen=True)
class Status:
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset()
    """
    The set of signals the status may react to.
    This is used to improve the performance.
    """

    def __init__(self) -> None:
        if type(self) is Status:  # pragma: no cover
            raise Exception("class Status is not instantiable")

    def preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        """
        :param game_state: the current game state.
        :param status_source: the position of this status.
        :param item: data to be preprocessed.
        :param signal: proprocessing signal.

        :returns: the preprocessed PreprocessableEvent and updated self.
                  If `None` is returned instead of a new self, then the status
                  is removed.
        """
        new_item, new_self = self._preprocess(game_state, status_source, item, signal)
        return self._post_preprocess(
            game_state,
            status_source,
            item,
            signal,
            new_item,
            new_self,
        )

    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        return item, self

    def _post_preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
            new_item: PreprocessableEvent,
            new_self: None | Self,
    ) -> tuple[PreprocessableEvent, None | Self]:
        return (new_item, new_self)

    def inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> GameState:
        """
        :param game_state: the current game state.
        :param status_source: the position of this status.
        :param info_type: the type of information.
        :param information: the information.

        :returns: the updated game state.
        """
        new_self = self._inform(game_state, status_source, info_type, information)
        if new_self == self:
            return game_state

        from ..summon import summon as sm
        from ..support import support as sp
        if isinstance(new_self, PersonalStatus):
            return eft.OverrideCharacterStatusEffect(
                target=status_source,
                status=new_self,
            ).execute(game_state)

        elif isinstance(new_self, PlayerHiddenStatus):
            return eft.OverrideHiddenStatusEffect(
                target_pid=status_source.pid,
                status=new_self,
            ).execute(game_state)

        elif isinstance(new_self, CombatStatus):
            return eft.OverrideCombatStatusEffect(
                target_pid=status_source.pid,
                status=new_self,
            ).execute(game_state)

        elif isinstance(new_self, sm.Summon):
            return eft.OverrideSummonEffect(
                target_pid=status_source.pid,
                summon=new_self,
            ).execute(game_state)

        elif isinstance(new_self, sp.Support):
            return eft.OverrideSupportEffect(
                target_pid=status_source.pid,
                support=new_self,
            ).execute(game_state)

        else:
            raise NotImplementedError

    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        return self

    def react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal,
            silent: bool = False,  # ignore post checkers if True
    ) -> list[eft.Effect]:
        """
        :param game_state: the current game state.
        :param source: the status position in the game.
        :param signal: the triggering signal.
        :param silent: ignores some post checkers if `True`. (just leave it as `False`)

        :returns: a list of effects generated.
        """
        es, new_status = self._react_to_signal(game_state, source, signal)
        es, new_status = self._post_react_to_signal(game_state, es, new_status, source, signal)

        from ..summon import summon as sm
        from ..support import support as sp
        # do the removal or update of the status
        if isinstance(self, HiddenStatus) \
                or isinstance(self, EquipmentStatus) \
                or isinstance(self, CharacterStatus):
            if new_status is None:
                es.append(eft.RemoveCharacterStatusEffect(
                    source,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateCharacterStatusEffect(
                    source,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, PlayerHiddenStatus):
            if new_status is None:
                es.append(eft.RemoveHiddenStatusEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateHiddenStatusEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, CombatStatus):
            if new_status is None:
                es.append(eft.RemoveCombatStatusEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateCombatStatusEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, sm.Summon):
            if new_status is None:
                es.append(eft.RemoveSummonEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateSummonEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, sp.Support):
            if new_status is None:
                es.append(eft.RemoveSupportEffect(
                    source.pid,
                    sid=self.sid,
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateSupportEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        else:  # pragma: no cover
            raise NotImplementedError

        es = self._post_update_react_to_signal(game_state, es, source, signal)

        if silent:
            return es

        has_damage = False
        has_swap = False
        for effect in es:
            has_damage = has_damage or isinstance(effect, eft.ReferredDamageEffect) \
                or isinstance(effect, eft.SpecificDamageEffect)
            has_swap = has_swap or (
                isinstance(effect, eft.SwapCharacterEffect)
                or isinstance(effect, eft.ForwardSwapCharacterEffect)
                or isinstance(effect, eft.ApplyElementalAuraEffect) and effect.element in (
                    Element.ELECTRO,
                    Element.PYRO,
                )
            )
        es += standard_post_effects(game_state, source.pid, has_damage, has_swap)

        return es

    def _post_update_react_to_signal(
            self,
            game_state: GameState,
            effects: list[eft.Effect],
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> list[eft.Effect]:
        return effects

    def _post_react_to_signal(
            self,
            game_state: GameState,
            effects: list[eft.Effect],
            new_status: None | Self,
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> tuple[list[eft.Effect], None | Self]:
        return effects, case_val(new_status == self, self, new_status)

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        """
        Returns a tuple, containg the effects and how to update self
        * if the returned new self is the same object as itself, then it is taken as no change
          requested
        * if the returned new self is none, then it is taken as a removal request
        * if the returned new self is different object than myself, then it is taken as an update
        """
        return [], self  # pragma: no cover

    def _is_swapping_source(self, source: StaticTarget, signal: TriggeringSignal) -> bool:
        """ Returns True if characters of the source player is swapping """
        return source.pid.is_player1() and signal is TriggeringSignal.SWAP_EVENT_1 \
            or source.pid.is_player2() and signal is TriggeringSignal.SWAP_EVENT_2

    def update(self, other: Self) -> None | Self:
        """
        Defines how the status update itself with an incoming status of the same type.
        """
        new_self = self._update(other)
        return self._post_update(new_self)

    def _post_update(self, new_self: None | Self) -> None | Self:
        return new_self

    def _update(self, other: Self) -> None | Self:
        return other

    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: None | StaticTarget = None,
    ):
        if target is None:
            target = status_source
        return (
            status_source.pid is target.pid
            and target.zone is Zone.CHARACTERS
            and status_source.id == game_state.get_player(
                status_source.pid
            ).get_characters().get_active_character_id()
        )

    def _some_char_equiped_talent(
            self,
            game_state: GameState,
            pid: Pid,
            char_type: type[Character],
    ) -> bool:
        alive_chars = game_state.get_player(pid).get_characters().get_alive_characters()
        return any(
            char.talent_equipped()
            for char in alive_chars
            if isinstance(char, char_type)
        )

    def perspective_view(self) -> Self:
        """
        Returns the self in the eyes of the opponent, hiding relevant information.
        """
        return self

    @classmethod
    def has_perspective_view(cls) -> bool:
        """
        Returns True if the status has a perspective view.
        """
        return cls.perspective_view is not Status.perspective_view

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of the content of the status. (excluding the type of status)
        """
        values = list(chain(*[
            [self.__getattribute__(field.name)]
            for field in fields(self)
        ]))
        ret_val = [encoding_plan.code_for(self)]
        for value in values:
            if isinstance(value, bool):
                ret_val.append(1 if value else 0)
            elif isinstance(value, int):
                ret_val.append(value)
            elif isinstance(value, Element):
                ret_val.append(value.value)
            elif value is None:
                ret_val.append(0)
            else:
                raise Exception(f"unknown type {type(value)}")
        fillings = encoding_plan.STATUS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"status {self} has too many fields")
        for _ in range(fillings):
            ret_val.append(0)
        return ret_val

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")  # pragma: no cover


############################## type ##############################

@dataclass(frozen=True)
class PlayerHiddenStatus(Status):
    pass


@dataclass(frozen=True)
class PersonalStatus(Status):
    def talent_equiped(self, game_state: GameState, status_source: StaticTarget) -> int:
        char = game_state.get_character_target(status_source)
        assert char is not None
        return char.talent_equipped()


@dataclass(frozen=True)
class HiddenStatus(PersonalStatus):
    """
    Basic status, describing character talents
    """
    pass


@dataclass(frozen=True)
class EquipmentStatus(PersonalStatus):
    """
    Basic status, describing weapon, artifact and character unique talents
    """


@dataclass(frozen=True)
class TalentEquipmentStatus(EquipmentStatus):
    pass


@dataclass(frozen=True)
class WeaponEquipmentStatus(EquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType]

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        raise NotImplementedError()

    BASE_DAMAGE_BOOST: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                dmg.source == status_source
                and dmg.damage_type.directly_from_character()
                and dmg.element is not Element.PIERCING
            ):
                return self._process_dmg(game_state, status_source, item)
        return super()._preprocess(game_state, status_source, item, signal)

    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        return dmg.delta_damage(self.BASE_DAMAGE_BOOST), self


@dataclass(frozen=True)
class ArtifactEquipmentStatus(EquipmentStatus):
    pass


@dataclass(frozen=True)
class CharacterStatus(PersonalStatus):
    """
    Basic status, private status to each character
    """
    pass


@dataclass(frozen=True)
class CombatStatus(Status):
    """
    Basic status, status shared across the team
    """

    @override
    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: None | StaticTarget = None,
    ) -> bool:
        """ target needs to be not None """
        assert target is not None
        active_char = game_state.get_player(status_source.pid).get_active_character()
        if active_char is None:
            return False
        return StaticTarget(
            pid=status_source.pid,
            zone=Zone.CHARACTERS,
            id=active_char.get_id(),
        ) == target


############################## template ##############################
@dataclass(frozen=True)
class _UsageStatus(Status):
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    AUTO_DESTROY: ClassVar[bool] = True

    @override
    def _post_preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
            new_item: PreprocessableEvent,
            new_self: None | Self,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if new_self is not None:
            if self.AUTO_DESTROY and new_self.usages <= 0:
                new_self = None
            elif new_self.usages < 0:
                new_self = replace(new_self, usages=0)
        return super()._post_preprocess(game_state, status_source, item, signal, new_item, new_self)

    @override
    def _post_update(self, new_self: None | Self) -> None | Self:
        """ remove the status if usages <= 0 """
        if new_self is not None:
            if self.AUTO_DESTROY and new_self.usages <= 0:
                new_self = None
            elif new_self.usages < 0:
                new_self = replace(new_self, usages=0)
        return super()._post_update(new_self)

    @override
    def _update(self, other: Self) -> None | Self:
        max_usages = max((self.usages, other.usages, self.MAX_USAGES))
        new_usages = min(self.usages + other.usages, max_usages)
        return replace(other, usages=new_usages)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


class _UsageLivingStatus(_UsageStatus):
    AUTO_DESTROY: ClassVar[bool] = False


@dataclass(frozen=True)
class _ShieldStatus(Status):
    def _is_target(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        from ..summon import summon as sm
        if isinstance(self, PersonalStatus):
            return item.target == status_source

        elif isinstance(self, CombatStatus):
            attached_active_character = StaticTarget(
                status_source.pid,
                zone=Zone.CHARACTERS,
                id=game_state.get_player(status_source.pid).just_get_active_character().get_id(),
            )
            return item.target == attached_active_character

        elif isinstance(self, sm.Summon):
            attached_active_character = StaticTarget(
                status_source.pid,
                zone=Zone.CHARACTERS,
                id=game_state.get_player(status_source.pid).just_get_active_character().get_id(),
            )
            return item.target == attached_active_character

        else:
            raise NotImplementedError  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FixedShieldStatus(_ShieldStatus, _UsageStatus):
    """ The shield status where only one usage can be consumed by a DMG effect """
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = 0  # shield amount per stack

    def _triggering_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            damage: eft.SpecificDamageEffect
    ) -> bool:
        return True

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_MINUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg) \
                    and self._triggering_condition(game_state, status_source, dmg):
                new_dmg_amount = max(0, dmg.damage - self.SHIELD_AMOUNT)
                new_dmg = replace(dmg, damage=new_dmg_amount)
                new_item = DmgPEvent(dmg=new_dmg)
                new_usages = self.usages - 1
                if self.AUTO_DESTROY and new_usages == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, usages=new_usages)

        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class StackedShieldStatus(_ShieldStatus, _UsageStatus):
    """ The shield status where all usages can be consumed by a DMG effect """
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = 1  # shield amount per usage

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_MINUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            assert self.usages <= type(self).MAX_USAGES
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg):
                usages_consumed = min(ceil(dmg.damage / self.SHIELD_AMOUNT), self.usages)
                new_dmg_amount = max(0, dmg.damage - usages_consumed * self.SHIELD_AMOUNT)
                new_dmg = replace(dmg, damage=new_dmg_amount)
                new_item = DmgPEvent(dmg=new_dmg)
                new_usages = self.usages - usages_consumed
                if new_usages == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, usages=new_usages)

        return super()._preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class PrepareSkillStatus(Status):
    pass


@dataclass(frozen=True, kw_only=True)
class RevivalStatus(Status):
    @abstractmethod
    def revivable(self, game_state: GameState, char: StaticTarget) -> bool:
        pass


@dataclass(frozen=True, kw_only=True)
class _InfusionStatus(_UsageStatus):
    MAX_USAGES: ClassVar[int] = BIG_INT
    ELEMENT: ClassVar[Element]
    damage_boost: int = 0
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        new_item: None | DmgPEvent = None
        if isinstance(item, DmgPEvent):
            dmg = item.dmg
            if signal is Preprocessables.DMG_ELEMENT:
                if self._dmg_element_condition(game_state, status_source, dmg):
                    new_item = replace(item, dmg=replace(dmg, element=self.ELEMENT))
            if signal is Preprocessables.DMG_AMOUNT_PLUS:
                if self.damage_boost != 0  \
                        and self._dmg_boost_condition(game_state, status_source, dmg):
                    new_item = replace(item, dmg=replace(
                        dmg, damage=dmg.damage + self.damage_boost))
        if new_item is not None:
            return new_item, self
        else:
            return item, self

    def _dmg_element_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is Element.PHYSICAL \
            and item.damage_type.direct_normal_attack() \
            and self._target_is_self_active(game_state, status_source, item.source)

    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return (
            item.element is self.ELEMENT
            and item.damage_type.directly_from_character()
            and self._target_is_self_active(game_state, status_source, item.source)
        )

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -1
        return [], replace(self, usages=d_usages)


############################## Hidden Status ##############################


@dataclass(frozen=True, kw_only=True)
class ArcaneLegendUsedStatus(PlayerHiddenStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class ChargedAttackStatus(PlayerHiddenStatus):
    """
    When present, character's normal attack of the player should be treated as charged-attack
    """
    can_charge: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.can_charge:
            return [], replace(self, can_charge=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class PlungeAttackStatus(PlayerHiddenStatus):
    can_plunge: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
    ))

    # @override
    # def _inform(
    #         self,
    #         game_state: GameState,
    #         status_source: StaticTarget,
    #         info_type: Informables,
    #         information: InformableEvent,
    # ) -> Self:
    #     if info_type is Informables.SKILL_USAGE:
    #         assert isinstance(information, SkillIEvent)
    #         if information.source == status_source \
    #                 and self.can_plunge:
    #             return replace(self, can_plunge=False)
    #     return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.can_plunge:
            return [], replace(self, can_plunge=False)
        elif signal is TriggeringSignal.ROUND_END and self.can_plunge:
            return [], replace(self, can_plunge=False)
        elif self._is_swapping_source(source, signal):
            if not self.can_plunge:
                return [], replace(self, can_plunge=True)
        return [], self

    @override
    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_plunge, '*', '')})"


@dataclass(frozen=True, kw_only=True)
class DeathThisRoundStatus(PlayerHiddenStatus):
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.CHARACTER_DEATH:
            assert isinstance(information, CharacterDeathIEvent)
            if not self.activated and information.target.pid == status_source.pid:
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            if self.activated:
                return [], replace(self, activated=False)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.activated, '*', '')})"

############################## Equipment Status ##############################

########## Weapon Status ##########


@dataclass(frozen=True, kw_only=True)
class _SacrificialWeaponStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False
    DICE_GAIN_NUM: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if (
                    self.usages > 0
                    and information.skill_type.is_elemental_skill()
                    and information.source == status_source
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            if self.activated:
                assert self.usages > 0
                equiper = game_state.get_character_target(source)
                assert equiper is not None
                return [
                    eft.AddDiceEffect(
                        pid=source.pid,
                        element=equiper.ELEMENT(),
                        num=self.DICE_GAIN_NUM,
                    )
                ], replace(self, activated=False, usages=-1)
        elif signal is TriggeringSignal.ROUND_END:
            if self.usages < self.MAX_USAGES:
                return [], replace(self, usages=self.MAX_USAGES)
        return [], self

#### Bow ####


@dataclass(frozen=True, kw_only=True)
class AmosBowStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 2

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import AmosBow
        return AmosBow

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.PRE_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if not (
                    self.usages > 0
                    and self._target_is_self_active(game_state, status_source, information.source)
            ):
                return self
            this_char = game_state.get_character_target(status_source)
            assert this_char is not None
            total_cost = (
                this_char.skill_cost(information.skill_type).num_dice()
                + this_char.skill_energy_cost(information.skill_type)
            )
            if total_cost < 5:
                return self
            return replace(self, activated=True)
        if info_type is Informables.POST_SKILL_USAGE and self.activated:
            return replace(self, activated=False)
        return self

    @override
    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        delta_dmg = self.BASE_DAMAGE_BOOST
        if not self.activated:
            return dmg.delta_damage(delta_dmg), self
        assert self.usages > 0
        delta_dmg += self.ADDITIONAL_DMG_BOOST
        return dmg.delta_damage(delta_dmg), replace(self, usages=self.usages - 1, activated=False)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class KingsSquireStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import KingsSquire
        return KingsSquire


@dataclass(frozen=True, kw_only=True)
class RavenBowStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import RavenBow
        return RavenBow


@dataclass(frozen=True, kw_only=True)
class SacrificialBowStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialBow
        return SacrificialBow

#### Catalyst ####


@dataclass(frozen=True, kw_only=True)
class AThousandFloatingDreamsStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST
    DMG_BOOST: ClassVar[int] = 1
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import AThousandFloatingDreams
        return AThousandFloatingDreams

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        item, new_self = super()._preprocess(game_state, status_source, item, signal)
        if new_self is None:
            return item, new_self
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    new_self.usages > 0
                    and dmg.source.pid is status_source.pid
                    and dmg.damage_type.directly_from_character()
                    and dmg.reaction is not None
            ):
                return (
                    item.delta_damage(new_self.DMG_BOOST),
                    replace(new_self, usages=new_self.usages - 1),
                )
        return item, new_self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FruitOfFulfillmentStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import FruitOfFulfillment
        return FruitOfFulfillment


@dataclass(frozen=True, kw_only=True)
class MagicGuideStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import MagicGuide
        return MagicGuide


@dataclass(frozen=True, kw_only=True)
class SacrificialFragmentsStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialFragments
        return SacrificialFragments

#### Claymore ####


@dataclass(frozen=True, kw_only=True)
class SacrificialGreatswordStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialGreatsword
        return SacrificialGreatsword


@dataclass(frozen=True, kw_only=True)
class TheBellStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import TheBell
        return TheBell

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if (
                    self.usages > 0
                    and not self.activated
                    and information.source == status_source
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            return [
                eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=RebelliousShieldStatus,
                ),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            assert not self.activated
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class WhiteIronGreatswordStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import WhiteIronGreatsword
        return WhiteIronGreatsword


@dataclass(frozen=True, kw_only=True)
class WolfsGravestoneStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE
    HP_THRESHOLD: ClassVar[int] = 6
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 2

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import WolfsGravestone
        return WolfsGravestone

    @override
    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        oppo_active_char = game_state.get_player(
            status_source.pid.other()
        ).just_get_active_character()
        final_dmg_boost = self.BASE_DAMAGE_BOOST
        if oppo_active_char.get_hp() <= self.HP_THRESHOLD:
            final_dmg_boost += self.ADDITIONAL_DMG_BOOST
        return dmg.delta_damage(final_dmg_boost), self


#### Polearm ####

@dataclass(frozen=True, kw_only=True)
class LithicSpearStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import LithicSpear
        return LithicSpear


@dataclass(frozen=True, kw_only=True)
class VortexVanquisherStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 1

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import VortexVanquisher
        return VortexVanquisher

    @override
    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        this_player = game_state.get_player(status_source.pid)
        active_char = this_player.just_get_active_character()
        final_dmg_boost = self.BASE_DAMAGE_BOOST
        if (
                any(
                    isinstance(status, StackedShieldStatus)
                    for status in this_player.get_combat_statuses()
                )
                or any(
                    isinstance(status, StackedShieldStatus)
                    for status in active_char.get_character_statuses()
                )
        ):
            final_dmg_boost += self.ADDITIONAL_DMG_BOOST
        return dmg.delta_damage(final_dmg_boost), self


@dataclass(frozen=True, kw_only=True)
class WhiteTasselStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import WhiteTassel
        return WhiteTassel

#### Sword ####


@dataclass(frozen=True, kw_only=True)
class AquilaFavoniaStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = False
    HP_RECOVERY: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import AquilaFavonia
        return AquilaFavonia

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if (
                    self.usages > 0
                    and not self.activated
                    and information.source.pid is status_source.pid.other()
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            if self._target_is_self_active(game_state, source, source):
                return [
                    eft.RecoverHPEffect(
                        target=source,
                        recovery=self.HP_RECOVERY,
                    ),
                ], replace(self, usages=-1, activated=False)
            else:
                return [], replace(self, usages=0, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class SacrificialSwordStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialSword
        return SacrificialSword


@dataclass(frozen=True, kw_only=True)
class TravelersHandySwordStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD

    @classproperty
    def WEAPON_CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import TravelersHandySword
        return TravelersHandySword


########## Artifact Status ##########


@dataclass(frozen=True, kw_only=True)
class GamblersEarringsStatus(ArtifactEquipmentStatus):
    informed_num: int = 0
    triggered_num: int = 0
    MAX_TRIGGER_NUM: ClassVar[int] = 3
    NUM_DICE_PER_TRIGGER: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.DEATH_EVENT,
    ))

    def triggerable(self) -> bool:
        return self.triggered_num < self.MAX_TRIGGER_NUM and self.informed_num > 0

    def informable(self) -> bool:
        return self.triggered_num + self.informed_num < self.MAX_TRIGGER_NUM

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.CHARACTER_DEATH:
            assert isinstance(information, CharacterDeathIEvent)
            if information.target.pid is status_source.pid.other() \
                    and self.informable():
                return replace(self, informed_num=self.informed_num + 1)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.DEATH_EVENT:
            if self.triggerable():
                this_player = game_state.get_player(source.pid)
                active_char_id = this_player.just_get_active_character().get_id()
                if active_char_id is not source.id:
                    return [], replace(self, informed_num=0)
                additions = self.informed_num * self.NUM_DICE_PER_TRIGGER
                return [
                    eft.AddDiceEffect(pid=source.pid, element=Element.OMNI, num=additions)
                ], replace(
                    self,
                    triggered_num=self.triggered_num + self.informed_num,
                    informed_num=0
                )
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({self.informed_num},{self.triggered_num})"


@dataclass(frozen=True, kw_only=True)
class GeneralsAncientHelmStatus(ArtifactEquipmentStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=UnmovableMountainStatus,
                ),
            ], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class InstructorsCapStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.REACTION_TRIGGERED:
            assert isinstance(information, ReactionIEvent)
            if (
                    not self.activated
                    and self.usages > 0
                    and information.source == status_source
                    and information.source_type.directly_from_character()
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            this_char = game_state.get_character_target(source)
            assert this_char is not None
            return [
                eft.AddDiceEffect(
                    pid=source.pid,
                    element=this_char.ELEMENT(),
                    num=1,
                ),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TenacityOfTheMillelithStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
        TriggeringSignal.ROUND_START,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DELT:
            assert isinstance(information, DmgIEvent)
            dmg = information.dmg
            if (
                    not self.activated
                    and self.usages > 0
                    and dmg.target == status_source
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG and self.activated:
            if not self._target_is_self_active(game_state, source, source):
                return [], replace(self, activated=False)
            this_char = game_state.get_character_target(source)
            assert this_char is not None
            return [
                eft.AddDiceEffect(
                    pid=source.pid,
                    element=this_char.ELEMENT(),
                    num=1,
                ),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=UnmovableMountainStatus,
                ),
            ], self
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


############################## Combat Status ##############################


@dataclass(frozen=True)
class CatalyzingFieldStatus(CombatStatus):
    damage_boost: ClassVar[int] = 1
    usages: int = 2

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | CatalyzingFieldStatus]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, eft.DmgPEvent)
            dmg = item.dmg
            assert self.usages >= 1
            elem_can_boost = dmg.element is Element.ELECTRO or dmg.element is Element.DENDRO
            legal_to_boost = status_source.pid is dmg.source.pid and dmg.damage_type.can_boost()
            target_is_active = dmg.target.id == game_state.get_player(
                dmg.target.pid
            ).just_get_active_character().get_id()
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(dmg, damage=dmg.damage + CatalyzingFieldStatus.damage_boost)
                new_item = DmgPEvent(dmg=new_damage)
                if self.usages == 1:
                    return new_item, None
                else:
                    return new_item, CatalyzingFieldStatus(self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class ChangingShiftsStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.dice_cost.num_dice() >= self.COST_DEDUCTION:
                assert item.dice_cost.num_dice() == item.dice_cost[Element.ANY]
                new_cost = (item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                return replace(item, dice_cost=new_cost), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class CrystallizeStatus(CombatStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2


@dataclass(frozen=True)
class DendroCoreStatus(CombatStatus):
    """
    When you deal Pyro DMG or Electro DMG to an opposing active character, DMG dealt +2.
    Usage(s): 1
    =====
    Experiment results:
    - normally the maxinum num of usage(s) is 1
    """
    damage_boost: ClassVar[int] = 2
    usages: int = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | DendroCoreStatus]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            assert self.usages >= 1
            elem_can_boost = dmg.element is Element.ELECTRO or dmg.element is Element.PYRO
            legal_to_boost = status_source.pid is dmg.source.pid and dmg.damage_type.can_boost()
            target_is_active = dmg.target.id == game_state.get_player(
                dmg.target.pid
            ).just_get_active_character().get_id()
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(dmg, damage=dmg.damage + DendroCoreStatus.damage_boost)
                new_item = DmgPEvent(dmg=new_damage)
                if self.usages == 1:
                    return new_item, None
                else:  # pragma: no cover
                    return new_item, DendroCoreStatus(self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    # @override
    # def update(self, other: DendroCoreStatus) -> DendroCoreStatus:
    #     total_count = min(self.count + other.count, 2)
    #     return DendroCoreStatus(total_count)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class IHaventLostYetOnCooldownStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceEnduringRockStatus(CombatStatus):
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DELT:
            assert isinstance(information, DmgIEvent)
            if (
                    not self.activated
                    and information.dmg.element is Element.GEO
                    and information.dmg.source.pid is status_source.pid
                    and information.dmg.damage_type.directly_from_character()
            ):
                return replace(self, activated=True)
                ...
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            if not self.activated:
                return [], self
            combat_statuses = game_state.get_player(source.pid).get_combat_statuses()
            stacked_shield_status = next((
                status
                for status in combat_statuses
                if isinstance(status, StackedShieldStatus)
            ), None)
            if stacked_shield_status is None:
                return [], replace(self, activated=False)
            assert isinstance(stacked_shield_status, CombatStatus)
            return [
                eft.OverrideCombatStatusEffect(
                    target_pid=source.pid,
                    status=replace(stacked_shield_status, usages=stacked_shield_status.usages + 3)
                )
            ], None
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceFerventFlamesStatus(CombatStatus):
    DMG_BOOST: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.reaction is not None
                    and dmg.reaction.elem_reaction(Element.PYRO)
                    and dmg.damage_type.from_character()
                    and self._target_is_self_active(game_state, status_source, dmg.source)
            ):
                return replace(item, dmg=replace(dmg, damage=dmg.damage + self.DMG_BOOST)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceShatteringIceStatus(CombatStatus):
    DMG_BOOST: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.damage_type.directly_from_character()
                    and self._target_is_self_active(game_state, status_source, dmg.source)
            ):
                return replace(item, dmg=replace(dmg, damage=dmg.damage + self.DMG_BOOST)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceSprawlingGreeneryStatus(CombatStatus):
    DMG_BOOST: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        # TODO
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.source.pid is status_source.pid
                    and dmg.reaction is not None
                    and dmg.damage_type.can_boost()
            ):
                return replace(item, dmg=replace(dmg, damage=dmg.damage + self.DMG_BOOST)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class KingsSquireEffectStatus(CharacterStatus):
    COST_DEDUCTION: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if (
                    item.source == status_source
                    and item.event_sub_type is CharacterSkillType.ELEMENTAL_SKILL
                    and item.dice_cost.can_cost_less_elem()
            ):
                new_cost = item.dice_cost.cost_less_elem(self.COST_DEDUCTION)
                return replace(item, dice_cost=new_cost), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class LeaveItToMeStatus(CombatStatus):
    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.event_speed is EventSpeed.COMBAT_ACTION:
                return replace(item, event_speed=EventSpeed.FAST_ACTION), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class RebelliousShieldStatus(CombatStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2


@dataclass(frozen=True, kw_only=True)
class ReviveOnCooldownStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FreshWindOfFreedomStatus(CombatStatus):
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.DEATH_EVENT,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.CHARACTER_DEATH:
            assert isinstance(information, CharacterDeathIEvent)
            if information.target.pid is status_source.pid.other() \
                    and game_state.get_player(status_source.pid).in_action_phase() \
                    and not self.activated:
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.DEATH_EVENT:
            if self.activated:
                return [eft.ConsecutiveActionEffect(target_pid=source.pid)], None
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class WhenTheCraneReturnedStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))
    triggered: bool = False

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source.pid is status_source.pid and not self.triggered:
                return replace(self, triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.triggered:
            return [
                eft.ForwardSwapCharacterEffect(source.pid),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class WhereIsTheUnseenRazorStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.CARD:
            assert isinstance(item, CardPEvent)
            from ..card.card import WeaponEquipmentCard
            if not (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, WeaponEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
            ):
                return replace(
                    item,
                    dice_cost=item.dice_cost.cost_less_elem(self.COST_DEDUCTION)
                ), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class WindAndFreedomStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))
    triggered: bool = False

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source.pid is status_source.pid and not self.triggered:
                return replace(self, triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.triggered:
            return [
                eft.ForwardSwapCharacterEffect(source.pid),
            ], replace(self, triggered=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


############################## Character Status ##############################

@dataclass(frozen=True)
class FrozenStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            can_reaction = dmg.element is Element.PYRO or dmg.element is Element.PHYSICAL
            is_damage_target = dmg.target == status_source
            if is_damage_target and can_reaction:
                return (
                    DmgPEvent(dmg=replace(dmg, damage=dmg.damage + FrozenStatus.damage_boost)),
                    None
                )
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | FrozenStatus]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True)
class JueyunGuobaStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.source == status_source and dmg.damage_type.direct_normal_attack():
                dmg = replace(dmg, damage=dmg.damage + JueyunGuobaStatus.DAMAGE_BOOST)
                return DmgPEvent(dmg=dmg), replace(self, usages=self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class LithicGuardStatus(CharacterStatus, StackedShieldStatus):
    MAX_USAGES: ClassVar[int] = 3


@dataclass(frozen=True)
class LotusFlowerCrispStatus(CharacterStatus, FixedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    SHIELD_AMOUNT: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -BIG_INT
        return [], replace(self, usages=d_usages)


@dataclass(frozen=True)
class MintyMeatRollsStatus(CharacterStatus, _UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if status_source == item.source \
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK \
                    and item.dice_cost[Element.ANY] >= self.COST_DEDUCTION:
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, replace(self, usages=self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -BIG_INT
        return [], replace(self, usages=d_usages)


@dataclass(frozen=True)
class MushroomPizzaStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            es.append(
                eft.RecoverHPEffect(
                    source,
                    1,
                )
            )
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -1

        return es, replace(self, usages=d_usages)


@dataclass(frozen=True)
class NorthernSmokedChickenStatus(CharacterStatus):
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if status_source == item.source \
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK \
                    and item.dice_cost[Element.ANY] >= self.COST_DEDUCTION:
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class SatiatedStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class TandooriRoastChickenStatus(CharacterStatus):
    DMG_BOOST: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                dmg.source == status_source
                and dmg.damage_type.direct_elemental_skill()
                and dmg.element is not Element.PIERCING
            ):
                return item.delta_damage(self.DMG_BOOST), None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class UnmovableMountainStatus(CharacterStatus, StackedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


############################## Character Specific Status ##############################
"""
Group statues by characters, characters ordered alphabetically
"""

#### Albedo ####


@dataclass(frozen=True, kw_only=True)
class DescentOfDivinityStatus(TalentEquipmentStatus):
    pass


#### Arataki Itto ####


@dataclass(frozen=True, kw_only=True)
class AratakiIchibanStatus(TalentEquipmentStatus, _UsageLivingStatus):
    usages: int = 0  # here means num of normal attacks in the past
    ACTIVATION_THRESHOLD: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    def activated(self) -> bool:
        return self.usages + 1 >= self.ACTIVATION_THRESHOLD

    @property
    def dmg_boost(self) -> int:
        return self.DAMAGE_BOOST

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated() \
                or info_type is not Informables.POST_SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent)
        if status_source != information.source \
                or information.skill_type != CharacterSkill.SKILL1:
            return self

        return replace(self, usages=self.usages + 1)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-self.usages)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class RagingOniKingStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2  # duration
    ELEMENT: ClassVar[Element] = Element.GEO
    damage_boost: int = 1
    status_gaining_usages: int = 1
    status_gaining_available: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return (
            super()._dmg_boost_condition(game_state, status_source, item)
            and item.damage_type.direct_normal_attack()
        )

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source == status_source \
                    and information.skill_type is CharacterSkill.SKILL1 \
                    and not self.status_gaining_available:
                return replace(self, status_gaining_available=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        elif signal is TriggeringSignal.COMBAT_ACTION:
            if self.status_gaining_available:
                return [
                    eft.AddCharacterStatusEffect(
                        target=source,
                        status=SuperlativeSuperstrengthStatus,
                    ),
                ], replace(self, usages=0, status_gaining_usages=0, status_gaining_available=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class SuperlativeSuperstrengthStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 3
    DAMAGE_BOOST: ClassVar[int] = 1
    TALENT_DAMAGE_BOOST: ClassVar[int] = 1
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.direct_charged_attack():
                character = game_state.get_character_target(status_source)
                assert character is not None, f"source {status_source} in {game_state}"
                dmg_boost = self.DAMAGE_BOOST
                if character.talent_equipped():
                    talent = character.get_equipment_statuses().just_find(AratakiIchibanStatus)
                    if talent.activated():
                        dmg_boost += talent.dmg_boost
                new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + dmg_boost))
                new_self = replace(self, usages=self.usages - 1)
                return new_item, new_self
        elif signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            if (
                    self.usages >= 2
                    and status_source == item.source
                    and item.event_type is EventType.SKILL1
                    and player.get_dice().is_even()
                    and item.dice_cost[Element.ANY] > 0
            ):
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, self
        return item, self


#### Bennett ####


@dataclass(frozen=True, kw_only=True)
class GrandExpectationStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class _InspirationFieldStatus(CombatStatus, _UsageStatus):
    usages: int = 2  # duration
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = False
    DMG_BOOST: ClassVar[int] = 2
    BOOST_LOCK: ClassVar[bool]
    HP_CAP: ClassVar[int] = 7
    RECOVERY: ClassVar[int] = 2

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    })

    def _boostable(self, char: Character) -> bool:
        return not self.BOOST_LOCK or char.get_hp() >= self.HP_CAP

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if self.activated:
                return self
            active_char_id = game_state.get_player(
                status_source.pid
            ).just_get_active_character().get_id()
            if information.source == StaticTarget(status_source.pid, Zone.CHARACTERS, active_char_id):
                return replace(self, activated=True)
        return self

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            active_char = game_state.get_player(status_source.pid).just_get_active_character()
            active_char_source = StaticTarget(
                status_source.pid,
                Zone.CHARACTERS,
                active_char.get_id(),
            )
            if not (
                    item.dmg.source == active_char_source
                    and item.dmg.damage_type.directly_from_character()
                    and self._boostable(active_char)
            ):
                return item, self
            return replace(item, dmg=replace(
                item.dmg, damage=item.dmg.damage + self.DMG_BOOST
            )), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            if not self.activated:
                return [], self
            active_char = game_state.get_player(source.pid).just_get_active_character()
            if active_char.get_hp() >= self.HP_CAP:
                return [], replace(self, usages=0, activated=False)
            return [
                eft.RecoverHPEffect(
                    target=StaticTarget(source.pid, Zone.CHARACTERS, active_char.get_id()),
                    recovery=self.RECOVERY,
                )
            ], replace(self, usages=0, activated=False)
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class InspirationFieldStatus(_InspirationFieldStatus):
    BOOST_LOCK: ClassVar[bool] = True


@dataclass(frozen=True, kw_only=True)
class InspirationFieldEnhancedStatus(_InspirationFieldStatus):
    BOOST_LOCK: ClassVar[bool] = False

#### Chongyun ####


@dataclass(frozen=True, kw_only=True)
class ChonghuasFrostFieldStatus(CombatStatus, _InfusionStatus):
    ELEMENT: ClassVar[Element] = Element.CRYO

    # TODO: other effects'll be implemented when Chongyun is implemented


#### Collei ####

@dataclass(frozen=True, kw_only=True)
class ColleiTalentStatus(HiddenStatus):
    """ Saves the elemental skill usages of Collei per round """
    elemental_skill_used: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if (
                    not self.elemental_skill_used
                    and information.source == status_source
                    and information.skill_type is CharacterSkill.SKILL2
            ):
                return replace(self, elemental_skill_used=True)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.elemental_skill_used:
            return [], replace(self, elemental_skill_used=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class FloralSidewinderStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class SproutStatus(CombatStatus, _UsageStatus):
    activated: bool = False
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DELT:
            assert isinstance(information, DmgIEvent)
            dmg = information.dmg
            if (
                    not self.activated
                    and dmg.source.pid is status_source.pid
                    and dmg.reaction is not None
                    and dmg.reaction.elem_reaction(Element.DENDRO)
                    and dmg.damage_type.directly_from_character()
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.DENDRO,
                    damage=1,
                    damage_type=DamageType(status=True),
                )
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


#### Dehya ####


@dataclass(frozen=True, kw_only=True)
class IncinerationDriveStatus(CharacterStatus, PrepareSkillStatus):
    DAMAGE: ClassVar[int] = 3
    DMG_ELEM: ClassVar[Element] = Element.PYRO

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
        TriggeringSignal.ACT_PRE_SKILL,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ACT_PRE_SKILL:
            return [
                eft.RemoveCharacterStatusEffect(
                    target=source,
                    status=type(self),
                ),
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.DMG_ELEM,
                    damage=self.DAMAGE,
                    damage_type=DamageType(elemental_burst=True, status=True),
                ),
            ], self
        elif self._is_swapping_source(source, signal):
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class StalwartAndTrueStatus(TalentEquipmentStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.END_ROUND_CHECK_OUT,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            this_char = game_state.get_character_target(source)
            assert this_char is not None
            if (
                    this_char.alive()
                    and this_char.get_hp() <= 6
            ):
                return [eft.RecoverHPEffect(
                    target=source,
                    recovery=2,
                )], self
        return [], self

#### Electro Hypostasis ####


@dataclass(frozen=True, kw_only=True)
class ElectroCrystalCoreHiddenStatus(HiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.GAME_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=ElectroCrystalCoreStatus,
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElectroCrystalCoreStatus(CharacterStatus, RevivalStatus):
    _HEAL_AMOUNT: ClassVar[int] = 3
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.TRIGGER_REVIVAL,
    })

    @override
    def revivable(self, game_state: GameState, char: StaticTarget) -> bool:
        return True

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.TRIGGER_REVIVAL:
            character = game_state.get_character_target(source)
            assert character is not None
            assert character.get_hp() == 0
            return [], None
        return [], self

    @override
    def _post_update_react_to_signal(
            self,
            game_state: GameState,
            effects: list[eft.Effect],
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> list[eft.Effect]:
        if signal is TriggeringSignal.TRIGGER_REVIVAL:
            effects.append(
                eft.ReviveRecoverHPEffect(
                    target=source,
                    recovery=self._HEAL_AMOUNT,
                )
            )
        return effects


@dataclass(frozen=True, kw_only=True)
class RockPaperScissorsComboPaperStatus(CharacterStatus, PrepareSkillStatus):
    DAMAGE: ClassVar[int] = 3

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
        TriggeringSignal.ACT_PRE_SKILL,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ACT_PRE_SKILL:
            return [
                eft.RemoveCharacterStatusEffect(
                    target=source,
                    status=type(self),
                ),
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.ELECTRO,
                    damage=self.DAMAGE,
                    damage_type=DamageType(elemental_skill=True, status=True),
                ),
            ], self
        elif self._is_swapping_source(source, signal):
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class RockPaperScissorsComboScissorsStatus(CharacterStatus, PrepareSkillStatus):
    DAMAGE: ClassVar[int] = 2

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
        TriggeringSignal.ACT_PRE_SKILL,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ACT_PRE_SKILL:
            return [
                eft.RemoveCharacterStatusEffect(
                    target=source,
                    status=type(self),
                ),
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.ELECTRO,
                    damage=self.DAMAGE,
                    damage_type=DamageType(elemental_skill=True, status=True),
                ),
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=RockPaperScissorsComboPaperStatus,
                ),
            ], self
        elif self._is_swapping_source(source, signal):
            return [], None
        return [], self


#### Fatui Pyro Agent ####

@dataclass(frozen=True, kw_only=True)
class PaidInFullStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class StealthMasterStatus(HiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.GAME_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=StealthStatus,
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class StealthStatus(CharacterStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_BOOST: ClassVar[int] = 1
    INFUSION_ELEMENT: ClassVar[Element] = Element.PYRO

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.source == status_source and dmg.damage_type.directly_from_character():
                return item.delta_damage(self.DAMAGE_BOOST), replace(self, usages=self.usages - 1)
        elif signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source == status_source
                    and dmg.element is Element.PHYSICAL
                    and dmg.damage_type.directly_from_character()
            ):
                return item, self
            char = game_state.get_character_target(status_source)
            assert char is not None
            if not char.talent_equipped():
                return item, self
            return item.convert_element(self.INFUSION_ELEMENT), self

        return super()._preprocess(game_state, status_source, item, signal)


#### Fischl ####

@dataclass(frozen=True, kw_only=True)
class StellarPredatorStatus(TalentEquipmentStatus):
    pass


#### Ganyu ####

@dataclass(frozen=True, kw_only=True)
class GanyuTalentStatus(HiddenStatus):
    elemental_skill2ed: bool = False

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.is_skill_from_character(
                    game_state,
                    status_source.pid,
                    CharacterSkill.SKILL3,
            ):
                return replace(self, elemental_skill2ed=True)
        return self


@dataclass(frozen=True, kw_only=True)
class IceLotusStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class UndividedHeartStatus(TalentEquipmentStatus):
    pass


#### Hu Tao ####


@dataclass(frozen=True, kw_only=True)
class BloodBlossomStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            return [
                eft.SpecificDamageEffect(
                    source=source,
                    target=source,
                    element=Element.PYRO,
                    damage=1,
                    damage_type=DamageType(no_boost=True, status=True),
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ParamitaPapilioStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2
    ELEMENT: ClassVar[Element] = Element.PYRO
    damage_boost: int = 1


@dataclass(frozen=True, kw_only=True)
class SanguineRougeStatus(TalentEquipmentStatus):
    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            this_char = game_state.get_character_target(status_source)
            assert this_char is not None
            if (
                    item.dmg.source == status_source
                    and item.dmg.element is Element.PYRO
                    and item.dmg.damage_type.directly_from_character()
                    and this_char.get_hp() <= 6
            ):
                return item.delta_damage(1), self
        return item, self


#### Jadeplume Terrorshroom ##

@dataclass(frozen=True, kw_only=True)
class ProliferatingSporesStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class RadicalVitalityHiddenStatus(HiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.GAME_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=RadicalVitalityStatus,
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class RadicalVitalityStatus(CharacterStatus, _UsageLivingStatus):
    activated: bool = False
    to_clear: bool = False
    usages: int = 0
    NOMINAL_MAX_USAGES: ClassVar[int] = 3
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.POST_DMG,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    })

    def max_usages(self, game_state: GameState, source: StaticTarget) -> int:
        return self.NOMINAL_MAX_USAGES + (
            1
            if self.talent_equiped(game_state, source)
            else 0
        )

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DELT:
            assert isinstance(information, DmgIEvent)
            dmg = information.dmg
            if (
                not self.activated
                and (
                    (
                    dmg.source == status_source
                    and dmg.element.is_pure_element()
                    and dmg.damage_type.directly_from_character()
                    )
                    or (
                    dmg.target == status_source
                    and dmg.element.is_pure_element()
                    )
                )
                and self.usages < self.max_usages(game_state, status_source)
            ):
                return replace(self, activated=True)
        return self

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                dmg.source == status_source
                and dmg.damage_type.direct_elemental_burst()
            ):
                return item.delta_damage(self.usages), replace(self, to_clear=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            d_usages = 0
            if self.activated:
                d_usages = 1
            if self.to_clear:
                d_usages = -self.usages
            if d_usages == 0:
                return [], self
            assert self.usages + d_usages <= self.max_usages(game_state, source)
            return [], replace(self, usages=d_usages, activated=False, to_clear=False)
        elif signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            if self.usages >= self.max_usages(game_state, source):
                char = game_state.get_character_target(source)
                assert char is not None
                return [
                    eft.EnergyDrainEffect(
                        target=source,
                        drain=char.get_max_energy(),
                    ),
                ], replace(self, usages=-self.usages)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + \
            f"({'*' if self.activated else '' }|{'*' if self.to_clear else ''})"


#### Jean ####

@dataclass(frozen=True, kw_only=True)
class LandsOfDandelionStatus(TalentEquipmentStatus):
    pass


#### Kaedehara Kazuha ####


@dataclass(frozen=True, kw_only=True)
class MidareRanzanStatus(CharacterStatus):
    _protected: bool = True
    _needs_removal: bool = False
    _ELEMENT: ClassVar[Element] = Element.ANEMO
    _DMG_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source == status_source \
                    and not self._protected \
                    and not self._needs_removal:
                return replace(self, _needs_removal=True)
        return self

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if isinstance(item, DmgPEvent):
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self

            if signal is Preprocessables.DMG_ELEMENT:
                if dmg.damage_type.direct_plunge_attack():
                    new_item = DmgPEvent(dmg=replace(dmg, element=self._ELEMENT))
                    return new_item, self
            elif signal is Preprocessables.DMG_AMOUNT_PLUS:
                if dmg.damage_type.direct_plunge_attack():
                    new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + self._DMG_BOOST))
                    return new_item, None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            if self._protected:
                return [], replace(self, _protected=False)
            elif self._needs_removal:
                return [], None
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({self._protected}, {self._needs_removal})"


@dataclass(frozen=True, kw_only=True)
class MidareRanzanCryoStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class MidareRanzanElectroStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.ELECTRO


@dataclass(frozen=True, kw_only=True)
class MidareRanzanHydroStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class MidareRanzanPyroStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.PYRO


_MIDARE_RANZAN_MAP: dict[Element, type[MidareRanzanStatus]] = HashableDict({
    Element.ANEMO: MidareRanzanStatus,
    Element.CRYO: MidareRanzanCryoStatus,
    Element.ELECTRO: MidareRanzanElectroStatus,
    Element.HYDRO: MidareRanzanHydroStatus,
    Element.PYRO: MidareRanzanPyroStatus,
})


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class _PoeticsOfFuubutsuElementStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    _ELEM: Element
    _DMG_BOOST: ClassVar[int] = 1
    _BOOSTABLE_ELEMS: ClassVar[frozenset[Element]] = Reaction.SWIRL.value.reaction_elems[0]

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    status_source.pid != dmg.source.pid
                    or not (
                        dmg.damage_type.directly_from_character()
                        or dmg.damage_type.directly_from_summon()
                    )
                    or dmg.element is not self._ELEM
            ):
                return item, self

            assert self.usages > 0
            new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + self._DMG_BOOST))
            return new_item, replace(self, usages=self.usages - 1)
        return item, self


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuCryoStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuElectroStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.ELECTRO


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuHydroStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuPyroStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.PYRO


_POETICS_OF_FUUBUTSU_MAP: dict[Element, type[_PoeticsOfFuubutsuElementStatus]] = HashableDict({
    Element.CRYO: PoeticsOfFuubutsuCryoStatus,
    Element.ELECTRO: PoeticsOfFuubutsuElectroStatus,
    Element.HYDRO: PoeticsOfFuubutsuHydroStatus,
    Element.PYRO: PoeticsOfFuubutsuPyroStatus,
})

#### Kaeya ####


@dataclass(frozen=True, kw_only=True)
class IcicleStatus(CombatStatus, _UsageStatus):
    usages: int = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
    ))

    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | IcicleStatus]:
        if self._is_swapping_source(source, signal):
            effects: list[eft.Effect] = [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.CRYO,
                    damage=2,
                    damage_type=DamageType(status=True),
                ),
            ]
            return effects, replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ColdBloodedStrikeStatus(TalentEquipmentStatus):
    """
    Equipping this status implies the equipped character is Kaeya
    """
    usages: int = 1
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated or self.usages == 0:
            return self

        if info_type is not Informables.POST_SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent)
        if status_source != information.source \
                or information.skill_type != CharacterSkill.SKILL2:
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            assert self.usages >= 1
            es.append(
                eft.RecoverHPEffect(
                    target=source,
                    recovery=2,
                )
            )
            new_self = replace(new_self, usages=self.usages - 1, activated=False)

        elif signal is TriggeringSignal.ROUND_END:
            new_self = type(self)(usages=1, activated=False)

        return es, new_self

    def __str__(self) -> str:
        return super().__str__() + case_val(self.activated, "(*)", '')

#### Keqing ####


@dataclass(frozen=True, kw_only=True)
class KeqingTalentStatus(HiddenStatus):
    can_infuse: bool
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | KeqingTalentStatus]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            return [], type(self)(can_infuse=False)
        return [], self  # pragma: no cover

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_infuse, 1, 0)})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ThunderingPenanceStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class KeqingElectroInfusionStatus(CharacterStatus, _InfusionStatus):
    ELEMENT: ClassVar[Element] = Element.ELECTRO

    def __str__(self) -> str:
        return super().__str__() + f"({self.damage_boost})"

#### Klee ####


@dataclass(frozen=True, kw_only=True)
class ExplosiveSparkStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.direct_charged_attack():
                new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + self.DAMAGE_BOOST))
                new_self = replace(self, usages=self.usages - 1)
                return new_item, new_self
        elif signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            if (
                    status_source == item.source
                    and item.event_type is EventType.SKILL1
                    and player.get_dice().is_even()
                    and item.dice_cost[Element.ANY] + item.dice_cost[Element.PYRO] > 0
            ):
                elems = [Element.PYRO, Element.ANY]
                cost_deduction_left = self.COST_DEDUCTION
                deduction: dict[Element, int] = {}
                for elem in elems:
                    deduction[elem] = cost_deduction_left
                    cost_deduction_left -= item.dice_cost[elem]
                    if cost_deduction_left <= 0:
                        break
                if item.dice_cost[Element.PYRO] > 0:
                    item = replace(
                        item,
                        dice_cost=(item.dice_cost - deduction).validify()
                    )
                return item, self
        return item, self


@dataclass(frozen=True, kw_only=True)
class PoundingSurpriseStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class SparksnSplashStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated or self.usages == 0:
            return self

        if info_type is not Informables.POST_SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent), information
        if status_source.pid is not information.source.pid:
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            assert self.usages >= 1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.SELF_SELF,
                    element=Element.PYRO,
                    damage=2,
                    damage_type=DamageType(status=True, no_boost=True)
                )
            )
            new_self = replace(new_self, usages=-1, activated=False)

        return es, new_self


#### Maguu Kenki ####

@dataclass(frozen=True, kw_only=True)
class TranscendentAutomatonStatus(TalentEquipmentStatus):
    pass


#### Mona ####


@dataclass(frozen=True, kw_only=True)
class IllusoryBubbleStatus(CombatStatus):
    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_MUL:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source.pid is status_source.pid
                    and item.dmg.damage_type.directly_from_character()
            ):
                return replace(item, dmg=replace(item.dmg, damage=item.dmg.damage * 2)), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class IllusoryTorrentStatus(HiddenStatus):
    available: bool = True
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if self.available \
                    and item.source == status_source \
                    and item.event_speed is EventSpeed.COMBAT_ACTION:
                return replace(
                    item, event_speed=EventSpeed.FAST_ACTION
                ), replace(self, available=False)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        new_self = self
        if signal is TriggeringSignal.ROUND_END:
            if not self.available:
                new_self = replace(new_self, available=True)
        return [], new_self

    def __str__(self) -> str:
        return super().__str__() + f"({'*' if self.available else ''})"


@dataclass(frozen=True, kw_only=True)
class ProphecyOfSubmersionStatus(TalentEquipmentStatus):
    DMG_BOOST: ClassVar[int] = 2

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.source.pid is status_source.pid
                    and dmg.damage_type.can_boost()
                    and dmg.reaction is not None
                    and dmg.reaction.elem_reaction(Element.HYDRO)
                    and (
                        game_state.get_player(
                            status_source.pid
                        ).just_get_active_character().get_id() == status_source.id
                    )
            ):
                dmg = replace(dmg, damage=dmg.damage + self.DMG_BOOST)
                return DmgPEvent(dmg=dmg), self
        return super()._preprocess(game_state, status_source, item, signal)

#### Nahida ####


@dataclass(frozen=True, kw_only=True)
class SeedOfSkandhaStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    activated_usages: int = 0
    priority: int = 0

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_REACTION,
    ))

    @override
    def inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> GameState:
        if info_type is Informables.DMG_DELT:
            assert isinstance(information, DmgIEvent)
            if (
                    self.usages == 0
                    or information.dmg.reaction is None
                    or information.dmg.target != status_source
            ):
                return game_state
            chars = game_state.get_player(status_source.pid).get_characters()
            this_char = chars.get_character(cast(int, status_source.id))
            assert this_char is not None
            if type(self) not in this_char.get_character_statuses():
                return game_state
            base_priority = 0
            for char in chars:
                if char is this_char:
                    continue
                if (status := char.get_character_statuses().find(type(self))) is not None:
                    assert isinstance(status, type(self))
                    base_priority = max(base_priority, status.priority)
            return eft.OverrideCharacterStatusEffect(
                target=status_source,
                status=replace(self, activated_usages=self.activated_usages +
                               1, priority=base_priority + 1)
            ).execute(game_state)
        return game_state

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_REACTION:
            if self.activated_usages == 0:
                return [], self
            dmg_element: Element
            oppo_player = game_state.get_player(source.pid.other())
            oppo_chars = oppo_player.get_characters()
            from ..character.character import Nahida
            if (
                    any(char.talent_equipped() for char in oppo_chars if isinstance(char, Nahida))
                    and ShrineOfMayaStatus in oppo_player.get_combat_statuses()
                    and any(char.ELEMENT() is Element.PYRO for char in oppo_chars)
            ):
                dmg_element = Element.DENDRO
            else:
                dmg_element = Element.PIERCING
            return [eft.SpecificDamageEffect(
                source=source,
                target=source,
                element=dmg_element,
                damage=1,
                damage_type=DamageType(status=True, no_boost=True),
            )], replace(self, usages=-1, activated_usages=-1, priority=0)
        return [], self

    @override
    def _post_update_react_to_signal(
            self,
            game_state: GameState,
            effects: list[eft.Effect],
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> list[eft.Effect]:
        if signal is TriggeringSignal.POST_REACTION:
            if self.activated_usages == 0:
                return effects
            characters = game_state.get_player(source.pid).get_characters()
            assert isinstance(source.id, int)
            ordered_chars = characters.get_character_ordered_from_id(source.id)
            for char in ordered_chars[1:]:
                status = char.get_character_statuses().find(type(self))
                if status is not None:
                    assert isinstance(status, type(self))
                    char_source = replace(source, id=char.get_id())
                    effects += (
                        eft.SpecificDamageEffect(
                            source=char_source,
                            target=char_source,
                            element=Element.PIERCING,
                            damage=1,
                            damage_type=DamageType(status=True, no_boost=True),
                        ),
                        eft.UpdateCharacterStatusEffect(
                            target=char_source,
                            status=replace(status, usages=-1),
                        )
                    )
            return effects
        return effects

    @override
    def _update(self, other: Self) -> None | Self:
        new_self = super()._update(other)
        if new_self is None:
            return None
        return replace(new_self, activated_usages=self.activated_usages + other.activated_usages)


@dataclass(frozen=True, kw_only=True)
class ShrineOfMayaStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source.pid is status_source.pid
                    and dmg.damage_type.directly_from_character()
                    and dmg.reaction is not None
            ):
                return item, self
            dmg = replace(dmg, damage=dmg.damage + self.DAMAGE_BOOST)
            return DmgPEvent(dmg=dmg), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheSeedOfStoredKnowledgeStatus(TalentEquipmentStatus):
    pass


#### Ningguang ####

@dataclass(frozen=True, kw_only=True)
class JadeScreenStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_THRESHOLD: ClassVar[int] = 2

    @override
    def _triggering_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            damage: eft.SpecificDamageEffect
    ) -> bool:
        return damage.damage >= self.DAMAGE_THRESHOLD

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.element is Element.GEO
                    and item.dmg.source.pid is status_source.pid
                    and item.dmg.damage_type.can_boost()
            ):
                active_char = game_state.get_player(status_source.pid).just_get_active_character()
                from ..character.character import Ningguang
                if isinstance(active_char, Ningguang) and active_char.talent_equipped():
                    return item.delta_damage(1), self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class StrategicReserveStatus(TalentEquipmentStatus):
    pass


#### Noelle ####

@dataclass(frozen=True, kw_only=True)
class FullPlateStatus(CombatStatus, StackedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    heal_usages: int = 1
    MAX_HEAL_USAGES: ClassVar[int] = 1
    HEAL_AMOUNT: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_MUL:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.element is Element.PHYSICAL
                    and self._target_is_self_active(game_state, status_source, item.dmg.target)
            ):
                from math import ceil
                return replace(item, dmg=replace(item.dmg, damage=ceil(item.dmg.damage / 2))), self
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            if self.heal_usages <= 0:
                return [], self
            this_player = game_state.get_player(source.pid)
            char_self = this_player.just_get_active_character()
            if not char_self.talent_equipped():
                return [], self
            effects: list[eft.Effect] = []
            for char in this_player.get_characters().get_character_in_activity_order():
                if char.alive():
                    effects.append(eft.RecoverHPEffect(
                        target=StaticTarget(source.pid, Zone.CHARACTERS, char.get_id()),
                        recovery=self.HEAL_AMOUNT,
                    ))
            return effects, replace(self, usages=0, heal_usages=self.heal_usages - 1)
        elif signal is TriggeringSignal.ROUND_END:
            if self.heal_usages < self.MAX_HEAL_USAGES:
                return [], replace(self, heal_usages=self.MAX_HEAL_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class IGotYourBackStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class SweepingTimeStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2  # duration
    ELEMENT: ClassVar[Element] = Element.GEO
    damage_boost: int = 2
    dice_reduction_usages: int = 1
    DICE_REDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return (
            super()._dmg_boost_condition(game_state, status_source, item)
            and item.damage_type.direct_normal_attack()
        )

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if (
                    self.dice_reduction_usages > 0
                    and status_source == item.source
                    and item.event_type is EventType.SKILL1
                    and item.dice_cost[Element.GEO] >= self.DICE_REDUCTION
            ):
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.GEO: self.DICE_REDUCTION}).validify()
                )
                return item, replace(self, dice_reduction_usages=self.dice_reduction_usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1, dice_reduction_usages=1)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({self.dice_reduction_usages})"


#### Qiqi ####

@dataclass(frozen=True, kw_only=True)
class FortunePreservingTalismanStatus(CombatStatus, _UsageStatus):
    """
    Tested, Qiqi's burst doesn't trigger this status
    """
    usages: int = 3
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 3
    HEAL_AMOUNT: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            from ..character.character import Qiqi
            if (
                    not self.activated
                    and information.is_skill_from_character(game_state, status_source.pid)
                    and not information.is_skill_from_character(
                        game_state,
                        status_source.pid,
                        CharacterSkill.ELEMENTAL_BURST,
                        Qiqi,
                    )
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            active_char = game_state.get_player(source.pid).just_get_active_character()
            if active_char.hp_lost() == 0:
                return [], replace(self, usages=0, activated=False)
            return [
                eft.RecoverHPEffect(
                    target=StaticTarget.from_char_id(source.pid, active_char.get_id()),
                    recovery=self.HEAL_AMOUNT,
                )
            ], replace(self, usages=-1, activated=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class QiqiTalentStatus(HiddenStatus):
    revival_count: int = 0
    MAX_COUNT: ClassVar[int] = 2

    def revivable(self) -> bool:
        return self.revival_count < self.MAX_COUNT

    def __str__(self) -> str:
        return super().__str__() + f"({self.revival_count})"


@dataclass(frozen=True, kw_only=True)
class RiteOfResurrectionStatus(TalentEquipmentStatus):
    pass


#### Rhodeia of Loch ####


@dataclass(frozen=True, kw_only=True)
class StreamingSurgeStatus(TalentEquipmentStatus):
    pass


#### Sangonomiya Kokomi ####

@dataclass(frozen=True, kw_only=True)
class CeremonialGarmentStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.source == status_source
                    and dmg.damage_type.direct_normal_attack()
            ):
                return item.delta_damage(self.DAMAGE_BOOST), replace(self, activated=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            self_chars = game_state.get_player(source.pid).get_characters()
            return [
                eft.RecoverHPEffect(
                    target=StaticTarget.from_char_id(source.pid, char.get_id()),
                    recovery=1,
                )
                for char in self_chars.get_alive_character_in_activity_order()
            ], replace(self, usages=0, activated=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TamakushiCasketStatus(TalentEquipmentStatus):
    pass


#### Shenhe ####


@dataclass(frozen=True, kw_only=True)
class IcyQuillStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 3
    DMG_BOOST: ClassVar[int] = 1
    normal_attack_deduction_usages: int = 1
    DEFAULT_NORMAL_ATTACK_DEDUCTION_USAGES: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source.pid is status_source.pid
                    and dmg.element is Element.CRYO
                    and dmg.damage_type.from_character()
            ):
                return item, self
            dmg = replace(dmg, damage=dmg.damage + self.DMG_BOOST)
            from ..character.character import Shenhe
            new_self = self
            if (
                self.normal_attack_deduction_usages > 0
                and any(
                    char.talent_equipped()
                    for char in game_state.get_player(status_source.pid).get_characters()
                    if isinstance(char, Shenhe)
                )
                and dmg.damage_type.direct_normal_attack()
            ):
                # if talent equipped and triggered
                d_usages = 0
                new_self = replace(
                    new_self,
                    normal_attack_deduction_usages=self.normal_attack_deduction_usages - 1,
                )
            else:
                new_self = replace(new_self, usages=self.usages - 1)
            return DmgPEvent(dmg=dmg), new_self
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            if self.normal_attack_deduction_usages < self.DEFAULT_NORMAL_ATTACK_DEDUCTION_USAGES:
                return [], replace(
                    self,
                    usages=0,
                    normal_attack_deduction_usages=self.DEFAULT_NORMAL_ATTACK_DEDUCTION_USAGES,
                )
        return [], self


@dataclass(frozen=True, kw_only=True)
class MysticalAbandonStatus(TalentEquipmentStatus):
    pass


#### Tighnari ####


@dataclass(frozen=True, kw_only=True)
class KeenSightStatus(TalentEquipmentStatus):
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            characters = player.get_characters()
            if (
                    status_source == item.source
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK
                    and player.get_dice().is_even()
                    and characters.just_get_character(
                        cast(int, status_source.id)
                    ).get_character_statuses().contains(VijnanaSuffusionStatus)
                    and item.dice_cost[Element.ANY] > 0
            ):
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class VijnanaSuffusionStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if (
                self.activated
                or self.usages == 0
                or not isinstance(information, DmgIEvent)
                or status_source != information.dmg.source
                or not information.dmg.damage_type.direct_charged_attack()
        ):
            return self

        return replace(self, activated=True)

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        new_item: None | DmgPEvent = None
        if signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.direct_charged_attack():
                new_item = DmgPEvent(dmg=replace(dmg, element=Element.DENDRO))
        if new_item is not None:
            return new_item, self
        else:
            return item, self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            from ..summon.summon import ClusterbloomArrowSummon
            assert self.usages >= 1
            es.append(
                eft.AddSummonEffect(
                    target_pid=source.pid,
                    summon=ClusterbloomArrowSummon,
                )
            )
            new_self = replace(new_self, usages=-1, activated=False)

        return es, new_self

    @override
    def _update(self, other: Self) -> None | Self:
        new_usages = min(self.usages + other.usages, self.MAX_USAGES)
        return type(self)(
            usages=new_usages,
            activated=other.activated,
        )

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages}{case_val(self.activated, '*', '')})"

#### Venti ####


@dataclass(frozen=True, kw_only=True)
class EmbraceOfWindsStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class StormzoneStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    triggered: bool = False
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.dice_cost.num_dice() >= self.COST_DEDUCTION:
                assert item.dice_cost.num_dice() == item.dice_cost[Element.ANY]
                assert not self.triggered
                new_cost = (item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                return replace(item, dice_cost=new_cost), replace(self, triggered=True)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if self.triggered and self._is_swapping_source(source, signal):
            from ..character.character import Venti
            has_talent = any(
                char.talent_equipped()
                for char in game_state.get_player(source.pid).get_characters()
                if isinstance(char, Venti)
            )
            effects: list[eft.Effect] = []
            if has_talent:
                effects.append(eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=WindsOfHarmonyStatus,
                ))
            return effects, replace(self, usages=-1, triggered=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class WindsOfHarmonyStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if status_source.pid is item.source.pid \
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK \
                    and item.dice_cost[Element.ANY] >= self.COST_DEDUCTION:
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self

#### Xingqiu ####


@dataclass(frozen=True, kw_only=True)
class RainSwordStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_THRESHOLD: ClassVar[int] = 3
    TALENT_DMG_THRESHOLD: ClassVar[int] = 2

    @override
    def _triggering_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            damage: eft.SpecificDamageEffect
    ) -> bool:
        from ..character.character import Xingqiu
        talent_equipped = any(
            True
            for char in game_state.get_player(status_source.pid).get_characters()
            if (
                isinstance(char, Xingqiu)
                and char.talent_equipped()
            )
        )
        return damage.damage >= (
            self.TALENT_DMG_THRESHOLD if talent_equipped else self.DAMAGE_THRESHOLD
        )


@dataclass(frozen=True, kw_only=True)
class RainbowBladeworkStatus(CombatStatus, _UsageStatus):
    activated: bool = False
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DAMAGE: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.HYDRO

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if (
                not isinstance(information, SkillIEvent)
                or information.skill_true_type is not CharacterSkillType.NORMAL_ATTACK
                or status_source.pid is not information.source.pid
        ):
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            assert self.usages >= 1
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DAMAGE,
                    damage_type=DamageType(status=True),
                )
            ], replace(self, usages=-1, activated=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheScentRemainedStatus(TalentEquipmentStatus):
    pass

#### Yae Miko ####


@dataclass(frozen=True, kw_only=True)
class RiteOfDispatchStatus(CharacterStatus):
    COST_DEDUCTION: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        """
        The assumption here is the equiper only pay elemental skill with electro or omni dice
        """
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if (
                    status_source == item.source
                    and item.event_type is EventType.SKILL2
                    and item.dice_cost.num_dice() > 0
            ):
                item = replace(
                    item,
                    dice_cost=(item.dice_cost - {Element.ELECTRO: self.COST_DEDUCTION}).validify()
                )
                return item, None
        return item, self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class TenkoThunderboltsStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.PRE_ACTION,
    ))

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.PRE_ACTION:
            if game_state.get_active_player_id() is source.pid:
                return [
                    eft.ReferredDamageEffect(
                        source=source,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        element=Element.ELECTRO,
                        damage=3,
                        damage_type=DamageType(status=True),
                    ),
                ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheShrinesSacredShadeStatus(TalentEquipmentStatus):
    pass


#### Yoimiya ####

@dataclass(frozen=True, kw_only=True)
class AurousBlazeStatus(CombatStatus, _UsageStatus):
    usages: int = 2  # duration
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated:
            return self

        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if status_source.pid is not information.source.pid:
                return self
            source_char = game_state.get_character_target(information.source)
            assert source_char is not None
            from ..character.character import Yoimiya
            if isinstance(source_char, Yoimiya):
                return self
            return replace(self, activated=True)

        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
            assert self.usages >= 1
            return [eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=1,
                damage_type=DamageType(status=True),
            )], replace(self, usages=0, activated=False)

        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)

        return [], self


@dataclass(frozen=True, kw_only=True)
class NaganoharaMeteorSwarmStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class NiwabiEnshouStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = False
    DAMAGE_BOOST: ClassVar[int] = 1
    INFUSION_ELEMENT: ClassVar[Element] = Element.PYRO

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.source == status_source and dmg.damage_type.direct_normal_attack():
                return item.delta_damage(self.DAMAGE_BOOST), (
                    self
                    if self.activated
                    else replace(self, activated=True)
                )
        elif signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source == status_source
                    and dmg.element is Element.PHYSICAL
                    and dmg.damage_type.directly_from_character()
            ):
                return item, self
            return item.convert_element(self.INFUSION_ELEMENT), (
                self
                if self.activated
                else replace(self, activated=True)
            )

        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            if self.activated:
                this_char = game_state.get_character_target(source)
                assert this_char is not None
                return (
                    []
                    if not this_char.talent_equipped()
                    else [eft.ReferredDamageEffect(
                        source=source,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        element=Element.PYRO,
                        damage=1,
                        damage_type=DamageType(status=True),
                    )]
                ), replace(self, usages=-1, activated=False)
        return [], self
