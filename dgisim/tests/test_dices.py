import unittest

from dgisim.src.dices import *
from dgisim.src.element.element import *


class TestDices(unittest.TestCase):

    def test_just_satisfy_pure_request(self):
        requirement = AbstractDices({
            Element.PYRO: 2,
        })
        payment1 = ActualDices({
            Element.OMNI: 2,
        })
        payment2 = ActualDices({
            Element.OMNI: 1,
            Element.PYRO: 1,
        })
        payment3 = ActualDices({
            Element.PYRO: 2,
        })
        payment4 = ActualDices({
            Element.PYRO: 3,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))

    def test_just_satisfy_typical_1pure_2any(self):
        requirement = AbstractDices({
            Element.DENDRO: 1,
            Element.ANY: 2,
        })
        payment1 = ActualDices({
            Element.OMNI: 3,
        })
        payment2 = ActualDices({
            Element.OMNI: 1,
            Element.PYRO: 1,
            Element.ELECTRO: 1,
        })
        payment3 = ActualDices({
            Element.DENDRO: 3,
        })
        payment4 = ActualDices({
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.ANEMO: 1,
        })
        payment5 = ActualDices({
            Element.GEO: 2,
            Element.ANEMO: 1,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertTrue(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_just_satisfy_typical_elemental_skill(self):
        requirement = AbstractDices({
            Element.ELECTRO: 3,
        })
        payment1 = ActualDices({
            Element.OMNI: 3,
        })
        payment2 = ActualDices({
            Element.OMNI: 1,
            Element.ELECTRO: 2,
        })
        payment3 = ActualDices({
            Element.ELECTRO: 3,
        })
        payment4 = ActualDices({
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.ANEMO: 1,
        })
        payment5 = ActualDices({
            Element.GEO: 2,
            Element.ANEMO: 1,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_just_satisfy_typical_all_omni(self):
        requirement = AbstractDices({
            Element.OMNI: 4,
        })
        payment1 = ActualDices({
            Element.OMNI: 4,
        })
        payment2 = ActualDices({
            Element.OMNI: 1,
            Element.ELECTRO: 3,
        })
        payment3 = ActualDices({
            Element.ELECTRO: 4,
        })
        payment4 = ActualDices({
            Element.OMNI: 4,
            Element.DENDRO: 1,
        })
        payment5 = ActualDices({
            Element.GEO: 2,
            Element.ANEMO: 2,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

