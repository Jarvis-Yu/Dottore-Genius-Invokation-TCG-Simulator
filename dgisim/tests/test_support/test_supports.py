import unittest
from typing_extensions import Self, override

from dgisim.src.support.supports import Supports
from dgisim.src.support.support import Support

class SupportA(Support):
    pass

class SupportB(Support):
    @override
    def _update(self, other: Self) -> None | Self:
        return type(self)(sid=self.sid)

class SupportC(Support):
    @override
    def _update(self, other: Self) -> None | Self:
        return None

class TestSupports(unittest.TestCase):
    def test_get_supports(self):
        supports = Supports((SupportA(sid=1), SupportB(sid=2), SupportC(sid=3)), max_num=4)
        supports_tuple = supports.get_supports()
        self.assertIsInstance(supports_tuple[0], SupportA)
        self.assertIsInstance(supports_tuple[1], SupportB)
        self.assertIsInstance(supports_tuple[2], SupportC)

    def test_find_by_sid(self):
        supports = Supports((SupportA(sid=1), SupportB(sid=2), SupportC(sid=3)), max_num=4)
        self.assertIsInstance(supports.find_by_sid(1), SupportA)
        self.assertIsInstance(supports.find_by_sid(3), SupportC)
        self.assertIsInstance(supports.find_by_sid(2), SupportB)
        self.assertIsNone(supports.find_by_sid(-1))

    def test_update_support(self):
        supports = Supports((SupportA(sid=1), SupportB(sid=3)), max_num=4)
        self.assertRaises(Exception, lambda: supports.update_support(SupportC(sid=1)))
        self.assertRaises(Exception, lambda: supports.update_support(SupportC(sid=3)))
        supports = supports.update_support(SupportC(sid=2))
        self.assertIn(SupportC, supports)
        supports = supports.update_support(SupportC(sid=2))
        self.assertNotIn(SupportC, supports)
        old_ptr = supports.find_by_sid(3)
        new_ptr = SupportB(sid=3)
        supports = supports.update_support(new_ptr)
        curr_ptr = supports.find_by_sid(3)
        self.assertIs(curr_ptr, old_ptr)
        self.assertIsNot(curr_ptr, new_ptr)

        # test max num
        supports = Supports((SupportA(sid=1), SupportB(sid=3)), max_num=2)
        self.assertRaises(Exception, lambda: supports.update_support(SupportC(sid=2)))

    def test_remove_by_sid(self):
        supports = Supports((SupportA(sid=1), SupportB(sid=3)), max_num=4)
        supports = supports.remove_by_sid(3)
        self.assertIn(SupportA, supports)
        self.assertNotIn(SupportB, supports)
        supports = supports.remove_by_sid(0)
        self.assertIn(SupportA, supports)
        self.assertNotIn(SupportB, supports)

    def test_contains_exactly(self):
        supports = Supports((SupportA(sid=1), SupportB(sid=3)), max_num=4)
        self.assertTrue(supports.contains_exactly(SupportA, 1))
        self.assertFalse(supports.contains_exactly(SupportA, 2))
        self.assertFalse(supports.contains_exactly(SupportB, 1))
    
    def test_len(self):
        supports = Supports((SupportA(sid=1), SupportB(sid=3), SupportA(sid=2)), max_num=4)
        self.assertEqual(supports.len(), 3)
        self.assertEqual(len(supports), 3)
        supports = supports.remove_by_sid(1)
        self.assertEqual(supports.len(), 2)
        self.assertEqual(len(supports), 2)
