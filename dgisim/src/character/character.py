"""
This file contains the base class Character for all characters,
and implementation of all characters. (in alphabetic order)
"""
from __future__ import annotations
from dataclasses import replace
from typing import Callable, Optional, TYPE_CHECKING, Union
from typing_extensions import override, Self
from functools import lru_cache

from ..card import card as cd
from ..effect import effect as eft
from ..status import status as stt
from ..status import statuses as stts
from ..summon import summon as sm

from ..dices import AbstractDices
from ..effect.effects_template import *
from ..effect.enums import Zone, DynamicCharacterTarget, TriggeringSignal
from ..effect.structs import StaticTarget, DamageType
from ..element import *
from ..helper.quality_of_life import case_val
from ..state.enums import Pid
from .enums import CharacterSkill, Faction, WeaponType

if TYPE_CHECKING:
    from ..state.game_state import GameState

__all__ = [
    # base
    "Character",

    # concretes
    "AratakiItto",
    "Bennett",
    "ElectroHypostasis",
    "KaedeharaKazuha",
    "Kaeya",
    "Keqing",
    "Klee",
    "Mona",
    "Nahida",
    "Noelle",
    "RhodeiaOfLoch",
    "Shenhe",
    "Tighnari",
    "Venti",
    "Xingqiu",
    "YaeMiko",
]


class Character:
    _ELEMENT = Element.ANY
    _WEAPON_TYPE: WeaponType
    _TALENT_STATUS: None | type[stt.TalentEquipmentStatus]
    _FACTIONS: frozenset[Faction]

    _NORMAL_ATTACK_COST: None | AbstractDices = None
    _ELEMENTAL_SKILL1_COST: None | AbstractDices = None
    _ELEMENTAL_SKILL2_COST: None | AbstractDices = None
    _ELEMENTAL_BURST_COST: None | AbstractDices = None

    def __init__(
        self,
        id: int,
        alive: bool,
        hp: int,
        max_hp: int,
        energy: int,
        max_energy: int,
        hiddens: stts.Statuses,
        equipments: stts.EquipmentStatuses,
        statuses: stts.Statuses,
        elemental_aura: ElementalAura,
    ):
        self._id = id
        self._alive = alive
        self._hp = hp
        self._max_hp = max_hp
        self._energy = energy
        self._max_energy = max_energy
        self._hiddens = hiddens
        self._equipments = equipments
        self._statuses = statuses
        self._aura = elemental_aura

    @classmethod
    def _talent_status(cls) -> None | type[stt.TalentEquipmentStatus]:
        return cls._TALENT_STATUS

    def get_id(self) -> int:
        return self._id

    def get_alive(self) -> bool:
        return self._alive

    def get_hp(self) -> int:
        return self._hp

    def get_max_hp(self) -> int:
        return self._max_hp

    def get_energy(self) -> int:
        return self._energy

    def get_max_energy(self) -> int:
        return self._max_energy

    def get_hidden_statuses(self) -> stts.Statuses:
        return self._hiddens

    def get_equipment_statuses(self) -> stts.EquipmentStatuses:
        return self._equipments

    def get_character_statuses(self) -> stts.Statuses:
        return self._statuses

    def get_elemental_aura(self) -> ElementalAura:
        return self._aura

    def get_all_statuses_ordered(self) -> list[stts.Statuses]:
        return [self._hiddens, self._equipments, self._statuses]

    def get_all_statuses_ordered_flattened(self) -> tuple[stt.Status, ...]:
        return sum([statuses.get_statuses() for statuses in self.get_all_statuses_ordered()], ())

    def factory(self) -> CharacterFactory:
        return CharacterFactory(self, type(self))

    @classmethod
    def FACTIONS(cls) -> frozenset[Faction]:
        return cls._FACTIONS

    @classmethod
    def of_faction(cls, faction: Faction) -> bool:
        return faction in cls._FACTIONS

    @classmethod
    def ELEMENT(cls) -> Element:
        return cls._ELEMENT

    @classmethod
    def WEAPON_TYPE(cls) -> WeaponType:
        return cls._WEAPON_TYPE

    @classmethod
    def from_default(cls, id: int = -1) -> Character:
        raise Exception("Not Overriden")

    @classmethod
    @lru_cache(maxsize=1)
    def skills(cls) -> tuple[CharacterSkill, ...]:
        """ Provides the skill types with corresponding cost that the character has """
        my_skills: list[CharacterSkill] = []
        if cls._normal_attack is not Character._normal_attack:
            my_skills.append(CharacterSkill.NORMAL_ATTACK)
        if cls._elemental_skill1 is not Character._elemental_skill1:
            my_skills.append(CharacterSkill.ELEMENTAL_SKILL1)
        if cls._elemental_skill2 is not Character._elemental_skill2:
            my_skills.append(CharacterSkill.ELEMENTAL_SKILL2)
        if cls._elemental_burst is not Character._elemental_burst:
            my_skills.append(CharacterSkill.ELEMENTAL_BURST)
        return tuple(my_skills)

    @classmethod
    def skill_cost(cls, skill_type: CharacterSkill) -> AbstractDices:
        if skill_type is CharacterSkill.NORMAL_ATTACK and cls._NORMAL_ATTACK_COST is not None:
            return cls._NORMAL_ATTACK_COST
        elif skill_type is CharacterSkill.ELEMENTAL_SKILL1 and cls._ELEMENTAL_SKILL1_COST is not None:
            return cls._ELEMENTAL_SKILL1_COST
        elif skill_type is CharacterSkill.ELEMENTAL_SKILL2 and cls._ELEMENTAL_SKILL2_COST is not None:
            return cls._ELEMENTAL_SKILL2_COST
        elif skill_type is CharacterSkill.ELEMENTAL_BURST and cls._ELEMENTAL_BURST_COST is not None:
            return cls._ELEMENTAL_BURST_COST
        raise NotImplementedError(f"{skill_type} cost for {cls.__name__} not defined")

    def skill(self, game_state: GameState, source: StaticTarget, skill_type: CharacterSkill) -> tuple[eft.Effect, ...]:
        """
        This should only be called to get effects right before the skill is to be executed.

        Otherwise faulty effects may be generated.
        """
        return self._post_skill(
            game_state,
            source,
            skill_type,
            self._skill(game_state, source, skill_type),
        )

    def _skill(self, game_state: GameState, source: StaticTarget, skill_type: CharacterSkill) -> tuple[eft.Effect, ...]:
        if skill_type is CharacterSkill.NORMAL_ATTACK:
            return self.normal_attack(game_state, source)
        elif skill_type is CharacterSkill.ELEMENTAL_SKILL1:
            return self.elemental_skill1(game_state, source)
        elif skill_type is CharacterSkill.ELEMENTAL_SKILL2:
            return self.elemental_skill2(game_state, source)
        elif skill_type is CharacterSkill.ELEMENTAL_BURST:
            return self.elemental_burst(game_state, source)
        raise Exception(f"Not Overriden, skill_type={skill_type}")

    def _post_skill(
            self,
            game_state: GameState,
            source: StaticTarget,
            skill_type: CharacterSkill,
            effects: tuple[eft.Effect, ...],
    ) -> tuple[eft.Effect, ...]:
        return effects + (
            eft.DefeatedCheckerEffect(),
            eft.BroadCastSkillInfoEffect(
                source=source,
                skill=skill_type,
            ),
            eft.SwapCharacterCheckerEffect(  # handle swap events
                my_active=source,
                oppo_active=StaticTarget(
                    pid=source.pid.other(),
                    zone=Zone.CHARACTERS,
                    id=game_state.get_other_player(source.pid).just_get_active_character().get_id()
                )
            ),
            eft.AllStatusTriggererEffect(
                pid=source.pid,
                signal=TriggeringSignal.POST_REACTION,
            ),
            eft.AllStatusTriggererEffect(
                pid=source.pid,
                signal=TriggeringSignal.DEATH_EVENT,
            ),
            eft.DeathCheckCheckerEffect(),  # detect death swap request
            eft.AllStatusTriggererEffect(
                pid=source.pid,
                signal=TriggeringSignal.POST_DMG,
            ),
        )

    def normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return self._post_normal_attack(
            game_state,
            source,
            self._normal_attack(
                self._pre_normal_attack(game_state, source), source
            )
        )

    def _pre_normal_attack(self, game_state: GameState, source: StaticTarget) -> GameState:
        return game_state

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_normal_attack(
            self,
            game_state: GameState,
            source: StaticTarget,
            effects: tuple[eft.Effect, ...]
    ) -> tuple[eft.Effect, ...]:
        return effects + (
            eft.AliveMarkCheckerEffect(),
            eft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            ),
        )

    def elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return self._post_elemental_skill1(
            game_state,
            source,
            self._elemental_skill1(
                self._pre_elemental_skill1(game_state, source), source
            )
        )

    def _pre_elemental_skill1(self, game_state: GameState, source: StaticTarget) -> GameState:
        return game_state

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_elemental_skill1(
            self,
            game_state: GameState,
            source: StaticTarget,
            effects: tuple[eft.Effect, ...]
    ) -> tuple[eft.Effect, ...]:
        return effects + (
            eft.AliveMarkCheckerEffect(),
            eft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            ),
        )

    def elemental_skill2(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return self._post_elemental_skill2(
            game_state,
            source,
            self._elemental_skill2(
                self._pre_elemental_skill2(game_state, source), source
            )
        )

    def _pre_elemental_skill2(self, game_state: GameState, source: StaticTarget) -> GameState:
        return game_state

    def _elemental_skill2(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_elemental_skill2(self, game_state: GameState, source: StaticTarget, effects: tuple[eft.Effect, ...]) -> tuple[eft.Effect, ...]:
        return effects + (
            eft.AliveMarkCheckerEffect(),
            eft.EnergyRechargeEffect(
                target=source,
                recharge=1,
            ),
        )

    def elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return self._post_elemental_burst(
            game_state,
            source,
            self._elemental_burst(
                self._pre_elemental_burst(game_state, source), source
            )
        )

    def _pre_elemental_burst(self, game_state: GameState, source: StaticTarget) -> GameState:
        return game_state

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        raise Exception("Not Overriden")

    def _post_elemental_burst(
            self,
            game_state: GameState,
            source: StaticTarget,
            effects: tuple[eft.Effect, ...]
    ) -> tuple[eft.Effect, ...]:
        return effects + (
            eft.AliveMarkCheckerEffect(),
        )

    def talent_equiped(self) -> bool:
        talent_status = self._talent_status()
        if talent_status is None:
            return False
        return self.get_equipment_statuses().contains(talent_status)

    def alive(self) -> bool:
        return self._alive

    def defeated(self) -> bool:
        return not self._alive

    def satiated(self) -> bool:
        from ..status.status import SatiatedStatus
        return self._statuses.contains(SatiatedStatus)

    def can_cast_skill(self) -> bool:
        from ..status.status import FrozenStatus
        return not self._statuses.contains(FrozenStatus) and not self.defeated()

    def name(self) -> str:
        return self.__class__.__name__

    def _all_unique_data(self) -> tuple:
        return (
            self._id,
            self._alive,
            self._hp,
            self._max_hp,
            self._energy,
            self._max_energy,
            self._hiddens,
            self._equipments,
            self._statuses,
            self._aura,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, _) -> Self:
        return self

    def dict_str(self) -> Union[dict, str]:
        return {
            "id": str(self._id),
            "Alive": str(self._alive),
            "Aura": str(self._aura),
            "HP": str(self._hp),
            "Max HP": str(self._max_hp),
            "Energy": str(self._energy),
            "Max Energy": str(self._max_energy),
            "Hiddens": self._hiddens.dict_str(),
            "Equipments": self._equipments.dict_str(),
            "Statuses": self._statuses.dict_str(),
        }


class CharacterFactory:
    def __init__(self, character: Character, char_type: type[Character]) -> None:
        self._char = char_type
        self._id = character.get_id()
        self._alive = character.get_alive()
        self._hp = character.get_hp()
        self._max_hp = character.get_max_hp()
        self._energy = character.get_energy()
        self._max_energy = character.get_max_energy()
        self._hiddens = character.get_hidden_statuses()
        self._equipments = character.get_equipment_statuses()
        self._statuses = character.get_character_statuses()
        self._aura = character.get_elemental_aura()

    def alive(self, alive: bool) -> CharacterFactory:
        self._alive = alive
        return self

    def hp(self, hp: int) -> CharacterFactory:
        self._hp = hp
        return self

    def energy(self, energy: int) -> CharacterFactory:
        self._energy = energy
        return self

    def hiddens(self, hiddens: stts.Statuses) -> CharacterFactory:
        self._hiddens = hiddens
        return self

    def f_hiddens(self, f: Callable[[stts.Statuses], stts.Statuses]) -> CharacterFactory:
        return self.hiddens(f(self._hiddens))

    def equipments(self, equipments: stts.EquipmentStatuses) -> CharacterFactory:
        self._equipments = equipments
        return self

    def f_equipments(self, f: Callable[[stts.EquipmentStatuses], stts.EquipmentStatuses]) -> CharacterFactory:
        return self.equipments(f(self._equipments))

    def character_statuses(self, statuses: stts.Statuses) -> CharacterFactory:
        self._statuses = statuses
        return self

    def f_character_statuses(self, f: Callable[[stts.Statuses], stts.Statuses]) -> CharacterFactory:
        return self.character_statuses(f(self._statuses))

    def elemental_aura(self, aura: ElementalAura) -> CharacterFactory:
        self._aura = aura
        return self

    def build(self) -> Character:
        return self._char(
            id=self._id,
            alive=self._alive,
            hp=self._hp,
            max_hp=self._max_hp,
            energy=self._energy,
            max_energy=self._max_energy,
            hiddens=self._hiddens,
            equipments=self._equipments,
            statuses=self._statuses,
            elemental_aura=self._aura,
        )


class AratakiItto(Character):
    _ELEMENT = Element.GEO
    _WEAPON_TYPE = WeaponType.CLAYMORE
    _TALENT_STATUS = stt.AratakiIchibanStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.GEO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.GEO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.GEO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.SuperlativeSuperstrengthStatus,
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.UshiSummon,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=5,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.RagingOniKing,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Bennett(Character):
    # basic info
    _ELEMENT = Element.PYRO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.GrandExpectationStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.PYRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.PYRO: 4,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=3,
                damage_type=DamageType(elemental_skill=True),
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
        ]
        this_player = game_state.get_player(source.pid)
        talent_equiped = self.talent_equiped()
        if stt.InspirationFieldStatus in this_player.get_combat_statuses() and talent_equiped:
            effects.append(
                eft.RemoveCombatStatusEffect(
                    target_pid=source.pid,
                    status=stt.InspirationFieldStatus,
                )
            )
        effects.append(
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=(
                    stt.InspirationFieldStatus
                    if not talent_equiped
                    else stt.InspirationFieldEnhancedStatus
                )
            )
        )
        return tuple(effects)

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class ElectroHypostasis(Character):
    _ELEMENT = Element.ELECTRO
    _WEAPON_TYPE = WeaponType.NONE
    _TALENT_STATUS = None
    _FACTIONS = frozenset((Faction.MONSTER,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.ELECTRO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.ELECTRO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.ELECTRO,
            damage=1,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=2,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.RockPaperScissorsComboScissorsStatus,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.ChainsOfWardingThunderSummon,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=8,
            max_hp=8,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses((stt.ElectroCrystalCoreHiddenStatus(),)),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class KaedeharaKazuha(Character):
    _ELEMENT = Element.ANEMO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.PoeticsOfFuubutsuStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.ANEMO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.ANEMO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.ANEMO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        # POTENTIAL BUG: if there's some ANEMO infusion in the future, normal attack cannot
        #                trigger talent.
        #                may need some redesigning in the future.
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    @override
    def _elemental_skill1(
            self,
            game_state: GameState,
            source: StaticTarget
    ) -> tuple[eft.Effect, ...]:
        midare_to_use: type[stt.MidareRanzanStatus] = stt.MidareRanzanStatus
        oppo_active_character_aura = (
            game_state
            .get_player(source.pid.other())
            .just_get_active_character()
            .get_elemental_aura()
        )
        reaction = Reaction.consult_reaction_with_aura(oppo_active_character_aura, Element.ANEMO)
        if reaction is not None and reaction.first_elem in stt._MIDARE_RANZAN_MAP:
            midare_to_use = stt._MIDARE_RANZAN_MAP[reaction.first_elem]
        effects: tuple[eft.Effect, ...] = (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ANEMO,
                damage=3,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=midare_to_use,
            ),
        )
        if self.talent_equiped() \
                and reaction is not None \
                and reaction.first_elem in stt._POETICS_OF_FUUBUTSU_MAP:
            poetic_status = stt._POETICS_OF_FUUBUTSU_MAP[reaction.first_elem]
            effects += (
                eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=poetic_status,
                ),
            )
        return effects

    @override
    def _post_skill(
            self,
            game_state: GameState,
            source: StaticTarget,
            skill_type: CharacterSkill,
            effects: tuple[eft.Effect, ...],
    ) -> tuple[eft.Effect, ...]:
        """ override for the afterwards swap of Kazuha's elemental skill """
        appended_effects: tuple[eft.Effect, ...] = super()._post_skill(
            game_state, source, skill_type, effects
        )
        if skill_type is CharacterSkill.ELEMENTAL_SKILL1:
            appended_effects += (
                eft.ForwardSwapCharacterCheckEffect(
                    target_player=source.pid,
                ),
            )
        return appended_effects

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        oppo_active_character_aura = (
            game_state
            .get_player(source.pid.other())
            .just_get_active_character()
            .get_elemental_aura()
        )
        reaction = Reaction.consult_reaction_with_aura(oppo_active_character_aura, Element.ANEMO)
        summon_element: None | Element = None
        if reaction is not None:
            assert reaction.first_elem in stt._MIDARE_RANZAN_MAP
            summon_element = reaction.first_elem
        effects: tuple[eft.Effect, ...] = (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ANEMO,
                damage=3,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.UpdateSummonEffect(
                target_pid=source.pid,
                summon=sm.AutumnWhirlwindSummon(
                    usages=2,
                    curr_elem=Element.ANEMO,
                    ready_elem=summon_element,
                ),
            ),
        )
        if self.talent_equiped() \
                and reaction is not None \
                and reaction.first_elem in stt._POETICS_OF_FUUBUTSU_MAP:
            poetic_status = stt._POETICS_OF_FUUBUTSU_MAP[reaction.first_elem]
            effects += (
                eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=poetic_status,
                ),
            )
        return effects

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Kaeya(Character):
    # basic info
    _ELEMENT = Element.CRYO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.ColdBloodedStrikeStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.CRYO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.CRYO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.CRYO: 4,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=3,
                damage_type=DamageType(elemental_skill=True),
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=1,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.OverrideCombatStatusEffect(
                target_pid=source.pid,
                status=stt.IcicleStatus(),
            )
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Keqing(Character):
    # basic info
    _ELEMENT = Element.ELECTRO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.ThunderingPenanceStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.ELECTRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.ELECTRO: 4,
    })

    # consts
    BASE_ELECTRO_INFUSION_DURATION: int = 2

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=3,
                damage_type=DamageType(elemental_skill=True)
            )
        ]

        # check if can gain ElectroInfusionStatus
        can_infuse = False

        intrinsic_talent = self.get_hidden_statuses().just_find(stt.KeqingTalentStatus)
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
                eft.PublicRemoveAllCardEffect(
                    source.pid,
                    cd.LightningStiletto,
                )
            )
            can_infuse = True

        if can_infuse:
            if self.talent_equiped():
                effects.append(
                    eft.OverrideCharacterStatusEffect(
                        target=source,
                        status=stt.KeqingElectroInfusionStatus(
                            usages=self.BASE_ELECTRO_INFUSION_DURATION + 1,
                            damage_boost=1,
                        ),
                    )
                )
            else:
                effects.append(
                    eft.OverrideCharacterStatusEffect(
                        target=source,
                        status=stt.KeqingElectroInfusionStatus(
                            usages=self.BASE_ELECTRO_INFUSION_DURATION
                        ),
                    )
                )
        else:
            effects.append(
                eft.PublicAddCardEffect(
                    pid=source.pid,
                    card=cd.LightningStiletto,
                )
            )

        return tuple(effects)

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        assert self.get_energy() == self.get_max_energy()
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.PIERCING,
                damage=3,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=4,
                damage_type=DamageType(elemental_burst=True),
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Keqing:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            statuses=stts.Statuses(()),
            hiddens=stts.Statuses((
                stt.KeqingTalentStatus(can_infuse=False),
            )),
            equipments=stts.EquipmentStatuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Klee(Character):
    _ELEMENT = Element.PYRO
    _WEAPON_TYPE = WeaponType.CATALYST
    _TALENT_STATUS = stt.PoundingSurpriseStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.PYRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.PYRO: 3,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PYRO,
            damage=1,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=3,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.OverrideCharacterStatusEffect(
                target=source,
                status=stt.ExplosiveSparkStatus(usages=case_val(self.talent_equiped(), 2, 1)),
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=3,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid.other(),
                status=stt.SparksnSplashStatus,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Mona(Character):
    _ELEMENT = Element.HYDRO
    _WEAPON_TYPE = WeaponType.CATALYST
    _TALENT_STATUS = stt.ProphecyOfSubmersionStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.HYDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.HYDRO: 3,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.HYDRO,
            damage=1,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.HYDRO,
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.ReflectionSummon,
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.HYDRO,
                damage=4,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.IllusoryBubbleStatus,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            hiddens=stts.Statuses((
                stt.IllusoryTorrentStatus(),
            )),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Nahida(Character):
    _ELEMENT = Element.DENDRO
    _WEAPON_TYPE = WeaponType.CATALYST
    _TALENT_STATUS = stt.TheSeedOfStoredKnowledgeStatus
    _FACTIONS = frozenset((Faction.SUMERU,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.DENDRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.DENDRO: 3,
    })
    _ELEMENTAL_SKILL2_COST = AbstractDices({
        Element.DENDRO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.DENDRO: 3,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.DENDRO,
            damage=1,
        )

    def _elemental_skill_template(
            self,
            game_state: GameState,
            source: StaticTarget,
            dmg_amount: int,
            single_target: bool = False
    ) -> tuple[eft.Effect, ...]:
        oppo_pid = source.pid.other()
        oppo_active_character = game_state.get_player(oppo_pid).just_get_active_character()
        has_reaction = \
            oppo_active_character.get_elemental_aura().consult_reaction(self.ELEMENT()) is not None
        effects: list[eft.Effect] = [
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=self.ELEMENT(),
                damage=dmg_amount,
                damage_type=DamageType(elemental_skill=True),
            ),
        ]
        char_ids = (
            (oppo_active_character.get_id(),)
            if single_target
            else tuple(
                char.get_id()
                for char in game_state.get_player(
                    oppo_pid
                ).get_characters().get_character_in_activity_order()
            )
        )
        for id in char_ids:
            effects.append(eft.UpdateCharacterStatusEffect(
                target=StaticTarget(oppo_pid, Zone.CHARACTERS, id),
                status=stt.SeedOfSkandhaStatus(activated_usages=(
                    1
                    if (
                        id == oppo_active_character.get_id()
                        and has_reaction
                        and oppo_active_character.get_character_statuses().find(
                            stt.SeedOfSkandhaStatus
                        ) is None
                    )
                    else 0
                )),
            ))
        return tuple(effects)

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        oppo_active_character = game_state.get_player(
            source.pid.other()
        ).just_get_active_character()
        SKILL_DMG = 2
        return self._elemental_skill_template(
            game_state,
            source,
            dmg_amount=SKILL_DMG,
            single_target=stt.SeedOfSkandhaStatus not in oppo_active_character.get_character_statuses(),
        )

    def _elemental_skill2(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        SKILL_DMG = 3
        return self._elemental_skill_template(game_state, source, SKILL_DMG)

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [eft.EnergyDrainEffect(
            target=source,
            drain=self.get_max_energy(),
        )]
        if (
                self.talent_equiped()
                and any(
                    char.ELEMENT() is Element.ELECTRO
                    for char in game_state.get_player(source.pid).get_characters()
                )
        ):
            # talent card effect for electro
            for char in game_state.get_player(source.pid.other()).get_characters():
                original_status = char.get_character_statuses().find(stt.SeedOfSkandhaStatus)
                if original_status is not None:
                    assert isinstance(original_status, stt.SeedOfSkandhaStatus)
                    effects.append(eft.OverrideCharacterStatusEffect(
                        target=StaticTarget(source.pid.other(), Zone.CHARACTERS, char.get_id()),
                        status=replace(original_status, usages=original_status.usages + 1),
                    ))
        effects.append(eft.ReferredDamageEffect(
            source=source,
            target=DynamicCharacterTarget.OPPO_ACTIVE,
            element=self.ELEMENT(),
            damage=4,
            damage_type=DamageType(elemental_burst=True),
        ))
        if (
                self.talent_equiped()
                and any(
                    char.ELEMENT() is Element.HYDRO
                    for char in game_state.get_player(source.pid).get_characters()
                )
        ):
            # talent card effect for hydro
            effects.append(eft.UpdateCombatStatusEffect(
                target_pid=source.pid,
                status=stt.ShrineOfMayaStatus(usages=3),
            ))
        else:
            effects.append(eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.ShrineOfMayaStatus,
            ))
        return tuple(effects)

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Noelle(Character):
    _ELEMENT = Element.GEO
    _WEAPON_TYPE = WeaponType.CLAYMORE
    _TALENT_STATUS = stt.IGotYourBackStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.GEO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.GEO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.GEO: 4,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.FullPlateStatus,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=4,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.SweepingTimeStatus,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class RhodeiaOfLoch(Character):
    # basic info
    _ELEMENT = Element.HYDRO
    _WEAPON_TYPE = WeaponType.NONE
    _TALENT_STATUS = stt.StreamingSurgeStatus
    _FACTIONS = frozenset((Faction.MONSTER,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.HYDRO: 3,
    })
    _ELEMENTAL_SKILL2_COST = AbstractDices({
        Element.HYDRO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.HYDRO: 3,
    })

    # consts
    _SUMMONS = (
        sm.OceanicMimicSquirrelSummon,
        sm.OceanicMimicRaptorSummon,
        sm.OceanicMimicFrogSummon,
    )

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.HYDRO,
            damage=1,
        )

    def _not_summoned_types(
            self,
            game_state: GameState,
            pid: Pid
    ) -> tuple[type[sm.Summon], ...]:
        summons = game_state.get_player(pid).get_summons()
        return tuple(
            summon
            for summon in self._SUMMONS
            if summon not in summons
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        from random import choice
        summons_to_choose = self._not_summoned_types(game_state, source.pid)
        summon: type[sm.Summon]
        if summons_to_choose:
            summon = choice(summons_to_choose)
        else:  # if all kinds of summons have been summoned
            summon = choice(self._SUMMONS)
        return (
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=summon,
            ),
        )

    def _elemental_skill2(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        from random import choice

        # first choice
        summons_to_choose = self._not_summoned_types(game_state, source.pid)
        fst_summon: type[sm.Summon]

        if summons_to_choose:
            fst_summon = choice(summons_to_choose)
        else:  # if all kinds of summons have been summoned
            fst_summon = choice(self._SUMMONS)

        # second choice
        summons_to_choose = tuple(
            summon
            for summon in summons_to_choose
            if summon is not fst_summon
        )
        snd_summon: type[sm.Summon]

        if summons_to_choose:
            snd_summon = choice(summons_to_choose)
        else:  # if all kinds of summons have been summoned, choose a random that is not chosen
            snd_summon = choice([
                summon
                for summon in self._SUMMONS
                if summon is not fst_summon
            ])

        assert fst_summon is not snd_summon
        return (
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=fst_summon,
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=snd_summon,
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        summons = game_state.get_player(source.pid).get_summons()
        effects: list[eft.Effect] = [
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.HYDRO,
                damage=2 + 2 * len(summons),
                damage_type=DamageType(elemental_burst=True)
            ),
        ]

        if self.talent_equiped():
            effects.append(eft.AllSummonIncreaseUsage(target_pid=source.pid, d_usages=1))

        return tuple(effects)

    @classmethod
    def from_default(cls, id: int = -1) -> RhodeiaOfLoch:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Shenhe(Character):
    _ELEMENT = Element.CRYO
    _WEAPON_TYPE = WeaponType.POLEARM
    _TALENT_STATUS = stt.MysticalAbandonStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.CRYO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.CRYO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.CRYO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=2,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.IcyQuillStatus,
            )
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=1,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.TalismanSpiritSummon,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Tighnari(Character):
    _ELEMENT = Element.DENDRO
    _WEAPON_TYPE = WeaponType.BOW
    _TALENT_STATUS = stt.KeenSightStatus
    _FACTIONS = frozenset((Faction.SUMERU,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.DENDRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.DENDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.DENDRO: 3,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.DENDRO,
                damage=2,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.VijnanaSuffusionStatus,
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=2,
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.PIERCING,
                damage=1,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.DENDRO,
                damage=4,
                damage_type=DamageType(elemental_burst=True),
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Tighnari:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Venti(Character):
    _ELEMENT = Element.ANEMO
    _WEAPON_TYPE = WeaponType.BOW
    _TALENT_STATUS = stt.EmbraceOfWindsStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.ANEMO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.ANEMO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.ANEMO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ANEMO,
                damage=2,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.StormzoneStatus,
            )
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ANEMO,
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.StormEyeSummon,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Xingqiu(Character):
    _ELEMENT = Element.HYDRO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.TheScentRemainedStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.HYDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.HYDRO: 3,
    })

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.HYDRO,
                damage=2,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.ApplyElementalAuraEffect(
                target=source,
                element=Element.HYDRO,
            ),
            eft.UpdateCombatStatusEffect(
                target_pid=source.pid,
                status=stt.RainSwordStatus(usages=case_val(self.talent_equiped(), 3, 2))
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.HYDRO,
                damage=1,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.ApplyElementalAuraEffect(
                target=source,
                element=Element.HYDRO,
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.RainbowBladeworkStatus,
            ),
        )

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class YaeMiko(Character):
    _ELEMENT = Element.ELECTRO
    _WEAPON_TYPE = WeaponType.CATALYST
    _TALENT_STATUS = stt.TheShrinesSacredShadeStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _NORMAL_ATTACK_COST = AbstractDices({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _ELEMENTAL_SKILL1_COST = AbstractDices({
        Element.ELECTRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDices({
        Element.ELECTRO: 3,
    })

    # constants
    _SUMMON_TYPE = sm.SesshouSakura

    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.ELECTRO,
            damage=1,
        )

    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.SesshouSakura,
            ),
        )

    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.ELECTRO,
                damage=4,
                damage_type=DamageType(elemental_burst=True),
            ),
        ]
        if game_state.get_player(source.pid).get_summons().find(self._SUMMON_TYPE) is not None:
            if self.talent_equiped():
                effects.append(
                    eft.AddCharacterStatusEffect(
                        target=source,
                        status=stt.RiteOfDispatchStatus,
                    )
                )
            effects += (
                eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=stt.TenkoThunderboltsStatus,
                ),
                eft.RemoveSummonEffect(
                    target_pid=source.pid,
                    summon=self._SUMMON_TYPE,
                )
            )
        return tuple(effects)

    @classmethod
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=2,
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )
