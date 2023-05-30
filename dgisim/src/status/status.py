from __future__ import annotations
from typing import TypeVar
from typing_extensions import override
from enum import Enum

import dgisim.src.event.effect as eft
import dgisim.src.state.game_state as gs


class TriggerringEvent(Enum):
    pass


T = TypeVar('T', bound="Status")


class Status:
    def __init__(self) -> None:
        if type(self) is Status:
            raise Exception("class Status is not instantiable")

    def preprocess(self: T, damage_effect: eft.DamageEffect) -> tuple[eft.DamageEffect, T]:
        return (damage_effect, self)

    # def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
    #     raise Exception("TODO")

    def react_to_signal(self, source: eft.StaticTarget, signal: eft.TriggeringSignal) -> tuple[eft.Effect, ...]:
        raise Exception("TODO")

    def same_type_as(self, status: Status) -> bool:
        return type(self) == type(status)

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")


class CharacterTalentStatus(Status):
    """
    Basic status, describing character talents
    """
    pass


class EquipmentStatus(Status):
    """
    Basic status, describing weapon, artifact and character unique talents
    """


class CharacterStatus(Status):
    """
    Basic status, private status to each character
    """
    pass


class CombatStatus(Status):
    """
    Basic status, status shared across the team
    """
    pass


class NumberedStatus(Status):
    """
    This class has a num which acts as a counter
    """

    def __init__(self, num: int = 0) -> None:
        self._num = num

    def num(self) -> int:
        return self._num

    def __str__(self) -> str:
        return super().__str__() + f"({self._num})"


class NumberedAutoDestroyStatus(NumberedStatus):
    """
    This class destroys the status if the new counter <= 0;
    To set how the status react to signal, override the method `actual_react_to_signal`
    """

    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        """
        This method adds effects destorying or updating the current status based on the new number
        provided
        """
        num, es = self.actual_react_to_signal(source, signal)
        if num <= 0:
            es += (
                eft.RemoveCharacterStatusEffect(
                    source,
                    type(self),
                ),
            )
        elif num != self.num():
            es += (
                eft.UpdateStatusEffect(
                    source,
                    MushroomPizzaStatus(num),
                ),
            )
        return es

    def actual_react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[int, tuple[eft.Effect, ...]]:
        """
        This method should provide what this status actually does
        It is supposed to be overriden
        Return value is (new_num, effects):
        - The new_num is the new num the reacted status should have
        - The effects are just the effects generated according to the signal
        """
        raise Exception("Not overriden")


class SatiatedStatus(CharacterStatus):
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveCharacterStatusEffect(
                source,
                type(self),
            ),)
        return ()


class MushroomPizzaStatus(CharacterStatus, NumberedAutoDestroyStatus):
    def __init__(self, num: int = 2) -> None:
        super().__init__(num)

    @override
    def actual_react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[int, tuple[eft.Effect, ...]]:
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            new_num = self.num() - 1
            es = (
                eft.RecoverHPEffect(
                    source,
                    1,
                ),
            )
            return new_num, es
        return (self.num(), ())
