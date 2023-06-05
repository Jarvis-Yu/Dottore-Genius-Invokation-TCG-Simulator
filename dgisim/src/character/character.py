from __future__ import annotations
from typing import Tuple, Callable, Union
from enum import Enum

import dgisim.src.state.game_state as gs
from dgisim.src.status.status import Status
from dgisim.src.status.statuses import Statuses, EquipmentStatuses, OrderedStatuses, TalentStatuses
from dgisim.src.element.element import ElementalAura
from dgisim.src.effect.event_pre import EventPre
from dgisim.src.dices import AbstractDices
from dgisim.src.effect.event import *
import dgisim.src.effect.effect as efft
from dgisim.src.helper.level_print import level_print_single, INDENT, level_print


class CharacterSkill(Enum):
    NORMAL_ATTACK = 0
    BURST = 1
    ELEMENTAL_SKILL1 = 2
    ELEMENTAL_SKILL2 = 3


class Character:

    def __init__(
        self,
        id: int,
        hp: int,
        max_hp: int,
        energy: int,
        max_energy: int,
        talents: Statuses,
        equipments: EquipmentStatuses,
        statuses: Statuses,
        elemental_aura: ElementalAura,
    ):
        self._id = id
        self._hp = hp
        self._max_hp = max_hp
        self._energy = energy
        self._max_energy = max_energy
        self._talents = talents
        self._equipments = equipments
        self._statuses = statuses
        self._aura = elemental_aura

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

    def get_talent_statuses(self) -> Statuses:
        return self._talents

    def get_equipment_statuses(self) -> EquipmentStatuses:
        return self._equipments

    def get_character_statuses(self) -> Statuses:
        return self._statuses

    def get_elemental_aura(self) -> ElementalAura:
        return self._aura

    def get_all_statuses_ordered(self) -> list[Statuses]:
        return [self._talents, self._equipments, self._statuses]

    def get_all_statuses_ordered_flattened(self) -> tuple[Status, ...]:
        return sum([statuses.get_statuses() for statuses in self.get_all_statuses_ordered()], ())

    def factory(self) -> CharacterFactory:
        return CharacterFactory(self, type(self))

    def address(self, game_state: gs.GameState) -> efft.StaticTarget:
        pid = game_state.belongs_to(self)
        if pid is None:
            raise Exception("target character is not in the current game state")
        me = efft.StaticTarget(pid, efft.Zone.CHARACTER, self.get_id())
        return me

    @classmethod
    def from_default(cls, id: int = -1) -> Character:
        raise Exception("Not Overriden")

    import dgisim.src.action as act

    def skill(self, game_state: gs.GameState, skill_type: CharacterSkill, instruction: act.Instruction) -> tuple[efft.Effect, ...]:
        if skill_type is CharacterSkill.NORMAL_ATTACK:
            return self.normal_attack(game_state, skill_type)
        elif skill_type is CharacterSkill.ELEMENTAL_SKILL1:
            return self.elemental_skill1(game_state, skill_type)
        raise Exception("Not Overriden")

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        raise Exception("Not Overriden")

    def elemental_skill1(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        raise Exception("Not Overriden")

    def alive(self) -> bool:
        return not self.defeated()

    def defeated(self) -> bool:
        return self._hp == 0

    def satiated(self) -> bool:
        from dgisim.src.status.status import SatiatedStatus
        return self._statuses.contains(SatiatedStatus)

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
            "Aura": str(self._aura),
            "HP": str(self._hp),
            "Max HP": str(self._max_hp),
            "Energy": str(self._energy),
            "Max Energy": str(self._max_energy),
            "Talents": str(self._talents),
            "Equipments": str(self._equipments),
            "Statuses": str(self._statuses),
        }, indent)

    def dict_str(self) -> Union[dict, str]:
        return {
            "id": str(self._id),
            "Aura": str(self._aura),
            "HP": str(self._hp),
            "Max HP": str(self._max_hp),
            "Energy": str(self._energy),
            "Max Energy": str(self._max_energy),
            "Talents": str(self._talents),
            "Equipments": str(self._equipments),
            "Statuses": str(self._statuses),
        }


class CharacterFactory:
    def __init__(self, character: Character, char_type: type[Character]) -> None:
        self._char = char_type
        self._id = character.get_id()
        self._hp = character.get_hp()
        self._max_hp = character.get_max_hp()
        self._energy = character.get_energy()
        self._max_energy = character.get_max_energy()
        self._talents = character.get_talent_statuses()
        self._equipments = character.get_equipment_statuses()
        self._statuses = character.get_character_statuses()
        self._aura = character.get_elemental_aura()

    def hp(self, hp: int) -> CharacterFactory:
        self._hp = hp
        return self

    def energy(self, energy: int) -> CharacterFactory:
        self._energy = energy
        return self

    def character_statuses(self, statuses: Statuses) -> CharacterFactory:
        self._statuses = statuses
        return self

    def f_character_statuses(self, f: Callable[[Statuses], Statuses]) -> CharacterFactory:
        return self.character_statuses(f(self._statuses))

    def elemental_aura(self, aura: ElementalAura) -> CharacterFactory:
        self._aura = aura
        return self

    def build(self) -> Character:
        return self._char(
            id=self._id,
            hp=self._hp,
            max_hp=self._max_hp,
            energy=self._energy,
            max_energy=self._max_energy,
            talents=self._talents,
            equipments=self._equipments,
            statuses=self._statuses,
            elemental_aura=self._aura,
        )


class Keqing(Character):

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        return normal_attack_template(
            source=self.address(game_state),
            element=efft.Element.PHYSICAL,
            damage=2,
        )

    def elemental_skill1(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        from dgisim.src.card.card import LightningStiletto

        source = self.address(game_state)
        # TODO: check for talent card and balabala
        return (
            efft.ReferredDamageEffect(
                source=source,
                target=efft.DynamicCharacterTarget.OPPO_ACTIVE,
                element=efft.Element.ELECTRO,
                damage=3,
            ),
            efft.AddCardEffect(
                target=source,
                card=LightningStiletto,
            ),
            efft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            )
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Keqing:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            statuses=OrderedStatuses(()),
            talents=TalentStatuses(()),
            equipments=EquipmentStatuses(()),
            elemental_aura=ElementalAura.from_default(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Keqing):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Kaeya(Character):

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        return normal_attack_template(
            source=self.address(game_state),
            element=efft.Element.PHYSICAL,
            damage=2,
        )

    def elemental_skill1(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        from dgisim.src.card.card import LightningStiletto

        source = self.address(game_state)
        return (
            efft.ReferredDamageEffect(
                source=source,
                target=efft.DynamicCharacterTarget.OPPO_ACTIVE,
                element=efft.Element.CRYO,
                damage=3,
            ),
            efft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            )
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Kaeya:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            talents=TalentStatuses(()),
            equipments=EquipmentStatuses(()),
            statuses=OrderedStatuses(()),
            elemental_aura=ElementalAura.from_default(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Kaeya):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Oceanid(Character):

    def normal_attack(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        return normal_attack_template(
            source=self.address(game_state),
            element=efft.Element.HYDRO,
            damage=1,
        )

    def elemental_skill1(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[efft.Effect, ...]:
        # TODO: add summons
        return ()

    @classmethod
    def from_default(cls, id: int = -1) -> Oceanid:
        return cls(
            id=id,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            talents=TalentStatuses(()),
            equipments=EquipmentStatuses(()),
            statuses=OrderedStatuses(()),
            elemental_aura=ElementalAura.from_default(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Oceanid):
            return False
        return self._all_unique_data() == other._all_unique_data()
