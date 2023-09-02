from __future__ import annotations

import random
from _operator import itemgetter
from collections import Counter, defaultdict
from functools import cache, lru_cache
from heapq import heappop, heapify
from typing import Any, Iterable, Iterator, Optional
from typing_extensions import override, Self, TYPE_CHECKING

from .element import Element
from .helper.hashable_dict import HashableDict
from .helper.quality_of_life import BIG_INT, case_val

if TYPE_CHECKING:
    from .state.game_state import GameState
    from .state.player_state import PlayerState

__all__ = [
    "AbstractDices",
    "ActualDices",
    "Dices",
]


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

    def is_empty(self) -> bool:
        return not any(val > 0 for val in self._dices.values())

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
        picked_dices: dict[Element, int] = HashableDict(Counter(
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
        return self._dices.to_dict()

    def dict_str(self) -> dict[str, Any]:
        existing_dices = dict([
            (dice.name, str(num))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return existing_dices

    def __copy__(self) -> Self:  # pragma: no cover
        return self

    def __deepcopy__(self, _) -> Self:  # pragma: no cover
        return self

    @classmethod
    def from_empty(cls) -> Self:
        return cls(HashableDict((
            (elem, 0)
            for elem in cls._LEGAL_ELEMS
        )))


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

    # tested against the actual game in Genshin
    _LEGAL_ELEMS_ORDERED: tuple[Element, ...] = (
        Element.OMNI,
        Element.CRYO,
        Element.HYDRO,
        Element.PYRO,
        Element.ELECTRO,
        Element.GEO,
        Element.DENDRO,
        Element.ANEMO,
    )
    # the bigger the i, the higher the priority
    _LEGAL_ELEMS_ORDERED_DICT: dict[Element, int] = {
        elem: i
        for i, elem in enumerate(reversed(_LEGAL_ELEMS_ORDERED))
    }
    _LEGAL_ELEMS_ORDERED_DICT_REV: dict[int, Element] = {
        i: elem
        for elem, i in _LEGAL_ELEMS_ORDERED_DICT.items()
    }

    # probably correct priorities
    _ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY: tuple[Element, ...] = _LEGAL_ELEMS_ORDERED[:0:-1]

    _ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY: tuple[Element, ...] = \
        _ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY + (Element.OMNI,)

    # Dict[element, global_priority]
    _ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY_DCT: dict[Element, int] = {
        elem: i
        for i, elem in enumerate(_ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY)
    }

    _ELEMENTS_AND_OMNI = _ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY

    _ELEMENTS = _ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY

    _NUMBER_OF_ELEMENTS: int = len(_ELEMENTS_BY_DECREASING_GLOBAL_PRIORITY)

    def _satisfy(self, requirement: AbstractDices) -> bool:
        assert self.is_legal() and requirement.is_legal()

        # satisfy all pure elements first
        pure_deducted: HashableDict[Element, int] = HashableDict((
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
    def _omni_filler_priority(*,
                              omni_supply: int,
                              omni_needed: int,
                              element_supply: int,
                              element_needed: int,
                              element_prioritized: bool
                              ) -> tuple[int, int]:
        """
        return
        Tuple[
            how many OMNI (+ first priority elements if it so) spend if we select this ELEMENT as OMNI filler,
            how many OMNI spent
        ]

        return BIG_INT if no possibility
        """
        if element_supply + omni_supply >= element_needed + omni_needed:
            if element_prioritized:
                return element_needed + omni_needed, element_needed + omni_needed - element_supply
            else:
                omni = max((element_needed + omni_needed) - element_supply, 0)
                return omni, omni  # don't spend element_needed, so engaged 0 elements of element_supply
        else:
            # return None
            return BIG_INT, BIG_INT

    def smart_selection(
            self,
            requirement: AbstractDices,
            game_state: Optional[GameState] = None,
            local_precedence_arg: Optional[list[set[Element]]] = None,
    ) -> Optional[ActualDices]:
        """ trying to fill requirement with self._dices """

        # result in dict format
        result_dct: dict[Element, int] = defaultdict(int)

        # optimisation check - if required dices > avaiable dices, break
        if requirement.num_dices() > self.num_dices():
            return None

        supply: dict[Element, int] = defaultdict(int)
        supply.update(self._dices)

        need: dict[Element, int] = defaultdict(int)
        need.update(requirement._dices)

        local_precedence: list[set[Element]] = \
            [] if local_precedence_arg is None else local_precedence_arg
        local_precedence_reversed: list[set[Element]] = local_precedence[::-1]
        assert local_precedence is not None
        assert local_precedence_reversed is not None
        assert len(local_precedence) <= self._NUMBER_OF_ELEMENTS + 2

        # list of first priority elements
        first_priority_elements: set[Element] = (set() if local_precedence == [] else local_precedence[0])

        @cache
        def get_local_priority(element: Element) -> tuple[int, int]:
            """ get priority by element, lower tuple is bigger priority and should be spent first """
            nonlocal local_precedence
            if element == Element.OMNI:
                return self._NUMBER_OF_ELEMENTS + 2, -1  # OMNI has biggest tuple
            for i, elem_set in enumerate(local_precedence, start=1):
                if element in elem_set:
                    return (self._NUMBER_OF_ELEMENTS + 1 - i,
                            self._ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY_DCT[element]
                    )
            else:
                return -1, self._ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY_DCT[element]

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
            def comparision_of_omni_priorities(x: tuple[Element, tuple[int, int]]) -> tuple[int, int, int, int]:
                """ to sort by ascedence of least_spend omni+1st priority, then omni"""
                type_of_element: Element = x[0]

                order = x[1]
                number_of_regular_dices: int = order[0]
                number_of_omni: int = order[1]
                priority_local, priority_global = get_local_priority(
                    type_of_element
                )  # lower - should be spent first
                # return number_of_dices if number_of_dices is not None else
                # -1, type_of_element
                return number_of_regular_dices, priority_local, number_of_omni, priority_global

            # find the elements to fill the OMNI requirement that costs
            # the least (first_priority_elements number + OMNI elements number)
            elem_cost_mapping: list[tuple[Element, Optional[tuple[int, int]]]] = [
                (
                    element,
                    self._omni_filler_priority(
                        element_supply=supply[element],
                        element_needed=need[element],
                        omni_needed=need[Element.OMNI],
                        element_prioritized=element in first_priority_elements,
                        omni_supply=supply[Element.OMNI]
                    )
                )
                for element in _PURE_ELEMS
                if supply[element] + supply[Element.OMNI] >= need[element] + need[Element.OMNI]
            ]

            if not elem_cost_mapping:
                # Cant fill OMNI requirement
                return None

            # at first - find min priority
            least_spend = min(
                elem_cost_mapping,
                key=comparision_of_omni_priorities
            )[1]  # type: ignore

            # at second - find all with this priority
            best_omni_fillers: list[Element] = [
                elem
                for elem, omni_to_spent in elem_cost_mapping
                if omni_to_spent == least_spend
            ]

            assert best_omni_fillers, "Unknown error"

            # get list of least-omni-spending candidates
            filler_element: Element = min([
                (get_local_priority(elem), elem)
                for elem in best_omni_fillers
            ])[1]

            # filler_element: Element = min_precedence_omni_potential_fillers[0]  # incorrect

            filler_element_count = min(need[Element.OMNI], supply[filler_element])
            filler_omni_count = need[Element.OMNI] - filler_element_count

            result_dct[filler_element] += filler_element_count
            result_dct[Element.OMNI] += filler_omni_count

            need[Element.OMNI] -= filler_element_count + filler_omni_count
            supply[filler_element] -= filler_element_count
            supply[Element.OMNI] -= filler_omni_count

            assert need[Element.OMNI] == 0, "need element omni not 0"
            assert supply[filler_element] >= 0, "supply <0"
            assert supply[Element.OMNI] >= 0, "supply <0"

        # 2nd step - fill the pure Elements
        # with pure Elements and OMNI

        for el in self._ELEMENTS:
            # 2.1 fill element with itself
            number_of_el = min(need[el], supply[el])

            result_dct[el] += number_of_el
            need[el] -= number_of_el
            supply[el] -= number_of_el

            check_asserts()

            # 2.2 fill Element with OMNI if needed
            if need[el] > supply[Element.OMNI]:
                return None

            number_of_omni = need[el]

            result_dct[Element.OMNI] += number_of_omni
            need[el] -= number_of_omni
            supply[Element.OMNI] -= number_of_omni

            check_asserts()

        # 3rd step - fill ANY with all avaiable elements

        elements_by_precedence: list[tuple[tuple[int, int], Element]] = [
            (get_local_priority(element), element) for element in self._ELEMENTS_AND_OMNI
        ]
        heapify(elements_by_precedence)

        while need[Element.ANY] > 0 and elements_by_precedence:
            precedence, elem = heappop(elements_by_precedence)

            number_of_spent_element = min(need[Element.ANY], supply[elem])

            result_dct[elem] += number_of_spent_element
            need[Element.ANY] -= number_of_spent_element
            supply[elem] -= number_of_spent_element

            check_asserts()

        if need[Element.ANY] > 0:
            raise Exception("Should not be reached!")
            # now it's dead code, but remained for the sake of stability for future changes

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
            for elem in list(_PURE_ELEMS):
                this_count = remaining.get(elem, 0)
                if best_count > omni and this_count >= omni and this_count < best_count:
                    best_elem = elem
                    best_count = this_count
                elif best_count < omni and this_count > best_count:
                    best_elem = elem
                    best_count = this_count
                elif best_count == omni:
                    break
            if best_elem is not None:
                best_count = min(best_count, omni)
                answer[best_elem] += best_count
                remaining[best_elem] -= best_count
                omni_required += omni - best_count
            else:
                omni_required += omni
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

    def _init_ordered_dices(
            self,
            priority_elems: None | frozenset[Element]
    ) -> HashableDict[Element, int]:
        character_elems: frozenset[Element]
        if priority_elems is None:
            character_elems = frozenset()
        else:
            character_elems = priority_elems

        dices: dict[Element, int] = {}
        if self[Element.OMNI] > 0:
            dices[Element.OMNI] = self[Element.OMNI]
        # list[tuple[alive chars have elem, num of elem, priority of elem]]
        sorted_categories: list[tuple[int, int, int]] = sorted(
            (
                (
                    case_val(elem in character_elems, 1, 0),
                    self[elem],
                    self._LEGAL_ELEMS_ORDERED_DICT[elem],
                )
                for elem in self.elems()
                if elem is not Element.OMNI and self[elem] > 0
            ),
            reverse=True
        )
        for _, _, priority in sorted_categories:
            elem = self._LEGAL_ELEMS_ORDERED_DICT_REV[priority]
            dices[elem] = self[elem]
        return HashableDict.from_dict(dices)

    def dices_ordered(self, player_state: None | PlayerState) -> dict[Element, int]:
        return self.readonly_dices_ordered(player_state).to_dict()

    def readonly_dices_ordered(self, player_state: None | PlayerState) -> HashableDict[Element, int]:
        return self._init_ordered_dices(
            None
            if player_state is None
            else frozenset(
                char.element()
                for char in player_state.get_characters().get_alive_characters()
            )
        )

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
