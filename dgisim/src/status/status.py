from __future__ import annotations
from typing import TypeVar, Union, Optional, ClassVar
from typing_extensions import override, Self
from enum import Enum
from dataclasses import dataclass, replace
from math import ceil

import dgisim.src.state.game_state as gs
import dgisim.src.card.card as cd
import dgisim.src.effect.effect as eft
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.element.element import Element
from dgisim.src.helper.quality_of_life import just, BIG_INT, case_val


class TriggerringEvent(Enum):
    pass


@dataclass(frozen=True)
class Status:
    class PPType(Enum):
        """ PreProcessType """
        # Damages
        DMG_ELEMENT = "DmgElement"    # To determine the element
        DMG_REACTION = "DmgReaction"  # To determine the reaction
        DMG_AMOUNT = "DmgNumber"      # To determine final amount of damage

    def __init__(self) -> None:
        if type(self) is Status:  # pragma: no cover
            raise Exception("class Status is not instantiable")

    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        """
        Returns the processed Preprocessable and possibly updated or deleted self
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
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        return (item, self)

    def _post_preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
            new_item: eft.Preprocessable,
            new_self: Optional[Self],
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        return (new_item, new_self)

    def inform(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            information: eft.SpecificDamageEffect | CharacterSkill | cd.Card,
            info_source: Optional[eft.StaticTarget] = None,
    ) -> gs.GameState:
        new_self = self._inform(game_state, status_source, information, info_source)
        if new_self == self:
            return game_state

        import dgisim.src.summon.summon as sm
        if isinstance(new_self, CharacterTalentStatus) \
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

        else:
            raise NotImplementedError

    def _inform(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            information: eft.SpecificDamageEffect | CharacterSkill | cd.Card,
            info_source: Optional[eft.StaticTarget],
    ) -> Self:
        return self

    # def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
    #     raise Exception("TODO")

    def react_to_signal(
            self, game_state: gs.GameState, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> list[eft.Effect]:
        es, new_status = self._react_to_signal(source, signal)
        es, new_status = self._post_react_to_signal(es, new_status, signal)

        import dgisim.src.summon.summon as sm
        # do the removal or update of the status
        if isinstance(self, CharacterTalentStatus) \
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
                    my_active=eft.StaticTarget(
                        pid=source.pid,
                        zone=eft.Zone.CHARACTER,
                        id=game_state.get_player(source.pid).just_get_active_character().get_id(),
                    ),
                    oppo_active=eft.StaticTarget(
                        pid=source.pid.other(),
                        zone=eft.Zone.CHARACTER,
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
            signal: eft.TriggeringSignal,
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if new_status != self:
            return effects, new_status
        return effects, self

    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        """
        Returns a tuple, containg the effects and how to update self
        * if the returned new self is the same object as myself, then it is taken as no change
          requested
        * if the returned new self is none, then it is taken as a removal request
        * if the returned new self is different object than myself, then it is taken as an update
        """
        return [], self

    def same_type_as(self, status: Status) -> bool:
        return type(self) == type(status)

    def update(self, other: Self) -> Optional[Self]:
        new_self = self._update(other)
        return self._post_update(new_self)

    def _post_update(self, new_self: Optional[Self]) -> Optional[Self]:
        return new_self

    def _update(self, other: Self) -> Optional[Self]:
        return other

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")  # pragma: no cover


@dataclass(frozen=True)
class CharacterTalentStatus(Status):
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


@dataclass(frozen=True)
class _DurationStatus(Status):
    """
    This class has a duration which acts as a counter
    """
    duration: int
    max_duration: ClassVar[int] = BIG_INT

    @override
    def _post_update(self, new_self: Optional[Self]) -> Optional[Self]:
        """ remove the status if duration <= 0 """
        if new_self is not None and new_self.duration <= 0:
            new_self = None
        return super()._post_update(new_self)

    @override
    def _update(self, other: Self) -> Optional[Self]:
        new_duration = min(self.duration + other.duration, self.max_duration)
        return replace(self, duration=new_duration)

    def __str__(self) -> str:
        return super().__str__() + f"({self.duration})"  # pragma: no cover


@dataclass(frozen=True)
class _UsageStatus(Status):
    usages: int
    max_usages: ClassVar[int] = BIG_INT

    @override
    def _post_update(self, new_self: Optional[Self]) -> Optional[Self]:
        """ remove the status if usages <= 0 """
        if new_self is not None and new_self.usages <= 0:
            new_self = None
        return super()._post_update(new_self)

    @override
    def _update(self, other: Self) -> Optional[Self]:
        new_usages = min(self.usages + other.usages, self.max_usages)
        return type(self)(usages=new_usages)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class ShieldStatus(Status):
    def _is_target(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> bool:
        import dgisim.src.summon.summon as sm
        assert isinstance(item, eft.SpecificDamageEffect)
        if isinstance(self, CharacterTalentStatus) \
                or isinstance(self, EquipmentStatus) \
                or isinstance(self, CharacterStatus):
            return item.target == status_source

        elif isinstance(self, CombatStatus):
            attached_active_character = eft.StaticTarget(
                status_source.pid,
                zone=eft.Zone.CHARACTER,
                id=game_state.get_player(status_source.pid).just_get_active_character().get_id(),
            )
            return item.target == attached_active_character

        elif isinstance(self, sm.Summon):
            attached_active_character = eft.StaticTarget(
                status_source.pid,
                zone=eft.Zone.CHARACTER,
                id=game_state.get_player(status_source.pid).just_get_active_character().get_id(),
            )
            return item.target == attached_active_character

        else:
            raise NotImplementedError  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class StackedShieldStatus(ShieldStatus):
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = 1  # shield amount per stack

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        cls = type(self)
        if signal is Status.PPType.DMG_AMOUNT:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.usages <= type(self).MAX_USAGES
            if item.damage > 0 and self.usages > 0 \
                    and item.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, item, signal):
                usages_consumed = min(ceil(item.damage / cls.SHIELD_AMOUNT), self.usages)
                new_dmg = max(0, item.damage - usages_consumed * cls.SHIELD_AMOUNT)
                new_item = replace(item, damage=new_dmg)
                new_usages = self.usages - usages_consumed
                if new_usages == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, usages=new_usages)

        return super()._preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FixedShieldStatus(ShieldStatus):
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = 0  # shield amount per stack

    def _trigerring_condition(self, damage: eft.SpecificDamageEffect) -> bool:
        return True

    @staticmethod
    def _auto_destroy() -> bool:
        return True

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        cls = type(self)
        if signal is Status.PPType.DMG_AMOUNT:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.usages <= type(self).MAX_USAGES
            if item.damage > 0 and self.usages > 0 \
                    and item.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, item, signal) \
                    and self._trigerring_condition(item):
                new_dmg = max(0, item.damage - cls.SHIELD_AMOUNT)
                new_item = replace(item, damage=new_dmg)
                new_usages = self.usages - 1
                if self._auto_destroy() and new_usages == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, usages=new_usages)

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
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[DendroCoreStatus]]:
        if signal is Status.PPType.DMG_AMOUNT:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.usages >= 1
            elem_can_boost = item.element is Element.ELECTRO or item.element is Element.PYRO
            legal_to_boost = status_source.pid is item.source.pid
            target_is_active = item.target.id == game_state.get_player(
                item.target.pid
            ).just_get_active_character().get_id()
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(item, damage=item.damage + DendroCoreStatus.damage_boost)
                if self.usages == 1:
                    return new_damage, None
                else:
                    return new_damage, DendroCoreStatus(self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    # @override
    # def update(self, other: DendroCoreStatus) -> DendroCoreStatus:
    #     total_count = min(self.count + other.count, 2)
    #     return DendroCoreStatus(total_count)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class CatalyzingFieldStatus(CombatStatus):
    damage_boost: ClassVar[int] = 1
    usages: int = 2

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[CatalyzingFieldStatus]]:
        if signal is Status.PPType.DMG_AMOUNT:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.usages >= 1
            elem_can_boost = item.element is Element.ELECTRO or item.element is Element.DENDRO
            legal_to_boost = status_source.pid is item.source.pid
            target_is_active = item.target.id == game_state.get_player(
                item.target.pid
            ).just_get_active_character().get_id()
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(item, damage=item.damage + CatalyzingFieldStatus.damage_boost)
                if self.usages == 1:
                    return new_damage, None
                else:
                    return new_damage, CatalyzingFieldStatus(self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class FrozenStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 2

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        if signal is Status.PPType.DMG_AMOUNT:
            assert isinstance(item, eft.SpecificDamageEffect)
            can_reaction = item.element is Element.PYRO or item.element is Element.PHYSICAL
            is_damage_target = item.target == status_source
            if is_damage_target and can_reaction:
                return replace(item, damage=item.damage + FrozenStatus.damage_boost), None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[FrozenStatus]]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class SatiatedStatus(CharacterStatus):

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[SatiatedStatus]]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class MushroomPizzaStatus(CharacterStatus, _DurationStatus):
    duration: int = 2

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[MushroomPizzaStatus]]:
        es: list[eft.Effect] = []
        d_duration = 0
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            d_duration = -1
            es.append(
                eft.RecoverHPEffect(
                    source,
                    1,
                )
            )

        return es, replace(self, duration=d_duration)


@dataclass(frozen=True)
class JueyunGuobaStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 1
    duration: int = 1

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[Self]]:
        if signal is Status.PPType.DMG_AMOUNT:
            assert isinstance(item, eft.SpecificDamageEffect)
            if item.source == status_source and item.damage_type.normal_attack:
                item = replace(item, damage=item.damage + JueyunGuobaStatus.damage_boost)
                return item, None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[JueyunGuobaStatus]]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return [], None
        return [], self


############################## Infusions ##############################


@dataclass(frozen=True, kw_only=True)
class _InfusionStatus(CharacterStatus, _DurationStatus):
    max_duration: ClassVar[int] = BIG_INT
    element: ClassVar[Optional[Element]] = None
    damage_boost: int = 0

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_InfusionStatus]]:
        assert self.element is not None
        new_item: Optional[eft.SpecificDamageEffect] = None
        if isinstance(item, eft.SpecificDamageEffect):
            if signal is Status.PPType.DMG_ELEMENT:
                if self._dmg_element_condition(game_state, status_source, item):
                    new_item = replace(item, element=self.element)
            if signal is Status.PPType.DMG_AMOUNT:
                if self.damage_boost != 0  \
                        and self._dmg_boost_condition(game_state, status_source, item):
                    new_item = replace(item, damage=item.damage + self.damage_boost)
        if new_item is not None:
            return new_item, self
        else:
            return item, self

    def _dmg_element_condition(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is Element.PHYSICAL \
            and item.damage_type.normal_attack \
            and status_source == item.source \


    def _dmg_boost_condition(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is self.element and status_source == item.source

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[_InfusionStatus]]:
        d_duration = 0
        if signal is eft.TriggeringSignal.ROUND_END:
            d_duration = -1
        return [], replace(self, duration=d_duration)


@dataclass(frozen=True, kw_only=True)
class ElectroInfusionStatus(_InfusionStatus):
    element: ClassVar[Optional[Element]] = Element.ELECTRO


############################## Character specific ##############################


#### Keqing ####

@dataclass(frozen=True, kw_only=True)
class KeqingTalentStatus(CharacterTalentStatus):
    can_infuse: bool

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[KeqingTalentStatus]]:
        if signal is eft.TriggeringSignal.COMBAT_ACTION:
            return [], type(self)(can_infuse=False)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_infuse, 1, 0)})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ThunderingPenanceStatus(EquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class KeqingElectroInfusionStatus(ElectroInfusionStatus):
    pass

    def __str__(self) -> str:
        return super().__str__() + f"({self.damage_boost})"


#### Kaeya ####


@dataclass(frozen=True, kw_only=True)
class Icicle(CombatStatus, _UsageStatus):
    usages: int = 3

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Icicle]]:
        if source.pid.is_player1() and signal is eft.TriggeringSignal.SWAP_EVENT_1 \
                or source.pid.is_player2() and signal is eft.TriggeringSignal.SWAP_EVENT_2:
            effects: list[eft.Effect] = [
                eft.ReferredDamageEffect(
                    source=source,
                    target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.CRYO,
                    damage=2,
                    damage_type=eft.DamageType(status=True),
                ),
            ]
            return effects, replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ColdBloodedStrikeStatus(EquipmentStatus):
    """
    Equipping this status implies the equipped character is Kaeya
    """
    usages: int = 1
    activated: bool = False

    @override
    def _inform(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            information: eft.SpecificDamageEffect | CharacterSkill | cd.Card,
            info_source: Optional[eft.StaticTarget],
    ) -> ColdBloodedStrikeStatus:
        if self.activated or self.usages == 0:
            return self

        if not isinstance(information, CharacterSkill):
            return self

        assert info_source != None
        if status_source != info_source \
                or information != CharacterSkill.ELEMENTAL_SKILL1:
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[ColdBloodedStrikeStatus]]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is eft.TriggeringSignal.COMBAT_ACTION and self.activated:
            assert self.usages >= 1
            es.append(
                eft.RecoverHPEffect(
                    target=source,
                    recovery=2,
                )
            )
            new_self = replace(new_self, usages=self.usages - 1, activated=False)

        elif signal is eft.TriggeringSignal.ROUND_END:
            new_self = ColdBloodedStrikeStatus(usages=1, activated=False)

        return es, new_self

    def __str__(self) -> str:
        return super().__str__() + case_val(self.activated, "(*)", '')


#### Rhodeia of Loch ####

@dataclass(frozen=True, kw_only=True)
class StreamingSurgeStatus(EquipmentStatus):
    pass
