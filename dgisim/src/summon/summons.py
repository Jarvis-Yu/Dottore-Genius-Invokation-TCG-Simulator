from __future__ import annotations
from typing import Optional, Union, Iterator

from dgisim.src.helper.quality_of_life import just
from dgisim.src.summon.summon import Summon


class Summons:
    def __init__(self, summons: tuple[Summon, ...], max_num: int) -> None:
        assert len(summons) <= max_num
        self._summons = summons
        self._max_num = max_num

    def get_summons(self) -> tuple[Summon, ...]:
        return self._summons

    def find(self, summon_type: type[Summon]) -> Optional[Summon]:
        return next((s for s in self._summons if type(s) is summon_type), None)

    def just_find(self, summon_type: type[Summon]) -> Summon:
        return just(self.find(summon_type))

    def update_summon(self, incoming_summon: Summon, force: bool=False) -> Summons:
        summons = list(self._summons)
        for i, summon in enumerate(summons):
            if type(summon) != type(incoming_summon):
                continue
            new_summon: Optional[Summon]
            if force:
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

    def contains(self, summon_type: Union[type[Summon], Summon]) -> bool:
        return any(type(s) is summon_type for s in self._summons)

    def __iter__(self) -> Iterator[Summon]:
        return iter(self._summons)

    def __str__(self) -> str:  # pragma: no cover
        return f"[{'.'.join(map(str, self._summons))}]"