import unittest
from dataclasses import dataclass
from enum import Enum

from dgisim.src.helper.quality_of_life import *    

class TestQualityOfLife(unittest.TestCase):
    def test_big_int(self):
        self.assertGreater(BIG_INT, 0x0fffffff)

    def test_case_val(self):
        class A:
            pass
        a = A()
        b = Exception("123")
        self.assertIsInstance(case_val(True, a, b), A)
        self.assertIsInstance(case_val(False, a, b), Exception)

    def test_dataclass_repr(self):
        class XYZ:
            pass

        class EnumClass(Enum):
            ENUM1 = 1
            ENUM2 = 2

        @dataclass(repr=False)
        class DataClass:
            xyz: type[XYZ]
            enum_val: EnumClass

            def __repr__(self) -> str:
                return dataclass_repr(self)

        dataClass = DataClass(XYZ, EnumClass.ENUM2)
        representation = repr(dataClass)
        self.assertIn("=XYZ,", representation)
        self.assertIn("ENUM2)", representation)

    def test_just(self):
        x: None | int = None
        self.assertRaises(Exception, lambda: just(x))
        y: None | int = 2
        self.assertEqual(just(x, y), y)
        x = 10
        self.assertEqual(just(x, y), x)
