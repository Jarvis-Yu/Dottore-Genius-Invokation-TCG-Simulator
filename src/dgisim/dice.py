from __future__ import annotations

import random
from collections import Counter, defaultdict
from functools import cache
from heapq import heappop, heapify
from typing import Any, Iterator, Iterable
from typing_extensions import override, Self, TYPE_CHECKING

from .element import Element
from .helper.hashable_dict import HashableDict
from .helper.quality_of_life import BIG_INT, case_val

if TYPE_CHECKING:
    from .character.characters import Characters
    from .encoding.encoding_plan import EncodingPlan
    from .state.game_state import GameState
    from .state.player_state import PlayerState

__all__ = [
    "AbstractDice",
    "ActualDice",
    "Dice",
]


class Dice:
    """
    Base class for dice
    """
    _LEGAL_ELEMS = frozenset(elem for elem in Element)

    def __init__(self, dice: dict[Element, int]) -> None:
        """
        :param dice: the initial dice of this object.

        Once `dice` is passed in, it'll be stored in an internal frozen dictionary,
        ensuring immutability.

        For performance, you may want to directly pass in a HashableDict object
        instead of an ordinary dict.
        """
        self._dice = HashableDict.from_dict(dice)

    def __add__(self, other: Dice | dict[Element, int]) -> Self:
        dice: dict[Element, int]
        if isinstance(other, Dice):
            dice = other._dice
        else:
            dice = other
        return type(self)(self._dice + dice)

    def __sub__(self, other: Dice | dict[Element, int]) -> Self:
        dice: dict[Element, int]
        if isinstance(other, Dice):
            dice = other._dice
        else:
            dice = other
        return type(self)(self._dice - dice)

    def num_dice(self) -> int:
        """
        :returns: total number of dice.

        Time complexity = O(k), k is kinds of dice held by this object.
        """
        return sum(self._dice.values())

    def is_even(self) -> bool:
        """
        :returns: if total number of dice is even.

        Time complexity = O(k), k is kinds of dice held by this object.
        """
        return self.num_dice() % 2 == 0

    def is_empty(self) -> bool:
        """
        :returns: if total number of dice is even.

        Worst time complexity = O(k), k is kinds of dice held by this object.
        """
        return not any(val > 0 for val in self._dice.values())

    def is_legal(self) -> bool:
        """
        :returns: `True` if number of each kind of die is non-negative and all
                  are one of the legal elements of this class.

        Worst time complexity = O(k), k is kinds of dice held by this object.
        """
        return all(map(lambda x: x >= 0, self._dice.values())) \
            and all(elem in self._LEGAL_ELEMS for elem in self._dice)

    def validify(self) -> Self:
        """
        :returns: validified version of this object. All dice of illegal elements
                  are removed. All kinds of dice with non-positive number are removed.
        """
        if self.is_legal():
            return self
        return type(self)(dict(
            (elem, n)
            for elem, n in self._dice.items()
            if elem in self._LEGAL_ELEMS and n > 0
        ))

    def elems(self) -> Iterable[Element]:
        """
        :returns: all elements that have a number.
        """
        return self._dice.keys()

    def pick_random_dice(self, num: int) -> tuple[Self, Self]:
        """
        :param num: the number of random dice to pick.

        :returns: a tuple of left dice and picked dice.
        """
        num = min(self.num_dice(), num)
        if num == 0:
            return (self, type(self).from_empty())
        picked_dice: dict[Element, int] = HashableDict(Counter(
            random.sample(list(self._dice.keys()), counts=self._dice.values(), k=num)
        ))
        return type(self)(self._dice - picked_dice), type(self)(picked_dice)

    def __contains__(self, elem: Element) -> bool:
        return (
            elem in self._LEGAL_ELEMS
            and self[elem] > 0
        )

    def __iter__(self) -> Iterator[Element]:
        return (
            elem
            for elem in self._dice
            if self[elem] > 0
        )

    def __getitem__(self, index: Element) -> int:
        return self._dice.get(index, 0)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dice):
            return False
        return self is other or self._dice == other._dice

    def __hash__(self) -> int:
        return hash(self._dice)

    def __repr__(self) -> str:
        existing_dice = dict([
            (dice.name, str(num))
            for dice, num in self._dice.items()
            if num != 0
        ])
        return (
            '{'
            + ", ".join(
                f"{key}: {val}"
                for key, val in existing_dice.items()
            )
            + '}'
        )

    def to_dict(self) -> dict[Element, int]:
        """ :returns: a dicrionary that contains the dice info. """
        return self._dice.to_dict()

    def get_dices(self) -> HashableDict[Element, int]:
        """ :returns: the internal frozen dictionary of dice. """
        return self._dice

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this Dice.
        """
        ret_val: list[int] = []
        for elem in Element:
            ret_val.extend((elem.value, self[elem]))
        return ret_val

    def dict_str(self) -> dict[str, Any]:
        existing_dice = dict([
            (dice.name, str(num))
            for dice, num in self._dice.items()
            if num != 0
        ])
        return existing_dice

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


class ActualDice(Dice):
    """
    Used for the actual dice a player can have.
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

    def _satisfy(self, requirement: AbstractDice) -> bool:
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
        most_pure: int = max(pure_deducted.values())
        if omni_remained + most_pure < requirement[Element.OMNI]:
            return False

        # We have enough dice to satisfy Element.ANY, so success
        return True

    def loosely_satisfy(self, requirement: AbstractDice) -> bool:
        """
        :returns: `True` if `requirement` can be satisfied.

        Asserts self and requirement are legal.
        """
        if self.num_dice() < requirement.num_dice():
            return False
        return self._satisfy(requirement)

    def just_satisfy(self, requirement: AbstractDice) -> bool:
        """
        :returns: `True` if `self` exactly satisfies `requirement`, that is not
                  a single extra die is contained.

        Asserts self and requirement are legal.
        """
        if self.num_dice() != requirement.num_dice():
            return False
        return self._satisfy(requirement)

    def basically_satisfy(
            self,
            requirement: AbstractDice,
    ) -> None | ActualDice:
        """
        :param game_state: the context the selection is based on, but not used by
                           this method, so leave it as `None` by default.

        :returns: a way to fulfill the `requirement`, not necessarily the smartest
                  solution is returned. If it is impossible to fulfill, then
                  `None` is returned.
        """
        if requirement.num_dice() > self.num_dice():
            return None
        # TODO: optimize for having game_state
        from collections import defaultdict
        remaining: dict[Element, int] = self._dice.copy()
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
            best_elem: None | Element = None
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
        return ActualDice(answer)

    def smart_selection(
            self,
            requirement: AbstractDice,
            characters: None | Characters = None,
            local_precedence: None | list[set[Element]] = None,
    ) -> None | Self:
        """
        :param player_state: the context the selection is based on, but not used by
                           this method, so leave it as `None` by default.

        :returns: a way to fulfill the `requirement`, which tries to keep as many
                  useful dice as possible. If it is impossible to fulfill, then
                  `None` is returned.
        """

        # result in dict format
        result_dict: dict[Element, int] = defaultdict(int)

        # optimisation check - if required dices > avaiable dices, break
        if requirement.num_dice() > self.num_dice():
            return None

        supply: dict[Element, int] = defaultdict(int)
        supply.update(self._dice)

        need: dict[Element, int] = defaultdict(int)
        need.update(requirement._dice)

        if local_precedence is None:
            if characters is None:
                local_precedence = []
            else:
                chars = characters.get_characters()
                active_char = characters.get_active_character()
                if active_char is None:
                    local_precedence = [{char.ELEMENT() for char in chars}]
                else:
                    local_precedence = [
                        {active_char.ELEMENT()},
                        {char.ELEMENT() for char in chars} - {active_char.ELEMENT()},
                    ]
        assert len(local_precedence) <= self._NUMBER_OF_ELEMENTS + 2

        # list of first priority elements
        first_priority_elements: set[Element] = (
            set()
            if len(local_precedence) < 1
            else local_precedence[0]
        )

        def omni_filler_priority(
                omni_supply: int,
                omni_needed: int,
                elem_supply: int,
                elem_needed: int,
                elem_prioritized: bool
        ) -> tuple[int, int]:
            """
            return
            Tuple[
                how many OMNI (+ first priority elements if it so) spend if we select this ELEMENT as OMNI filler,
                how many OMNI spent
            ]

            return BIG_INT if no possibility
            """
            if elem_prioritized:
                return elem_needed + omni_needed, elem_needed + omni_needed - elem_supply
            else:
                omni = max((elem_needed + omni_needed) - elem_supply, 0)
                return omni, omni  # don't spend element_needed, so engaged 0 elements of element_supply

        @cache
        def get_local_priority(element: Element) -> tuple[int, int]:
            """ get priority by element, lower tuple is bigger priority and should be spent first """
            nonlocal local_precedence
            assert local_precedence is not None
            if element is Element.OMNI:
                return self._NUMBER_OF_ELEMENTS + 2, -1  # OMNI has biggest tuple
            for i, elem_set in enumerate(local_precedence, start=1):
                if element in elem_set:
                    return (self._NUMBER_OF_ELEMENTS + 1 - i,
                            self._ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY_DCT[element]
                    )
            else:
                return -1, self._ELEMENTS_AND_OMNI_BY_DECREASING_GLOBAL_PRIORITY_DCT[element]

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
            elem_cost_mapping: list[tuple[Element, tuple[int, int]]] = [
                (
                    element,
                    omni_filler_priority(
                        elem_supply=supply[element],
                        elem_needed=need[element],
                        omni_needed=need[Element.OMNI],
                        elem_prioritized=element in first_priority_elements,
                        omni_supply=supply[Element.OMNI]
                    )
                )
                for element in _PURE_ELEMS
                if supply[element] + supply[Element.OMNI] >= need[element] + need[Element.OMNI]
            ]

            if not elem_cost_mapping:
                # Can't fill OMNI requirement
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

            filler_element_count = min(need[Element.OMNI], supply[filler_element])
            filler_omni_count = need[Element.OMNI] - filler_element_count

            result_dict[filler_element] += filler_element_count
            result_dict[Element.OMNI] += filler_omni_count

            need[Element.OMNI] -= filler_element_count + filler_omni_count
            supply[filler_element] -= filler_element_count
            supply[Element.OMNI] -= filler_omni_count

            assert need[Element.OMNI] == 0, "need element omni not 0"
            assert supply[filler_element] >= 0, "supply <0"
            assert supply[Element.OMNI] >= 0, "supply <0"

        # 2nd step - fill the pure Elements
        # with pure Elements and OMNI

        for elem in self._ELEMENTS:
            # 2.1 fill element with itself
            num_of_elem = min(need[elem], supply[elem])

            result_dict[elem] += num_of_elem
            need[elem] -= num_of_elem
            supply[elem] -= num_of_elem

            # 2.2 fill Element with OMNI if needed
            if need[elem] > supply[Element.OMNI]:
                return None

            number_of_omni = need[elem]

            result_dict[Element.OMNI] += number_of_omni
            need[elem] -= number_of_omni
            supply[Element.OMNI] -= number_of_omni

        # 3rd step - fill ANY with all avaiable elements

        elements_by_precedence: list[tuple[tuple[int, int], Element]] = [
            (get_local_priority(element), element) for element in self._ELEMENTS_AND_OMNI
        ]
        heapify(elements_by_precedence)

        while need[Element.ANY] > 0 and elements_by_precedence:
            precedence, elem = heappop(elements_by_precedence)

            number_of_spent_element = min(need[Element.ANY], supply[elem])

            result_dict[elem] += number_of_spent_element
            need[Element.ANY] -= number_of_spent_element
            supply[elem] -= number_of_spent_element

        assert sum(need.values()) == 0
        return type(self)(dice=result_dict)

    def _init_ordered_dice(
            self,
            priority_elems: None | frozenset[Element]
    ) -> HashableDict[Element, int]:
        character_elems: frozenset[Element]
        if priority_elems is None:
            character_elems = frozenset()
        else:
            character_elems = priority_elems

        dice: dict[Element, int] = {}
        if self[Element.OMNI] > 0:
            dice[Element.OMNI] = self[Element.OMNI]
        # list[tuple[alive chars have elem, num of elem, priority of elem]]
        sorted_categories: list[tuple[int, int, int]] = sorted(
            [
                (
                    case_val(elem in character_elems, 1, 0),
                    self[elem],
                    self._LEGAL_ELEMS_ORDERED_DICT[elem],
                )
                for elem in self.elems()
                if elem is not Element.OMNI and self[elem] > 0
            ],
            reverse=True
        )
        for _, _, priority in sorted_categories:
            elem = self._LEGAL_ELEMS_ORDERED_DICT_REV[priority]
            dice[elem] = self[elem]
        return HashableDict.from_dict(dice)

    def dice_ordered(self, player_state: None | PlayerState) -> dict[Element, int]:
        """
        :returns: an ordered dictionary of dice contained by `self`.
                  The ordering follows the in-game top-down ordering when a
                  player has multiple dice.
        """
        return self.readonly_dice_ordered(player_state).to_dict()

    def readonly_dice_ordered(self, player_state: None | PlayerState) -> HashableDict[Element, int]:
        """
        :returns: the same value as `.dice_ordered()` but a readonly version.

        This method has a better performance.
        """
        return self._init_ordered_dice(
            None
            if player_state is None
            else frozenset(
                char.ELEMENT()
                for char in player_state.get_characters().get_alive_characters()
            )
        )

    def _init_ordered_dice_collection(self) -> HashableDict[Element, int]:
        dice = self._init_ordered_dice(None)
        if Element.OMNI not in dice:
            return dice
        mutable_dice = dice.to_dict()
        mutable_dice[Element.OMNI] = mutable_dice.pop(Element.OMNI)
        return HashableDict(mutable_dice)

    def dice_collection_ordered(self) -> dict[Element, int]:
        """
        :returns: an ordered dictionary of dice contained by `self`.
                  The ordering follows the collection order of supports like
                  Liben and Vanarana.
        """
        return self.readonly_dice_collection_ordered().to_dict()

    def readonly_dice_collection_ordered(self) -> HashableDict[Element, int]:
        """
        :returns: the same value as `.dice_collection_ordered()` but a readonly version.

        This method has a better performance.
        """
        return self._init_ordered_dice_collection()

    def hide_all(self) -> Self:
        """
        :returns: the hidden version of actual dice. (replace all by `ANY`)
        """
        return ActualDice.from_all(self.num_dice(), Element.ANY)  # type: ignore

    @classmethod
    def from_random(cls, size: int, excepted_elems: set[Element] = set()) -> ActualDice:
        """
        :returns: a random `ActualDice` object with `size` of dice chosen from `expected_elems`.
        """
        dice = ActualDice.from_empty()
        dice._dice._unfreeze()
        for i in range(size):
            elem = random.choice(tuple(ActualDice._LEGAL_ELEMS - excepted_elems))
            dice._dice[elem] += 1
        dice._dice.freeze()
        return dice

    @classmethod
    def from_all(cls, size: int, elem: Element) -> ActualDice:
        dice = ActualDice.from_empty()
        dice._dice._unfreeze()
        dice._dice[Element.OMNI] = size
        dice._dice.freeze()
        return dice

    @classmethod
    def from_dice(cls, dice: Dice) -> None | ActualDice:
        """
        :returns: a new object of `ActualDice` if the `dice` provided is legal
                  in the context of `ActualDice`.
        """
        new_dice = ActualDice(dice._dice)
        if not new_dice.is_legal():
            return None
        else:
            return new_dice


class AbstractDice(Dice):
    """
    Used for the dice cost of cards and other actions
    """
    _LEGAL_ELEMS = frozenset({
        Element.OMNI,  # represents the request for dice of the same type
        Element.PYRO,
        Element.HYDRO,
        Element.ANEMO,
        Element.ELECTRO,
        Element.DENDRO,
        Element.CRYO,
        Element.GEO,
        Element.ANY,
    })

    def can_cost_less_any(self) -> bool:
        """
        :returns: `True` if less `Element.ANY` can be required.
        """
        return self[Element.ANY] > 0

    def cost_less_any(self, num: int) -> Self:
        """
        :returns: a new `AbstractDice` object where `num` less ANY dice are costed.

        This method ensures the return value is legal.
        """
        return (self - {Element.ANY: 1}).validify()

    def can_cost_less_elem(self, elem: None | Element = None) -> bool:
        """
        :param elem: if this value is None (by default), then any element is considered,
                     otherwise, only `elem` is considered.

        :returns: `True` if less elemental dice can be costed.
        """
        if elem is not None:
            return self[elem] > 0 or self[Element.ANY] > 0
        else:
            return any(
                self[elem] > 0
                for elem in _PURE_ELEMS
            ) or self[Element.ANY] > 0

    def cost_less_elem(self, num: int, elem: None | Element = None) -> Self:
        """
        :param elem: if this value is None (by default), then elements of a particular
                     order are removed (max to `num`). Otherwise, only dice of `elem`
                     are removed.

        :returns: a new `AbstractDice` object where `num` less `elem` are required.
        """
        if elem is None:
            elem = next((
                elem
                for elem in ActualDice._LEGAL_ELEMS_ORDERED
                if self[elem] > 0
            ), None)
            if elem is None:
                # as self[ANY_PURE_ELEM] is 0, it doesn't matter which elem to choose
                elem = Element.PYRO
        elem_less_amount = min(self[elem], num)
        any_less_amount = max(0, num - elem_less_amount)
        ret_val = (self - {elem: elem_less_amount, Element.ANY: any_less_amount}).validify()
        assert ret_val.is_legal(), f"{self} - {num}{elem} -> {ret_val}"
        return ret_val

    @classmethod
    def from_dice(cls, dice: Dice) -> None | AbstractDice:
        """
        :returns: a new object of `ActualDice` if the `dice` provided is legal
                  in the context of `ActualDice`.
        """
        new_dice = AbstractDice(dice._dice)
        if not new_dice.is_legal():
            return None
        else:
            return new_dice
