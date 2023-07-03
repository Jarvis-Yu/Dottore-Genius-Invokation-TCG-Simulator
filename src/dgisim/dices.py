from __future__ import annotations
import random
from enum import Enum
from typing import Optional, Iterator, Iterable, TypeVar, Union
from typing_extensions import Self, override, TYPE_CHECKING

from .helper.hashable_dict import HashableDict
from .helper.level_print import level_print
from .helper.quality_of_life import BIG_INT
from .element.element import Element

if TYPE_CHECKING:
    from .state.game_state import GameState


class Dices:
    _LEGAL_ELEMS = frozenset(elem for elem in Element)

    def __init__(self, dices: dict[Element, int]) -> None:
        self._dices = HashableDict(dices)

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

    def is_legal(self) -> bool:
        return all(map(lambda x: x >= 0, self._dices.values())) \
            and all(elem in self._LEGAL_ELEMS for elem in self._dices)

    def validify(self) -> Self:
        if self.is_legal():
            return self
        return type(self)(dict(
            (elem, max(0, n))
            for elem, n in self._dices.items()
            if elem in self._LEGAL_ELEMS
        ))

    def elems(self) -> Iterable[Element]:
        return self._dices.keys()

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
        if index in self._dices:
            return self._dices[index]
        return 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dices):
            return False
        return self._dices == other._dices

    def __hash__(self) -> int:
        return hash(self._dices)

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        existing_dices = dict([
            (dice.name, str(num))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return level_print(existing_dices, indent)

    def dict_str(self) -> Union[dict, str]:
        existing_dices = dict([
            (dice.name, str(num))
            for dice, num in self._dices.items()
            if num != 0
        ])
        return existing_dices


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
            else:
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
            count = BIG_INT
            for elem in list(_PURE_ELEMS) + [Element.OMNI]:
                this_count = remaining.get(elem, 0)
                if this_count >= omni and this_count < count:
                    best_elem = elem
                    count = this_count
            if best_elem is None:
                return None
            else:
                answer[best_elem] += omni
                remaining[best_elem] -= omni
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
            if remaining[Element.OMNI] < omni_required:
                return None
            answer[Element.OMNI] += omni_required
        return ActualDices(answer)

    @classmethod
    def from_empty(cls) -> ActualDices:
        return ActualDices(dict([
            (elem, 0)
            for elem in ActualDices._LEGAL_ELEMS
        ]))

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
    def from_pre(cls, omni: int, any: int, element: Optional[Element] = None, num: Optional[int] = None) -> AbstractDices:
        assert element is None or element in AbstractDices._LEGAL_ELEMS
        dices = {Element.OMNI: omni, Element.ANY: any, }
        if element is not None and num is not None:
            dices[element] = num
        return AbstractDices(dices)

    @classmethod
    def from_dices(cls, dices: Dices) -> Optional[AbstractDices]:
        new_dices = AbstractDices(dices._dices)
        if not new_dices.is_legal():
            return None
        else:
            return new_dices
