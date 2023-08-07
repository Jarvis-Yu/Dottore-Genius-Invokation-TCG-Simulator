import unittest

from dgisim.src.summon.summon import *
from dgisim.src.summon.summons import *

class SummonA(Summon):
    ...

class SummonB(Summon):
    ...

class TestSummons(unittest.TestCase):
    def test_get_summons(self):
        summons_tuple = (SummonA(), SummonB())
        summons = Summons(summons_tuple, max_num=4)
        self.assertEqual(summons.get_summons(), summons_tuple)

    def test_full(self):
        summons = Summons((), max_num=4)
        self.assertFalse(summons.full())

        summons = Summons((SummonA(), SummonA(), SummonB()), max_num=4)
        self.assertFalse(summons.full())

        summons = Summons((SummonA(), SummonB(), SummonA(), SummonB()), max_num=4)
        self.assertTrue(summons.full())

    def test_len(self):
        summons = Summons((), max_num=4)
        self.assertEqual(summons.len(), 0)

        summons = Summons((SummonA(), SummonA(), SummonB()), max_num=4)
        self.assertEqual(summons.len(), 3)

        summons = Summons((SummonA(), SummonB(), SummonA(), SummonB()), max_num=4)
        self.assertEqual(summons.len(), 4)

    def test_eq_hash(self):
        summonsA = Summons((), max_num=4)
        summonsB = Summons((), max_num=4)
        summonsC = Summons((SummonA(), SummonB()), max_num=4)
        summonsD = Summons((SummonA(), SummonB()), max_num=4)
        summonsE = Summons((SummonB(), SummonA()), max_num=4)
        self.assertEqual(summonsA, summonsB)
        self.assertEqual(hash(summonsA), hash(summonsB))
        self.assertNotEqual(summonsA, summonsC)
        self.assertNotEqual(hash(summonsA), hash(summonsC))
        self.assertEqual(summonsC, summonsD)
        self.assertEqual(hash(summonsC), hash(summonsD))
        self.assertNotEqual(summonsC, summonsE)
        self.assertEqual(hash(summonsC), hash(summonsE))  # hash equal for having same data
        self.assertNotEqual(summonsC, SummonA)
