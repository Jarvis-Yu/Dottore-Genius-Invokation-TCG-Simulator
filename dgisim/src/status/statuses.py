from __future__ import annotations
from typing import TypeVar, Optional

from dgisim.src.status.status import Status


_T = TypeVar('_T', bound='Statuses')


class Statuses:
    def __init__(self, statuses: tuple[Status, ...]):
        self._statuses = statuses

    def update_statuses(self: _T, status: Status) -> _T:
        cls = type(self)
        statuses = list(self._statuses)
        for i, b in enumerate(statuses):
            if type(b) is type(status):
                statuses[i] = status
                return cls(tuple(statuses))
        statuses.append(status)
        return cls(tuple(statuses))

    def contains(self, status: type[Status]) -> bool:
        return any(type(b) is status for b in self._statuses)

    def find(self, status: type[Status]) -> Optional[Status]:
        return next((bf for bf in self._statuses if type(bf) is status), None)

    def remove(self, status: type[Status]) -> Statuses:
        return Statuses(tuple(
            filter(lambda bf: type(bf) != status, self._statuses)
        ))

    def get_statuses(self) -> tuple[Status, ...]:
        return self._statuses

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Statuses):
            return False
        return self is other or self == other

    def __hash__(self) -> int:
        return hash(self._statuses)

    def __str__(self) -> str:
        return '[' + ', '.join(map(str, self._statuses)) + ']'


class EquipmentStatuses(Statuses):
    pass


class OrderedStatuses(Statuses):
    pass


class TalentStatuses(Statuses):
    pass
