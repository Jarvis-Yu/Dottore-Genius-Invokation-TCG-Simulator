from __future__ import annotations
from typing import TypeVar, Union, Optional
from typing_extensions import override
from enum import Enum
from dataclasses import dataclass, replace

import dgisim.src.effect.effect as eft
import dgisim.src.state.game_state as gs


class TriggerringEvent(Enum):
    pass


T = TypeVar('T', bound="Status")


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
            self: T, item: eft.Preprocessable, signal: Status.PPType
    ) -> tuple[eft.Preprocessable, Optional[T]]:
        return (item, self)

    # def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
    #     raise Exception("TODO")

    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        raise Exception("TODO")

    def same_type_as(self, status: Status) -> bool:
        return type(self) == type(status)

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
        if new_duration <= 0:
            if isinstance(self, CharacterStatus) \
                    or isinstance(self, CharacterTalentStatus) \
                    or isinstance(self, EquipmentStatus):
                es.append(eft.RemoveStatusEffect(
                    source,
                    type(self),
                ))
            else:
                raise NotImplementedError
        elif new_duration != self.duration:
            es.append(eft.UpdateStatusEffect(
                source,
                replace(self, duration=new_duration),
            ))
        return es

    def __str__(self) -> str:
        return super().__str__() + f"({self.duration})"


@dataclass(frozen=True)
class SatiatedStatus(CharacterStatus):
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveStatusEffect(
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
class JueyunGuobaStatus(CharacterStatus, _DurationStatus):
    duration: int = 1

    @override
    def preprocess(
            self: T, item: eft.Preprocessable, signal: Status.PPType
    ) -> tuple[eft.Preprocessable, Optional[T]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            # TODO: check damage type
            item = replace(item, damage=item.damage+1)
            return item, None
        return super().preprocess(item, signal)

    @override
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        es: list[eft.Effect] = []
        new_duration = self.duration
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            new_duration -= 1
        es += self.auto_destory(source, new_duration)
        return tuple(es)
