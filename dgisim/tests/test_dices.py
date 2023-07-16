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

    # test_smart_selection template
    # def test_smart_selection(self):
    #     input_actual_dices: ActualDices = ActualDices()
    #     input_abstract_dices: AbstractDices = AbstractDices()
    #     input_precedence: List[Set[Element]] = []
    #     #
    #     # self.assertEqual()

    # def test_smart_selection_omni(self, k: int, n: int):
    def test_smart_selection_omni(
            self, k: int = 3, n: int = 2, element: Element = Element.GEO):
        input_actual_dices: ActualDices = ActualDices(dices={element: k})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.OMNI: n})
        input_precedence: List[Set[Element]] = []

        actual = input_actual_dices.smart_selection(
            requirement=input_abstract_dices,
            game_state=None,
            local_precedence=input_precedence)

        if k >= n:
            expected = ActualDices(dices={element: n})
        else:
            expected = None
        print(actual.to_string())
        print(expected.to_string())
        self.assertEqual(actual, expected)

    def test_smart_selection_any(
            self, k: int = 3, n: int = 2, element: Element = Element.GEO):
        input_actual_dices: ActualDices = ActualDices(dices={element: k})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.ANY: n})
        input_precedence: List[Set[Element]] = []

        actual = input_actual_dices.smart_selection(
            requirement=input_abstract_dices,
            game_state=None,
            local_precedence=input_precedence)

        if k >= n:
            expected = ActualDices(dices={element: n})
        else:
            expected = None

        self.assertEqual(actual, expected)

        # result_1
        #
        #
        # self.assertEqual()

    NUMBER_OF_ELEMENTS: int = len(ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY)

    all_elements: List[Element] = ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY

    def test_smart_selection_all_any(self, number_of_any: int = 6):
        """one die of every element"""

        input_actual_dices: ActualDices = ActualDices(
            dices={el: 1 for el in self.all_elements})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.ANY: number_of_any})
        input_precedence: List[Set[Element]] = [
            {el} for el in self.all_elements]

        actual: ActualDices = input_actual_dices.smart_selection(
            requirement=input_abstract_dices, game_state=None, local_precedence=input_precedence)

        if self.NUMBER_OF_ELEMENTS >= number_of_any:
            expected: Optional[ActualDices] = ActualDices(
                {el: 1 for el in self.all_elements[-number_of_any:]})
        else:
            expected: Optional[ActualDices] = None

        self.assertEqual(actual, expected)

    def test_smart_selection_all_any_plus_one_omni_actual(
            self, number_of_any_need: int = 6):
        """one die of every element"""

        input_actual_dices: ActualDices = ActualDices(
            dices={el: 1 for el in self.all_elements[-(number_of_any_need - 1):] + [Element.OMNI]})
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.ANY: number_of_any_need})
        input_precedence: List[Set[Element]] = [
            {el} for el in self.all_elements]

        actual: ActualDices = input_actual_dices.smart_selection(
            requirement=input_abstract_dices, game_state=None, local_precedence=input_precedence)

        if number_of_any_need <= self.NUMBER_OF_ELEMENTS + 1:
            expected: Optional[ActualDices] = input_actual_dices
        else:
            expected: Optional[ActualDices] = None

        self.assertEqual(actual, expected)
