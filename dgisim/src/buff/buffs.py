from __future__ import annotations


from dgisim.src.buff.buff import Buffable


class Buffs:
    def __init__(self, buffs: tuple[Buffable, ...]):
        self._buffs = buffs

    def update_buffs(self, buff: Buffable) -> Buffs:
        # TODO
        return self

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
