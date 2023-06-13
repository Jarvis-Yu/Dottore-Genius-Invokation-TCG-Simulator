from __future__ import annotations
from typing import FrozenSet, Optional, cast, Union, ClassVar, Iterable, Callable
from enum import Enum
from dataclasses import InitVar, dataclass, asdict, replace, field
from itertools import chain

import dgisim.src.status.statuses as stts
import dgisim.src.status.status as stt
import dgisim.src.summon.summon as sm
from dgisim.src.element.element import Element, Reaction, ReactionDetail
import dgisim.src.character.character as chr
import dgisim.src.state.game_state as gs
import dgisim.src.state.player_state as ps
import dgisim.src.card.card as cd
import dgisim.src.dices as ds
from dgisim.src.helper.quality_of_life import just


class Zone(Enum):
    CHARACTER = 0
    SUMMONS = 1
    SUPPORT = 2
    COMBAT_STATUSES = 3
    # HAND = 4


class TriggeringSignal(Enum):
    FAST_ACTION = 0
    COMBAT_ACTION = 1
    DEATH_EVENT = 2
    SWAP_EVENT = 3
    ROUND_START = 4
    END_ROUND_CHECK_OUT = 5  # summons etc.
    ROUND_END = 6  # remove frozen etc.


class DynamicCharacterTarget(Enum):
    SELF_SELF = 0
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6


# TODO: postpone this until further tests are done
#       needs to investigate how Klee's burst and Mona's or Sucrose's Talent co-work
@dataclass(frozen=True, kw_only=True)
class DamageType:
    normal_attack: bool = False
    charged_attack: bool = False
    plunge_attack: bool = False
    elemental_skill: bool = False
    elemental_burst: bool = False
    summon: bool = False


@dataclass(frozen=True)
class StaticTarget:
    pid: gs.GameState.Pid
    zone: Zone
    id: int


@dataclass(frozen=True)
class Effect:
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        raise Exception("Not Overriden or Implemented")

    def name(self) -> str:
        return self.__class__.__name__

    def dict_str(self) -> Union[dict, str]:
        return asdict(self)

    def __str__(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class TriggerrbleEffect(Effect):
    pass


@dataclass(frozen=True)
class DirectEffect(Effect):
    pass


@dataclass(frozen=True)
class CheckerEffect(Effect):
    pass


@dataclass(frozen=True)
class PhaseEffect(Effect):
    pass


@dataclass(frozen=True)
class TriggerStatusEffect(Effect):
    target: StaticTarget
    status: type[Union[stt.CharacterTalentStatus, stt.EquipmentStatus, stt.CharacterStatus]]
    signal: TriggeringSignal

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
        character = cast(chr.Character, character)
        effects: Iterable[Effect] = []

        statuses: stts.Statuses
        if issubclass(self.status, stt.CharacterTalentStatus):
            statuses = character.get_talent_statuses()
        elif issubclass(self.status, stt.EquipmentStatus):
            statuses = character.get_equipment_statuses()
        elif issubclass(self.status, stt.CharacterStatus):
            statuses = character.get_character_statuses()
        else:
            raise Exception("Unexpected Status Type to Trigger", self.status)
        status = statuses.find(self.status)
        if status is None:
            return game_state
        effects = status.react_to_signal(self.target, self.signal)
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TriggerCombatStatusEffect(Effect):
    target_pid: gs.GameState.Pid  # the player the status belongs to
    status: type[stt.CombatStatus]
    signal: TriggeringSignal

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        effects: Iterable[Effect] = []
        statuses = game_state.get_player(self.target_pid).get_combat_statuses()
        status = statuses.find(self.status)
        if status is None:
            return game_state
        effects = status.react_to_signal(
            StaticTarget(
                pid=self.target_pid,
                zone=Zone.COMBAT_STATUSES,
                id=-1,
            ),
            self.signal,
        )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TriggerSummonEffect(Effect):
    target_pid: gs.GameState.Pid
    summon: type[sm.Summon]
    signal: TriggeringSignal

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        effects: Iterable[Effect] = []
        summons = game_state.get_player(self.target_pid).get_summons()
        summon = summons.find(self.summon)
        if summon is None:
            return game_state
        effects = summon.react_to_signal(
            StaticTarget(
                pid=self.target_pid,
                zone=Zone.SUMMONS,
                id=-1,
            ),
            self.signal,
        )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


def _loopAllStatuses(
        game_state: gs.GameState,
        pid: gs.GameState.Pid,
        f: Callable[[gs.GameState, stt.Status, StaticTarget], gs.GameState]
) -> gs.GameState:
    """
    Perform f on all statuses of player pid in order
    f(game_state, status, status_source) -> game_state
    """
    player = game_state.get_player(pid)

    # characters first
    characters = player.get_characters()
    ordered_characters = characters.get_character_in_activity_order()
    for character in ordered_characters:
        # get character's private statuses and add triggerStatusEffect to global effect_stack
        statuses = character.get_all_statuses_ordered_flattened()
        character_id = character.get_id()
        target = StaticTarget(
            pid,
            Zone.CHARACTER,
            character_id
        )
        for status in statuses:
            game_state = f(game_state, status, target)

    # combat status
    combat_statuses = player.get_combat_statuses()
    target = StaticTarget(
        pid,
        Zone.COMBAT_STATUSES,
        -1,  # not used
    )
    for status in combat_statuses:
        game_state = f(game_state, status, target)

    # summons
    summons = player.get_summons()
    target = StaticTarget(
        pid,
        Zone.SUMMONS,
        -1
    )
    for summon in summons:
        game_state = f(game_state, summon, target)

    # supports TODO

    return game_state


def _triggerAllStatusesEffects(
        game_state: gs.GameState, pid: gs.GameState.Pid, signal: TriggeringSignal
) -> list[Effect]:
    """
    Takes the current game_state, trigger all statuses in order of player pid
    Returns the triggering effects in order (first to last)
    """
    effects: list[Effect] = []

    def f(game_state: gs.GameState, status: stt.Status, target: StaticTarget) -> gs.GameState:
        nonlocal effects
        if isinstance(status, stt.CharacterTalentStatus) \
                or isinstance(status, stt.EquipmentStatus) \
                or isinstance(status, stt.CharacterStatus):
            effects.append(TriggerStatusEffect(target, type(status), signal))

        elif isinstance(status, stt.CombatStatus):
            effects.append(TriggerCombatStatusEffect(target.pid, type(status), signal))

        elif isinstance(status, sm.Summon):
            effects.append(TriggerSummonEffect(target.pid, type(status), signal))

        return game_state

    _loopAllStatuses(game_state, pid, f)
    return effects


def _preprocessByAllStatuses(
        game_state: gs.GameState,
        pid: gs.GameState.Pid,
        item: Preprocessable,
        pp_type: stt.Status.PPType,
) -> tuple[gs.GameState, Preprocessable]:
    def f(game_state: gs.GameState, status: stt.Status, status_source: StaticTarget) -> gs.GameState:
        nonlocal item
        item, new_status = status.preprocess(game_state, status_source, item, pp_type)

        if isinstance(status, stt.CharacterTalentStatus) \
                or isinstance(status, stt.EquipmentStatus) \
                or isinstance(status, stt.CharacterStatus):
            if new_status is None:
                game_state = RemoveCharacterStatusEffect(
                    status_source, type(status)).execute(game_state)
            elif new_status != status:
                assert type(status) == type(new_status)
                game_state = OverrideCharacterStatusEffect(
                    status_source,
                    new_status,  # type: ignore
                ).execute(game_state)

        elif isinstance(status, stt.CombatStatus):
            if new_status is None:
                game_state = RemoveCombatStatusEffect(
                    status_source.pid,
                    type(status),
                ).execute(game_state)
            elif new_status != status:
                assert type(status) == type(new_status)
                game_state = OverrideCombatStatusEffect(
                    status_source.pid,
                    new_status,  # type: ignore
                ).execute(game_state)

        elif isinstance(status, sm.Summon):
            summon = status
            new_summon = new_status
            pid = status_source.pid
            if new_summon is None:
                game_state = RemoveSummonEffect(
                    pid,
                    type(summon),
                ).execute(game_state)
            elif new_summon != summon:
                assert type(summon) == type(new_summon)
                game_state = OverrideSummonEffect(
                    pid,
                    new_summon,  # type: ignore
                ).execute(game_state)

        return game_state

    game_state = _loopAllStatuses(game_state, pid, f)
    return game_state, item


@dataclass(frozen=True)
class AllStatusTriggererEffect(TriggerrbleEffect):
    """
    This effect triggers the characters' statuses with the provided signal in order.
    """
    pid: gs.GameState.Pid
    signal: TriggeringSignal

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        effects = _triggerAllStatusesEffects(game_state, self.pid, self.signal)
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class SwapCharacterCheckerEffect(CheckerEffect):
    pass


@dataclass(frozen=True)
class DeathCheckCheckerEffect(CheckerEffect):
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        p1_character = game_state.get_player1().get_characters().get_active_character()
        p2_character = game_state.get_player2().get_characters().get_active_character()
        assert p1_character is not None and p2_character is not None
        pid: gs.GameState.Pid
        if p1_character.defeated():
            pid = gs.GameState.Pid.P1
        elif p2_character.defeated():
            pid = gs.GameState.Pid.P2
        else:  # if no one defeated, continue
            return game_state
        death_swap_player = game_state.get_player(pid)
        waiting_player = game_state.get_other_player(pid)
        # TODO: check if game ends
        if death_swap_player.defeated():
            raise Exception("Not reached, should be caught by DefeatedCheckerEffect")
        effects: list[Effect] = []
        # TODO: trigger other death based effects
        effects.append(DeathSwapPhaseStartEffect())
        effects.append(DeathSwapPhaseEndEffect(
            pid,
            death_swap_player.get_phase(),
            waiting_player.get_phase(),
        ))
        return game_state.factory().effect_stack(
            game_state.get_effect_stack().push_many_fl(tuple(effects))
        ).player(
            pid,
            game_state.get_player(pid).factory().phase(
                ps.PlayerState.Act.ACTION_PHASE
            ).build()
        ).other_player(
            pid,
            game_state.get_other_player(pid).factory().phase(
                ps.PlayerState.Act.PASSIVE_WAIT_PHASE
            ).build()
        ).build()


@dataclass(frozen=True)
class DefeatedCheckerEffect(CheckerEffect):
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        if game_state.get_player1().defeated() \
                or game_state.get_player2().defeated():
            return game_state.factory().phase(game_state.get_mode().game_end_phase()).build()
        return game_state


@dataclass(frozen=True)
class DeathSwapPhaseStartEffect(PhaseEffect):
    pass


@dataclass(frozen=True)
class DeathSwapPhaseEndEffect(PhaseEffect):
    my_pid: gs.GameState.Pid
    my_last_phase: ps.PlayerState.Act
    other_last_phase: ps.PlayerState.Act

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        player = game_state.get_player(self.my_pid)
        other_player = game_state.get_other_player(self.my_pid)
        player = player.factory().phase(self.my_last_phase).build()
        other_player = other_player.factory().phase(self.other_last_phase).build()
        return game_state.factory().player(
            self.my_pid,
            player
        ).other_player(
            self.my_pid,
            other_player
        ).build()


@dataclass(frozen=True)
class EndPhaseCheckoutEffect(PhaseEffect):
    """
    This is responsible for triggering character statuses/summons/supports by the
    end of the round.
    """

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        active_id = game_state.get_active_player_id()
        # active_player = game_state.get_player(active_id)
        effects = [
            AllStatusTriggererEffect(
                active_id,
                TriggeringSignal.END_ROUND_CHECK_OUT
            ),
            # TODO: add active_player's team status, summons status... here
            AllStatusTriggererEffect(
                active_id.other(),
                TriggeringSignal.END_ROUND_CHECK_OUT
            ),
            # TODO: add active_player's team status, summons status... here
        ]
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class EndRoundEffect(PhaseEffect):
    """
    This is responsible for triggering other clean ups (e.g. remove satiated)
    """

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        active_id = game_state.get_active_player_id()
        active_player = game_state.get_player(active_id)
        effects = [
            AllStatusTriggererEffect(
                active_id,
                TriggeringSignal.ROUND_END
            ),
            # TODO: add active_player's team status, summons status... here
            AllStatusTriggererEffect(
                active_id.other(),
                TriggeringSignal.ROUND_END
            ),
            # TODO: add active_player's team status, summons status... here
        ]
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TurnEndEffect(PhaseEffect):
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        active_player_id = game_state.get_active_player_id()
        player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        assert player.get_phase() is ps.PlayerState.Act.ACTION_PHASE
        # TODO: other tidy up
        if other_player.get_phase() is ps.PlayerState.Act.END_PHASE:
            return game_state
        return game_state.factory().active_player(
            active_player_id.other()
        ).player(
            active_player_id,
            player.factory().phase(ps.PlayerState.Act.PASSIVE_WAIT_PHASE).build()
        ).other_player(
            active_player_id,
            other_player.factory().phase(ps.PlayerState.Act.ACTION_PHASE).build()
        ).build()


@dataclass(frozen=True)
class EndPhaseTurnEndEffect(PhaseEffect):
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        active_player_id = game_state.get_active_player_id()
        player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        assert player.get_phase() is ps.PlayerState.Act.ACTIVE_WAIT_PHASE
        return game_state.factory().active_player(
            active_player_id.other()
        ).player(
            active_player_id,
            player.factory().phase(ps.PlayerState.Act.PASSIVE_WAIT_PHASE).build()
        ).other_player(
            active_player_id,
            other_player.factory().phase(ps.PlayerState.Act.ACTIVE_WAIT_PHASE).build()
        ).build()


@dataclass(frozen=True)
class SetBothPlayerPhaseEffect(PhaseEffect):
    phase: ps.PlayerState.Act

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player1(
            lambda p: p.factory().phase(self.phase).build()
        ).f_player2(
            lambda p: p.factory().phase(self.phase).build()
        ).build()


@dataclass(frozen=True)
class SwapCharacterEffect(DirectEffect):
    target: StaticTarget

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        assert self.target.zone == Zone.CHARACTER
        pid = self.target.pid
        player = game_state.get_player(pid)
        characters = player.get_characters()
        characters = characters.factory().active_character_id(self.target.id).build()
        player = player.factory().characters(characters).build()
        # TODO: Trigger swap event
        return game_state.factory().player(pid, player).build()


@dataclass(frozen=True)
class ForwardSwapCharacterEffect(DirectEffect):
    target_player: gs.GameState.Pid

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        characters = game_state.get_player(self.target_player).get_characters()
        ordered_chars = characters.get_character_in_activity_order()
        next_char: Optional[chr.Character] = None
        for char in ordered_chars[1:] + ordered_chars[:1]:
            if char.alive():
                next_char = char
                break
        if next_char is None:
            raise Exception("Not reached, there should be defeat checker before")
        return game_state.factory().f_player(
            self.target_player,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().active_character_id(next_char.get_id()).build()
            ).build()
        ).build()


_DAMAGE_ELEMENTS: FrozenSet[Element] = frozenset({
    Element.PYRO,
    Element.HYDRO,
    Element.ANEMO,
    Element.ELECTRO,
    Element.DENDRO,
    Element.CRYO,
    Element.GEO,
    Element.PHYSICAL,
    Element.PIERCING,
})


@dataclass(frozen=True)
class SpecificDamageEffect(Effect):
    source: StaticTarget
    target: StaticTarget
    element: Element
    damage: int
    reaction: Optional[ReactionDetail] = None

    @staticmethod
    def _damage_preprocess(
            game_state: gs.GameState, damage: SpecificDamageEffect, pp_type: stt.Status.PPType
    ) -> tuple[gs.GameState, SpecificDamageEffect]:
        source_id = damage.source.pid
        game_state, item = _preprocessByAllStatuses(game_state, source_id, damage, pp_type)
        assert type(item) == SpecificDamageEffect
        game_state, item = _preprocessByAllStatuses(game_state, source_id.other(), item, pp_type)
        assert type(item) == SpecificDamageEffect
        damage = item
        return game_state, damage

    @classmethod
    def _element_confirmation(
            cls, game_state: gs.GameState, damage: SpecificDamageEffect
    ) -> tuple[gs.GameState, SpecificDamageEffect]:
        """ This is the pass to check final damage element """
        return cls._damage_preprocess(game_state, damage, stt.Status.PPType.DmgElement)

    @classmethod
    def _reaction_confirmation(
            cls, game_state: gs.GameState, damage: SpecificDamageEffect
    ) -> tuple[gs.GameState, SpecificDamageEffect, Optional[ReactionDetail]]:
        """ This is the pass to check final damage reaction type """
        target_char = game_state.get_character_target(damage.target)
        assert target_char is not None

        # try to identify the reaction
        second_elem = damage.element
        all_aura = target_char.get_elemental_aura()
        reaction: Optional[Reaction] = None
        reactionDetail: Optional[ReactionDetail] = None
        first_elem: Optional[Element] = None
        for first_elem in all_aura:
            reaction = Reaction.consult_reaction(first_elem, second_elem)
            if reaction is not None:
                break

        # generate & update new aura
        new_aura = all_aura
        if reaction is not None:
            assert first_elem is not None
            new_aura = new_aura.remove(first_elem)
            reactionDetail = ReactionDetail(reaction, first_elem, second_elem)
            damage = replace(damage, reaction=reactionDetail)
        elif new_aura.aurable(second_elem):
            new_aura = new_aura.add(second_elem)

        if new_aura != all_aura:
            game_state = game_state.factory().f_player(
                just(game_state.belongs_to(target_char)),
                lambda p: p.factory().f_characters(
                    lambda cs: cs.factory().character(
                        target_char.factory().elemental_aura(new_aura).build()
                    ).build()
                ).build()
            ).build()

        game_state, damage = cls._damage_preprocess(
            game_state, damage, stt.Status.PPType.DmgReaction
        )
        return game_state, damage, reactionDetail

    @classmethod
    def _damage_confirmation(
            cls, game_state: gs.GameState, damage: SpecificDamageEffect
    ) -> tuple[gs.GameState, SpecificDamageEffect]:
        """ This is the pass to check final damage amount """
        return cls._damage_preprocess(game_state, damage, stt.Status.PPType.DmgAmount)

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        # Preprocessing
        game_state, elemented_damage = self._element_confirmation(game_state, self)
        game_state, reactioned_damage, reaction = self._reaction_confirmation(
            game_state, elemented_damage
        )
        if reaction is not None:
            reactioned_damage = replace(
                reactioned_damage,
                damage=reactioned_damage.damage + reaction.reaction_type.damage_boost(),
            )
        game_state, actual_damage = self._damage_confirmation(game_state, reactioned_damage)

        # Get damage target
        target = game_state.get_character_target(actual_damage.target)
        if target is None:
            return game_state

        # Damage Calculation
        hp = target.get_hp()
        hp = max(0, hp - actual_damage.damage)

        pid = self.target.pid
        effects: list[Effect] = [DefeatedCheckerEffect()]

        # LATESET_TODO: use the reaction information to generate further effects
        if reaction is None:
            pass

        elif reaction.reaction_type is Reaction.VAPORIZE \
                or reaction.reaction_type is Reaction.MELT:
            pass

        elif reaction.reaction_type is Reaction.OVERLOADED:
            oppo_active_id = game_state \
                .get_player(actual_damage.target.pid) \
                .just_get_active_character() \
                .get_id()
            assert actual_damage.target.zone is Zone.CHARACTER
            if actual_damage.target.id is oppo_active_id:
                effects.append(
                    ForwardSwapCharacterEffect(pid)
                )

        elif reaction.reaction_type is Reaction.SUPERCONDUCT \
                or reaction.reaction_type is Reaction.ELECTRO_CHARGED:
            effects.append(
                ReferredDamageEffect(
                    source=self.source,
                    target_ref=actual_damage.target,
                    target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                    element=Element.PIERCING,
                    damage=1,
                )
            )

        elif reaction.reaction_type is Reaction.SWIRL:
            effects.append(
                ReferredDamageEffect(
                    source=self.source,
                    target_ref=actual_damage.target,
                    target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                    element=reaction.first_elem,
                    damage=1,
                )
            )

        elif reaction.reaction_type is Reaction.FROZEN:
            effects.append(
                AddCharacterStatusEffect(
                    target=actual_damage.target,
                    status=stt.FrozenStatus,
                )
            )

        elif reaction.reaction_type is Reaction.QUICKEN:
            effects.append(
                AddCombatStatusEffect(
                    target_pid=actual_damage.source.pid,
                    status=stt.CatalyzingFieldStatus,
                )
            )

        elif reaction.reaction_type is Reaction.BLOOM:
            effects.append(
                AddCombatStatusEffect(
                    target_pid=actual_damage.source.pid,
                    status=stt.DendroCoreStatus,
                )
            )

        elif reaction.reaction_type is Reaction.CRYSTALLIZE:
            effects.append(
                AddCombatStatusEffect(
                    target_pid=actual_damage.source.pid,
                    status=stt.CrystallizeStatus,
                )
            )

        elif reaction.reaction_type is Reaction.BURNING:
            effects.append(
                AddSummonEffect(
                    target_pid=actual_damage.source.pid,
                    summon=sm.BurningFlameSummon,
                )
            )

        else:
            # this exception shouldn't be reached by now, but leave it here just to be safe
            raise Exception(f"Reaction {reaction.reaction_type} not handled")

        if hp != target.get_hp():
            target = target.factory().hp(hp).build()

        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().character(target).build()
            ).build()
        ).f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class ReferredDamageEffect(Effect):
    source: StaticTarget
    target: DynamicCharacterTarget
    element: Element
    damage: int
    # this field is used as a reference if the target is OFF_FIELD
    # e.g. super-conduct caused by swirl
    target_ref: Optional[StaticTarget] = field(kw_only=True, default=None)

    def legal(self) -> bool:
        return self.element in _DAMAGE_ELEMENTS

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        targets: list[Optional[chr.Character]] = []
        effects: list[Effect] = []
        char: Optional[chr.Character]

        if self.target is DynamicCharacterTarget.OPPO_ACTIVE:
            targets.append(
                game_state.get_other_player(self.source.pid).get_characters().get_active_character()
            )
        elif self.target is DynamicCharacterTarget.OPPO_OFF_FIELD:
            opponenet_characters = game_state.get_other_player(self.source.pid).get_characters()
            avoided_id: int
            if self.target_ref is None:
                avoided_id = just(opponenet_characters.get_active_character_id())
            else:
                assert self.target_ref.pid is self.source.pid.other()
                assert self.target_ref.zone is Zone.CHARACTER
                avoided_id = self.target_ref.id
            for char in opponenet_characters.get_characters():
                if char.get_id() != avoided_id:
                    targets.append(char)
        else:
            raise Exception("Not implemented yet")

        for char in targets:
            if char is None:
                continue
            pid = game_state.belongs_to(char)
            if pid is None:
                continue
            effects.append(
                SpecificDamageEffect(
                    source=self.source,
                    target=StaticTarget(
                        pid=pid,
                        zone=Zone.CHARACTER,
                        id=char.get_id(),
                    ),
                    element=self.element,
                    damage=self.damage,
                    reaction=None,
                )
            )

        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class EnergyRechargeEffect(Effect):
    target: StaticTarget
    recharge: int

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
        character = cast(chr.Character, character)
        energy = min(character.get_energy() + self.recharge, character.get_max_energy())
        if energy == character.get_energy():
            return game_state
        character = character.factory().energy(energy).build()
        player = game_state.get_player(self.target.pid)
        characters = player.get_characters().factory().character(character).build()
        player = player.factory().characters(characters).build()
        return game_state.factory().player(
            self.target.pid,
            player
        ).build()


@dataclass(frozen=True)
class EnergyDrainEffect(Effect):
    target: StaticTarget
    drain: int

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
        character = cast(chr.Character, character)
        energy = max(character.get_energy() - self.drain, 0)
        if energy == character.get_energy():
            return game_state
        character = character.factory().energy(energy).build()
        player = game_state.get_player(self.target.pid)
        characters = player.get_characters().factory().character(character).build()
        player = player.factory().characters(characters).build()
        return game_state.factory().player(
            self.target.pid,
            player
        ).build()


@dataclass(frozen=True)
class RecoverHPEffect(Effect):
    target: StaticTarget
    recovery: int

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
        character = cast(chr.Character, character)
        hp = min(character.get_hp() + self.recovery, character.get_max_hp())
        if hp == character.get_hp():
            return game_state
        return game_state.factory().f_player(
            self.target.pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    character.get_id(),
                    lambda c: c.factory().hp(hp).build()
                ).build()
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveCardEffect(Effect):
    pid: gs.GameState.Pid
    card: type[cd.Card]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        pid = self.pid
        card = self.card
        hand_cards = game_state.get_player(pid).get_hand_cards()
        if not hand_cards.contains(card) or hand_cards[card] <= 0:
            return game_state
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_hand_cards(
                lambda cs: cs.remove(card)
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveAllCardEffect(Effect):
    pid: gs.GameState.Pid
    card: type[cd.Card]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        pid = self.pid
        card = self.card
        hand_cards = game_state.get_player(pid).get_hand_cards()
        if not hand_cards.contains(card) or hand_cards[card] <= 0:
            return game_state
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_hand_cards(
                lambda cs: cs.remove_all(card)
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveDiceEffect(Effect):
    pid: gs.GameState.Pid
    dices: ds.ActualDices

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        pid = self.pid
        dices = self.dices
        new_dices = game_state.get_player(pid).get_dices() - dices
        if not new_dices.is_legal():
            raise Exception("Not enough dices for this effect")
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().dices(new_dices).build()
        ).build()


@dataclass(frozen=True)
class AddCharacterStatusEffect(Effect):
    target: StaticTarget
    status: type[Union[stt.CharacterTalentStatus, stt.EquipmentStatus, stt.CharacterStatus]]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        assert isinstance(character, chr.Character)
        if issubclass(self.status, stt.CharacterTalentStatus):
            character = character.factory().f_talents(
                lambda ts: ts.update_status(self.status())
            ).build()
        elif issubclass(self.status, stt.EquipmentStatus):
            character = character.factory().f_equipments(
                lambda es: es.update_status(self.status())
            ).build()
        elif issubclass(self.status, stt.CharacterStatus):
            character = character.factory().f_character_statuses(
                lambda cs: cs.update_status(self.status())
            ).build()
        return game_state.factory().f_player(
            self.target.pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().character(character).build()
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveCharacterStatusEffect(DirectEffect):
    target: StaticTarget
    status: type[Union[stt.CharacterTalentStatus, stt.EquipmentStatus, stt.CharacterStatus]]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_character_target(self.target)
        if character is None:
            return game_state
        new_character = character
        if issubclass(self.status, stt.CharacterTalentStatus):
            new_character = character.factory().f_talents(
                lambda ts: ts.remove(self.status)
            ).build()
        elif issubclass(self.status, stt.EquipmentStatus):
            new_character = character.factory().f_equipments(
                lambda es: es.remove(self.status)
            ).build()
        elif issubclass(self.status, stt.CharacterStatus):
            new_character = character.factory().f_character_statuses(
                lambda cs: cs.remove(self.status)
            ).build()
        return game_state.factory().f_player(
            self.target.pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().character(new_character).build()
            ).build()
        ).build()


@dataclass(frozen=True)
class UpdateCharacterStatusEffect(Effect):
    target: StaticTarget
    status: Union[stt.CharacterTalentStatus, stt.EquipmentStatus, stt.CharacterStatus]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        assert isinstance(character, chr.Character)
        if isinstance(self.status, stt.CharacterTalentStatus):
            character = character.factory().f_talents(
                lambda ts: ts.update_status(self.status)
            ).build()
        elif isinstance(self.status, stt.EquipmentStatus):
            character = character.factory().f_equipments(
                lambda es: es.update_status(self.status)
            ).build()
        elif isinstance(self.status, stt.CharacterStatus):
            character = character.factory().f_character_statuses(
                lambda cs: cs.update_status(self.status)
            ).build()
        return game_state.factory().f_player(
            self.target.pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().character(character).build()
            ).build()
        ).build()


@dataclass(frozen=True)
class OverrideCharacterStatusEffect(Effect):
    target: StaticTarget
    status: Union[stt.CharacterTalentStatus, stt.EquipmentStatus, stt.CharacterStatus]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        assert isinstance(character, chr.Character)
        if isinstance(self.status, stt.CharacterTalentStatus):
            character = character.factory().f_talents(
                lambda ts: ts.update_status(self.status, force=True)
            ).build()
        elif isinstance(self.status, stt.EquipmentStatus):
            character = character.factory().f_equipments(
                lambda es: es.update_status(self.status, force=True)
            ).build()
        elif isinstance(self.status, stt.CharacterStatus):
            character = character.factory().f_character_statuses(
                lambda cs: cs.update_status(self.status, force=True)
            ).build()
        return game_state.factory().f_player(
            self.target.pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().character(character).build()
            ).build()
        ).build()


@dataclass(frozen=True)
class AddCombatStatusEffect(Effect):
    target_pid: gs.GameState.Pid
    status: type[stt.CombatStatus]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(self.status())
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveCombatStatusEffect(Effect):
    target_pid: gs.GameState.Pid
    status: type[stt.CombatStatus]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.remove(self.status)
            ).build()
        ).build()


@dataclass(frozen=True)
class UpdateCombatStatusEffect(Effect):
    target_pid: gs.GameState.Pid
    status: stt.CombatStatus

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(self.status)
            ).build()
        ).build()


@dataclass(frozen=True)
class OverrideCombatStatusEffect(Effect):
    target_pid: gs.GameState.Pid
    status: stt.CombatStatus

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(self.status, force=True)
            ).build()
        ).build()


@dataclass(frozen=True)
class AddSummonEffect(Effect):
    target_pid: gs.GameState.Pid
    summon: type[sm.Summon]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(self.summon())
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveSummonEffect(Effect):
    target_pid: gs.GameState.Pid
    summon: type[sm.Summon]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.remove_summon(self.summon)
            ).build()
        ).build()


@dataclass(frozen=True)
class UpdateSummonEffect(Effect):
    target_pid: gs.GameState.Pid
    summon: sm.Summon

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(self.summon)
            ).build()
        ).build()


@dataclass(frozen=True)
class OverrideSummonEffect(Effect):
    target_pid: gs.GameState.Pid
    summon: sm.Summon

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(self.summon, force=True)
            ).build()
        ).build()


@dataclass(frozen=True)
class AddCardEffect(Effect):
    pid: gs.GameState.Pid
    card: type[cd.Card]

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        return game_state.factory().f_player(
            self.pid,
            lambda p: p.factory().f_hand_cards(
                lambda cs: cs.add(self.card)
            ).build()
        ).build()


@dataclass(frozen=True)
class CastSkillEffect(Effect):
    target: StaticTarget
    skill: chr.CharacterSkill

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        assert isinstance(character, chr.Character)
        if not character.can_cast_skill():
            return game_state
        effects = character.skill(game_state, self.skill)
        if not effects:
            return game_state
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


# This has to be by the end of the file or there's cyclic import error
Preprocessable = Union[SpecificDamageEffect, int]
