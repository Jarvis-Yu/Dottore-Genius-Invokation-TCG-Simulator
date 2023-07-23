from __future__ import annotations
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .effect import Effect

__all__ = [
    "EffectStack",
]


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
        if not effects:
            return self
        return EffectStack(self._effects + effects)

    def push_many_fl(self, effects: Iterable[Effect]) -> EffectStack:
        """
        fl means the effects passed in are executed from the first to the last
        """
        effects = tuple(effects)
        if not effects:
            return self
        return EffectStack(self._effects + effects[::-1])

    def contains(self, effect_type: type[Effect]) -> bool:
        for effect in self._effects:
            if type(effect) == effect_type:
                return True
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EffectStack):
            return False
        return self is other or self._effects == other._effects

    def __hash__(self) -> int:
        return hash(self._effects)

    def __str__(self) -> str:
        return str(self._effects)

    def dict_str(self) -> dict | str:
        content = {}
        for i, effect in enumerate(reversed(self._effects)):
            content[f"{str(i)}-{effect.name()}"] = effect.dict_str()
        return content
