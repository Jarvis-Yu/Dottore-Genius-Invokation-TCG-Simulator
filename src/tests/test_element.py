import unittest

from src.dgisim.element import *


class TestElement(unittest.TestCase):
    def test_reaction_detail(self):
        ReactionDetail(Reaction.BLOOM, Element.DENDRO, Element.HYDRO)
        ReactionDetail(Reaction.BLOOM, Element.HYDRO, Element.DENDRO)
        self.assertRaises(
            Exception,
            lambda: ReactionDetail(Reaction.BLOOM, Element.DENDRO, Element.GEO)
        )
        self.assertRaises(
            Exception,
            lambda: ReactionDetail(Reaction.ELECTRO_CHARGED, Element.PYRO, Element.CRYO)
        )

    def test_elemental_aura(self):
        # peek()
        aura = ElementalAura.from_default().add(Element.DENDRO).add(Element.CRYO)
        self.assertIs(aura.peek(), Element.CRYO)
        self.assertIs(aura.peek(), Element.CRYO)
        aura = ElementalAura.from_default()
        self.assertIsNone(aura.peek())

        # eq and hash
        aura1 = ElementalAura.from_default().add(Element.DENDRO).add(Element.CRYO)
        aura2 = ElementalAura.from_default().add(Element.CRYO).add(Element.DENDRO)
        aura3 = ElementalAura.from_default().add(Element.CRYO)
        self.assertEqual(aura1, aura2)
        self.assertEqual(hash(aura1), hash(aura2))
        self.assertNotEqual(aura1, aura3)
        self.assertNotEqual(hash(aura1), hash(aura3))
        self.assertNotEqual(aura1, "aura1")
