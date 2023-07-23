from __future__ import annotations
import random
from collections import Counter
from typing import Any, Optional, Iterator, Iterable, TypeVar, Union
from typing_extensions import Self, override, TYPE_CHECKING

from .helper.hashable_dict import HashableDict
from .helper.quality_of_life import BIG_INT
from .element import Element
from collections import defaultdict
from typing import Optional, Iterator, Iterable, Union

if TYPE_CHECKING:
    from .state.game_state import GameState

__all__ = [
    "AbstractDices",
    "ActualDices",
    "Dices",
]
from typing_extensions import Self

from dgisim.src.element.element import Element
from dgisim.src.helper.hashable_dict import HashableDict
from dgisim.src.helper.level_print import level_print
from dgisim.src.helper.quality_of_life import BIG_INT

ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY: list[Element] = [Element.PYRO,
                                                         Element.HYDRO,
                                                         Element.ANEMO,
                                                         Element.ELECTRO,
                                                         Element.DENDRO,
                                                         Element.CRYO,
                                                         Element.GEO, ]


class Dices:
    """
    Base class for dices
    """
    _LEGAL_ELEMS = frozenset(elem for elem in Element)

    def __init__(self, dices: dict[Element, int]) -> None:
        self._dices = HashableDict.from_dict(dices)

    def __add__(self, other: Dices | dict[Element, int]) -> Self:
        dices: dict[Element, int]
        if isinstance(other, Dices):
            dices = other._dices
        else:
            dices = other
        return type(self)(self._dices + dices)

    def __sub__(self, other: Dices | dict[Element, int]) -> Self:
        dices: dict[Element, int]
        if isinstance(other, Dices):
            dices = other._dices
        else:
            dices = other
        return type(self)(self._dices - dices)

    def num_dices(self) -> int:
        return sum(self._dices.values())

    def is_even(self) -> bool:
        return self.num_dices() % 2 == 0

    def is_legal(self) -> bool:
        return all(map(lambda x: x >= 0, self._dices.values())) \
            and all(elem in self._LEGAL_ELEMS for elem in self._dices)

    def validify(self) -> Self:
        if self.is_legal():
            return self
        return type(self)(dict(
            (elem, n)
            for elem, n in self._dices.items()
            if elem in self._LEGAL_ELEMS and n > 0
        ))

    def elems(self) -> Iterable[Element]:
        return self._dices.keys()

    def pick_random_dices(self, num: int) -> tuple[Self, Self]:
        """
        Returns the left dices and selected dices
        """
        num = min(self.num_dices(), num)
        if num == 0:
            return (self, type(self).from_empty())
        picked_dices: dict[Element, int] = dict(Counter(
            random.sample(list(self._dices.keys()), counts=self._dices.values(), k=num)
        ))
        return type(self)(self._dices - picked_dices), type(self)(picked_dices)

    def __contains__(self, elem: Element) -> bool:
        return (
            elem in self._LEGAL_ELEMS
            and self[elem] > 0
        )

    def __iter__(self) -> Iterator[Element]:
        return (
            elem
            for elem in self._dices
            if self[elem] > 0
        )

    def __getitem__(self, index: Element) -> int:
        return self._dices.get(index, 0)

    def _normalized_dices(self):
        return {key: value for key, value in self._dices.items() if value != 0}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dices):
            return False
        return self is other or self._dices == other._dices

    def __hash__(self) -> int:
        return hash(self._dices)

    def __repr__(self) -> str:
        existing_dices = dict([
            (dice.name, str(num))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return (
            '{'
            + ", ".join(
                f"{key}: {val}"
                for key, val in existing_dices.items()
            )
            + '}'
        )

    def to_dict(self) -> dict[Element, int]:
        return dict(self._dices.items())

    def dict_str(self) -> dict[str, Any]:
        existing_dices = dict([
            (dice.name, str(num))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return existing_dices

    @classmethod
    def from_empty(cls) -> Self:
        return cls(dict([
            (elem, 0)
            for elem in cls._LEGAL_ELEMS
        ]))


_PURE_ELEMS = frozenset({
    Element.PYRO,
    Element.HYDRO,
    Element.ANEMO,
    Element.ELECTRO,
    Element.DENDRO,
    Element.CRYO,
    Element.GEO,
})


class ActualDices(Dices):
    """
    Used for the actual dices a player can have.
    """
    _LEGAL_ELEMS = frozenset({
        Element.OMNI,
        Element.PYRO,
        Element.HYDRO,
        Element.ANEMO,
        Element.ELECTRO,
        Element.DENDRO,
        Element.CRYO,
        Element.GEO,
    })

    def _satisfy(self, requirement: AbstractDices) -> bool:
        assert self.is_legal() and requirement.is_legal()

        # satisfy all pure elements first
        pure_deducted = HashableDict((
            (elem, self[elem] - requirement[elem])
            for elem in _PURE_ELEMS
        ), frozen=False)
        omni_needed = sum(
            -num
            for num in pure_deducted.values()
            if num < 0
        )

        # if OMNI given cannot cover pure misses, fail
        if self[Element.OMNI] < omni_needed:
            return False

        # test OMNI requirement
        omni_remained = self[Element.OMNI] - omni_needed
        most_pure = max(pure_deducted.values())
        if omni_remained + most_pure < requirement[Element.OMNI]:
            return False

        # We have enough dices to satisfy Element.ANY, so success
        return True

    def loosely_satisfy(self, requirement: AbstractDices) -> bool:
        """
        Asserts self and requirement are legal, and then check if self can match
        requirement.
        """
        if self.num_dices() < requirement.num_dices():
            return False
        return self._satisfy(requirement)

    def just_satisfy(self, requirement: AbstractDices) -> bool:
        """
        Asserts self and requirement are legal, and then check if self can match
        requirement.

        self must have the same number of dices as requirement asked for.
        """
        if self.num_dices() != requirement.num_dices():
            return False
        return self._satisfy(requirement)

    @staticmethod
    def _how_much_omni_and_first_priority_spends(*,
                                                 element_supply: int,
                                                 omni_supply: int,
                                                 omni_need: int, element_need: int,
                                                 element_priority: bool) -> int:
        """
        how many OMNI (+ first priority elements if it so) spend if we select this ELEMENT as OMNI filler.
        return BIG_INT if no possibility
        """
        # TODO сделать возврат сколько и чего
        if element_supply + omni_supply > element_need + omni_need:
            if element_priority:
                return element_need + omni_need
            else:
                return max((element_need + omni_need) - element_supply, 0)
        else:
            # return None
            return BIG_INT

    def smart_selection(
            self,
            requirement: AbstractDices,
            game_state: Optional[gs.GameState] = None,
            local_precedence: Optional[list[set[Element]]] = None,
    ) -> Optional[ActualDices]:
        result_dct: dict[Element, int] = defaultdict(
            int)  # result in dict format

        supply: dict[Element, int] = defaultdict(int)
        supply.update(dict(self._dices))

        need: dict[Element, int] = defaultdict(int)
        need.update(dict(requirement._dices))

        local_precedence = local_precedence if local_precedence is not None else []
        first_priority_elements = ([] if local_precedence in [None, []]
                                   else local_precedence[0])  # list of first priority elements

        def get_precedence(element: Element) -> tuple[int, int]:
            nonlocal local_precedence
            """get precedence by element, bigger number is lower precedence"""
            for i, set_ in enumerate(local_precedence, start=1):
                if element in set_:
                    return i, ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY[::-1].index(
                        element)
            else:
                return BIG_INT, 0

        def check_asserts():
            """
            assert non-negativity of variables:
            need supply result_dct
            """

            def check_dict(name: str, dct: dict):
                for el, val in dct.items():
                    assert val >= 0, f"{el} in {name} < 0 {val=}"

            nonlocal result_dct, supply, need

            check_dict("result_dct", result_dct)
            check_dict("supply", supply)
            check_dict("need", need)

        # 1 step - fill OMNI requirement
        if requirement[Element.OMNI] > 0:
            def comparision(x: tuple[Element, int]) -> tuple[int, int, int]:
                """to sort by ascedence of least_spend"""
                type_of_element: Element = x[0]
                number_of_dices: Optional[int] = x[1]
                priority_local, priority_global = (
                    get_precedence(type_of_element))
                # return number_of_dices if number_of_dices is not None else
                # -1, type_of_element
                return number_of_dices, priority_local, priority_global

            array: list[tuple[Element, Optional[int]]] = \
                [(element,
                  self._how_much_omni_and_first_priority_spends(
                      element_supply=supply[element],
                      element_need=need[element],
                      omni_need=need[Element.OMNI],
                      element_priority=element in first_priority_elements,
                      omni_supply=supply[Element.OMNI])
                  )
                 for element in _PURE_ELEMS]

            # TODO rewrite minimum get
            array = list(sorted(array, key=comparision))

            least_spend = array[0][1]
            least_spend_omni_elements = []
            if least_spend != BIG_INT:
                for el in array:
                    if el[1] == least_spend:
                        least_spend_omni_elements.append(el[0])
            else:
                raise Exception("Cant feed OMNI requirement")

            assert least_spend_omni_elements, "Unknown error"

            precedence_of_least_spend_omni = {element: get_precedence(element)
                                              for element
                                              in least_spend_omni_elements}

            max_precedence_omni_potential_fillers: list[Element] = []
            max_precedence = max(precedence_of_least_spend_omni.values())
            for key, val in precedence_of_least_spend_omni.items():
                if val == max_precedence:
                    max_precedence_omni_potential_fillers.append(key)

            # TODO: выбор наилучшего заполнителя OMNI - now just first
            filler_element: Element = max_precedence_omni_potential_fillers[0]

            # how many omni and how many filler (we already know Element which
            # is filler)
            if supply[filler_element] >= need[Element.OMNI]:
                filler_element_count = need[Element.OMNI]
                filler_omni_count = 0
            else:
                filler_element_count = supply[filler_element]
                filler_omni_count = need[Element.OMNI] - filler_element_count

            result_dct[filler_element] += filler_element_count
            result_dct[Element.OMNI] += filler_omni_count

            need[Element.OMNI] -= filler_element_count + filler_omni_count
            supply[filler_element] -= filler_element_count
            supply[Element.OMNI] -= filler_omni_count

            assert need[Element.OMNI] == 0, "need element omni not 0"
            assert supply[filler_element] >= 0, "supply <0"
            assert supply[Element.OMNI] >= 0, "supply <0"

        # 2 step - fill the Elements needs and ANY (files ANY parallely)

        global ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY

        reverse_order_need_list: list[Element] = list(
            sorted(ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY,
                   key=lambda el: get_precedence(el)
                   ))[::-1]  # + [Element.ANY]

        for el in reverse_order_need_list:
            if need[el] <= supply[el]:  # if element can fill itself
                number_of_el = need[el]
                # print(number_of_el)

                result_dct[el] += number_of_el
                need[el] -= number_of_el
                supply[el] -= number_of_el
                check_asserts()

                if supply[el] > 0 and need[Element.ANY] > 0:
                    number_of_el = min(supply[el], need[Element.ANY])
                    print(number_of_el)

                    result_dct[el] += number_of_el
                    need[Element.ANY] -= number_of_el
                    supply[el] -= number_of_el
                    check_asserts()
            else:  # if OMNI dices needs
                number_of_el = supply[el]

                result_dct[el] += number_of_el
                need[el] -= number_of_el
                supply[el] -= number_of_el

                check_asserts()

                if need[el] <= supply[Element.OMNI]:
                    number_of_omni = need[el]

                    result_dct[Element.OMNI] += number_of_omni
                    need[el] -= number_of_omni
                    supply[Element.OMNI] -= number_of_omni

                    check_asserts()
                else:
                    return None

        # 3 process ANY need with OMNI

        if need[Element.ANY] > 0:
            if supply[Element.OMNI] >= need[Element.ANY]:
                number_of_spent_omni = need[Element.ANY]

                result_dct[Element.OMNI] += number_of_spent_omni
                need[Element.ANY] -= number_of_spent_omni
                supply[Element.OMNI] -= number_of_spent_omni

                check_asserts()
            else:
                return None

        assert set(need.values()) == {0}
        return ActualDices(dices=result_dct)

    def basically_satisfy(
            self,
            requirement: AbstractDices,
            game_state: Optional[GameState] = None,
    ) -> Optional[ActualDices]:
        if requirement.num_dices() > self.num_dices():
            return None
        # TODO: optimize for having game_state
        from collections import defaultdict
        remaining: dict[Element, int] = self._dices.copy()
        answer: dict[Element, int] = defaultdict(int)
        pures: dict[Element, int] = HashableDict(frozen=False)
        omni = 0
        any = 0
        omni_required = 0
        for elem in requirement:
            if elem in _PURE_ELEMS:
                pures[elem] = requirement[elem]
            elif elem is Element.OMNI:
                omni = requirement[elem]
            elif elem is Element.ANY:
                any = requirement[elem]
            else:  # pragma: no cover
                raise Exception("Unknown element")
        if len(pures) > 0:
            for elem in pures:
                if remaining.get(elem, 0) < pures[elem]:
                    answer[elem] += remaining.get(elem, 0)
                    omni_required += pures[elem] - remaining.get(elem, 0)
                    remaining[elem] = 0
                else:
                    answer[elem] += pures[elem]
                    remaining[elem] -= pures[elem]
        if omni > 0:
            best_elem: Optional[Element] = None
            best_count = 0
            for elem in list(_PURE_ELEMS) + [Element.OMNI]:
                this_count = remaining.get(elem, 0)
                if best_count > omni and this_count >= omni and this_count < best_count:
                        best_elem = elem
                        best_count = this_count
                elif best_count < omni and this_count > best_count:
                    best_elem = elem
                    best_count = this_count
                elif best_count == omni:
                    break
            assert best_elem is not None
            best_count = min(best_count, omni)
            answer[best_elem] += best_count
            remaining[best_elem] -= best_count
            omni_required += omni - best_count
        if any > 0:
            from operator import itemgetter
            sorted_elems = sorted(remaining.items(), key=itemgetter(1))
            for elem, num in sorted_elems:
                if elem in _PURE_ELEMS:
                    num = min(num, any)
                    answer[elem] += num
                    remaining[elem] -= num
                    any -= num
                    if any == 0:
                        break
            if any > 0:
                answer[Element.OMNI] += any
                remaining[Element.OMNI] -= any
        if omni_required > 0:
            if remaining.get(Element.OMNI, 0) < omni_required:
                return None
            answer[Element.OMNI] += omni_required
        return ActualDices(answer)

    @classmethod
    def from_random(cls, size: int) -> ActualDices:
        dices = ActualDices.from_empty()
        dices._dices._unfreeze()
        for i in range(size):
            elem = random.choice(tuple(ActualDices._LEGAL_ELEMS))
            dices._dices[elem] += 1
        dices._dices.freeze()
        return dices

    @classmethod
    def from_all(cls, size: int, elem: Element) -> ActualDices:
        dices = ActualDices.from_empty()
        dices._dices._unfreeze()
        dices._dices[Element.OMNI] = size
        dices._dices.freeze()
        return dices

    @classmethod
    def from_dices(cls, dices: Dices) -> Optional[ActualDices]:
        new_dices = ActualDices(dices._dices)
        if not new_dices.is_legal():
            return None
        else:
            return new_dices


class AbstractDices(Dices):
    """
    Used for the dice cost of cards and other actions
    """
    _LEGAL_ELEMS = frozenset({
        Element.OMNI,  # represents the request for dices of the same type
        Element.PYRO,
        Element.HYDRO,
        Element.ANEMO,
        Element.ELECTRO,
        Element.DENDRO,
        Element.CRYO,
        Element.GEO,
        Element.ANY,
    })

    @classmethod
    def from_dices(cls, dices: Dices) -> Optional[AbstractDices]:
        new_dices = AbstractDices(dices._dices)
        if not new_dices.is_legal():
            return None
        else:
            return new_dices
