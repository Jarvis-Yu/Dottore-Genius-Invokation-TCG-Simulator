from __future__ import annotations

import random
from collections import Counter
from collections import defaultdict
from functools import cache
from heapq import heappop, heapify
from typing import Any
from typing import Optional, Iterator, Iterable

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from .state.game_state import GameState

__all__ = [
    "AbstractDices",
    "ActualDices",
    "Dices",
]

from typing_extensions import Self

from dgisim.src.element import Element
from dgisim.src.helper.hashable_dict import HashableDict
from dgisim.src.helper.quality_of_life import BIG_INT

# higher PRIORITY - should be spent first
ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY: tuple[Element, ...] = (
    Element.PYRO,
    Element.HYDRO,
    Element.ANEMO,
    Element.ELECTRO,
    Element.DENDRO,
    Element.CRYO,
    Element.GEO,
)

ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY: tuple[Element, ...] = tuple(
    list(ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY) + [Element.OMNI]
)

ELEMENTS_AND_OMNI = ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY

ELEMENTS = ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY

NUMBER_OF_ELEMENTS: int = len(ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY)

ELEMENTS_BY_INCREASING_GLOBAL_PRIORITY: tuple[Element, ...] \
    = ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY[::-1]

ELEMENTS_AND_OMNI_BY_INCREASING_GLOBAL_PRIORITY = \
    ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY[::-1]


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
        picked_dices: dict[Element, int] = dict(Counter(random.sample(
            list(self._dices.keys()), counts=self._dices.values(), k=num)))
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

    #
    # def _normalized_dices(self):
    # return {key: value for key, value in self._dices.items() if value != 0}

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
    def _how_much_omni_and_first_priority_to_spend(*,
                                                   omni_supply: int,
                                                   omni_needed: int,
                                                   element_supply: int,
                                                   element_needed: int,
                                                   element_prioritized: bool
                                                   ) -> int:
        """
        how many OMNI (+ first priority elements if it so) spend if we select this ELEMENT as OMNI filler.
        return BIG_INT if no possibility
        """
        if element_supply + omni_supply >= element_needed + omni_needed:
            if element_prioritized:
                return element_needed + omni_needed
            else:
                return max((element_needed + omni_needed) - element_supply, 0)
        else:
            # return None
            return BIG_INT

    def smart_selection(
            self,
            requirement: AbstractDices,
            game_state: Optional[GameState] = None,
            local_precedence_arg: Optional[list[set[Element]]] = None,
    ) -> Optional[ActualDices]:
        # result in dict format
        result_dct: dict[Element, int] = defaultdict(int)

        # optimisation check - if required dices > avaiable dices, break
        if sum(requirement._dices.values()) > sum(self._dices.values()):
            return None

        supply: dict[Element, int] = defaultdict(int)
        supply.update(dict(self._dices))

        need: dict[Element, int] = defaultdict(int)
        need.update(dict(requirement._dices))

        local_precedence: list[set[Element]] = \
            [] if local_precedence_arg is None else local_precedence_arg
        local_precedence_reversed: list[set[Element]] = local_precedence[::-1]
        assert local_precedence is not None
        assert local_precedence_reversed is not None
        assert len(local_precedence) <= NUMBER_OF_ELEMENTS + 2

        # list of first priority elements
        first_priority_elements = ([] if local_precedence == [] else local_precedence[0])

        @cache
        def get_local_priority(element: Element) -> tuple[int, int]:
            nonlocal local_precedence
            """get priority by element, lower tuple is bigger priority and should be spent first"""
            if element == Element.OMNI:
                return NUMBER_OF_ELEMENTS + 2, -1  # OMNI has biggest tuple
            for i, set_ in enumerate(local_precedence, start=1):
                if element in set_:
                    return NUMBER_OF_ELEMENTS + 1 - i, ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY.index(  # to check it
                        element)
            else:
                return -1, ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY.index(
                    element)  # to check it

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

        # 1st step - fill OMNI requirement
        if requirement[Element.OMNI] > 0:
            @cache
            def comparision(x: tuple[Element, int]) -> tuple[int, int, int]:
                """to sort by ascedence of least_spend"""
                type_of_element: Element = x[0]
                number_of_dices: int = x[1]
                priority_local, priority_global = get_local_priority(
                    type_of_element
                )  # lower - should be spent first
                # return number_of_dices if number_of_dices is not None else
                # -1, type_of_element
                return number_of_dices, priority_local, priority_global

            elements_how_many_omni_to_spent_if_fill_omni: list[tuple[Element, Optional[int]]] = \
                [
                    (element,
                  self._how_much_omni_and_first_priority_to_spend(
                      element_supply=supply[element],
                      element_needed=need[element],
                      omni_needed=need[Element.OMNI],
                      element_prioritized=element in first_priority_elements,
                      omni_supply=supply[Element.OMNI])
                  )
                 for element in _PURE_ELEMS
                ]

            least_spend = min(
                elements_how_many_omni_to_spent_if_fill_omni,
                key=comparision
            )[1]  # type: ignore
            least_spend_omni_elements: list[Element] = []
            if least_spend != BIG_INT:
                for elmnt, omni_to_spent in elements_how_many_omni_to_spent_if_fill_omni:
                    if omni_to_spent == least_spend:
                        least_spend_omni_elements.append(elmnt)
            else:
                # Cant feed OMNI requirement
                return None

            assert least_spend_omni_elements, "Unknown error"

            precedence_of_least_spend_omni: list[tuple[Element, tuple[int, int]]] = [
                (element, get_local_priority(element))
                for element
                in least_spend_omni_elements
            ]

            # get list of least-omni-spending candidates
            min_precedence_omni_potential_fillers: list[Element] = []
            min_precedence: tuple[int, int] = min(
                precedence_of_least_spend_omni, key=lambda x: x[1]
            )[1]
            for elmnt, precedence in precedence_of_least_spend_omni:
                if precedence == min_precedence:
                    min_precedence_omni_potential_fillers.append(elmnt)

            # exTODO: selection of best filler for OMNI - now just first
            filler_element: Element = min(
                min_precedence_omni_potential_fillers,
                key=get_local_priority
            )
            # filler_element: Element = min_precedence_omni_potential_fillers[0]  # incorrect

            # how many omni and how many filler (we already know Element which
            # is filler_element)
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

        # 2nd step - fill the Elements except ANY and OMNI needs with Elements
        # and OMNI

        global ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY

        for el in ELEMENTS:
            # 2.1 fill element with itself
            number_of_el = min(need[el], supply[el])

            result_dct[el] += number_of_el
            need[el] -= number_of_el
            supply[el] -= number_of_el

            check_asserts()

            # 2.2 fill Element with OMNI if needed
            if need[el] <= supply[Element.OMNI]:
                number_of_omni = need[el]

                result_dct[Element.OMNI] += number_of_omni
                need[el] -= number_of_omni
                supply[Element.OMNI] -= number_of_omni

                check_asserts()
            else:
                return None

        # 3nd step - fill ANY with all avaiable elements

        # def neg_tuple(tpl: tuple[int, int]):
        #     return -tpl[0], -tpl[1]

        elements_by_precedence: list[tuple[tuple[int, int], Element]] = [
            (get_local_priority(element), element) for element in ELEMENTS_AND_OMNI
        ]
        heapify(elements_by_precedence)

        while need[Element.ANY] > 0 and elements_by_precedence:
            precedence, elmnt = heappop(elements_by_precedence)

            number_of_spent_element = min(need[Element.ANY], supply[elmnt])

            result_dct[elmnt] += number_of_spent_element
            need[Element.ANY] -= number_of_spent_element
            supply[elmnt] -= number_of_spent_element

            check_asserts()

        if need[Element.ANY] > 0:
            return None  # now it's dead code, but remained for the sake of stability for future changes

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


