from __future__ import annotations
from itertools import chain
from typing import Iterator, Optional, TYPE_CHECKING, TypeVar
from typing_extensions import override, Self

from ..status import status as stt

from ..helper.quality_of_life import just

if TYPE_CHECKING:
    from ..encoding.encoding_plan import EncodingPlan

__all__ = [
    "Statuses",
    "EquipmentStatuses",
]

_U = TypeVar('_U')


class Statuses:
    """
    A container for easy statuses managing.
    """

    def __init__(self, statuses: tuple[stt.Status, ...]):
        self._statuses = statuses

    def update_status(self, incoming_status: stt.Status, override: bool = False) -> Self:
        """
        :param override: set to `True` if the `incoming_status` unconditionally overrides the
                         existing status of the same type. (or simple add to statuses if there's not
                         one)

        Updates existing status of the same type with the `incoming_status`,
        or append the new_status to the end of current statuses.
        """
        cls = type(self)
        statuses = list(self._statuses)
        for i, status in enumerate(statuses):
            if type(status) is not type(incoming_status):
                continue
            new_status: Optional[stt.Status]
            if override:
                new_status = incoming_status
            else:
                new_status = status.update(incoming_status)
            if status == new_status:
                return self
            if new_status is None:
                return self.remove(type(status))
            statuses[i] = new_status
            return cls(tuple(statuses))
        statuses.append(incoming_status)
        return cls(tuple(statuses))

    def contains(self, status: type[stt.Status]) -> bool:
        """ :returns: `True` if `status` can be found. """
        return any(type(b) is status for b in self._statuses)

    def __contains__(self, status: type[stt.Status]) -> bool:
        return self.contains(status)

    def find(self, status: type[stt.Status]) -> None | stt.Status:
        """ :returns: the status of the exact type `status`, or `None` if not found. """
        return next((bf for bf in self._statuses if type(bf) is status), None)

    def just_find(self, status: type[_U]) -> _U:
        """ :returns: the status of the exact type `status`, or an exception is thrown. """
        assert issubclass(status, stt.Status)
        found_status = just(self.find(status))
        assert isinstance(found_status, status)
        return found_status  # type: ignore

    def find_type(self, status: type[stt.Status]) -> None | stt.Status:
        """ :returns: the status of the type `status`, or `None` if not found. """
        return next((bf for bf in self._statuses if isinstance(bf, status)), None)

    def just_find_type(self, status: type[_U]) -> _U:
        """ :returns: the status of the type `status`, or an exception is thrown. """
        assert issubclass(status, stt.Status)
        found_status = just(self.find_type(status))
        assert isinstance(found_status, status)
        return found_status  # type: ignore

    def remove(self, status: type[stt.Status]) -> Self:
        """ :returns: the `Statuses` where status is removed. """
        return type(self)(tuple(
            filter(lambda bf: type(bf) != status, self._statuses)
        ))

    def get_statuses(self) -> tuple[stt.Status, ...]:
        """ :returns: tuple of statuses. """
        return self._statuses

    def encoding(self, encoding_plan: EncodingPlan, fixed_len: None | int = None) -> list[int]:
        """
        :returns: the encoding of this `Statuses` object.
        """
        statuses_encoding: list[list[int]] = [
            status.encoding(encoding_plan)
            for status in self._statuses
        ]
        fixed_len = encoding_plan.STATUSES_FIXED_LEN if fixed_len is None else fixed_len
        fillings = fixed_len - len(statuses_encoding)
        for _ in range(fillings):
            statuses_encoding.append([0] * encoding_plan.STATUS_FIXED_LEN)
        return list(chain.from_iterable(statuses_encoding))

    def __iter__(self) -> Iterator[stt.Status]:
        return iter(self._statuses)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Statuses):  # pragma: no cover
            return False
        return self is other or self._statuses == other._statuses

    def __hash__(self) -> int:
        return hash(self._statuses)

    def __str__(self) -> str:
        return '[' + ', '.join(map(str, self._statuses)) + ']'

    def dict_str(self) -> list[str]:
        return [
            str(status)
            for status in self._statuses
        ]


class EquipmentStatuses(Statuses):
    _CATEGORIES = (stt.TalentEquipmentStatus, stt.WeaponEquipmentStatus,
                   stt.ArtifactEquipmentStatus)

    def update_status(self, incoming_status: stt.Status, override: bool = False) -> Self:
        """
        :param override: set to `True` if the `incoming_status` unconditionally overrides the
                         existing status of the same category. (or simple add to statuses if
                         there's not one)

        Updates existing status of the same category with the `incoming_status`,
        or append the new_status to the end of current statuses.

        Unlike `Statuses`, only one status of the same category (talent, weapon, artifact) can exist.
        """
        cls = type(self)
        statuses = list(self._statuses)
        for i, status in enumerate(statuses):
            if not any(
                isinstance(incoming_status, category) and isinstance(status, category)
                for category in self._CATEGORIES
            ):
                continue
            if type(status) is not type(incoming_status):
                return self.remove(type(status)).update_status(incoming_status)
            new_status: Optional[stt.Status]
            if override:
                new_status = incoming_status
            else:
                assert type(status) is type(incoming_status)
                new_status = status.update(incoming_status)  # type: ignore
            if status == new_status:
                return self
            if new_status is None:  # pragma: no cover
                return self.remove(type(status))
            statuses[i] = new_status
            return cls(tuple(statuses))
        statuses.append(incoming_status)
        return cls(tuple(statuses))

    @override
    def encoding(self, encoding_plan: EncodingPlan, fixed_len: None | int = 3) -> list[int]:
        """
        :returns: the encoding of this `Statuses` object.
        """
        statuses_encoding: list[list[int]] = [
            status.encoding(encoding_plan)
            for status in self._statuses
        ]
        assert fixed_len is not None
        fillings = fixed_len - len(statuses_encoding)
        for _ in range(fillings):
            statuses_encoding.append([0] * encoding_plan.STATUS_FIXED_LEN)
        return list(chain.from_iterable(statuses_encoding))
