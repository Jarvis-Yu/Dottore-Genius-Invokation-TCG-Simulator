import unittest
from typing import Optional

from dgisim.src.dices import *
from dgisim.src.dices import ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY, NUMBER_OF_ELEMENTS, ELEMENTS
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
        self.assertEqual(payment.basically_satisfy(
            requirement), ActualDices({Element.CRYO: 3}))

        requirement = AbstractDices({Element.OMNI: 3})
        payment = ActualDices({Element.CRYO: 2, Element.OMNI: 2})
        self.assertEqual(payment.basically_satisfy(requirement),
                         ActualDices({Element.CRYO: 2, Element.OMNI: 1}))

    def test_basically_satisfy_failures(self):
        requirement = AbstractDices({Element.ANY: 8})
        payment = ActualDices({Element.OMNI: 7})
        self.assertIsNone(payment.basically_satisfy(requirement))

        requirement = AbstractDices({Element.OMNI: 4})
        payment = ActualDices({Element.GEO: 3, Element.ELECTRO: 2,
                               Element.HYDRO: 1, Element.DENDRO: 3})
        self.assertIsNone(payment.basically_satisfy(requirement))

    # # test_smart_selection template
    # # def test_smart_selection(self):
    # #     input_actual_dices: ActualDices = ActualDices()
    # #     input_abstract_dices: AbstractDices = AbstractDices()
    # #     input_precedence: List[set[Element]] = []
    # #     #
    # #     # self.assertEqual()
    #
    # def test_smart_selection_omni(self, k: int, n: int):
    def test_smart_selection_omni(
            self, k: int = 3, n: int = 2, element: Element = Element.GEO):
        """test if element can fill OMNI"""
        input_actual_dices: ActualDices = ActualDices(dices={element: k})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.OMNI: n})
        input_precedence: list[set[Element]] = []

        actual = input_actual_dices.smart_selection(
            requirement=input_abstract_dices,
            game_state=None,
            local_precedence_arg=input_precedence)

        if k >= n:
            expected = ActualDices(dices={element: n})
        else:
            expected = None
        self.assertEqual(actual, expected)

    def test_smart_selection_any(self):
        """test one Element can fill ANY"""
        element: Element = Element.GEO
        for any_number in (2, 3, 5):
            for element_number in (2, 3, 5):
                with self.subTest(any_number=any_number, element_number=element_number):
                    input_actual_dices: ActualDices = ActualDices(dices={element: element_number})
                    input_abstract_dices: AbstractDices = AbstractDices(
                        dices={Element.ANY: any_number})
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dices.smart_selection(
                        requirement=input_abstract_dices,
                        game_state=None,
                        local_precedence_arg=input_precedence)

                    if element_number >= any_number:
                        expected = ActualDices(dices={element: any_number})
                    else:
                        expected = None

                    self.assertEqual(actual, expected)

    def test_smart_selection_all_any(self, number_of_any: int = 6):
        """test one die of every element can fill any in proper order"""
        # TODO parametrize
        input_actual_dices: ActualDices = ActualDices(
            dices={el: 1 for el in ELEMENTS})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.ANY: number_of_any})
        input_precedence: list[set[Element]] = [
            {el} for el in ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY]

        actual: Optional[ActualDices] = input_actual_dices.smart_selection(
            requirement=input_abstract_dices, game_state=None, local_precedence_arg=input_precedence)

        if NUMBER_OF_ELEMENTS >= number_of_any:
            expected: Optional[ActualDices] = ActualDices(
                {el: 1 for el in ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY[-number_of_any:]})
        else:
            expected = None

        self.assertEqual(actual, expected)

    def test_smart_selection_all_any_plus_one_omni_actual(
            self, a: int = 0, b: int = 6):
        """test one die of every element from a to b, b-a+1 ANY
        a<b"""

        input_actual_dices: ActualDices = ActualDices(
            dices={el: 1 for el in ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY[a:b]})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.ANY: (b - a)})
        input_precedence: list[set[Element]] = [
            {el} for el in ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY]

        actual: Optional[ActualDices] = input_actual_dices.smart_selection(
            requirement=input_abstract_dices, game_state=None, local_precedence_arg=input_precedence)

        if b <= NUMBER_OF_ELEMENTS + 1:
            expected: Optional[ActualDices] = input_actual_dices
        else:
            expected = None

        self.assertEqual(actual, expected)

    def test_concrete_element(
            self, needed: int = 5, supply: int = 7, element: Element = Element.GEO):
        """test fill element with itself
        needed=1..10
        supply=1..10"""

        for needed in range(1, 11):
            for supply in range(1, 11):
                with self.subTest(needed=needed, supply=supply):
                    input_actual_dices: ActualDices = ActualDices(dices={element: supply})
                    input_abstract_dices: AbstractDices = AbstractDices(
                        dices={element: needed})
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dices.smart_selection(
                        requirement=input_abstract_dices,
                        game_state=None,
                        local_precedence_arg=input_precedence)

                    if supply >= needed:
                        expected = ActualDices(dices={element: needed})
                    else:
                        expected = None

                    self.assertEqual(actual, expected)

    def test_priority(self):
        """basic test on elements local priority"""
        element_geo = Element.GEO
        element_pyro = Element.PYRO
        for any_needed_number in range(5, 16, 5):
            for element_geo_number in range(20):
                for element_pyro_number in range(20):
                    for element_first_bigger_precedence in [False, True]:
                        with self.subTest(any_needed_number=any_needed_number,
                                          element_geo_number=element_geo_number,
                                          element_pyro_number=element_pyro_number,
                                          element_first_bigger_precedence=element_first_bigger_precedence):
                            input_actual_dices: ActualDices = ActualDices(
                                dices={element_geo: element_geo_number,
                                       element_pyro: element_pyro_number}
                            )
                            input_abstract_dices: AbstractDices = AbstractDices(
                                dices={Element.ANY: any_needed_number})

                            input_precedence: list[set[Element]] = [
                                {element_geo}, {element_pyro}]

                            if not element_first_bigger_precedence:
                                input_precedence = input_precedence[::-1]

                            actual = input_actual_dices.smart_selection(
                                requirement=input_abstract_dices,
                                game_state=None,
                                local_precedence_arg=input_precedence
                            )

                            if element_pyro_number + element_geo_number >= any_needed_number:
                                # element 1 should have lower precedence
                                element_1 = element_geo
                                element_2 = element_pyro
                                element_1_number = element_geo_number
                                element_2_number = element_pyro_number

                                if element_first_bigger_precedence:
                                    element_1, element_2 = element_2, element_1
                                    element_1_number, element_2_number = element_2_number, element_1_number

                                if element_1_number >= any_needed_number:
                                    element_1_filling, element_2_filling = any_needed_number, 0
                                else:
                                    element_1_filling, element_2_filling = (
                                        element_1_number, any_needed_number - element_1_number)

                                expected = ActualDices(
                                    dices={element_1: element_1_filling,
                                           element_2: element_2_filling}
                                )
                            else:
                                expected = None

                            self.assertEqual(
                                actual, expected, msg=f"{actual=} {expected=}")
