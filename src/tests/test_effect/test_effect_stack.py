import unittest
from dataclasses import dataclass

from src.dgisim.effect.effect_stack import EffectStack
from src.dgisim.effect.effect import Effect


@dataclass(frozen=True, kw_only=True)
class IdEffect(Effect):
    id: int


class TestEffectStack(unittest.TestCase):
    BASE_EFFECT_STACK = EffectStack((
        IdEffect(id=1),
        IdEffect(id=2),
    ))

    def test_push_many_lf(self):
        effect_stack = EffectStack((
            IdEffect(id=1),
            IdEffect(id=2),
        ))
        effect_stack = effect_stack.push_many_lf((
            IdEffect(id=3),
            IdEffect(id=4),
        ))
        effect_stack, effect = effect_stack.pop()
        self.assertEqual(effect.id, 4)  # type: ignore
        effect_stack, effect = effect_stack.pop()
        self.assertEqual(effect.id, 3)  # type: ignore

        new_effect_stack = effect_stack.push_many_lf(())
        self.assertIs(new_effect_stack, effect_stack)

    def test_contains(self):
        effect_stack_a = self.BASE_EFFECT_STACK
        effect_stack_b = EffectStack((
            Effect(),
            Effect(),
            Effect(),
        ))
        effect_stack_c = EffectStack((
            Effect(),
            Effect(),
            Effect(),
            IdEffect(id=1),
        ))
        effect_stack_d = EffectStack((
            IdEffect(id=1),
            Effect(),
            Effect(),
            Effect(),
        ))
        effect_stack_e = EffectStack((
            Effect(),
            Effect(),
            IdEffect(id=1),
            Effect(),
        ))
        self.assertTrue(effect_stack_a.contains(IdEffect))
        self.assertFalse(effect_stack_b.contains(IdEffect))
        self.assertTrue(effect_stack_c.contains(IdEffect))
        self.assertTrue(effect_stack_d.contains(IdEffect))
        self.assertTrue(effect_stack_e.contains(IdEffect))

    def test__eq__(self):
        effect_stack_a1 = EffectStack((
            IdEffect(id=1),
            IdEffect(id=2),
        ))
        effect_stack_a2 = EffectStack((
            IdEffect(id=1),
            IdEffect(id=2),
        ))
        effect_stack_a3 = effect_stack_a1
        effect_stack_b1 = EffectStack((
            IdEffect(id=2),
            IdEffect(id=1),
        ))
        self.assertTrue(effect_stack_a1 == effect_stack_a2)
        self.assertTrue(effect_stack_a2 == effect_stack_a1)
        self.assertTrue(effect_stack_a1 == effect_stack_a3)
        self.assertTrue(effect_stack_a2 != effect_stack_b1)
        self.assertTrue(effect_stack_a2 != Effect())

    def test__hash__(self):
        effect_stack_a1 = EffectStack((
            IdEffect(id=1),
            IdEffect(id=2),
        ))
        effect_stack_a2 = EffectStack((
            IdEffect(id=1),
            IdEffect(id=2),
        ))
        x = set()
        x.add(effect_stack_a1)
        x.add(effect_stack_a2)
        self.assertEqual(len(x), 1)
