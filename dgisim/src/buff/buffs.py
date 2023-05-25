from __future__ import annotations
from typing import TypeVar

from dgisim.src.buff.buff import Buffable


T = TypeVar('T', bound='Buffs')


class Buffs:
    def __init__(self, buffs: tuple[Buffable, ...]):
        self._buffs = buffs

    def update_buffs(self: T, buff: Buffable) -> T:
        cls = type(self)
        buffs = list(self._buffs)
        for i, b in enumerate(buffs):
            if type(b) is type(buff):
                buffs[i] = buff
                return cls(tuple(buffs))
        buffs.append(buff)
        return cls(tuple(buffs))

    def contains(self, buff: type[Buffable]) -> bool:
        return any(type(b) is buff for b in self._buffs)

    def get_buffs(self) -> tuple[Buffable, ...]:
        return self._buffs

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Buffs):
            return False
        return self is other or self == other

    def __hash__(self) -> int:
        return hash(self._buffs)

    def __str__(self) -> str:
        return '[' + ', '.join(map(str, self._buffs)) + ']'


class EquipmentBuffs(Buffs):
    pass


class OrderedBuffs(Buffs):
    pass

class TalentBuffs(Buffs):
    pass
