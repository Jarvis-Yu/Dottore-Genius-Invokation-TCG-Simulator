from __future__ import annotations
from typing import TypeVar
from typing_extensions import override
from enum import Enum

import dgisim.src.event.effect as eft
import dgisim.src.state.game_state as gs


class TriggerringEvent(Enum):
    pass


class Buffable:
    def preprocess(self):
        raise Exception("TODO")

    def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
        raise Exception("TODO")

    def react_to_signal(self, source: eft.StaticTarget, signal: eft.TriggeringSignal) -> tuple[eft.Effect, ...]:
        raise Exception("TODO")

    def same_type_as(self, buff: Buffable) -> bool:
        return type(self) == type(buff)

    def __str__(self) -> str:
        return self.__class__.__name__


class CharacterTalentBuff(Buffable):
    """
    Basic buff, describing character talents
    """
    pass


class EquipmentBuff(Buffable):
    """
    Basic buff, describing weapon, artifact and character unique talents
    """


class CharacterBuff(Buffable):
    """
    Basic buff, private buff to each character
    """
    pass


class TeamBuff(Buffable):
    """
    Basic buff, buff shared across the team
    """
    pass


class NumberedBuff(Buffable):
    """
    This class has a num which acts as a counter
    """

    def __init__(self, num: int = 0) -> None:
        self._num = num

    def num(self) -> int:
        return self._num


class NumberedAutoDestroyBuff(NumberedBuff):
    """
    This class destroys the buff if the new counter <= 0;
    To set how the buff react to signal, override the method `actual_react_to_signal`
    """

    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        """
        This method adds effects destorying or updating the current buff based on the new number
        provided
        """
        num, es = self.actual_react_to_signal(source, signal)
        if num <= 0:
            es += (
                eft.RemoveCharacterBuffEffect(
                    source,
                    type(self),
                ),
            )
        elif num != self.num():
            es += (
                eft.UpdateBuffEffect(
                    source,
                    MushroomPizzaBuff(num),
                ),
            )
        return es

    def actual_react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[int, tuple[eft.Effect, ...]]:
        """
        This method should provide what this buff actually does
        It is supposed to be overriden
        Return value is (new_num, effects):
        - The new_num is the new num the reacted buff should have
        - The effects are just the effects generated according to the signal
        """
        raise Exception("Not overriden")


class SatiatedBuff(CharacterBuff):
    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveCharacterBuffEffect(
                source,
                type(self),
            ),)
        return ()


class MushroomPizzaBuff(CharacterBuff, NumberedAutoDestroyBuff):
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
