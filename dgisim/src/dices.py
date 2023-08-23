from __future__ import annotations
import random
from collections import Counter
from functools import lru_cache
from typing import Any, Optional, Iterator, Iterable

from typing_extensions import Self, override, TYPE_CHECKING

from .helper.hashable_dict import HashableDict
from .helper.quality_of_life import BIG_INT, case_val
from .element import Element

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
                char.ELEMENT()
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
