from __future__ import annotations
from typing import Iterable, Union

from dgisim.src.event.effect import Effect

class EffectStack:
    def __init__(self, effects: tuple[Effect, ...]) -> None:
        self._effects = effects

    def is_not_empty(self) -> bool:
        return not self.is_empty()

    def is_empty(self) -> bool:
        return len(self._effects) == 0

    def pop(self) -> tuple[EffectStack, Effect]:
        assert not self.is_empty()
        return (EffectStack(tuple(self._effects[:-1])), self._effects[-1])

    def peek(self) -> Effect:
        assert not self.is_empty()
        return self._effects[-1]

    def push_one(self, effect: Effect) -> EffectStack:
        return EffectStack(self._effects + (effect, ))

    def push_many_lf(self, effects: Iterable[Effect]) -> EffectStack:
        """
        lf means the effects passed in are executed from the last to the first
        """
        effects = tuple(effects)
        return EffectStack(self._effects + effects)

    def push_many_fl(self, effects: Iterable[Effect]) -> EffectStack:
        """
        fl means the effects passed in are executed from the first to the last
        """
        effects = tuple(effects)
        return EffectStack(self._effects + effects[::-1])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EffectStack):
            return False
        return self._effects == other._effects

    def __hash__(self) -> int:
        return hash(self._effects)

    def to_string(self, indent: int) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self._effects)

    def dict_str(self) -> Union[dict, str]:
        content = {}
        for effect in reversed(self._effects):
            content[effect.name()] = effect.dict_str()
        return content
