import unittest

from dgisim.src.dices import *
from dgisim.src.element import *


class TestDices(unittest.TestCase):
    def test_pick_random_dices(self):
        dices = Dices(ActualDices.from_random(8).to_dict())
        left, picked = dices.pick_random_dices(3)
        self.assertEqual(picked.num_dices(), 3)
        self.assertEqual(left.num_dices(), 5)
        sum_backed = left + picked
        self.assertEqual(dices, sum_backed)
        self.assertEqual(hash(dices), hash(sum_backed))
        
        left, picked = dices.pick_random_dices(0)
        self.assertIs(dices, left)
        self.assertEqual(picked.num_dices(), 0)

    def test_contains(self):
        dices = Dices({Element.ANEMO: 3, Element.PYRO: 0, Element.OMNI: -2})
        self.assertIn(Element.ANEMO, dices)
        self.assertNotIn(Element.PYRO, dices)
        self.assertNotIn(Element.OMNI, dices)

    def test_eq(self):
        dices = Dices({})
        self.assertNotEqual(dices, "dices")

    def test_to_dict(self):
        random_actual_dices = ActualDices.from_random(8)
        _dices = random_actual_dices._dices
        to_dict = random_actual_dices.to_dict()
        dices1 = Dices(_dices)
        dices2 = Dices(to_dict)
        self.assertEqual(dices1, dices2)
        self.assertIsNot(_dices, to_dict)

    def test_from_dices(self):
        dices = Dices({Element.PYRO: 6, Element.OMNI: 2})
        actual_dices = ActualDices.from_dices(dices)
        assert actual_dices is not None
        self.assertEqual(dices._dices, actual_dices._dices)

        dices = Dices({Element.PYRO: 6, Element.ANY: 2})
        actual_dices = ActualDices.from_dices(dices)
        self.assertIsNone(actual_dices)

        dices = Dices({Element.PYRO: 6, Element.OMNI: 2, Element.ANY: 2})
        abstract_dices = AbstractDices.from_dices(dices)
        assert abstract_dices is not None
        self.assertEqual(dices._dices, abstract_dices._dices)

        dices = Dices({Element.PYRO: 6, Element.OMNI: 2, Element.ANY: -2})
        abstract_dices = AbstractDices.from_dices(dices)
        self.assertIsNone(abstract_dices)

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

    def test_basically_satisfy_successes(self):
        requirement = AbstractDices({Element.OMNI: 3})
        payment = ActualDices({Element.CRYO: 3, Element.ANEMO: 1})
        self.assertEqual(payment.basically_satisfy(requirement), ActualDices({Element.CRYO: 3}))

        requirement = AbstractDices({Element.OMNI: 3})
        payment = ActualDices({Element.CRYO: 2, Element.OMNI: 2})
        self.assertEqual(payment.basically_satisfy(requirement), ActualDices({Element.CRYO: 2, Element.OMNI: 1}))

    def test_basically_satisfy_failures(self):
        requirement = AbstractDices({Element.ANY: 8})
        payment = ActualDices({Element.OMNI: 7})
        self.assertIsNone(payment.basically_satisfy(requirement))

        requirement = AbstractDices({Element.OMNI: 4})
        payment = ActualDices({Element.GEO: 3, Element.ELECTRO: 2, Element.HYDRO: 1, Element.DENDRO: 3})
        self.assertIsNone(payment.basically_satisfy(requirement))


