from __future__ import annotations
from typing import Optional, Union, Iterator

from dgisim.src.summon.summon import Summon


class Summons:
    def __init__(self, summons: tuple[Summon, ...], max_num: int) -> None:
        assert len(summons) <= max_num
        self._summons = summons
        self._max_num = max_num

    def get_summons(self) -> tuple[Summon, ...]:
        return self._summons

    def find(self, summon_type: type[Summon]) -> Optional[Summon]:
        for s in self._summons:
            if type(s) == summon_type:
                return s
        return None

    def update_summon(self, summon: Summon, force: bool=False) -> Summons:
        summons = list(self._summons)
        for i, s in enumerate(summons):
            if type(s) == type(summon):
                if force:
                    summons[i] = summon
                else:
                    summons[i] = summons[i].update(summon)
                return Summons(tuple(summons), self._max_num)
        raise NotImplementedError

    def remove_summon(self, summon: type[Summon]) -> Summons:
        raise NotImplementedError

    def contains(self, summon_type: Union[type[Summon], Summon]) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Summon]:
        return iter(self._summons)
