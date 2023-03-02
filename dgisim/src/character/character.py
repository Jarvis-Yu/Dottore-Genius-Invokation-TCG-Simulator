from __future__ import annotations
from typing import Tuple

from dgisim.src.buff.buffs import Buffs, EquipmentBuffs
from dgisim.src.element.element import ElementalAura
from dgisim.src.event.event_pre import EventPre
from dgisim.src.dices import Dices
from dgisim.src.event.event import *
from dgisim.src.helper.level_print import level_print_single, INDENT, level_print


class Character:

    SKILLS = tuple()

    def __init__(
        self,
        hp: int,
        max_hp: int,
        energy: int,
        max_energy: int,
        buffs: Buffs,
        equipments: EquipmentBuffs,
        elemental_aura: ElementalAura,
    ):
        self._hp = hp
        self._max_hp = max_hp
        self._energy = energy
        self._max_energy = max_energy

    @classmethod
    def from_default(cls) -> Character:
        raise Exception("Not Overriden")

    def skills(self) -> Tuple[EventPre]:
        return self.SKILLS

    def defeated(self) -> bool:
        # TODO
        return False

    def name(self) -> str:
        return self.__class__.__name__

    def _all_unique_data(self) -> Tuple:
        return (
            self._hp,
            self._max_hp,
            self._energy,
            self._max_energy,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Character):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int) -> str:
        new_indent = indent + INDENT
        return level_print({
            "HP": str(self._hp),
            "Max HP": str(self._max_hp),
            "Energy": str(self._energy),
            "Max Energy": str(self._max_energy),
        }, indent)


class Keqing(Character):
    NORMAL_ATTACK = EventPre(
        Dices.from_pre(1, 2),
        TypicalNormalAttackEvent(2, Element.PHYSICAL, 1)
    )
    SKILLS = (
        NORMAL_ATTACK,
    )

    @classmethod
    def from_default(cls) -> Keqing:
        return cls(
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            buffs=Buffs(),
            equipments=EquipmentBuffs(),
            elemental_aura=ElementalAura(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Keqing):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Kaeya(Character):

    NORMAL_ATTACK = EventPre(
        Dices.from_pre(1, 2),
        TypicalNormalAttackEvent(2, Element.PHYSICAL, 1)
    )
    SKILLS = (
        NORMAL_ATTACK,
    )

    @classmethod
    def from_default(cls) -> Kaeya:
        return cls(
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            buffs=Buffs(),
            equipments=EquipmentBuffs(),
            elemental_aura=ElementalAura(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Kaeya):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Oceanid(Character):

    NORMAL_ATTACK = EventPre(
        Dices.from_pre(1, 2),
        TypicalNormalAttackEvent(1, Element.HYDRO, 1)
    )
    SKILLS = (
        NORMAL_ATTACK,
    )

    @classmethod
    def from_default(cls) -> Oceanid:
        return cls(
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            buffs=Buffs(),
            equipments=EquipmentBuffs(),
            elemental_aura=ElementalAura(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Oceanid):
            return False
        return self._all_unique_data() == other._all_unique_data()
