from __future__ import annotations
from itertools import chain
from typing import Iterator, Optional, TYPE_CHECKING, Union

from ..helper.quality_of_life import just

if TYPE_CHECKING:
    from ..encoding.encoding_plan import EncodingPlan
    from .summon import Summon

__all__ = [
    "Summons",
]


class Summons:
    """
    A container for easy summons managing.
    """
    def __init__(self, summons: tuple[Summon, ...], max_num: int):
        assert len(summons) <= max_num
        self._summons = summons
        self._max_num = max_num

    def get_summons(self) -> tuple[Summon, ...]:
        return self._summons

    def find(self, summon_type: type[Summon]) -> None | Summon:
        return next((s for s in self._summons if type(s) is summon_type), None)

    def just_find(self, summon_type: type[Summon]) -> Summon:
        return just(self.find(summon_type))

    def update_summon(self, incoming_summon: Summon, override: bool = False) -> Summons:
        summons = list(self._summons)
        for i, summon in enumerate(summons):
            if type(summon) != type(incoming_summon):
                continue
            new_summon: Optional[Summon]
            if override:
                new_summon = incoming_summon
            else:
                new_summon = summon.update(incoming_summon)
            if summon == new_summon:
                return self
            if new_summon is None:
                return self.remove_summon(type(summon))
            summons[i] = new_summon
            return Summons(tuple(summons), self._max_num)
        if len(summons) < self._max_num:
            summons.append(incoming_summon)
        return Summons(tuple(summons), self._max_num)

    def remove_summon(self, summon_type: type[Summon]) -> Summons:
        return Summons(tuple(
            filter(lambda s: type(s) != summon_type, self._summons)
        ), self._max_num)

    def full(self) -> bool:
        return len(self) == self._max_num

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this `Summons` object.
        """
        summons_encoding: list[list[int]] = [
            summon.encoding(encoding_plan)
            for summon in self._summons
        ]
        fillings = encoding_plan.SUMMONS_FIXED_LEN - len(summons_encoding)
        for _ in range(fillings):
            summons_encoding.append([0] * encoding_plan.STATUS_FIXED_LEN)
        return list(chain.from_iterable(summons_encoding))

    def contains(self, summon_type: type[Summon] | Summon) -> bool:
        return any(type(s) is summon_type for s in self._summons)

    def __contains__(self, summon_type: type[Summon] | Summon) -> bool:
        return self.contains(summon_type)

    def __iter__(self) -> Iterator[Summon]:
        return iter(self._summons)

    def __str__(self) -> str:  # pragma: no cover
        return f"[{', '.join(map(str, self._summons))}]"

    def empty(self) -> bool:
        return not bool(self._summons)

    def len(self) -> int:
        return len(self)

    def __len__(self) -> int:
        return len(self._summons)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self is other or (
            self._summons == other._summons
            and self._max_num == other._max_num
        )

    def __hash__(self) -> int:
        return hash((
            self._summons,
            self._max_num,
        ))

    def dict_str(self) -> dict:
        return dict(
            (summon.__class__.__name__.removesuffix("Summon"), str(summon.content_repr()))
            for summon in self
        )
