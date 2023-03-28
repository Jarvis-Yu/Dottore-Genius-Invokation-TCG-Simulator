from __future__ import annotations
from typing import Tuple
from enum import Enum

import dgisim.src.state.game_state as gm
from dgisim.src.buff.buffs import Buffs, EquipmentBuffs
from dgisim.src.element.element import ElementalAura
from dgisim.src.event.event_pre import EventPre
from dgisim.src.dices import AbstractDices
from dgisim.src.event.event import *
from dgisim.src.helper.level_print import level_print_single, INDENT, level_print


class CharacterSkill(Enum):
    NORMAL_ATTACK = 0
    BURST = 1
    SKILL1 = 2
    SKILL2 = 3


class Character:

    def __init__(
        self,
        id: int,
        hp: int,
        max_hp: int,
        energy: int,
        max_energy: int,
        buffs: Buffs,
        equipments: EquipmentBuffs,
        elemental_aura: ElementalAura,
    ):
        self._id = id
        self._hp = hp
        self._max_hp = max_hp
        self._energy = energy
        self._max_energy = max_energy

    @classmethod
    def from_default(cls, id: int = -1) -> Character:
        raise Exception("Not Overriden")

    def normal_attack(self, game_state: gm.GameState) -> tuple[Effect, ...]:
        return ()

    def skill1(self, game_state: gm.GameState) -> tuple[Effect, ...]:
        return ()

    def skill2(self, game_state: gm.GameState) -> tuple[Effect, ...]:
        return ()

    def burst(self, game_state: gm.GameState) -> tuple[Effect, ...]:
        return ()

    def defeated(self) -> bool:
        # TODO
        return False

    def name(self) -> str:
        return self.__class__.__name__

    def _all_unique_data(self) -> Tuple:
        return (
            self._id,
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
            "id": str(self._id),
            "HP": str(self._hp),
            "Max HP": str(self._max_hp),
            "Energy": str(self._energy),
            "Max Energy": str(self._max_energy),
        }, indent)


class Keqing(Character):
    # NORMAL_ATTACK = EventPre(
    #     AbstractDices.from_pre(1, 2),
    #     TypicalNormalAttackEvent(2, Element.PHYSICAL, 1)
    # )
    # SKILLS = (
    #     NORMAL_ATTACK,
    # )

    @classmethod
    def from_default(cls, id: int = -1) -> Keqing:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            buffs=Buffs(),
            equipments=EquipmentBuffs(),
            elemental_aura=ElementalAura(),
        )

    def normal_attack(self, game_state: gm.GameState) -> tuple[Effect, ...]:
        # return normal_attack_template(game_state)
        return super().normal_attack(game_state)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Keqing):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Kaeya(Character):

    # NORMAL_ATTACK = EventPre(
    #     AbstractDices.from_pre(1, 2),
    #     TypicalNormalAttackEvent(2, Element.PHYSICAL, 1)
    # )
    # SKILLS = (
    #     NORMAL_ATTACK,
    # )

    @classmethod
    def from_default(cls, id: int = -1) -> Kaeya:
        return cls(
            id=id,
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

    # NORMAL_ATTACK = EventPre(
    #     AbstractDices.from_pre(1, 2),
    #     TypicalNormalAttackEvent(1, Element.HYDRO, 1)
    # )
    # SKILLS = (
    #     NORMAL_ATTACK,
    # )

    @classmethod
    def from_default(cls, id: int = -1) -> Oceanid:
        return cls(
            id=id,
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
