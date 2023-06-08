from __future__ import annotations
from typing import TypeVar, Union, Optional, ClassVar
from typing_extensions import override
from enum import Enum
from dataclasses import dataclass, replace

import dgisim.src.effect.effect as eft
import dgisim.src.state.game_state as gs
from dgisim.src.element.element import Element


class TriggerringEvent(Enum):
    pass


_T = TypeVar('_T', bound="Status")


@dataclass(frozen=True)
class Status:
    class PPType(Enum):
        # Damages
        DmgElement = "DmgElement"    # To determine the element
        DmgReaction = "DmgReaction"  # To determine the reaction
        DmgAmount = "DmgNumber"      # To determine final amount of damage

    def __init__(self) -> None:
        if type(self) is Status:
            raise Exception("class Status is not instantiable")

    def preprocess(
            self: _T,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_T]]:
        return (item, self)

    # def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
    #     raise Exception("TODO")

    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        raise Exception("TODO")

    def same_type_as(self, status: Status) -> bool:
        return type(self) == type(status)

    def update(self: _T, other: _T) -> _T:
        return self

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")


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

    def auto_destory(self, source: eft.StaticTarget, new_duration: int) -> list[eft.Effect]:
        """
        Automatically updates the duration or destroy the status based on the new_duration
        (when new_duration <= 0, the status is scheduled to be destroyed)
        """
        es: list[eft.Effect] = []
        if isinstance(self, CharacterTalentStatus) \
                or isinstance(self, EquipmentStatus) \
                or isinstance(self, CharacterStatus):
            if new_duration <= 0:
                es.append(eft.RemoveCharacterStatusEffect(
                    source,
                    type(self),
                ))
            elif new_duration != self.duration:
                es.append(eft.UpdateCharacterStatusEffect(
                    source,
                    replace(self, duration=new_duration),
                ))

        elif isinstance(self, CombatStatus):
            if new_duration <= 0:
                es.append(eft.RemoveCombatStatusEffect(
                    source.pid,
                    type(self),
                ))
            elif new_duration != self.duration:
                es.append(eft.UpdateCombatStatusEffect(
                    source.pid,
                    replace(self, duration=new_duration),
                ))
        return es

    def __str__(self) -> str:
        return super().__str__() + f"({self.duration})"

@dataclass(frozen=True)
class DendroCoreStatus(CombatStatus):
    damage_boost: ClassVar[int] = 2
    count: int = 1

    @override
    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[DendroCoreStatus]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.count >= 1
            elem_can_boost = item.element is Element.ELECTRO or item.element is Element.PYRO
            legal_to_boost = status_source.pid is item.source.pid
            if elem_can_boost and legal_to_boost:
                new_damage = replace(item, damage=item.damage + DendroCoreStatus.damage_boost)
                if self.count == 1:
                    return new_damage, None
                else:
                    return new_damage, DendroCoreStatus(self.count - 1)
        return super().preprocess(game_state, status_source, item, signal)

    @override
    def update(self, other: DendroCoreStatus) -> DendroCoreStatus:
        total_count = min(self.count + other.count, 2)
        return DendroCoreStatus(total_count)

    def __str__(self) -> str:
        return super().__str__() + f"({self.count})"


@dataclass(frozen=True)
class CatalyzingFieldStatus(CombatStatus):
    damage_boost: ClassVar[int] = 1
    count: int = 2

    @override
    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[CatalyzingFieldStatus]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.count >= 1
            elem_can_boost = item.element is Element.ELECTRO or item.element is Element.DENDRO
            legal_to_boost = status_source.pid is item.source.pid
            if elem_can_boost and legal_to_boost:
                new_damage = replace(item, damage=item.damage + CatalyzingFieldStatus.damage_boost)
                if self.count == 1:
                    return new_damage, None
                else:
                    return new_damage, CatalyzingFieldStatus(self.count - 1)
        return super().preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.count})"


@dataclass(frozen=True)
class FrozenStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 2

    @override
    def preprocess(
            self: _T,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_T]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            can_reaction = item.element is Element.PYRO or item.element is Element.PHYSICAL
            is_damage_target = item.target == status_source
            if is_damage_target and can_reaction:
                return replace(item, damage=item.damage + FrozenStatus.damage_boost), None
        return super().preprocess(game_state, status_source, item, signal)

    @override
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveCharacterStatusEffect(
                source,
                type(self),
            ),)
        return ()


@dataclass(frozen=True)
class SatiatedStatus(CharacterStatus):

    @override
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveCharacterStatusEffect(
                source,
                type(self),
            ),)
        return ()


@dataclass(frozen=True)
class MushroomPizzaStatus(CharacterStatus, _DurationStatus):
    duration: int = 2

    @override
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        es: list[eft.Effect] = []
        new_duration = self.duration
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            new_duration -= 1
            es.append(
                eft.RecoverHPEffect(
                    source,
                    1,
                )
            )
        es += self.auto_destory(source, new_duration)
        return tuple(es)


@dataclass(frozen=True)
class JueyunGuobaStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 1
    duration: int = 1

    @override
    def preprocess(
            self: _T,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_T]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            # TODO: check damage type
            if item.source == status_source:
                item = replace(item, damage=item.damage + JueyunGuobaStatus.damage_boost)
                return item, None
        return super().preprocess(game_state, status_source, item, signal)

    @override
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveCharacterStatusEffect(
                source,
                type(self),
            ),)
        return ()
