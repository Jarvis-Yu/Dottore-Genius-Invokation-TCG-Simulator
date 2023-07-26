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
from dataclasses import dataclass, replace
from enum import Enum
from math import ceil
from typing import ClassVar, cast, Optional, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft

from ..character.enums import CharacterSkill, WeaponType
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

    # hidden status
    "PlungeAttackStatus",

    # equipment status
    ## bow ##
    "RavenBowStatus",
    ## catalyst ##
    "MagicGuideStatus",
    ## claymore ##
    "WhiteIronGreatswordStatus",
    ## polearm ##
    "WhiteTasselStatus",
    ## sword ##
    "TravelersHandySwordStatus",

    # combat status
    "CatalyzingFieldStatus",
    "ChangingShiftsStatus",
    "CrystallizeStatus",
    "DendroCoreStatus",
    "FrozenStatus",
    "LeaveItToMeStatus",

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
    ## Rhodeia of Loch ##
    "StreamingSurgeStatus",
    ## Tighnari ##
    "KeenSightStatus",
    "VijnanaSuffusionStatus",
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
        if isinstance(new_self, HiddenStatus) \
                or isinstance(new_self, EquipmentStatus) \
                or isinstance(new_self, CharacterStatus):
            return eft.OverrideCharacterStatusEffect(
                target=status_source,
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
        es, new_status = self._post_react_to_signal(es, new_status, source, signal)

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

        has_damage = False
        has_swap = False
        for effect in es:
            has_damage = has_damage or isinstance(effect, eft.ReferredDamageEffect) \
                or isinstance(effect, eft.SpecificDamageEffect)
            has_swap = has_swap or isinstance(effect, eft.SwapCharacterEffect)  \
                or isinstance(effect, eft.ForwardSwapCharacterEffect)
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
            es.append(eft.DeathCheckCheckerEffect())

        return es

    def _post_react_to_signal(
            self,
            effects: list[eft.Effect],
            new_status: Optional[Self],
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if effects:
            if any(isinstance(effect, eft.ReferredDamageEffect) for effect in effects):
                effects.append(eft.AllStatusTriggererEffect(
                    pid=source.pid,
                    signal=TriggeringSignal.POST_DMG,
                ))
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
        return [], self

    def _is_swapping_source(self, source: StaticTarget, signal: TriggeringSignal) -> bool:
        """ Returns True if characters of the source player is swapping """
        return source.pid.is_player1() and signal is TriggeringSignal.SWAP_EVENT_1 \
            or source.pid.is_player2() and signal is TriggeringSignal.SWAP_EVENT_2

    def same_type_as(self, status: Status) -> bool:
        return type(self) == type(status)

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
class HiddenStatus(Status):
    """
    Basic status, describing character talents
    """
    pass


@dataclass(frozen=True)
class EquipmentStatus(Status):
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
        if signal is Preprocessables.DMG_AMOUNT:
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
class CharacterStatus(Status):
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
        new_usages = min(self.usages + other.usages, self.MAX_USAGES)
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
        if isinstance(self, HiddenStatus) \
                or isinstance(self, EquipmentStatus) \
                or isinstance(self, CharacterStatus):
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

    def _trigerring_condition(self, damage: eft.SpecificDamageEffect) -> bool:
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
        if signal is Preprocessables.DMG_AMOUNT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg) \
                    and self._trigerring_condition(dmg):
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
        if signal is Preprocessables.DMG_AMOUNT:
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
            if signal is Preprocessables.DMG_AMOUNT:
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
class PlungeAttackStatus(HiddenStatus):
    can_plunge: bool = False
    invalidate: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
        TriggeringSignal.SWAP_EVENT_1,
        TriggeringSignal.SWAP_EVENT_2,
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
                    and self.can_plunge:
                return replace(self, invalidate=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.invalidate:
            return [], replace(self, can_plunge=False, invalidate=False)
        elif signal is TriggeringSignal.ROUND_END and self.can_plunge:
            assert not self.invalidate
            return [], replace(self, can_plunge=False)
        elif self._is_swapping_source(source, signal):
            characters = game_state.get_player(source.pid).get_characters()
            active_char_id = characters.get_active_character_id()
            if source.id == active_char_id and not self.can_plunge:
                return [], replace(self, can_plunge=True)
        return [], self

    @override
    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_plunge, '*', '')})"

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
        if signal is Preprocessables.DMG_AMOUNT:
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
        if signal is Preprocessables.DMG_AMOUNT:
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
                else:
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
        if signal is Preprocessables.DMG_AMOUNT:
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
        return [], self


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
        if signal is Preprocessables.DMG_AMOUNT:
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
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -1
        return [], replace(self, usages=d_usages)


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
class NorthernSmokedChickenStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
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
        return [], self


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

        return replace(self, usages=self.usages+1)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-self.usages)
        return [], self


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
        if signal is Preprocessables.DMG_AMOUNT:
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
            elif signal is Preprocessables.DMG_AMOUNT:
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
        if signal is Preprocessables.DMG_AMOUNT:
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
        return [], self

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
        if signal is Preprocessables.DMG_AMOUNT:
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
