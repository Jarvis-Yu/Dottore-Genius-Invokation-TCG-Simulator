from __future__ import annotations
from typing import Optional, Tuple, Callable, Union
from enum import Enum
from dataclasses import dataclass
from dgisim.src.effect.event import eft, gs

import dgisim.src.state.game_state as gs
import dgisim.src.card.card as cd
from dgisim.src.status.status import Status
from dgisim.src.status.statuses import Statuses, EquipmentStatuses, OrderedStatuses, TalentStatuses
from dgisim.src.element.element import ElementalAura
from dgisim.src.effect.event_pre import EventPre
from dgisim.src.dices import AbstractDices
from dgisim.src.effect.event import *
import dgisim.src.effect.effect as eft
import dgisim.src.status.status as stt
from dgisim.src.element.element import *
from dgisim.src.helper.level_print import level_print_single, INDENT, level_print


class CharacterSkill(Enum):
    NORMAL_ATTACK = 0
    ELEMENTAL_BURST = 1
    ELEMENTAL_SKILL1 = 2
    ELEMENTAL_SKILL2 = 3


class Character:
    TALENT_STATUS: Optional[type[stt.EquipmentStatus]] = None

    def __init__(
        self,
        id: int,
        hp: int,
        max_hp: int,
        energy: int,
        max_energy: int,
        talents: TalentStatuses,
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

    def get_talent_statuses(self) -> TalentStatuses:
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

    def location(self, game_state: gs.GameState) -> eft.StaticTarget:
        pid = game_state.belongs_to(self)
        if pid is None:
            raise Exception("target character is not in the current game state")
        me = eft.StaticTarget(pid, eft.Zone.CHARACTER, self.get_id())
        return me

    @classmethod
    def from_default(cls, id: int = -1) -> Character:
        raise Exception("Not Overriden")

    import dgisim.src.action as act

    def skill(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[eft.Effect, ...]:
        return self._post_skill(
            game_state,
            self._skill(game_state, skill_type),
        )

    def _skill(self, game_state: gs.GameState, skill_type: CharacterSkill) -> tuple[eft.Effect, ...]:
        if skill_type is CharacterSkill.NORMAL_ATTACK:
            return self.normal_attack(game_state)
        elif skill_type is CharacterSkill.ELEMENTAL_SKILL1:
            return self.elemental_skill1(game_state)
        elif skill_type is CharacterSkill.ELEMENTAL_BURST:
            return self.elemental_burst(game_state)
        raise Exception("Not Overriden")

    def _post_skill(self, game_state: gs.GameState, effects: tuple[eft.Effect, ...]) -> tuple[eft.Effect, ...]:
        source = self.location(game_state)
        return effects + (
            eft.DeathCheckCheckerEffect(),
            eft.SwapCharacterCheckerEffect(
                my_active=source,
                oppo_active=eft.StaticTarget(
                    pid=source.pid.other(),
                    zone=eft.Zone.CHARACTER,
                    id=game_state.get_other_player(source.pid).just_get_active_character().get_id()
                )
            ),
        )

    def normal_attack(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return self._post_normal_attack(
            game_state,
            self._normal_attack(
                self._pre_normal_attack(game_state)
            )
        )

    def _pre_normal_attack(self, game_state: gs.GameState) -> gs.GameState:
        return game_state

    def _normal_attack(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_normal_attack(self, game_state: gs.GameState, effects: tuple[eft.Effect, ...]) -> tuple[eft.Effect, ...]:
        source = self.location(game_state)
        return effects + (
            eft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            ),
        )

    def elemental_skill1(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return self._post_elemental_skill1(
            game_state,
            self._elemental_skill1(
                self._pre_elemental_skill1(game_state)
            )
        )

    def _pre_elemental_skill1(self, game_state: gs.GameState) -> gs.GameState:
        return game_state

    def _elemental_skill1(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_elemental_skill1(self, game_state: gs.GameState, effects: tuple[eft.Effect, ...]) -> tuple[eft.Effect, ...]:
        source = self.location(game_state)
        return effects + (
            eft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            ),
        )

    def elemental_skill2(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return self._post_elemental_skill2(
            game_state,
            self._elemental_skill2(
                self._pre_elemental_skill2(game_state)
            )
        )

    def _pre_elemental_skill2(self, game_state: gs.GameState) -> gs.GameState:
        return game_state

    def _elemental_skill2(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_elemental_skill2(self, game_state: gs.GameState, effects: tuple[eft.Effect, ...]) -> tuple[eft.Effect, ...]:
        source = self.location(game_state)
        return effects + (
            eft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            ),
        )

    def elemental_burst(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return self._post_elemental_burst(
            game_state,
            self._elemental_burst(
                self._pre_elemental_burst(game_state)
            )
        )

    def _pre_elemental_burst(self, game_state: gs.GameState) -> gs.GameState:
        return game_state

    def _elemental_burst(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_elemental_burst(self, game_state: gs.GameState, effects: tuple[eft.Effect, ...]) -> tuple[eft.Effect, ...]:
        return effects

    def talent_equiped(self) -> bool:
        assert self.TALENT_STATUS is not None
        return self.get_equipment_statuses().contains(self.TALENT_STATUS)

    def alive(self) -> bool:
        return not self.defeated()

    def defeated(self) -> bool:
        return self._hp == 0

    def satiated(self) -> bool:
        from dgisim.src.status.status import SatiatedStatus
        return self._statuses.contains(SatiatedStatus)

    def can_cast_skill(self) -> bool:
        from dgisim.src.status.status import FrozenStatus
        return not self._statuses.contains(FrozenStatus)

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

    def talents(self, talents: TalentStatuses) -> CharacterFactory:
        self._talents = talents
        return self

    def f_talents(self, f: Callable[[TalentStatuses], TalentStatuses]) -> CharacterFactory:
        return self.talents(f(self._talents))

    def equipments(self, equipments: EquipmentStatuses) -> CharacterFactory:
        self._equipments = equipments
        return self

    def f_equipments(self, f: Callable[[EquipmentStatuses], EquipmentStatuses]) -> CharacterFactory:
        return self.equipments(f(self._equipments))

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
    BASE_ELECTRO_INFUSION_DURATION: int = 2
    TALENT_STATUS = stt.ThunderingPenanceStatus

    def _normal_attack(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            source=self.location(game_state),
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        source = self.location(game_state)
        effects: list[eft.Effect] = [
            eft.ReferredDamageEffect(
                source=source,
                target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=3,
            )
        ]

        # check if can gain ElectroInfusionStatus
        can_infuse = False

        intrinsic_talent = self.get_talent_statuses().just_find(stt.KeqingTalentStatus)
        if intrinsic_talent.can_infuse:
            can_infuse = True
            effects.append(
                eft.OverrideCharacterStatusEffect(
                    source,
                    stt.KeqingTalentStatus(can_infuse=False),
                )
            )

        cards = game_state.get_player(source.pid).get_hand_cards()
        if not can_infuse and cards.contains(cd.LightningStiletto):
            effects.append(
                eft.RemoveAllCardEffect(
                    source.pid,
                    cd.LightningStiletto,
                )
            )
            can_infuse = True

        talent_card_equiped = self.talent_equiped()
        if can_infuse:
            if talent_card_equiped:
                effects.append(
                    eft.OverrideCharacterStatusEffect(
                        target=source,
                        status=stt.ElectroInfusionStatus(
                            duration=self.BASE_ELECTRO_INFUSION_DURATION,
                            damage_boost=1,
                        ),
                    )
                )
            else:
                effects.append(
                    eft.OverrideCharacterStatusEffect(
                        target=source,
                        status=stt.ElectroInfusionStatus(
                            duration=self.BASE_ELECTRO_INFUSION_DURATION
                        ),
                    )
                )
        else:
            effects.append(
                eft.AddCardEffect(
                    pid=source.pid,
                    card=cd.LightningStiletto,
                )
            )

        return tuple(effects)

    def _elemental_burst(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        assert self.get_energy() == self.get_max_energy()
        source = self.location(game_state)
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=eft.DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.PIERCING,
                damage=3,
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=4,
            ),
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
            talents=TalentStatuses((stt.KeqingTalentStatus(can_infuse=False),)),
            equipments=EquipmentStatuses(()),
            elemental_aura=ElementalAura.from_default(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Keqing):
            return False
        return self._all_unique_data() == other._all_unique_data()


class Kaeya(Character):

    def _normal_attack(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            source=self.location(game_state),
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        from dgisim.src.card.card import LightningStiletto

        source = self.location(game_state)
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=3,
            ),
        )

    def _elemental_burst(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        source = self.location(game_state)
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=1,
            ),
            eft.OverrideCombatStatusEffect(
                target_pid=source.pid,
                status=stt.Icicle(),
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

    def _normal_attack(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            source=self.location(game_state),
            element=Element.HYDRO,
            damage=1,
        )

    def _elemental_skill1(self, game_state: gs.GameState) -> tuple[eft.Effect, ...]:
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
