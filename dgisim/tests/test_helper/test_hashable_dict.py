import unittest
from typing import Any

from dgisim.src.helper.hashable_dict import HashableDict


class testHashableDict(unittest.TestCase):
    def test_freeze(self):
        hashable_dict: HashableDict[Any, Any] = HashableDict()
        hashable_dict.freeze()
        self.assertTrue(hashable_dict._frozen)

        hashable_dict = HashableDict(frozen=False)
        hashable_dict.freeze()
        self.assertTrue(hashable_dict._frozen)

    def test_exceptions(self):
        hashable_dict: HashableDict[int, int] = HashableDict({1: 2, 10: 20}, frozen=False)
        hashable_dict.not_exist = "not-exist"
        hashable_dict[1] = 3
        del hashable_dict.not_exist  # type: ignore
        del hashable_dict[10]

        hashable_dict.freeze()
        self.assertRaises(Exception, lambda: hashable_dict.__setattr__("not_exist", 123))
        self.assertRaises(Exception, lambda: hashable_dict.__setitem__(1, 5))
        self.assertRaises(Exception, lambda: hashable_dict.__delattr__("_frozen"))
        self.assertRaises(Exception, lambda: hashable_dict.__delitem__(1))

    def test_hash_and_eq(self):
        dict1: HashableDict[int, int] = HashableDict({1: 2, 9: 8})
        dict2: HashableDict[int, int] = HashableDict({9: 8, 1: 2})
        dict3: HashableDict[int, int] = HashableDict({2: 1, 8: 9})
        self.assertEqual(hash(dict1), hash(dict2))
        self.assertNotEqual(hash(dict1), hash(dict3))
        self.assertNotEqual(hash(dict2), hash(dict3))
        self.assertEqual(dict1, dict2)
        self.assertNotEqual(dict1, dict3)
        self.assertNotEqual(dict2, dict3)
        self.assertNotEqual(dict1, type(dict1))
        self.assertNotEqual(dict1, "dict1")

        dict3._unfreeze()
        dict4: HashableDict[Any, Any] = HashableDict(frozen=False)
        self.assertRaises(Exception, lambda: hash(dict3))
        self.assertRaises(Exception, lambda: hash(dict4))

    def test_unfrozen(self):
        dict1: HashableDict[int, int] = HashableDict({1: 2, 9: 4})
        hash_before = hash(dict1)
        dict1._unfreeze()
        dict1[1] = 142857
        dict1.freeze()
        hash_after = hash(dict1)
        self.assertNotEqual(hash_before, hash_after)
        self.assertEqual(dict1[1], 142857)

    def test_frozen_set(self):
        dict1: HashableDict[int, int] = HashableDict({1: 2, 9: 4})
        x = dict1._to_frozen_set()
        dict1._unfreeze()
        y = dict1._to_frozen_set()
        self.assertEqual(x, y)

    def test_all_val_non_negative(self):
        dict1: HashableDict[int, int] = HashableDict(
            {"x": 1, "y": -10000000, "z": 0xf0000000}, frozen=False
        )
        self.assertFalse(dict1.all_val_non_negative())
        dict1["y"] = 0
        self.assertTrue(dict1.all_val_non_negative())
