from __future__ import annotations

from dgisim.src.event.effect import Effect

class EffectStack:
    def __init__(self, effects: tuple[Effect, ...]) -> None:
        self._effects = effects

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

    def push_many(self, effects: tuple[Effect, ...]) -> EffectStack:
        return EffectStack(self._effects + effects)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EffectStack):
            return False
        return self._effects == other._effects

    def __hash__(self) -> int:
        return hash(self._effects)
