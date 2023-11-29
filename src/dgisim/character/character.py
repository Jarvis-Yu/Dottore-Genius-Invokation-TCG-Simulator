"""
This file contains the base class Character for all characters,
and implementation of all characters. (in alphabetic order)
"""
from __future__ import annotations
from abc import abstractmethod
from dataclasses import replace
from functools import lru_cache
from itertools import chain
from typing import Callable, Optional, TYPE_CHECKING, Union, cast
from typing_extensions import override, Self

from ..effect import effect as eft
from ..status import status as stt
from ..status import statuses as stts
from ..summon import summon as sm

from ..dice import AbstractDice
from ..effect.effects_template import *
from ..effect.enums import Zone, DynamicCharacterTarget, TriggeringSignal
from ..effect.structs import StaticTarget, DamageType
from ..element import *
from ..helper.quality_of_life import case_val
from ..state.enums import Pid
from .enums import CharacterSkill, CharacterSkillType, Faction, WeaponType

if TYPE_CHECKING:
    from ..encoding.encoding_plan import EncodingPlan
    from ..state.game_state import GameState

__all__ = [
    # base
    "Character",

    # concretes
    "Albedo",
    "AratakiItto",
    "Bennett",
    "Collei",
    "Dehya",
    "ElectroHypostasis",
    "Fischl",
    "FatuiPyroAgent",
    "Ganyu",
    "HuTao",
    "JadeplumeTerrorshroom",
    "Jean",
    "KaedeharaKazuha",
    "Kaeya",
    "Keqing",
    "Klee",
    "MaguuKenki",
    "Mona",
    "Nahida",
    "Ningguang",
    "Noelle",
    "Qiqi",
    "RhodeiaOfLoch",
    "SangonomiyaKokomi",
    "Shenhe",
    "Tighnari",
    "Venti",
    "Xingqiu",
    "YaeMiko",
    "Yoimiya",
]


class Character:
    """
    The base class for all characters.
    """
    # element of the character
    _ELEMENT: Element = Element.ANY
    _WEAPON_TYPE: WeaponType
    # if the talent of this character is equitable, then assign the talent status here
    _TALENT_STATUS: None | type[stt.TalentEquipmentStatus]
    _FACTIONS: frozenset[Faction]

    _SKILL1_COST: None | AbstractDice = None
    _SKILL2_COST: None | AbstractDice = None
    _SKILL3_COST: None | AbstractDice = None
    _ELEMENTAL_BURST_COST: None | AbstractDice = None

    _SKILL1_ACTUAL_TYPE = CharacterSkillType.NORMAL_ATTACK
    _SKILL2_ACTUAL_TYPE = CharacterSkillType.ELEMENTAL_SKILL
    _SKILL3_ACTUAL_TYPE = CharacterSkillType.ELEMENTAL_SKILL
    _BURST_ACTUAL_TYPE = CharacterSkillType.ELEMENTAL_BURST

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
        """
        :param id: the unique identifier to distinguish from other characters of the same player.
        :param alive: used to indicate if the character is marked as defeated.
        :param hp: current hp.
        :param max_hp: maximum hp.
        :param energy: current energy.
        :param hiddens: hidden statuses.
        :param equipments: equipment statuses.
        :param statuses: character statuses.
        :param aura: elemental aura.

        :returns: a new instance of the character.
        """
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
        """
        :returns: the id as an unique identifier for a character of a player.

        Typically, when a player has n characters, each character is assigned
        an id from 1 to n from left to right.
        """
        return self._id

    def get_alive(self) -> bool:
        """
        :returns: the boolean value indicating if the character is actually defeated.
                  This is different from hp being 0.

        e.g. when Keqing's burst kills the next character and overloads to them,
        they can still be swapped out. But a character that has been defeated
        long ago cannot be overloaded out. In this case the just defeated characters
        are still marked as alive despite hp being 0, and `alive` turns `False` at
        a later time.
        """
        return self._alive

    def get_hp(self) -> int:
        """ :returns: the current hp.  """
        return self._hp

    def get_max_hp(self) -> int:
        """ :returns: the maximum hp.  """
        return self._max_hp

    def get_energy(self) -> int:
        """ :returns: the current energy. """
        return self._energy

    def get_max_energy(self) -> int:
        """ :returns: the maximum energy. """
        return self._max_energy

    def get_hidden_statuses(self) -> stts.Statuses:
        """
        :returns: the hidden statuses.

        Hidden statuses are the statues that belongs to the character but
        invisible in the game.

        e.g. Ganyu's talent deals more damage if Ganyu casted Frost Arrow before.
        So Ganyu needs a hidden status to record that information.
        """
        return self._hiddens

    def get_equipment_statuses(self) -> stts.EquipmentStatuses:
        """ :returns: the equipment statuses. """
        return self._equipments

    def get_character_statuses(self) -> stts.Statuses:
        """ :returns: the character statuses. """
        return self._statuses

    def get_elemental_aura(self) -> ElementalAura:
        """ :returns: the elemental aura. """
        return self._aura

    def get_all_statuses_ordered(self) -> list[stts.Statuses]:
        """
        :returns: a list of Statuses that are ordered so that those that should be
                  executed first has a lower index.
        """
        return [self._hiddens, self._equipments, self._statuses]

    def get_all_statuses_ordered_flattened(self) -> tuple[stt.Status, ...]:
        """
        :returns: a tuple of statuses that are ordered so that those that should be
                  executed first has a lower index.
        """
        return sum([statuses.get_statuses() for statuses in self.get_all_statuses_ordered()], ())

    def factory(self) -> CharacterFactory:
        """ :returns: a factory for the current character. """
        return CharacterFactory(self, type(self))

    def hp_lost(self) -> int:
        """ :returns: the lost hp. """
        return self._max_hp - self._hp

    @classmethod
    def FACTIONS(cls) -> frozenset[Faction]:
        """ :returns: the set of factions the character belongs to. """
        return cls._FACTIONS

    @classmethod
    def of_faction(cls, faction: Faction) -> bool:
        """ :returns: if this character belongs to the `faction`. """
        return faction in cls._FACTIONS

    @classmethod
    def ELEMENT(cls) -> Element:
        """ :returns: the element of the character. """
        return cls._ELEMENT

    @classmethod
    def WEAPON_TYPE(cls) -> WeaponType:
        """ :returns: the type of weapon the character wields. """
        return cls._WEAPON_TYPE

    @classmethod
    @abstractmethod
    def from_default(cls, id: int = -1) -> Character:
        """
        :returns: the default state of a character. Usually used to initialize a
                  new instance of the character.
        """
        pass

    @classmethod
    @lru_cache(maxsize=1)
    def skills(cls) -> tuple[CharacterSkill, ...]:
        """ :returns: the skill types the character supports """
        my_skills: list[CharacterSkill] = []
        if cls._normal_attack is not Character._normal_attack:
            my_skills.append(CharacterSkill.SKILL1)
        if cls._elemental_skill1 is not Character._elemental_skill1:
            my_skills.append(CharacterSkill.SKILL2)
        if cls._elemental_skill2 is not Character._elemental_skill2:
            my_skills.append(CharacterSkill.SKILL3)
        if cls._elemental_burst is not Character._elemental_burst:
            my_skills.append(CharacterSkill.ELEMENTAL_BURST)
        return tuple(my_skills)

    @classmethod
    def skill_actual_type(cls, skill: CharacterSkill) -> CharacterSkillType:
        """
        :returns: the type of skill the character's `skill` is.
                  e.g. Ganyu's Frost Arrow (SKILL3) is of type Normal Attack.
        """
        if skill is CharacterSkill.SKILL1:
            return cls._SKILL1_ACTUAL_TYPE
        elif skill is CharacterSkill.SKILL2:
            return cls._SKILL2_ACTUAL_TYPE
        elif skill is CharacterSkill.SKILL3:
            return cls._SKILL3_ACTUAL_TYPE
        elif skill is CharacterSkill.ELEMENTAL_BURST:
            return cls._BURST_ACTUAL_TYPE
        raise NotImplementedError(f"{skill} type for {cls.__name__} not defined")

    @classmethod
    def skill_cost(cls, skill_type: CharacterSkill) -> AbstractDice:
        """
        :returns: the basic dice cost of `skill_type`.
        """
        if skill_type is CharacterSkill.SKILL1 and cls._SKILL1_COST is not None:
            return cls._SKILL1_COST
        elif skill_type is CharacterSkill.SKILL2 and cls._SKILL2_COST is not None:
            return cls._SKILL2_COST
        elif skill_type is CharacterSkill.SKILL3 and cls._SKILL3_COST is not None:
            return cls._SKILL3_COST
        elif skill_type is CharacterSkill.ELEMENTAL_BURST and cls._ELEMENTAL_BURST_COST is not None:
            return cls._ELEMENTAL_BURST_COST
        raise NotImplementedError(f"{skill_type} cost for {cls.__name__} not defined")

    def skill_energy_cost(self, skill_type: CharacterSkill) -> int:
        """
        :returns: the basic energy cost of `skill_type`.
        """
        if skill_type is CharacterSkill.ELEMENTAL_BURST:
            return self._max_energy
        return 0

    def skill(self, game_state: GameState, source: StaticTarget, skill_type: CharacterSkill) -> tuple[eft.Effect, ...]:
        """
        :param game_state: current game state when the skill is casted.
        :param source: location information of this character.
        :param skill_type: the skill that is to be casted.

        :returns: the effects of the skill in the context.

        This should only be called to get effects right before the skill is to be executed.
        Otherwise faulty effects may be generated.
        """
        return (
            eft.BroadcastPreSkillInfoEffect(
                source=source,
                skill=skill_type,
            ),
        ) + self._post_skill(
            game_state,
            source,
            skill_type,
            self._skill(game_state, source, skill_type),
        )

    def _skill(self, game_state: GameState, source: StaticTarget, skill_type: CharacterSkill) -> tuple[eft.Effect, ...]:
        if skill_type is CharacterSkill.SKILL1:
            return self.normal_attack(game_state, source)
        elif skill_type is CharacterSkill.SKILL2:
            return self.elemental_skill1(game_state, source)
        elif skill_type is CharacterSkill.SKILL3:
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
            eft.BroadcastPostSkillInfoEffect(
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
            eft.DefeatedMarkCheckerEffect(),
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

    def talent_equipped(self) -> bool:
        """ :returns: if the talent is equipped. """
        talent_status = self._talent_status()
        if talent_status is None:
            return False
        return self.get_equipment_statuses().contains(talent_status)

    def alive(self) -> bool:
        """ Same as `.get_alive()`. """
        return self._alive

    def defeated(self) -> bool:
        """ Negation of `.alive()`. """
        return not self._alive

    def satiated(self) -> bool:
        """ :returns: if character is satiated. """
        from ..status.status import SatiatedStatus
        return self._statuses.contains(SatiatedStatus)

    def can_cast_skill(self) -> bool:
        """
        :returns: if skills can be casted.

        A character cannot cast skill when it is frozen, petrified or defeated.
        """
        from ..status.status import FrozenStatus
        return not self._statuses.contains(FrozenStatus) and not self.defeated()

    def name(self) -> str:
        """ :returns: name of the character (without breaks). """
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

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this character.
        """
        basics = [
            encoding_plan.code_for(self),
            self._ELEMENT.value,
            self._WEAPON_TYPE.value,
            self._id,
            1 if self._alive else 0,
            self._hp,
            self._max_hp,
            self._energy,
            self._max_energy,
        ]
        return list(chain(
            basics,
            self._aura.encoding(),
            self._hiddens.encoding(encoding_plan, encoding_plan.CHAR_HIDDEN_FIXED_LEN),
            self._equipments.encoding(encoding_plan),
            self._statuses.encoding(encoding_plan, encoding_plan.CHAR_STT_FIXED_LEN),
        ))

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


class Albedo(Character):
    _ELEMENT = Element.GEO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.DescentOfDivinityStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _SKILL1_COST = AbstractDice({
        Element.GEO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.GEO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.SolarIsotomaSummon,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        final_dmg = 4
        if sm.SolarIsotomaSummon in game_state.get_player(source.pid).get_summons():
            final_dmg += 2
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=final_dmg,
                damage_type=DamageType(elemental_burst=True)
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


class AratakiItto(Character):
    _ELEMENT = Element.GEO
    _WEAPON_TYPE = WeaponType.CLAYMORE
    _TALENT_STATUS = stt.AratakiIchibanStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _SKILL1_COST = AbstractDice({
        Element.GEO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.GEO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
                damage=4,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.RagingOniKingStatus,
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

    _SKILL1_COST = AbstractDice({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.PYRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
        talent_equiped = self.talent_equipped()
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


class Collei(Character):
    _ELEMENT = Element.DENDRO
    _WEAPON_TYPE = WeaponType.BOW
    _TALENT_STATUS = stt.FloralSidewinderStatus
    _FACTIONS = frozenset((Faction.SUMERU,))

    _SKILL1_COST = AbstractDice({
        Element.DENDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.DENDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.DENDRO: 3,
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
        talent_status: None | stt.ColleiTalentStatus = None
        trigger_sprout: bool = False
        if self.talent_equipped():
            talent_status = cast(
                stt.ColleiTalentStatus,
                self.get_hidden_statuses().find(stt.ColleiTalentStatus)
            )
            assert talent_status is not None
            if not talent_status.elemental_skill_used:
                oppo_active = game_state.get_player(source.pid.other()).just_get_active_character()
                trigger_sprout = \
                    oppo_active.get_elemental_aura().consult_reaction(Element.DENDRO) is not None
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.DENDRO,
                damage=3,
                damage_type=DamageType(elemental_skill=True),
            ),
        ) + (
            (
                eft.UpdateCombatStatusEffect(
                    target_pid=source.pid,
                    status=stt.SproutStatus(activated=trigger_sprout)
                ),
            )
            if talent_status is not None and not talent_status.elemental_skill_used
            else ()
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
                element=Element.DENDRO,
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.CuileinAnbarSummon,
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
            hiddens=stts.Statuses((stt.ColleiTalentStatus(),)),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Dehya(Character):
    _ELEMENT = Element.PYRO
    _WEAPON_TYPE = WeaponType.CLAYMORE
    _TALENT_STATUS = stt.StalwartAndTrueStatus
    _FACTIONS = frozenset((Faction.SUMERU,))

    _SKILL1_COST = AbstractDice({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.PYRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.PYRO: 4,
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
        effects: list[eft.Effect] = []
        summons = game_state.get_player(source.pid).get_summons()
        if sm.FierySanctumFieldSummon in summons:
            effects.append(eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ))
        effects.append(eft.AddSummonEffect(
            target_pid=source.pid,
            summon=sm.FierySanctumFieldSummon,
        ))
        return tuple(effects)

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
                element=Element.PYRO,
                damage=3,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.IncinerationDriveStatus,
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


class ElectroHypostasis(Character):
    _ELEMENT = Element.ELECTRO
    _WEAPON_TYPE = WeaponType.NONE
    _TALENT_STATUS = None
    _FACTIONS = frozenset((Faction.MONSTER,))

    _SKILL1_COST = AbstractDice({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ELECTRO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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


class FatuiPyroAgent(Character):
    _ELEMENT = Element.PYRO
    _WEAPON_TYPE = WeaponType.NONE
    _TALENT_STATUS = stt.PaidInFullStatus
    _FACTIONS = frozenset((Faction.FATUI,))

    _SKILL1_COST = AbstractDice({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.PYRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.PYRO: 3,
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
                element=Element.PYRO,
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.UpdateCharacterStatusEffect(
                target=source,
                status=stt.StealthStatus(usages=3 if self.talent_equipped() else 2),
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
                element=Element.PYRO,
                damage=5,
                damage_type=DamageType(elemental_burst=True),
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
            hiddens=stts.Statuses((stt.StealthMasterStatus(),)),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Fischl(Character):
    _ELEMENT = Element.ELECTRO
    _WEAPON_TYPE = WeaponType.BOW
    _TALENT_STATUS = stt.StellarPredatorStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _SKILL1_COST = AbstractDice({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ELECTRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.ELECTRO: 3,
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
                element=Element.ELECTRO,
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.OzSummon,
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
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.PIERCING,
                damage=2,
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
    def from_default(cls, id: int = -1) -> Self:
        return cls(
            id=id,
            alive=True,
            hp=10,
            max_hp=10,
            energy=0,
            max_energy=3,
            statuses=stts.Statuses(()),
            hiddens=stts.Statuses(()),
            equipments=stts.EquipmentStatuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Ganyu(Character):
    _ELEMENT = Element.CRYO
    _WEAPON_TYPE = WeaponType.BOW
    _TALENT_STATUS = stt.UndividedHeartStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _SKILL1_COST = AbstractDice({
        Element.CRYO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.CRYO: 3,
    })
    _SKILL3_COST = AbstractDice({
        Element.CRYO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.CRYO: 3,
    })

    _SKILL3_ACTUAL_TYPE = CharacterSkillType.NORMAL_ATTACK

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
                damage=1,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.IceLotusStatus,
            ),
        )

    @override
    def _elemental_skill2(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        piercing_dmg = 2
        if self.talent_equipped():
            talent_status = self.get_hidden_statuses().find(stt.GanyuTalentStatus)
            assert isinstance(talent_status, stt.GanyuTalentStatus)
            if talent_status.elemental_skill2ed:
                piercing_dmg = 3

        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.PIERCING,
                damage=piercing_dmg,
                damage_type=DamageType(elemental_skill=True),
            ),
        ) + normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.CRYO,
            damage=2,
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
                target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                element=Element.PIERCING,
                damage=1,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.SacredCryoPearlSummon,
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
            max_energy=3,
            hiddens=stts.Statuses((stt.GanyuTalentStatus(),)),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class HuTao(Character):
    _ELEMENT = Element.PYRO
    _WEAPON_TYPE = WeaponType.POLEARM
    _TALENT_STATUS = stt.SanguineRougeStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _SKILL1_COST = AbstractDice({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.PYRO: 2,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.PYRO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = []
        if stt.ParamitaPapilioStatus in self.get_character_statuses():
            charged_status = game_state.get_player(
                source.pid
            ).get_hidden_statuses().just_find(stt.ChargedAttackStatus)
            if charged_status.can_charge:
                effects.append(eft.AddCharacterStatusEffect(
                    target=StaticTarget.from_player_active(game_state, source.pid.other()),
                    status=stt.BloodBlossomStatus,
                ))
        return tuple(effects) + normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.PHYSICAL,
            damage=2,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.ParamitaPapilioStatus,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        dmg = 4
        heal = 2
        if self.get_hp() <= 6:
            dmg += 1
            heal += 1
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=dmg,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.RecoverHPEffect(
                target=source,
                recovery=heal,
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


class JadeplumeTerrorshroom(Character):
    _ELEMENT = Element.DENDRO
    _WEAPON_TYPE = WeaponType.NONE
    _TALENT_STATUS = stt.ProliferatingSporesStatus
    _FACTIONS = frozenset((Faction.MONSTER,))

    _SKILL1_COST = AbstractDice({
        Element.DENDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.DENDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.DENDRO: 3,
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
                element=Element.DENDRO,
                damage=3,
                damage_type=DamageType(elemental_skill=True),
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
                element=Element.DENDRO,
                damage=4,
                damage_type=DamageType(elemental_burst=True),
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
            hiddens=stts.Statuses((stt.RadicalVitalityHiddenStatus(),)),
            equipments=stts.EquipmentStatuses(()),
            statuses=stts.Statuses(()),
            elemental_aura=ElementalAura.from_default(),
        )


class Jean(Character):
    _ELEMENT = Element.ANEMO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.LandsOfDandelionStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _SKILL1_COST = AbstractDice({
        Element.ANEMO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ANEMO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.ANEMO: 4,
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
                damage=3,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.ForwardSwapCharacterEffect(
                target_player=source.pid.other(),
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
        ]
        self_characters = game_state.get_player(source.pid).get_characters()
        for character in self_characters.get_alive_character_in_activity_order():
            effects.append(eft.RecoverHPEffect(
                target=StaticTarget.from_char_id(source.pid, character.get_id()),
                recovery=2,
            ))
        effects.append(
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.DandelionFieldSummon,
            ),
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


class KaedeharaKazuha(Character):
    _ELEMENT = Element.ANEMO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.PoeticsOfFuubutsuStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _SKILL1_COST = AbstractDice({
        Element.ANEMO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ANEMO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
        if self.talent_equipped() \
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
        if skill_type is CharacterSkill.SKILL2:
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
        if self.talent_equipped() \
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

    _SKILL1_COST = AbstractDice({
        Element.CRYO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.CRYO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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

    _SKILL1_COST = AbstractDice({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ELECTRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
        from ..card.card import LightningStiletto
        if not can_infuse and cards.contains(LightningStiletto):
            effects.append(
                eft.PublicRemoveAllCardEffect(
                    source.pid,
                    LightningStiletto,
                )
            )
            can_infuse = True

        if can_infuse:
            if self.talent_equipped():
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
                    card=LightningStiletto,
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
    def from_default(cls, id: int = -1) -> Self:
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

    _SKILL1_COST = AbstractDice({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.PYRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
                status=stt.ExplosiveSparkStatus(usages=case_val(self.talent_equipped(), 2, 1)),
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


class MaguuKenki(Character):
    _ELEMENT = Element.ANEMO
    _WEAPON_TYPE = WeaponType.NONE
    _TALENT_STATUS = stt.TranscendentAutomatonStatus
    _FACTIONS = frozenset((Faction.MONSTER,))

    _SKILL1_COST = AbstractDice({
        Element.ANEMO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ANEMO: 3,
    })
    _SKILL3_COST = AbstractDice({
        Element.CRYO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.ShadowswordLoneGaleSummon,
            ),
        ) + (
            (
                eft.ForwardSwapCharacterEffect(
                    target_player=source.pid,
                ),
            )
            if self.talent_equipped()
            else ()
        )

    @override
    def _elemental_skill2(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.ShadowswordGallopingFrostSummon,
            ),
        ) + (
            (
                eft.BackwardSwapCharacterEffect(
                    target_player=source.pid,
                ),
            )
            if self.talent_equipped()
            else ()
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
                damage=4,
                damage_type=DamageType(elemental_burst=True),
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

    _SKILL1_COST = AbstractDice({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.HYDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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

    _SKILL1_COST = AbstractDice({
        Element.DENDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.DENDRO: 3,
    })
    _SKILL3_COST = AbstractDice({
        Element.DENDRO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
                self.talent_equipped()
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
                self.talent_equipped()
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


class Ningguang(Character):
    _ELEMENT = Element.GEO
    _WEAPON_TYPE = WeaponType.CATALYST
    _TALENT_STATUS = stt.StrategicReserveStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _SKILL1_COST = AbstractDice({
        Element.GEO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.GEO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.GEO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.GEO,
            damage=1,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=2,
                damage_type=DamageType(elemental_skill=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.JadeScreenStatus,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        final_dmg = 6
        if stt.JadeScreenStatus in game_state.get_player(source.pid).get_combat_statuses():
            final_dmg += 2
        return (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.GEO,
                damage=final_dmg,
                damage_type=DamageType(elemental_burst=True),
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


class Noelle(Character):
    _ELEMENT = Element.GEO
    _WEAPON_TYPE = WeaponType.CLAYMORE
    _TALENT_STATUS = stt.IGotYourBackStatus
    _FACTIONS = frozenset((Faction.MONDSTADT,))

    _SKILL1_COST = AbstractDice({
        Element.GEO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.GEO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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


class Qiqi(Character):
    _ELEMENT = Element.CRYO
    _WEAPON_TYPE = WeaponType.SWORD
    _TALENT_STATUS = stt.RiteOfResurrectionStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _SKILL1_COST = AbstractDice({
        Element.CRYO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.CRYO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.HeraldOfFrostSummon,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: tuple[eft.Effect, ...] = ()
        if self.talent_equipped():
            hidden_status = self.get_hidden_statuses().just_find(stt.QiqiTalentStatus)
            if hidden_status.revivable():
                self_chars = game_state.get_player(
                    source.pid
                ).get_characters().get_character_in_activity_order()
                defeated_chars = [
                    char
                    for char in self_chars
                    if char.defeated()
                ]
                if defeated_chars:
                    effects = (
                        eft.UpdateCharacterStatusEffect(
                            target=source,
                            status=replace(
                                hidden_status,
                                revival_count=hidden_status.revival_count + 1
                            )
                        ),
                    ) + tuple(
                        eft.ReviveRecoverHPEffect(
                            target=StaticTarget.from_char_id(source.pid, char.get_id()),
                            recovery=2,
                        )
                        for char in defeated_chars
                    )
        return effects + (
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.CRYO,
                damage=3,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.FortunePreservingTalismanStatus,
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
            hiddens=stts.Statuses((stt.QiqiTalentStatus(),)),
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

    _SKILL1_COST = AbstractDice({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.HYDRO: 3,
    })
    _SKILL3_COST = AbstractDice({
        Element.HYDRO: 5,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
                damage=4 + 1 * len(summons),
                damage_type=DamageType(elemental_burst=True)
            ),
        ]

        if self.talent_equipped():
            effects.append(eft.AllSummonIncreaseUsageEffect(target_pid=source.pid, d_usages=1))

        return tuple(effects)

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


class SangonomiyaKokomi(Character):
    _ELEMENT = Element.HYDRO
    _WEAPON_TYPE = WeaponType.CATALYST
    _TALENT_STATUS = stt.TamakushiCasketStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _SKILL1_COST = AbstractDice({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.HYDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.HYDRO: 3,
    })

    @override
    def _normal_attack(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return normal_attack_template(
            game_state=game_state,
            source=source,
            element=Element.HYDRO,
            damage=1,
        )

    @override
    def _elemental_skill1(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        return (
            eft.ApplyElementalAuraEffect(
                source=source,
                target=source,
                element=Element.HYDRO,
                source_type=DamageType(elemental_skill=True),
            ),
            eft.AddSummonEffect(
                target_pid=source.pid,
                summon=sm.BakeKurageSummon,
            ),
        )

    @override
    def _elemental_burst(self, game_state: GameState, source: StaticTarget) -> tuple[eft.Effect, ...]:
        effects: list[eft.Effect] = [
            eft.EnergyDrainEffect(
                target=source,
                drain=self.get_max_energy(),
            ),
            eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.HYDRO,
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
        ]
        self_characters = game_state.get_player(source.pid).get_characters()
        for character in self_characters.get_alive_character_in_activity_order():
            effects.append(eft.RecoverHPEffect(
                target=StaticTarget.from_char_id(source.pid, character.get_id()),
                recovery=1,
            ))
        effects.append(
            eft.AddCharacterStatusEffect(
                target=source,
                status=stt.CeremonialGarmentStatus,
            ),
        )
        if self.talent_equipped():
            usages = 1
            summon = game_state.get_player(source.pid).get_summons().find(sm.BakeKurageSummon)
            if summon is not None:
                usages = summon.usages + 1
            effects.append(
                eft.OverrideSummonEffect(
                    target_pid=source.pid,
                    summon=sm.BakeKurageSummon(usages=usages),
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


class Shenhe(Character):
    _ELEMENT = Element.CRYO
    _WEAPON_TYPE = WeaponType.POLEARM
    _TALENT_STATUS = stt.MysticalAbandonStatus
    _FACTIONS = frozenset((Faction.LIYUE,))

    _SKILL1_COST = AbstractDice({
        Element.CRYO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.CRYO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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

    _SKILL1_COST = AbstractDice({
        Element.DENDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.DENDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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

    _SKILL1_COST = AbstractDice({
        Element.ANEMO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ANEMO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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

    _SKILL1_COST = AbstractDice({
        Element.HYDRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.HYDRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
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
                source=source,
                target=source,
                element=Element.HYDRO,
                source_type=DamageType(elemental_skill=True),
            ),
            eft.UpdateCombatStatusEffect(
                target_pid=source.pid,
                status=stt.RainSwordStatus(usages=case_val(self.talent_equipped(), 3, 2))
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
                damage=2,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.ApplyElementalAuraEffect(
                source=source,
                target=source,
                element=Element.HYDRO,
                source_type=DamageType(elemental_burst=True),
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

    _SKILL1_COST = AbstractDice({
        Element.ELECTRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.ELECTRO: 3,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.ELECTRO: 3,
    })

    # constants
    _SUMMON_TYPE = sm.SesshouSakuraSummon

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
                summon=sm.SesshouSakuraSummon,
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
            if self.talent_equipped():
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


class Yoimiya(Character):
    _ELEMENT = Element.PYRO
    _WEAPON_TYPE = WeaponType.BOW
    _TALENT_STATUS = stt.NaganoharaMeteorSwarmStatus
    _FACTIONS = frozenset((Faction.INAZUMA,))

    _SKILL1_COST = AbstractDice({
        Element.PYRO: 1,
        Element.ANY: 2,
    })
    _SKILL2_COST = AbstractDice({
        Element.PYRO: 1,
    })
    _ELEMENTAL_BURST_COST = AbstractDice({
        Element.PYRO: 3,
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
        if self.talent_equipped():
            return (
                eft.UpdateCharacterStatusEffect(
                    target=source,
                    status=stt.NiwabiEnshouStatus(usages=3),
                ),
            )
        else:
            return (
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=stt.NiwabiEnshouStatus,
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
                element=Element.PYRO,
                damage=3,
                damage_type=DamageType(elemental_burst=True),
            ),
            eft.AddCombatStatusEffect(
                target_pid=source.pid,
                status=stt.AurousBlazeStatus,
            ),
        )

    @override
    def _post_elemental_skill1(
            self,
            game_state: GameState,
            source: StaticTarget,
            effects: tuple[eft.Effect, ...]
    ) -> tuple[eft.Effect, ...]:
        """ Removes energy recharge effect """
        return effects + (
            eft.AliveMarkCheckerEffect(),
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
