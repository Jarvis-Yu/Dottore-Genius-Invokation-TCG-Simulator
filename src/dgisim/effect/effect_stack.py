from __future__ import annotations
from itertools import chain
from typing import Iterable, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from .effect import Effect
    from ..encoding.encoding_plan import EncodingPlan

__all__ = [
    "EffectStack",
]


class EffectStack:
    """
    A class responsible for holding pending effects to be executed as a stack.
    """
    def __init__(self, effects: tuple[Effect, ...]) -> None:
        """
        :param effects: effects to be executed, ordered from last to first (to be executed).
        """
        self._effects = effects

    def is_not_empty(self) -> bool:
        """ :returns: `True` if there's at least one effect. """
        return not self.is_empty()

    def is_empty(self) -> bool:
        """ :returns: `True` if there no effects. """
        return len(self._effects) == 0

    def pop(self) -> tuple[EffectStack, Effect]:
        """ :returns: a tuple of left effects in the stack and popped effect. """
        assert not self.is_empty()
        return (EffectStack(tuple(self._effects[:-1])), self._effects[-1])

    def peek(self) -> Effect:
        """ :returns: the top effect. """
        assert not self.is_empty()
        return self._effects[-1]

    def _first_barrier_idx(self) -> int:
        from .effect import GroupEffectBarrierEffect
        last_barrier_idx = -1
        for i, effect in enumerate(self._effects):
            if isinstance(effect, GroupEffectBarrierEffect):
                last_barrier_idx = i
                break
        return last_barrier_idx

    def peek_all_left(self) -> tuple[Effect, ...]:
        """ :returns: all effects in pop order. """
        from .effect import GroupEffectBarrierEffect
        first_barrier_idx = self._first_barrier_idx()
        if first_barrier_idx == -1:
            return self._effects[::-1]
        return self._effects[first_barrier_idx-1::-1]

    def peek_all_rev_left(self) -> tuple[Effect, ...]:
        """ :returns: all effects in push order. """
        from .effect import GroupEffectBarrierEffect
        first_barrier_idx = self._first_barrier_idx()
        if first_barrier_idx == -1:
            return self._effects
        return self._effects[:first_barrier_idx]

    def pop_all_left(self) -> tuple[EffectStack, tuple[Effect, ...]]:
        """ :returns: EffectStack with remaining effects and all popped effects. """
        from .effect import GroupEffectBarrierEffect
        first_barrier_idx = self._first_barrier_idx()
        if first_barrier_idx == -1:
            return (EffectStack(()), self._effects[::-1])
        return (EffectStack(self._effects[first_barrier_idx+1:]), self._effects[first_barrier_idx-1::-1])

    def pop_all_rev_left(self) -> tuple[EffectStack, tuple[Effect, ...]]:
        """ :returns: EffectStack with remaining effects and all popped effects. """
        from .effect import GroupEffectBarrierEffect
        first_barrier_idx = self._first_barrier_idx()
        if first_barrier_idx == -1:
            return (EffectStack(()), self._effects)
        return (EffectStack(self._effects[first_barrier_idx+1:]), self._effects[:first_barrier_idx])

    def push_one(self, effect: Effect) -> EffectStack:
        """ :returns: the new EffectStack with `effect` pushed onto it. """
        return EffectStack(self._effects + (effect, ))

    def push_many_lf(self, effects: Sequence[Effect]) -> EffectStack:
        """
        :returns: the new EffectStack with `effects` pushed onto it.

        lf means the effects passed in are executed from the last to the first.
        """
        effects = tuple(effects)
        if not effects:
            return self
        return EffectStack(self._effects + effects)

    def push_many_fl(self, effects: Sequence[Effect]) -> EffectStack:
        """
        :returns: the new EffectStack with `effects` pushed onto it.

        fl means the effects passed in are executed from the first to the last.
        """
        effects = tuple(effects)
        if not effects:
            return self
        return EffectStack(self._effects + effects[::-1])

    def push_left(self, effects: Effect | Sequence[Effect]) -> EffectStack:
        """
        :returns: the new EffectStack with `effects` pushed onto it. The push follows FIFO, like a queue.
        """
        if not isinstance(effects, Sequence):
            effects = (effects, )
        effects = tuple(effects)
        return EffectStack(effects + self._effects)

    def push_barrier_left(self) -> EffectStack:
        """
        :returns: the new EffectStack with a barrier left-pushed.

        A barrier separates effects returned by `peek_all` into two groups, and only
        one group can be popped at a time.
        """
        from .effect import GroupEffectBarrierEffect
        return self.push_left(GroupEffectBarrierEffect())

    def contains(self, effect_type: type[Effect]) -> bool:
        """
        :returns: `True` if there's an effect of the exact type of`effect_type`.
        """
        for effect in self._effects:
            if type(effect) == effect_type:
                return True
        return False

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this EffectStack.
        """
        ret_val: list[list[int]] = [
            effect.encoding(encoding_plan)
            for effect in self._effects
        ]
        fillings = encoding_plan.EFFECTS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"Too many effects: {len(self._effects)}")
        for _ in range(fillings):
            ret_val.append([0] * encoding_plan.EFFECT_FIXED_LEN)
        return list(chain.from_iterable(ret_val))

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
