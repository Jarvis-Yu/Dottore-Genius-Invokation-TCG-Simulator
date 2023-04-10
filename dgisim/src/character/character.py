from __future__ import annotations
from typing import Tuple
from enum import Enum

import dgisim.src.state.game_state as gs
from dgisim.src.buff.buffs import Buffs, EquipmentBuffs, OrderedBuffs
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
        self._buffs = buffs

    def get_id(self) -> int:
        return self._id

    def get_hp(self) -> int:
        return self._hp

    def get_max_hp(self) -> int:
        return self._max_hp

    def get_energy(self) -> int:
        return self._energy

    def get_max_energy(self) -> int:
        return self._max_energy

    def get_buffs(self) -> Buffs:
        return self._buffs

    def factory(self) -> CharacterFactory:
        raise Exception("Not Overriden")

    def address(self, game_state: gs.GameState) -> StaticTarget:
        pid = game_state.belongs_to(self)
        if pid is None:
            raise Exception("target character is not in the current game state")
        me = StaticTarget(pid, Zone.CHARACTER, self.get_id())
        return me

    @classmethod
    def from_default(cls, id: int = -1) -> Character:
        raise Exception("Not Overriden")

    import dgisim.src.action as act

    def skill(self, game_state: gs.GameState, skill_type: CharacterSkill, instruction: act.Instruction) -> tuple[Effect, ...]:
        if skill_type is CharacterSkill.NORMAL_ATTACK:
            return self.normal_attack(game_state, skill_type)
        raise Exception("Not Overriden")

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[Effect, ...]:
        raise Exception("Not Overriden")

    def alive(self) -> bool:
        return not self.defeated()

    def defeated(self) -> bool:
        return self._hp == 0

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
            "Buffs": str(self._buffs),
        }, indent)


class CharacterFactory:
    def __init__(self, character: Character, char_type: type[Character]) -> None:
        self._char = char_type
        self._id = character.get_id()
        self._hp = character.get_hp()
        self._max_hp = character.get_max_hp()
        self._energy = character.get_energy()
        self._max_energy = character.get_max_energy()
        self._buffs = character.get_buffs()

    def hp(self, hp: int) -> CharacterFactory:
        self._hp = hp
        return self

    def energy(self, energy: int) -> CharacterFactory:
        self._energy = energy
        return self

    def build(self) -> Character:
        return self._char(
            id=self._id,
            hp=self._hp,
            max_hp=self._max_hp,
            energy=self._energy,
            max_energy=self._max_energy,
            buffs=self._buffs,
            equipments=EquipmentBuffs(()),
            elemental_aura=ElementalAura(),
        )


class Keqing(Character):

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[Effect, ...]:
        return normal_attack_template(
            source=self.address(game_state),
            element=Element.PHYSICAL,
            damage=2,
        )

    def factory(self) -> CharacterFactory:
        return CharacterFactory(self, type(self))

    @classmethod
    def from_default(cls, id: int = -1) -> Keqing:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            buffs=OrderedBuffs(()),
            equipments=EquipmentBuffs(()),
            elemental_aura=ElementalAura(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Keqing):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Kaeya(Character):

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[Effect, ...]:
        return normal_attack_template(
            source=self.address(game_state),
            element=Element.PHYSICAL,
            damage=2,
        )

    def factory(self) -> CharacterFactory:
        return CharacterFactory(self, type(self))

    @classmethod
    def from_default(cls, id: int = -1) -> Kaeya:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            buffs=OrderedBuffs(()),
            equipments=EquipmentBuffs(()),
            elemental_aura=ElementalAura(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Kaeya):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Oceanid(Character):

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[Effect, ...]:
        return normal_attack_template(
            source=self.address(game_state),
            element=Element.HYDRO,
            damage=1,
        )

    def factory(self) -> CharacterFactory:
        return CharacterFactory(self, type(self))

    @classmethod
    def from_default(cls, id: int = -1) -> Oceanid:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            buffs=OrderedBuffs(()),
            equipments=EquipmentBuffs(()),
            elemental_aura=ElementalAura(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Oceanid):
            return False
        return self._all_unique_data() == other._all_unique_data()
