from __future__ import annotations
from itertools import chain
from typing import Iterator, TYPE_CHECKING

from ..helper.quality_of_life import just
from .support import Support

if TYPE_CHECKING:
    from ..encoding.encoding_plan import EncodingPlan

__all__ = [
    "Supports",
]

class Supports:
    """
    A container for easy supports managing.
    """
    def __init__(self, supports: tuple[Support, ...], max_num: int):
        assert len(supports) <= max_num
        self._supports = supports
        self._max_num = max_num

    def get_supports(self) -> tuple[Support, ...]:
        return self._supports

    def find(self, support_type: type[Support], sid: int) -> None | Support:
        return next((
            s
            for s in self._supports
            if type(s) is support_type and s.sid == sid
        ), None)

    def just_find(self, support_type: type[Support], sid: int) -> Support:
        return just(self.find(support_type, sid))

    def find_by_sid(self, sid: int) -> None | Support:
        return next((
            s
            for s in self._supports
            if s.sid == sid
        ), None)

    def just_find_by_sid(self, sid: int) -> None | Support:  # pragma: no cover
        return just(self.find_by_sid(sid))

    def update_support(self, incoming_support: Support, override: bool = False) -> Supports:
        supports = list(self._supports)
        for i, support in enumerate(supports):
            sid = support.sid
            if type(support) != type(incoming_support) \
                    or sid != incoming_support.sid:
                continue
            new_support: None | Support
            if override:
                new_support = incoming_support
            else:
                new_support = support.update(incoming_support)
            if support == new_support:
                return self
            if new_support is None:
                return self.remove_support(type(support), support.sid)
            supports[i] = new_support
            return Supports(tuple(supports), self._max_num)
        if len(supports) >= self._max_num:
            raise Exception("Not Reached. "
                            + "Handle support destruction before updating when supports are full.")
        if any(s.sid == incoming_support.sid for s in supports):
            raise Exception("Incoming support cannot be added when support with same sid exists.")
        supports.append(incoming_support)
        return Supports(tuple(supports), self._max_num)

    def new_sid(self, support_type: type[Support]) -> int:
        """ Returns an available SID in this Supports object, start from 1 """
        existings: set[int] = set(s.sid for s in self._supports)
        i = 1
        while i in existings:
            i += 1
        return i

    def remove_support(self, support_type: type[Support], sid: int) -> Supports:
        return Supports(tuple(
            s
            for s in self._supports
            if not(type(s) is support_type and s.sid == sid)
        ), self._max_num)

    def remove_by_sid(self, sid: int) -> Supports:
        return Supports(tuple(
            s
            for s in self._supports
            if s.sid != sid
        ), self._max_num)

    def full(self) -> bool:
        return len(self) == self._max_num

    def contains_exactly(self, support_type: type[Support], sid: int) -> bool:
        return any(
            type(s) is support_type and s.sid == sid
            for s in self._supports
        )

    def contains(self, support_type: type[Support]) -> bool:
        return any(
            type(s) is support_type
            for s in self._supports
        )

    def __contains__(self, support_type: type[Support]) -> bool:
        return self.contains(support_type)

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this `Summons` object.
        """
        supports_encoding: list[list[int]] = [
            support.encoding(encoding_plan)
            for support in self._supports
        ]
        fillings = encoding_plan.SUPPORTS_FIXED_LEN - len(supports_encoding)
        for _ in range(fillings):
            supports_encoding.append([0] * encoding_plan.STATUS_FIXED_LEN)
        return list(chain.from_iterable(supports_encoding))

    def __iter__(self) -> Iterator[Support]:
        return iter(self._supports)

    def __str__(self) -> str:  # pragma: no cover
        return f"[{', '.join(map(str, self._supports))}]"

    def len(self) -> int:
        return len(self)

    def __len__(self) -> int:
        return len(self._supports)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self is other or (
            self._supports == other._supports
            and self._max_num == other._max_num
        )

    def __hash__(self) -> int:
        return hash((
            self._supports,
            self._max_num,
        ))

    def dict_str(self) -> dict:
        return dict(
            (
                support.__class__.__name__.removesuffix("Support") + f"<{support.sid}>",
                support.content_str()
            )
            for support in self
        )
