import unittest

from src.dgisim.character.character import * 
from src.dgisim.character.characters import Characters
from src.dgisim.dice import *
from src.dgisim.element import *
from src.dgisim.helper import just


class TestDice(unittest.TestCase):
    def test_pick_random_dice(self):
        dice = Dice(ActualDice.from_random(8).to_dict())
        left, picked = dice.pick_random_dice(3)
        self.assertEqual(picked.num_dice(), 3)
        self.assertEqual(left.num_dice(), 5)
        sum_backed = left + picked
        self.assertEqual(dice, sum_backed)
        self.assertEqual(hash(dice), hash(sum_backed))

        left, picked = dice.pick_random_dice(0)
        self.assertIs(dice, left)
        self.assertEqual(picked.num_dice(), 0)

    def test_contains(self):
        dice = Dice({Element.ANEMO: 3, Element.PYRO: 0, Element.OMNI: -2})
        self.assertIn(Element.ANEMO, dice)
        self.assertNotIn(Element.PYRO, dice)
        self.assertNotIn(Element.OMNI, dice)

    def test_eq(self):
        dice = Dice({})
        self.assertNotEqual(dice, "dice")

    def test_to_dict(self):
        random_actual_dice = ActualDice.from_random(8)
        _dice = random_actual_dice._dice
        to_dict = random_actual_dice.to_dict()
        dice1 = Dice(_dice)
        dice2 = Dice(to_dict)
        self.assertEqual(dice1, dice2)
        self.assertIsNot(_dice, to_dict)

    def test_from_dice(self):
        dice = Dice({Element.PYRO: 6, Element.OMNI: 2})
        actual_dice = ActualDice.from_dice(dice)
        assert actual_dice is not None
        self.assertEqual(dice._dice, actual_dice._dice)

        dice = Dice({Element.PYRO: 6, Element.ANY: 2})
        actual_dice = ActualDice.from_dice(dice)
        self.assertIsNone(actual_dice)

        dice = Dice({Element.PYRO: 6, Element.OMNI: 2, Element.ANY: 2})
        abstract_dice = AbstractDice.from_dice(dice)
        assert abstract_dice is not None
        self.assertEqual(dice._dice, abstract_dice._dice)

        dice = Dice({Element.PYRO: 6, Element.OMNI: 2, Element.ANY: -2})
        abstract_dice = AbstractDice.from_dice(dice)
        self.assertIsNone(abstract_dice)

    def test_just_satisfy_pure_request(self):
        requirement = AbstractDice({
            Element.PYRO: 2,
        })
        payment1 = ActualDice({
            Element.OMNI: 2,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.PYRO: 1,
        })
        payment3 = ActualDice({
            Element.PYRO: 2,
        })
        payment4 = ActualDice({
            Element.PYRO: 3,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))

    def test_just_satisfy_typical_1pure_2any(self):
        requirement = AbstractDice({
            Element.DENDRO: 1,
            Element.ANY: 2,
        })
        payment1 = ActualDice({
            Element.OMNI: 3,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.PYRO: 1,
            Element.ELECTRO: 1,
        })
        payment3 = ActualDice({
            Element.DENDRO: 3,
        })
        payment4 = ActualDice({
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.ANEMO: 1,
        })
        payment5 = ActualDice({
            Element.GEO: 2,
            Element.ANEMO: 1,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertTrue(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_just_satisfy_typical_elemental_skill(self):
        requirement = AbstractDice({
            Element.ELECTRO: 3,
        })
        payment1 = ActualDice({
            Element.OMNI: 3,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.ELECTRO: 2,
        })
        payment3 = ActualDice({
            Element.ELECTRO: 3,
        })
        payment4 = ActualDice({
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.ANEMO: 1,
        })
        payment5 = ActualDice({
            Element.GEO: 2,
            Element.ANEMO: 1,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_just_satisfy_typical_all_omni(self):
        requirement = AbstractDice({
            Element.OMNI: 4,
        })
        payment1 = ActualDice({
            Element.OMNI: 4,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.ELECTRO: 3,
        })
        payment3 = ActualDice({
            Element.ELECTRO: 4,
        })
        payment4 = ActualDice({
            Element.OMNI: 4,
            Element.DENDRO: 1,
        })
        payment5 = ActualDice({
            Element.GEO: 2,
            Element.ANEMO: 2,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_basically_satisfy_successes(self):
        requirement = AbstractDice({Element.OMNI: 3})
        payment = ActualDice({Element.CRYO: 3, Element.ANEMO: 1})
        self.assertEqual(payment.basically_satisfy(requirement), ActualDice({Element.CRYO: 3}))

        requirement = AbstractDice({Element.OMNI: 3})
        payment = ActualDice({Element.CRYO: 2, Element.OMNI: 2})
        self.assertEqual(payment.basically_satisfy(requirement),
                         ActualDice({Element.CRYO: 2, Element.OMNI: 1}))

        requirement = AbstractDice({Element.OMNI: 3})
        payment = ActualDice({Element.ANEMO: 1, Element.ELECTRO: 1,
                              Element.PYRO: 1, Element.OMNI: 2})
        self.assertEqual(just(payment.basically_satisfy(requirement))[Element.OMNI], 2)

    def test_basically_satisfy_failures(self):
        requirement = AbstractDice({Element.ANY: 8})
        payment = ActualDice({Element.OMNI: 7})
        self.assertIsNone(payment.basically_satisfy(requirement))

        requirement = AbstractDice({Element.OMNI: 4})
        payment = ActualDice({Element.GEO: 3, Element.ELECTRO: 2,
                              Element.HYDRO: 1, Element.DENDRO: 3})
        self.assertIsNone(payment.basically_satisfy(requirement))

    def test_ordered_actual_dice(self):
        dice = ActualDice({
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
            tuple(dice.readonly_dice_ordered(None).keys()),
            ActualDice._LEGAL_ELEMS_ORDERED,
        )

    def test_ordered_actual_dice_with_diff_nums(self):
        dice = ActualDice({
            Element.HYDRO: 1,
            Element.ELECTRO: 2,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 2,
            Element.OMNI: 1,
            Element.DENDRO: 2,
            Element.PYRO: 1,
        })
        keys = tuple(dice.readonly_dice_ordered(None).keys())
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

    def test_ordered_actual_dice_with_characters(self):
        dice = ActualDice({
            Element.HYDRO: 1,
            Element.ELECTRO: 2,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 2,
            Element.OMNI: 1,
            Element.DENDRO: 2,
            Element.PYRO: 1,
        })
        from src.dgisim.card.cards import Cards
        from src.dgisim.character.character import AratakiItto, Klee, Keqing
        from src.dgisim.character.characters import Characters
        from src.dgisim.mode import DefaultMode
        from src.dgisim.state.player_state import PlayerState
        player_state = PlayerState.from_chars_cards(
            DefaultMode(),
            Characters.from_iterable(
                [AratakiItto, Klee, Keqing]
            ).factory().active_character_id(2).build(),
            Cards({}),
        )
        keys = tuple(dice.readonly_dice_ordered(player_state).keys())
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

    def test_less_elem(self):
        dice = AbstractDice({Element.DENDRO: 1, Element.ANY: 2})
        self.assertTrue(dice.can_cost_less_elem())
        dice = dice.cost_less_elem(1)
        self.assertEqual(dice[Element.DENDRO], 0)
        self.assertEqual(dice[Element.ANY], 2)
        self.assertTrue(dice.can_cost_less_elem())
        dice = dice.cost_less_elem(1)
        self.assertEqual(dice[Element.DENDRO], 0)
        self.assertEqual(dice[Element.ANY], 1)
        self.assertTrue(dice.can_cost_less_elem())
        dice = dice.cost_less_elem(1)
        self.assertEqual(dice[Element.DENDRO], 0)
        self.assertEqual(dice[Element.ANY], 0)
        self.assertFalse(dice.can_cost_less_elem())

    def test_smart_selection_omni(
            self, element: Element = Element.GEO):
        """ test if element can fill OMNI """
        for omni_number in (2, 3, 5):
            for element_number in (2, 3, 5):
                with self.subTest(omni_number=omni_number, element_number=element_number):
                    input_actual_dice: ActualDice = ActualDice(dice={element: element_number})
                    input_abstract_dice: AbstractDice = AbstractDice(
                        dice={Element.OMNI: omni_number}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dice.smart_selection(
                        requirement=input_abstract_dice,
                        local_precedence=input_precedence
                    )

                    if element_number >= omni_number:
                        expected = ActualDice(dice={element: omni_number})
                    else:
                        expected = None
                    self.assertEqual(actual, expected)

    def test_smart_selection_any(self):
        """ test one Element can fill ANY """
        element: Element = Element.GEO
        for any_number in (2, 3, 5):
            for element_number in (2, 3, 5):
                with self.subTest(any_number=any_number, element_number=element_number):
                    input_actual_dice: ActualDice = ActualDice(dice={element: element_number})
                    input_abstract_dice: AbstractDice = AbstractDice(
                        dice={Element.ANY: any_number}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dice.smart_selection(
                        requirement=input_abstract_dice,
                        local_precedence=input_precedence
                    )
                    if element_number >= any_number:
                        expected = ActualDice(dice={element: any_number})
                    else:
                        expected = None

                    self.assertEqual(actual, expected)

    def test_smart_selection_all_any(self):
        """ test one die of every Element can fill ANY in proper order """
        for number_of_any in range(1, len(ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY) + 1):
            with self.subTest(number_of_any=number_of_any):
                input_actual_dice: ActualDice = ActualDice(
                    dice={el: 1 for el in ActualDice._ELEMENTS}
                )
                input_abstract_dice: AbstractDice = AbstractDice(
                    dice={Element.ANY: number_of_any}
                )
                input_precedence: list[set[Element]] = [
                    {el} for el in ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
                ]

                actual: None | ActualDice = input_actual_dice.smart_selection(
                    requirement=input_abstract_dice, local_precedence=input_precedence
                )

                if ActualDice._NUMBER_OF_ELEMENTS >= number_of_any:
                    expected: None | ActualDice = ActualDice(
                        {el: 1 for el in ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY[-number_of_any:]}
                    )
                else:
                    expected = None

                self.assertEqual(actual, expected)

    def test_smart_selection_all_any_plus_one_omni_actual(self):
        """ test one die of every element from a to b, and ANY need: b-a+1 (a<b) """
        elements_and_omni = (Element.OMNI,) + ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
        for a in range(len(elements_and_omni)):
            for b in range(a + 1, len(elements_and_omni)):
                # need = supply, need < supply, need > supply
                for any_need_number in [(b - a + 1), (b - a), (b - a + 2)]:
                    with self.subTest(a=a, b=b, any_need_number=any_need_number):
                        input_actual_dice: ActualDice = ActualDice(
                            dice={el: 1 for el in elements_and_omni[a:b + 1]}
                        )
                        input_abstract_dice: AbstractDice = AbstractDice(
                            dice={Element.ANY: any_need_number}
                        )
                        input_precedence: list[set[Element]] = [
                            {el} for el in ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
                        ]

                        actual: None | ActualDice = input_actual_dice.smart_selection(
                            requirement=input_abstract_dice,
                            local_precedence=input_precedence
                        )

                        if any_need_number == (b - a + 1):  # =
                            expected: None | ActualDice = input_actual_dice
                        elif any_need_number == (b - a):  # need < supply
                            expected = ActualDice(
                                dice={el: 1 for el in elements_and_omni[a + 1:b + 1]})
                        elif any_need_number == (b - a + 2):
                            expected = None
                        else:
                            raise Exception("unexpected any_need_number")
                        self.assertEqual(actual, expected)

    def test_smart_selection_concrete_element(
            self, element: Element = Element.GEO):
        """
        test fill element with itself
        needed=1..10
        supply=1..10
        """

        for needed in range(1, 11):
            for supply in range(1, 11):
                with self.subTest(needed=needed, supply=supply):
                    input_actual_dice: ActualDice = ActualDice(dice={element: supply})
                    input_abstract_dice: AbstractDice = AbstractDice(
                        dice={element: needed}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dice.smart_selection(
                        requirement=input_abstract_dice,
                        local_precedence=input_precedence
                    )

                    if supply >= needed:
                        expected = ActualDice(dice={element: needed})
                    else:
                        expected = None

                    self.assertEqual(actual, expected)

    def test_smart_selection_precedence(self):
        """ basic test on elements local precedence """
        element_geo = Element.GEO
        element_pyro = Element.PYRO
        for any_needed_number in (5, 10, 15):
            for element_geo_number in range(20):
                for element_pyro_number in range(20):
                    for element_first_bigger_precedence in [False, True]:
                        with self.subTest(
                                any_needed_number=any_needed_number,
                                element_geo_number=element_geo_number,
                                element_pyro_number=element_pyro_number,
                                element_first_bigger_precedence=element_first_bigger_precedence
                        ):
                            input_actual_dice: ActualDice = ActualDice(
                                dice={element_geo: element_geo_number,
                                       element_pyro: element_pyro_number}
                            )
                            input_abstract_dice: AbstractDice = AbstractDice(
                                dice={Element.ANY: any_needed_number}
                            )

                            input_precedence: list[set[Element]] = [
                                {element_geo}, {element_pyro}
                            ]

                            if not element_first_bigger_precedence:
                                input_precedence = input_precedence[::-1]

                            actual = input_actual_dice.smart_selection(
                                requirement=input_abstract_dice,
                                local_precedence=input_precedence
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

                                expected = ActualDice(
                                    dice={
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
        """ test empty need with non-empty supply """
        input_actual_dice: ActualDice = ActualDice(
            {el: 1 for el in ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY + (Element.OMNI,)})
        input_abstract_dice: AbstractDice = AbstractDice({})
        input_precedence: list[set[Element]] = []

        actual = input_actual_dice.smart_selection(
            requirement=input_abstract_dice,
            local_precedence=input_precedence
        )
        expected = ActualDice({})
        self.assertEqual(actual, expected)

    def test_smart_selection_empty_supply_empty_need(self):
        """ test empty need with non-empty supply """
        input_actual_dice: ActualDice = ActualDice({})
        input_abstract_dice: AbstractDice = AbstractDice({})
        input_precedence: list[set[Element]] = []

        actual = input_actual_dice.smart_selection(
            requirement=input_abstract_dice,
            local_precedence=input_precedence
        )
        expected = ActualDice({})
        self.assertEqual(actual, expected)

    def test_smart_selection_negative(self):
        """
        negative test
        to code-coverage
        Element and OtherElement and OMNI supply
        Element need
        """
        element = Element.GEO
        other_element = Element.CRYO

        for element_supply_number in range(5):
            for omni_supply_number in range(5):
                element_need_number = element_supply_number + omni_supply_number + 1
                with self.subTest(
                        element=element,
                        element_supply_number=element_supply_number,
                        omni_supply_number=omni_supply_number,
                        element_need_number=element_need_number
                ):
                    input_actual_dice: ActualDice = ActualDice(
                        {element: element_supply_number, Element.OMNI: omni_supply_number, other_element: 2}
                    )
                    input_abstract_dice: AbstractDice = AbstractDice(
                        {element: element_need_number}
                    )
                    input_precedence: list[set[Element]] = []

                    actual = input_actual_dice.smart_selection(
                        requirement=input_abstract_dice,
                        local_precedence=input_precedence
                    )

                    expected = None
                    self.assertEqual(actual, expected)

    def test_smart_selection_code_cover(self):
        """
        Element and OMNI feed OMNI
        code cover
        """
        first_element = Element.GEO  # most precedent element

        for first_element_supply_number in range(5):
            for omni_supply_number in range(5):
                for omni_need_number in [1, 3, 5]:
                    with self.subTest(
                            first_element=first_element,
                            first_element_supply_number=first_element_supply_number,
                            omni_supply_number=omni_supply_number,
                            omni_need_number=omni_need_number
                    ):
                        first_element_supply_number = 3
                        omni_supply_number = 2
                        omni_need_number = 4
                        input_actual_dice: ActualDice = ActualDice({
                            first_element: first_element_supply_number,
                            Element.OMNI: omni_supply_number,
                        })
                        input_abstract_dice: AbstractDice = AbstractDice(
                            {Element.OMNI: omni_need_number}
                        )
                        input_precedence: list[set[Element]] = [{first_element}]

                        actual = input_actual_dice.smart_selection(
                            requirement=input_abstract_dice,
                            local_precedence=input_precedence
                        )

                        if first_element_supply_number + omni_supply_number >= omni_need_number:
                            expected = ActualDice({
                                first_element: first_element_supply_number,
                                Element.OMNI: omni_need_number - first_element_supply_number,
                            })
                        else:
                            expected = None
                        self.assertEqual(actual, expected)

    def test_smart_selection_negative_2(self):
        """
        test for code coverage.
        supply: 2 of every elements
        need: 5 omni
        """
        elements_and_omni = (Element.OMNI,) + ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
        input_actual_dice = ActualDice(
            dice={el: 2 for el in elements_and_omni}
        )
        input_abstract_dice = AbstractDice(
            dice={Element.OMNI: 5}
        )
        input_precedence: list[set[Element]] = [
            {el} for el in ActualDice._ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY
        ]

        actual: None | ActualDice = input_actual_dice.smart_selection(
            requirement=input_abstract_dice, local_precedence=input_precedence
        )

        expected = None
        self.assertEqual(actual, expected)

    def test_lesser_omni_spent_when_two_first_priority_elems_present(self):
        """
        Test if the better less-omni-costing plan is chosen when there are two first priority
        elements present with different numbers.
        """
        for n1, n2 in ((1, 2), (2, 1)):
            with self.subTest(n1=n1, n2=n2):
                requirement = AbstractDice({Element.OMNI: 3})
                dice = ActualDice({Element.OMNI: 2, Element.CRYO: n1, Element.ANEMO: n2})
                selected_dice = dice.smart_selection(
                    requirement,
                    None,
                    local_precedence=[{Element.CRYO, Element.ANEMO}],
                )
                self.assertEqual(selected_dice[Element.OMNI], 1)  # type: ignore

    def test_smart_selection_based_on_player_state(self):
        requirement = AbstractDice({Element.OMNI: 3})
        dice = ActualDice({Element.OMNI: 2, Element.CRYO: 1, Element.ANEMO: 1})
        selected_dice = dice.smart_selection(requirement, Characters((
            Ganyu.from_default(1),
            Kaeya.from_default(2),
            Klee.from_default(3),
        ), active_character_id=2))
        assert selected_dice is not None
        self.assertEqual(selected_dice, ActualDice({Element.OMNI: 2, Element.ANEMO: 1}))

        selected_dice = dice.smart_selection(requirement, Characters((
            Ganyu.from_default(1),
            MaguuKenki.from_default(2),
            Klee.from_default(3),
        ), active_character_id=2))
        assert selected_dice is not None
        self.assertEqual(selected_dice, ActualDice({Element.OMNI: 2, Element.CRYO: 1}))

        dice = ActualDice({Element.OMNI: 2, Element.CRYO: 1, Element.ANEMO: 2})
        selected_dice = dice.smart_selection(requirement, Characters((
            Kaeya.from_default(1),
            Jean.from_default(2),
            Ganyu.from_default(3),
        ), active_character_id=2))
        assert selected_dice is not None
        self.assertEqual(selected_dice, ActualDice({Element.OMNI: 2, Element.CRYO: 1}))

        dice = ActualDice({Element.OMNI: 3})
        selected_dice = dice.smart_selection(requirement, Characters((
            Kaeya.from_default(1),
            Jean.from_default(2),
            Ganyu.from_default(3),
        ), active_character_id=2))
        assert selected_dice is not None
        self.assertEqual(selected_dice, ActualDice({Element.OMNI: 3}))
