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
from dataclasses import dataclass, replace
from enum import Enum
from math import ceil
from typing import ClassVar, cast, Optional, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft

from ..character.enums import CharacterSkill, WeaponType
from ..dices import ActualDices
from ..effect.enums import Zone, TriggeringSignal, DynamicCharacterTarget
from ..effect.structs import StaticTarget, DamageType
from ..element import Element, Reaction
from ..event import *
from ..helper.hashable_dict import HashableDict
from ..helper.quality_of_life import just, BIG_INT, case_val
from .enums import Preprocessables, Informables

if TYPE_CHECKING:
    from ..card.card import Card
    from ..character.character import Character
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

    # templates
    "StackedShieldStatus",
    "FixedShieldStatus",
    "PrepareSkillStatus",
    "RevivalStatus",

    # hidden status
    "PlungeAttackStatus",
    "DeathThisRoundStatus",

    # equipment status
    ## Weapon ##
    ### bow ###
    "RavenBowStatus",
    ### catalyst ###
    "MagicGuideStatus",
    ### claymore ###
    "WhiteIronGreatswordStatus",
    ### polearm ###
    "WhiteTasselStatus",
    ### sword ###
    "TravelersHandySwordStatus",
    ## Artifact ##
    "GamblersEarringsStatus",

    # combat status
    "CatalyzingFieldStatus",
    "ChangingShiftsStatus",
    "CrystallizeStatus",
    "DendroCoreStatus",
    "FrozenStatus",
    "LeaveItToMeStatus",
    "ReviveOnCooldown",

    # character status
    "JueyunGuobaStatus",
    "LotusFlowerCrispStatus",
    "MintyMeatRollsStatus",
    "MushroomPizzaStatus",
    "NorthernSmokedChickenStatus",
    "SatiatedStatus",

    # character specific status
    ## Arataki Itto ##
    "AratakiIchibanStatus",
    "RagingOniKing",
    "SuperlativeSuperstrengthStatus",
    ## Electro Hypostasis ##
    "ElectroCrystalCoreHiddenStatus",
    "ElectroCrystalCoreStatus",
    "RockPaperScissorsComboPaperStatus",
    "RockPaperScissorsComboScissorsStatus",
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
    "SparksnSplash",
    ## Mona ##
    "IllusoryBubbleStatus",
    "IllusoryTorrentStatus",
    "ProphecyOfSubmersionStatus",
    ## Rhodeia of Loch ##
    "StreamingSurgeStatus",
    ## Tighnari ##
    "KeenSightStatus",
    "VijnanaSuffusionStatus",
    ## Xingqiu ##
    "RainSwordStatus",
    "RainbowBladeworkStatus",
    "TheScentRemainedStatus",
]


############################## base ##############################
@dataclass(frozen=True)
class Status:
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset()

    def __init__(self) -> None:
        if type(self) is Status:  # pragma: no cover
            raise Exception("class Status is not instantiable")

    def preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        """
        Returns the processed PreprocessableEvent and possibly updated or deleted self
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        return item, self

    def _post_preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
            new_item: PreprocessableEvent,
            new_self: Optional[Self],
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        return (new_item, new_self)

    def inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> GameState:
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
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> list[eft.Effect]:
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

        has_damage = False
        has_swap = False
        for effect in es:
            has_damage = has_damage or isinstance(effect, eft.ReferredDamageEffect) \
                or isinstance(effect, eft.SpecificDamageEffect)
            has_swap = has_swap or isinstance(effect, eft.SwapCharacterEffect)  \
                or isinstance(effect, eft.ForwardSwapCharacterEffect)
        if has_damage:
            es.append(eft.AliveMarkCheckerEffect())
            es.append(eft.DefeatedCheckerEffect())
            es.append(eft.AllStatusTriggererEffect(
                pid=source.pid,
                signal=TriggeringSignal.POST_DMG,
            ))
        if has_swap or has_damage:
            es.append(
                eft.SwapCharacterCheckerEffect(
                    my_active=StaticTarget(
                        pid=source.pid,
                        zone=Zone.CHARACTERS,
                        id=game_state.get_player(source.pid).just_get_active_character().get_id(),
                    ),
                    oppo_active=StaticTarget(
                        pid=source.pid.other(),
                        zone=Zone.CHARACTERS,
                        id=game_state.get_player(
                            source.pid.other()).just_get_active_character().get_id(),
                    ),
                )
            )
        if has_damage:
            es.append(eft.AllStatusTriggererEffect(
                pid=source.pid,
                signal=TriggeringSignal.DEATH_EVENT,
            ))
            es.append(eft.DeathCheckCheckerEffect())

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
            new_status: Optional[Self],
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        return effects, case_val(new_status == self, self, new_status)

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        """
        Returns a tuple, containg the effects and how to update self
        * if the returned new self is the same object as myself, then it is taken as no change
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
        new_self = self._update(other)
        return self._post_update(new_self)

    def _post_update(self, new_self: Optional[Self]) -> Optional[Self]:
        return new_self

    def _update(self, other: Self) -> Optional[Self]:
        return other

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")  # pragma: no cover


############################## type ##############################

@dataclass(frozen=True)
class PlayerHiddenStatus(Status):
    pass


@dataclass(frozen=True)
class PersonalStatus(Status):
    pass


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
    BASE_DAMAGE_BOOST: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                dmg.source == status_source
                and (
                    dmg.damage_type.normal_attack
                    or dmg.damage_type.elemental_skill
                    or dmg.damage_type.elemental_burst
                )
                and dmg.element is not Element.PIERCING
            ):
                new_damage = replace(dmg, damage=dmg.damage + self.BASE_DAMAGE_BOOST)
                return DmgPEvent(dmg=new_damage), self
        return super()._preprocess(game_state, status_source, item, signal)


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
    pass


############################## template ##############################
@dataclass(frozen=True)
class _UsageStatus(Status):
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT

    @staticmethod
    def _auto_destroy() -> bool:
        return True

    @override
    def _post_preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
            new_item: PreprocessableEvent,
            new_self: Optional[Self],
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if new_self is not None:
            if self._auto_destroy() and new_self.usages <= 0:
                new_self = None
            elif new_self.usages < 0:
                new_self = replace(new_self, usages=0)
        return super()._post_preprocess(game_state, status_source, item, signal, new_item, new_self)

    @override
    def _post_update(self, new_self: Optional[Self]) -> Optional[Self]:
        """ remove the status if usages <= 0 """
        if new_self is not None:
            if self._auto_destroy() and new_self.usages <= 0:
                new_self = None
            elif new_self.usages < 0:
                new_self = replace(new_self, usages=0)
        return super()._post_update(new_self)

    @override
    def _update(self, other: Self) -> Optional[Self]:
        max_usages = max((self.usages, other.usages, self.MAX_USAGES))
        new_usages = min(self.usages + other.usages, max_usages)
        return replace(other, usages=new_usages)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


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

    def _triggering_condition(self, damage: eft.SpecificDamageEffect) -> bool:
        return True

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        cls = type(self)
        if signal is Preprocessables.DMG_AMOUNT_MINUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg) \
                    and self._triggering_condition(dmg):
                new_dmg_amount = max(0, dmg.damage - cls.SHIELD_AMOUNT)
                new_dmg = replace(dmg, damage=new_dmg_amount)
                new_item = DmgPEvent(dmg=new_dmg)
                new_usages = self.usages - 1
                if self._auto_destroy() and new_usages == 0:
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        cls = type(self)
        if signal is Preprocessables.DMG_AMOUNT_MINUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            assert self.usages <= type(self).MAX_USAGES
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg):
                usages_consumed = min(ceil(dmg.damage / cls.SHIELD_AMOUNT), self.usages)
                new_dmg_amount = max(0, dmg.damage - usages_consumed * cls.SHIELD_AMOUNT)
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        new_item: Optional[DmgPEvent] = None
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
            and item.damage_type.normal_attack \
            and status_source == item.source \


    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is self.ELEMENT and status_source == item.source

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -1
        return [], replace(self, usages=d_usages)


############################## Hidden Status ##############################


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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if signal is TriggeringSignal.ROUND_END:
            if self.activated:
                return [], replace(self, activated=False)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.activated, '*', '')})"

############################## Equipment Status ##############################

########## Weapon Status ##########

#### Bow ####


@dataclass(frozen=True, kw_only=True)
class RavenBowStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

#### Catalyst ####


@dataclass(frozen=True, kw_only=True)
class MagicGuideStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

#### Claymore ####


@dataclass(frozen=True, kw_only=True)
class WhiteIronGreatswordStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE

#### Polearm ####


@dataclass(frozen=True, kw_only=True)
class WhiteTasselStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM

#### Sword ####


@dataclass(frozen=True, kw_only=True)
class TravelersHandySwordStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD

########## Artifact Status ##########


@dataclass(frozen=True, kw_only=True)
class GamblersEarringsStatus(ArtifactEquipmentStatus):
    informed_num: int = 0
    triggered_num: int = 0
    MAX_TRIGGER_NUM: ClassVar[int] = 3
    NUM_DICES_PER_TRIGGER: ClassVar[int] = 2

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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if signal is TriggeringSignal.DEATH_EVENT:
            if self.triggerable():
                this_player = game_state.get_player(source.pid)
                active_char_id = this_player.just_get_active_character().get_id()
                if active_char_id is not source.id:
                    return [], replace(self, informed_num=0)
                additions = self.informed_num * self.NUM_DICES_PER_TRIGGER
                return [
                    eft.AddDiceEffect(pid=source.pid, dices=ActualDices({Element.OMNI: additions}))
                ], replace(
                    self,
                    triggered_num=self.triggered_num + self.informed_num,
                    informed_num=0
                )
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({self.informed_num},{self.triggered_num})"


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
    ) -> tuple[PreprocessableEvent, Optional[CatalyzingFieldStatus]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, eft.DmgPEvent)
            dmg = item.dmg
            assert self.usages >= 1
            elem_can_boost = dmg.element is Element.ELECTRO or dmg.element is Element.DENDRO
            legal_to_boost = status_source.pid is dmg.source.pid
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.dices_cost.num_dices() >= self.COST_DEDUCTION:
                assert item.dices_cost.num_dices() == item.dices_cost[Element.ANY]
                new_cost = (item.dices_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                return replace(item, dices_cost=new_cost), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class CrystallizeStatus(CombatStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2

    @override
    def _update(self, other: CrystallizeStatus) -> Optional[CrystallizeStatus]:
        new_stacks = min(just(type(self).MAX_USAGES, BIG_INT), self.usages + other.usages)
        return type(self)(usages=new_stacks)


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
    ) -> tuple[PreprocessableEvent, Optional[DendroCoreStatus]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            assert self.usages >= 1
            elem_can_boost = dmg.element is Element.ELECTRO or dmg.element is Element.PYRO
            legal_to_boost = status_source.pid is dmg.source.pid
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
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
    ) -> tuple[list[eft.Effect], Optional[FrozenStatus]]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True)
class LeaveItToMeStatus(CombatStatus):
    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.event_speed is EventSpeed.COMBAT_ACTION:
                return replace(item, event_speed=EventSpeed.FAST_ACTION), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True)
class ReviveOnCooldown(CombatStatus):
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

############################## Character Status ##############################


@dataclass(frozen=True)
class JueyunGuobaStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    damage_boost: ClassVar[int] = 1
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.source == status_source and dmg.damage_type.normal_attack:
                dmg = replace(dmg, damage=dmg.damage + JueyunGuobaStatus.damage_boost)
                return DmgPEvent(dmg=dmg), replace(self, usages=self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if status_source == item.source \
                    and item.event_type is EventType.NORMAL_ATTACK \
                    and item.dices_cost[Element.ANY] >= self.COST_DEDUCTION:
                item = replace(
                    item,
                    dices_cost=(item.dices_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, replace(self, usages=self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if status_source == item.source \
                    and item.event_type is EventType.NORMAL_ATTACK \
                    and item.dices_cost[Element.ANY] >= self.COST_DEDUCTION:
                item = replace(
                    item,
                    dices_cost=(item.dices_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


############################## Character Specific Status ##############################
"""
Group statues by characters, characters ordered alphabetically
"""

#### Arataki Itto ####


@dataclass(frozen=True, kw_only=True)
class AratakiIchibanStatus(TalentEquipmentStatus, _UsageStatus):
    usages: int = 0  # here means num of normal attacks in the past
    ACTIVATION_THRESHOLD: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @staticmethod
    def _auto_destroy() -> bool:
        return False

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
                or info_type is not Informables.SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent)
        if status_source != information.source \
                or information.skill_type != CharacterSkill.NORMAL_ATTACK:
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
class RagingOniKing(CharacterStatus, _InfusionStatus):
    usages: int = 2  # duration
    ELEMENT: ClassVar[Element] = Element.GEO
    damage_boost: int = 2
    status_gaining_usages: int = 1
    status_gaining_available: bool = False
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
        if info_type is Informables.SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source == status_source \
                    and information.skill_type is CharacterSkill.NORMAL_ATTACK \
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.charged_attack:
                character = game_state.get_character_target(status_source)
                assert character is not None, f"source {status_source} in {game_state}"
                dmg_boost = self.DAMAGE_BOOST
                if character.talent_equiped():
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
                    and item.event_type is EventType.NORMAL_ATTACK
                    and player.get_dices().is_even()
                    and item.dices_cost[Element.ANY] > 0
            ):
                item = replace(
                    item,
                    dices_cost=(item.dices_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
                )
                return item, self
        return item, self

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
        if info_type is Informables.SKILL_USAGE:
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if isinstance(item, DmgPEvent):
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self

            if signal is Preprocessables.DMG_ELEMENT:
                if dmg.damage_type.plunge_attack:
                    new_item = DmgPEvent(dmg=replace(dmg, element=self._ELEMENT))
                    return new_item, self
            elif signal is Preprocessables.DMG_AMOUNT_PLUS:
                if dmg.damage_type.plunge_attack:
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    status_source.pid != dmg.source.pid
                    or not (
                        dmg.damage_type.from_character()
                        or dmg.damage_type.from_summon()
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
    ) -> tuple[list[eft.Effect], Optional[IcicleStatus]]:
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

        if info_type is not Informables.SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent)
        if status_source != information.source \
                or information.skill_type != CharacterSkill.ELEMENTAL_SKILL1:
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[ColdBloodedStrikeStatus]]:
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
            new_self = ColdBloodedStrikeStatus(usages=1, activated=False)

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
    ) -> tuple[list[eft.Effect], Optional[KeqingTalentStatus]]:
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.charged_attack:
                new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + self.DAMAGE_BOOST))
                new_self = replace(self, usages=self.usages - 1)
                return new_item, new_self
        elif signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            if (
                    status_source == item.source
                    and item.event_type is EventType.NORMAL_ATTACK
                    and player.get_dices().is_even()
                    and item.dices_cost[Element.ANY] + item.dices_cost[Element.PYRO] > 0
            ):
                elems = [Element.PYRO, Element.ANY]
                cost_deduction_left = self.COST_DEDUCTION
                deduction: dict[Element, int] = {}
                for elem in elems:
                    deduction[elem] = cost_deduction_left
                    cost_deduction_left -= item.dices_cost[elem]
                    if cost_deduction_left <= 0:
                        break
                if item.dices_cost[Element.PYRO] > 0:
                    item = replace(
                        item,
                        dices_cost=(item.dices_cost - deduction).validify()
                    )
                return item, self
        return item, self


@dataclass(frozen=True, kw_only=True)
class PoundingSurpriseStatus(TalentEquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class SparksnSplash(CombatStatus, _UsageStatus):
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

        if info_type is not Informables.SKILL_USAGE:
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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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


#### Mona ####


@dataclass(frozen=True)
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
                    and item.dmg.damage_type.from_character()
            ):
                return replace(item, dmg=replace(item.dmg, damage=item.dmg.damage * 2)), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class ProphecyOfSubmersionStatus(TalentEquipmentStatus):
    DMG_BOOST: ClassVar[int] = 2

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
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


#### Rhodeia of Loch ####


@dataclass(frozen=True, kw_only=True)
class StreamingSurgeStatus(TalentEquipmentStatus):
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            characters = player.get_characters()
            if (
                    status_source == item.source
                    and item.event_type is EventType.NORMAL_ATTACK
                    and player.get_dices().is_even()
                    and characters.just_get_character(
                        cast(int, status_source.id)
                    ).get_character_statuses().contains(VijnanaSuffusionStatus)
                    and item.dices_cost[Element.ANY] > 0
            ):
                item = replace(
                    item,
                    dices_cost=(item.dices_cost - {Element.ANY: self.COST_DEDUCTION}).validify()
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
                or not information.dmg.damage_type.charged_attack
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
    ) -> tuple[PreprocessableEvent, Optional[Self]]:
        new_item: None | DmgPEvent = None
        if signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.charged_attack:
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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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


#### Xingqiu ####

@dataclass(frozen=True, kw_only=True)
class RainSwordStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_THRESHOLD: ClassVar[int] = 3

    @override
    def _triggering_condition(self, damage: eft.SpecificDamageEffect) -> bool:
        return damage.damage >= self.DAMAGE_THRESHOLD


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
                or information.skill_type is not CharacterSkill.NORMAL_ATTACK
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
    ) -> tuple[list[eft.Effect], Optional[Self]]:
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
