import unittest
from typing import Optional

from dgisim.src.dices import *
from dgisim.src.element import *
from dgisim.src.helper import just


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
        self.assertEqual(payment.basically_satisfy(requirement),
                         ActualDices({Element.CRYO: 2, Element.OMNI: 1}))

        requirement = AbstractDices({Element.OMNI: 3})
        payment = ActualDices({Element.ANEMO: 1, Element.ELECTRO: 1,
                              Element.PYRO: 1, Element.OMNI: 2})
        self.assertEqual(just(payment.basically_satisfy(requirement))[Element.OMNI], 2)

    def test_basically_satisfy_failures(self):
        requirement = AbstractDices({Element.ANY: 8})
        payment = ActualDices({Element.OMNI: 7})
        self.assertIsNone(payment.basically_satisfy(requirement))

        requirement = AbstractDices({Element.OMNI: 4})
        payment = ActualDices({Element.GEO: 3, Element.ELECTRO: 2,
                              Element.HYDRO: 1, Element.DENDRO: 3})
        self.assertIsNone(payment.basically_satisfy(requirement))

    def test_ordered_actual_dices(self):
        dices = ActualDices({
            Element.HYDRO: 1,
            Element.ELECTRO: 1,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 1,
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.PYRO: 1,
        })
        self.assertEqual(
            tuple(dices.readonly_dices_ordered(None).keys()),
            ActualDices._LEGAL_ELEMS_ORDERED,
        )

    def test_ordered_actual_dices_with_diff_nums(self):
        dices = ActualDices({
            Element.HYDRO: 1,
            Element.ELECTRO: 2,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 2,
            Element.OMNI: 1,
            Element.DENDRO: 2,
            Element.PYRO: 1,
        })
        keys = tuple(dices.readonly_dices_ordered(None).keys())
        expected_order = (
            Element.OMNI,
            Element.CRYO,
            Element.ELECTRO,
            Element.DENDRO,
            Element.HYDRO,
            Element.PYRO,
            Element.GEO,
            Element.ANEMO,
        )
        self.assertEqual(
            keys,
            expected_order,
        )

    def test_ordered_actual_dices_with_characters(self):
        dices = ActualDices({
            Element.HYDRO: 1,
            Element.ELECTRO: 2,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 2,
            Element.OMNI: 1,
            Element.DENDRO: 2,
            Element.PYRO: 1,
        })
        from dgisim.src.card.cards import Cards
        from dgisim.src.character.character import AratakiItto, Klee, Keqing
        from dgisim.src.character.characters import Characters
        from dgisim.src.mode import DefaultMode
        from dgisim.src.state.player_state import PlayerState
        player_state = PlayerState.from_chars_cards(
            DefaultMode(),
            Characters.from_iterable(
                [AratakiItto, Klee, Keqing]
            ).factory().active_character_id(2).build(),
            Cards({}),
        )
        keys = tuple(dices.readonly_dices_ordered(player_state).keys())
        expected_order = (
            Element.OMNI,
            Element.ELECTRO,
            Element.PYRO,
            Element.GEO,
            Element.CRYO,
            Element.DENDRO,
            Element.HYDRO,
            Element.ANEMO,
        )
        self.assertEqual(
            keys,
            expected_order,
        )

    # test_smart_selection template
    # def test_smart_selection(self):
    #     input_actual_dices: ActualDices = ActualDices()
    #     input_abstract_dices: AbstractDices = AbstractDices()
    #     input_precedence: List[set[Element]] = []
    #
    #     self.assertEqual()
    #
    # def test_smart_selection_TEMPLATE(self, k: int, n: int):

    def test_smart_selection_omni(
            self, element: Element = Element.GEO):
        """test if element can fill OMNI"""
        for omni_number in (2, 3, 5):
            for element_number in (2, 3, 5):
                with self.subTest(omni_number=omni_number, element_number=element_number):
                    input_actual_dices: ActualDices = ActualDices(dices={element: element_number})
                    input_abstract_dices: AbstractDices = AbstractDices(
                        dices={Element.OMNI: omni_number}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dices.smart_selection(
                        requirement=input_abstract_dices,
                        game_state=None,
                        local_precedence_arg=input_precedence
                    )

                    if element_number >= omni_number:
                        expected = ActualDices(dices={element: omni_number})
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
                        dices={Element.ANY: any_number}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dices.smart_selection(
                        requirement=input_abstract_dices,
                        game_state=None,
                        local_precedence_arg=input_precedence
                    )
                    if element_number >= any_number:
                        expected = ActualDices(dices={element: any_number})
                    else:
                        expected = None

                    self.assertEqual(actual, expected)

    def test_smart_selection_all_any(self):
        """test one die of every Element can fill ANY in proper order"""
        for number_of_any in range(1, len(Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY) + 1):
            with self.subTest(number_of_any=number_of_any):
                input_actual_dices: ActualDices = ActualDices(
                    dices={el: 1 for el in Dices._ELEMENTS}
                )
                input_abstract_dices: AbstractDices = AbstractDices(
                    dices={Element.ANY: number_of_any}
                )
                input_precedence: list[set[Element]] = [
                    {el} for el in Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
                ]

                actual: Optional[ActualDices] = input_actual_dices.smart_selection(
                    requirement=input_abstract_dices, game_state=None, local_precedence_arg=input_precedence
                )

                if Dices._NUMBER_OF_ELEMENTS >= number_of_any:
                    expected: Optional[ActualDices] = ActualDices(
                        {el: 1 for el in Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY[-number_of_any:]}
                    )
                else:
                    expected = None

                self.assertEqual(actual, expected)

    def test_smart_selection_all_any_plus_one_omni_actual(self):
        """test one die of every element from a to b, b-a+1 ANY
        a<b"""
        elements_and_omni = [Element.OMNI] + list(Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY)
        for a in range(len(elements_and_omni)):
            for b in range(a + 1, len(elements_and_omni)):
                # need = supply, need < supply, need > supply
                for any_need_number in [(b - a + 1), (b - a), (b - a + 2)]:
                    with self.subTest(a=a, b=b, any_need_number=any_need_number):
                        input_actual_dices: ActualDices = ActualDices(
                            dices={el: 1 for el in elements_and_omni[a:b + 1]}
                        )
                        input_abstract_dices: AbstractDices = AbstractDices(
                            dices={Element.ANY: any_need_number}
                        )
                        input_precedence: list[set[Element]] = [
                            {el} for el in Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
                        ]

                        actual: Optional[ActualDices] = input_actual_dices.smart_selection(
                            requirement=input_abstract_dices, game_state=None,
                            local_precedence_arg=input_precedence
                        )

                        if any_need_number == (b - a + 1):  # =
                            expected: Optional[ActualDices] = input_actual_dices
                        elif any_need_number == (b - a):  # need < supply
                            expected = ActualDices(
                                dices={el: 1 for el in elements_and_omni[a + 1:b + 1]})
                        elif any_need_number == (b - a + 2):
                            expected = None
                        self.assertEqual(actual, expected)

    def test_smart_selection_concrete_element(
            self, element: Element = Element.GEO):
        """test fill element with itself
        needed=1..10
        supply=1..10"""

        for needed in range(1, 11):
            for supply in range(1, 11):
                with self.subTest(needed=needed, supply=supply):
                    input_actual_dices: ActualDices = ActualDices(dices={element: supply})
                    input_abstract_dices: AbstractDices = AbstractDices(
                        dices={element: needed}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dices.smart_selection(
                        requirement=input_abstract_dices,
                        game_state=None,
                        local_precedence_arg=input_precedence
                    )

                    if supply >= needed:
                        expected = ActualDices(dices={element: needed})
                    else:
                        expected = None

                    self.assertEqual(actual, expected)

    def test_smart_selection_precedence(self):
        """basic test on elements local precedence"""
        element_geo = Element.GEO
        element_pyro = Element.PYRO
        for any_needed_number in range(5, 16, 5):
            for element_geo_number in range(20):
                for element_pyro_number in range(20):
                    for element_first_bigger_precedence in [False, True]:
                        with self.subTest(
                                any_needed_number=any_needed_number,
                                element_geo_number=element_geo_number,
                                element_pyro_number=element_pyro_number,
                                element_first_bigger_precedence=element_first_bigger_precedence
                        ):
                            input_actual_dices: ActualDices = ActualDices(
                                dices={element_geo: element_geo_number,
                                       element_pyro: element_pyro_number}
                            )
                            input_abstract_dices: AbstractDices = AbstractDices(
                                dices={Element.ANY: any_needed_number}
                            )

                            input_precedence: list[set[Element]] = [
                                {element_geo}, {element_pyro}
                            ]

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
                                        element_1_number, any_needed_number - element_1_number
                                    )

                                expected = ActualDices(
                                    dices={
                                        element_1: element_1_filling,
                                        element_2: element_2_filling
                                    }
                                )
                            else:
                                expected = None

                            self.assertEqual(
                                actual, expected, msg=f"{actual=} {expected=}"
                            )

    def test_smart_selection_something_supply_empty_need(self):
        """test empty need with non-empty supply"""
        input_actual_dices: ActualDices = ActualDices(
            {el: 1 for el in list(Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY) + [Element.OMNI]})
        input_abstract_dices: AbstractDices = AbstractDices({})
        input_precedence: list[set[Element]] = []

        actual = input_actual_dices.smart_selection(
            requirement=input_abstract_dices,
            game_state=None,
            local_precedence_arg=input_precedence
        )
        expected = ActualDices({})
        self.assertEqual(actual, expected)

    def test_smart_selection_empty_supply_empty_need(self):
        """test empty need with non-empty supply"""
        input_actual_dices: ActualDices = ActualDices({})
        input_abstract_dices: AbstractDices = AbstractDices({})
        input_precedence: list[set[Element]] = []

        actual = input_actual_dices.smart_selection(
            requirement=input_abstract_dices,
            game_state=None,
            local_precedence_arg=input_precedence
        )
        expected = ActualDices({})
        self.assertEqual(actual, expected)

    def test_smart_selection_negative(self):
        """negative test
        to code-coverage
        Element and OtherElement and OMNI supply
        Element need"""
        element = Element.GEO
        other_element = Element.CRYO

        for element_supply_number in range(5):
            for omni_supply_number in range(5):
                element_need_number = element_supply_number + omni_supply_number + 1
                with self.subTest(element=element, element_supply_number=element_supply_number,
                                  omni_supply_number=omni_supply_number, element_need_number=element_need_number):
                    # first_element_supply_number = 3
                    # omni_supply_number = 2
                    # omni_need_number = 4
                    input_actual_dices: ActualDices = ActualDices(
                        {element: element_supply_number, Element.OMNI: omni_supply_number, other_element: 2}
                    )
                    input_abstract_dices: AbstractDices = AbstractDices(
                        {element: element_need_number}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dices.smart_selection(
                        requirement=input_abstract_dices,
                        game_state=None,
                        local_precedence_arg=input_precedence
                    )

                    expected = None
                    self.assertEqual(actual, expected)

    def test_smart_selection_code_cover(self):
        """Element and OMNI feed OMNI
        code cover"""
        first_element = Element.GEO  # most precedent element

        for first_element_supply_number in range(5):
            for omni_supply_number in range(5):
                for omni_need_number in [1, 3, 5]:
                    with self.subTest(first_element=first_element,
                                      first_element_supply_number=first_element_supply_number,
                                      omni_supply_number=omni_supply_number, omni_need_number=omni_need_number):
                        first_element_supply_number = 3
                        omni_supply_number = 2
                        omni_need_number = 4
                        input_actual_dices: ActualDices = ActualDices(
                            {first_element: first_element_supply_number, Element.OMNI: omni_supply_number})
                        input_abstract_dices: AbstractDices = AbstractDices(
                            {Element.OMNI: omni_need_number})
                        input_precedence: list[set[Element]] = [{first_element}]

                        actual = input_actual_dices.smart_selection(
                            requirement=input_abstract_dices,
                            game_state=None,
                            local_precedence_arg=input_precedence
                        )

                        if first_element_supply_number + omni_supply_number >= omni_need_number:
                            expected = ActualDices({first_element: first_element_supply_number,
                                                    Element.OMNI: omni_need_number - first_element_supply_number})
                        else:
                            expected = None
                        self.assertEqual(actual, expected)

    def test_smart_selection_negative_2(self):
        """test for code coverage.
        supply: 2 of every elements
        need: 5 omni"""
        elements_and_omni = [Element.OMNI] + list(Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY)
        input_actual_dices: ActualDices = ActualDices(
            dices={el: 2 for el in elements_and_omni}
        )
        input_abstract_dices: AbstractDices = AbstractDices(
            dices={Element.OMNI: 5}
        )
        input_precedence: list[set[Element]] = [
            {el} for el in Dices._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
        ]

        actual: Optional[ActualDices] = input_actual_dices.smart_selection(
            requirement=input_abstract_dices, game_state=None, local_precedence_arg=input_precedence
        )

        expected = None
        self.assertEqual(actual, expected)
