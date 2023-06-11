from __future__ import annotations
from typing import TypeVar, Optional, Iterator

from dgisim.src.status.status import Status
from dgisim.src.helper.quality_of_life import just


_T = TypeVar('_T', bound='Statuses')


class Statuses:
    def __init__(self, statuses: tuple[Status, ...]):
        self._statuses = statuses

    def update_status(self: _T, incoming_status: Status, force: bool=False) -> _T:
        """
        Replaces existing status of the same type with the new_status,
        or append the new_status to the end of current statuses
        """
        cls = type(self)
        statuses = list(self._statuses)
        for i, status in enumerate(statuses):
            if type(status) is not type(incoming_status):
                continue
            new_status: Optional[Status]
            if force:
                new_status = incoming_status
            else:
                new_status = incoming_status.update(status)
            if status == new_status:
                return self
            if new_status is None:
                return self.remove(type(status))
            statuses[i] = new_status
            return cls(tuple(statuses))
        statuses.append(incoming_status)
        return cls(tuple(statuses))

    def contains(self, status: type[Status]) -> bool:
        return any(type(b) is status for b in self._statuses)

    def find(self, status: type[Status]) -> Optional[Status]:
        return next((bf for bf in self._statuses if type(bf) is status), None)

    def just_find(self, status: type[Status]) -> Status:
        return just(self.find(status))

    def remove(self: _T, status: type[Status]) -> _T:
        return type(self)(tuple(
            filter(lambda bf: type(bf) != status, self._statuses)
        ))

    def get_statuses(self) -> tuple[Status, ...]:
        return self._statuses

    def __iter__(self) -> Iterator[Status]:
        return iter(self._statuses)

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
