from __future__ import annotations
from dataclasses import asdict, dataclass, field, replace
from typing import FrozenSet, Iterable, Optional, TYPE_CHECKING, Union

from ..character import character as chr
from ..status import status as stt
from ..summon import summon as sm
from ..support import support as sp

from ..character.character_skill_enum import CharacterSkill
from ..element.element import Element, Reaction, ReactionDetail
from ..helper.quality_of_life import just, case_val
from ..state.enums import PID, ACT
from ..status.enums import PREPROCESSABLES
from ..status.status_processing import StatusProcessing

from .enums import DYNAMIC_CHARACTER_TARGET, TRIGGERING_SIGNAL, ZONE
from .structs import StaticTarget, DamageType

if TYPE_CHECKING:
    from ..card.card import Card
    from ..dices import ActualDices
    from ..state.game_state import GameState
    from ..status.statuses import Statuses


@dataclass(frozen=True)
class Effect:
    def execute(self, game_state: GameState) -> GameState:
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
    signal: TRIGGERING_SIGNAL

    def execute(self, game_state: GameState) -> GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
        effects: Iterable[Effect] = []

        statuses: Statuses
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
        effects = status.react_to_signal(game_state, self.target, self.signal)
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TriggerCombatStatusEffect(Effect):
    target_pid: PID  # the player the status belongs to
    status: type[stt.CombatStatus]
    signal: TRIGGERING_SIGNAL

    def execute(self, game_state: GameState) -> GameState:
        effects: Iterable[Effect] = []
        statuses = game_state.get_player(self.target_pid).get_combat_statuses()
        status = statuses.find(self.status)
        if status is None:
            return game_state
        effects = status.react_to_signal(
            game_state,
            StaticTarget(
                pid=self.target_pid,
                zone=ZONE.COMBAT_STATUSES,
                id=-1,
            ),
            self.signal,
        )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TriggerSummonEffect(Effect):
    target_pid: PID
    summon: type[sm.Summon]
    signal: TRIGGERING_SIGNAL

    def execute(self, game_state: GameState) -> GameState:
        effects: Iterable[Effect] = []
        summons = game_state.get_player(self.target_pid).get_summons()
        summon = summons.find(self.summon)
        if summon is None:
            return game_state
        effects = summon.react_to_signal(
            game_state,
            StaticTarget(
                pid=self.target_pid,
                zone=ZONE.SUMMONS,
                id=-1,
            ),
            self.signal,
        )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TriggerSupportEffect(Effect):
    target_pid: PID
    support_type: type[sp.Support]
    sid: int
    signal: TRIGGERING_SIGNAL

    def execute(self, game_state: GameState) -> GameState:
        effects: Iterable[Effect] = []
        supports = game_state.get_player(self.target_pid).get_supports()
        support = supports.find(self.support_type, self.sid)
        if support is None:
            return game_state
        effects = support.react_to_signal(
            game_state,
            StaticTarget(
                pid=self.target_pid,
                zone=ZONE.SUPPORTS,
                id=self.sid,
            ),
            self.signal,
        )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class AllStatusTriggererEffect(TriggerrbleEffect):
    """
    This effect triggers the characters' statuses with the provided signal in order.
    """
    pid: PID
    signal: TRIGGERING_SIGNAL

    def execute(self, game_state: GameState) -> GameState:
        effects = StatusProcessing.trigger_all_statuses_effects(game_state, self.pid, self.signal)
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class SwapCharacterCheckerEffect(CheckerEffect):
    my_active: StaticTarget
    oppo_active: StaticTarget

    def execute(self, game_state: GameState) -> GameState:
        my_ac_id = game_state.get_player(self.my_active.pid).just_get_active_character().get_id()
        oppo_ac_id = game_state.get_player(
            self.oppo_active.pid).just_get_active_character().get_id()
        my_pid = self.my_active.pid
        effects: list[Effect] = []
        if my_pid.is_player1():
            my_signal = TRIGGERING_SIGNAL.SWAP_EVENT_1
            oppo_signal = TRIGGERING_SIGNAL.SWAP_EVENT_2
        else:
            my_signal = TRIGGERING_SIGNAL.SWAP_EVENT_2
            oppo_signal = TRIGGERING_SIGNAL.SWAP_EVENT_1
        if my_ac_id != self.my_active.id:
            effects += [
                AllStatusTriggererEffect(
                    pid=my_pid,
                    signal=my_signal,
                ),
            ]
        if oppo_ac_id != self.oppo_active.id:
            effects += [
                AllStatusTriggererEffect(
                    pid=my_pid,
                    signal=oppo_signal,
                ),
            ]
        if not effects:
            return game_state
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class DeathCheckCheckerEffect(CheckerEffect):
    def execute(self, game_state: GameState) -> GameState:
        p1_character = game_state.get_player1().get_characters().get_active_character()
        p2_character = game_state.get_player2().get_characters().get_active_character()
        assert p1_character is not None and p2_character is not None
        pid: PID
        if p1_character.defeated():
            pid = PID.P1
        elif p2_character.defeated():
            pid = PID.P2
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
                ACT.ACTION_PHASE
            ).build()
        ).other_player(
            pid,
            game_state.get_other_player(pid).factory().phase(
                ACT.PASSIVE_WAIT_PHASE
            ).build()
        ).build()


@dataclass(frozen=True)
class DefeatedCheckerEffect(CheckerEffect):
    def execute(self, game_state: GameState) -> GameState:
        if game_state.get_player1().defeated() \
                or game_state.get_player2().defeated():
            return game_state.factory().phase(game_state.get_mode().game_end_phase()).build()
        return game_state


@dataclass(frozen=True)
class DeathSwapPhaseStartEffect(PhaseEffect):
    pass


@dataclass(frozen=True)
class DeathSwapPhaseEndEffect(PhaseEffect):
    my_pid: PID
    my_last_phase: ACT
    other_last_phase: ACT

    def execute(self, game_state: GameState) -> GameState:
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

    def execute(self, game_state: GameState) -> GameState:
        active_id = game_state.get_active_player_id()
        # active_player = game_state.get_player(active_id)
        effects = [
            AllStatusTriggererEffect(
                active_id,
                TRIGGERING_SIGNAL.END_ROUND_CHECK_OUT
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

    def execute(self, game_state: GameState) -> GameState:
        active_id = game_state.get_active_player_id()
        active_player = game_state.get_player(active_id)
        effects = [
            AllStatusTriggererEffect(
                active_id,
                TRIGGERING_SIGNAL.ROUND_END
            ),
            # TODO: add active_player's team status, summons status... here
        ]
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class TurnEndEffect(PhaseEffect):
    def execute(self, game_state: GameState) -> GameState:
        active_player_id = game_state.get_active_player_id()
        player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        assert player.get_phase() is ACT.ACTION_PHASE
        # TODO: other tidy up
        if other_player.get_phase() is ACT.END_PHASE:
            return game_state
        return game_state.factory().active_player_id(
            active_player_id.other()
        ).player(
            active_player_id,
            player.factory().phase(ACT.PASSIVE_WAIT_PHASE).build()
        ).other_player(
            active_player_id,
            other_player.factory().phase(ACT.ACTION_PHASE).build()
        ).build()


@dataclass(frozen=True)
class EndPhaseTurnEndEffect(PhaseEffect):
    def execute(self, game_state: GameState) -> GameState:
        active_player_id = game_state.get_active_player_id()
        player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        assert player.get_phase().is_active_wait_phase()
        return game_state.factory().active_player_id(
            active_player_id.other()
        ).player(
            active_player_id,
            player.factory().phase(ACT.PASSIVE_WAIT_PHASE).build()
        ).other_player(
            active_player_id,
            other_player.factory().phase(ACT.ACTIVE_WAIT_PHASE).build()
        ).build()


@dataclass(frozen=True)
class SetBothPlayerPhaseEffect(PhaseEffect):
    phase: ACT

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player1(
            lambda p: p.factory().phase(self.phase).build()
        ).f_player2(
            lambda p: p.factory().phase(self.phase).build()
        ).build()


@dataclass(frozen=True)
class SwapCharacterEffect(DirectEffect):
    target: StaticTarget

    def execute(self, game_state: GameState) -> GameState:
        assert self.target.zone == ZONE.CHARACTERS
        pid = self.target.pid
        player = game_state.get_player(pid)
        if player.just_get_active_character().get_id() == self.target.id:
            return game_state

        effects: list[Effect] = [
            AllStatusTriggererEffect(
                pid,
                case_val(
                    pid.is_player1(),
                    TRIGGERING_SIGNAL.SWAP_EVENT_1,
                    TRIGGERING_SIGNAL.SWAP_EVENT_2,
                ),
            ),
        ]
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().active_character_id(self.target.id).build()
            ).build()
        ).f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class ForwardSwapCharacterEffect(DirectEffect):
    target_player: PID

    def execute(self, game_state: GameState) -> GameState:
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


@dataclass(frozen=True, kw_only=True)
class SpecificDamageEffect(Effect):
    source: StaticTarget
    target: StaticTarget
    element: Element
    damage: int
    damage_type: DamageType
    reaction: Optional[ReactionDetail] = None

    @staticmethod
    def _damage_preprocess(
            game_state: GameState, damage: SpecificDamageEffect, pp_type: PREPROCESSABLES
    ) -> tuple[GameState, SpecificDamageEffect]:
        source_id = damage.source.pid
        game_state, item = StatusProcessing.preprocess_by_all_statuses(
            game_state,
            source_id,
            damage,
            pp_type
        )
        assert type(item) == SpecificDamageEffect
        damage = item
        return game_state, damage

    @classmethod
    def _element_confirmation(
            cls, game_state: GameState, damage: SpecificDamageEffect
    ) -> tuple[GameState, SpecificDamageEffect]:
        """ This is the pass to check final damage element """
        return cls._damage_preprocess(game_state, damage, PREPROCESSABLES.DMG_ELEMENT)

    @classmethod
    def _reaction_confirmation(
            cls, game_state: GameState, damage: SpecificDamageEffect
    ) -> tuple[GameState, SpecificDamageEffect, Optional[ReactionDetail]]:
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
            game_state, damage, PREPROCESSABLES.DMG_REACTION
        )
        return game_state, damage, reactionDetail

    @classmethod
    def _damage_confirmation(
            cls, game_state: GameState, damage: SpecificDamageEffect
    ) -> tuple[GameState, SpecificDamageEffect]:
        """ This is the pass to check final damage amount """
        return cls._damage_preprocess(game_state, damage, PREPROCESSABLES.DMG_AMOUNT)

    def execute(self, game_state: GameState) -> GameState:
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
            assert actual_damage.target.zone is ZONE.CHARACTERS
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
                    target=DYNAMIC_CHARACTER_TARGET.OPPO_OFF_FIELD,
                    element=Element.PIERCING,
                    damage=1,
                    damage_type=DamageType(no_boost=True),
                )
            )

        elif reaction.reaction_type is Reaction.SWIRL:
            effects.append(
                ReferredDamageEffect(
                    source=self.source,
                    target_ref=actual_damage.target,
                    target=DYNAMIC_CHARACTER_TARGET.OPPO_OFF_FIELD,
                    element=reaction.first_elem,
                    damage=1,
                    damage_type=DamageType(no_boost=True),
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
    target: DYNAMIC_CHARACTER_TARGET
    element: Element
    damage: int
    damage_type: DamageType
    # this field is used as a reference if the target is OFF_FIELD
    # e.g. super-conduct caused by swirl
    target_ref: Optional[StaticTarget] = field(kw_only=True, default=None)

    def legal(self) -> bool:
        return self.element in _DAMAGE_ELEMENTS

    def execute(self, game_state: GameState) -> GameState:
        targets: list[Optional[chr.Character]] = []
        effects: list[Effect] = []
        char: Optional[chr.Character]

        if self.target is DYNAMIC_CHARACTER_TARGET.OPPO_ACTIVE:
            targets.append(
                game_state.get_other_player(self.source.pid).get_characters().get_active_character()
            )
        elif self.target is DYNAMIC_CHARACTER_TARGET.OPPO_OFF_FIELD:
            opponenet_characters = game_state.get_other_player(self.source.pid).get_characters()
            avoided_id: int
            if self.target_ref is None:
                avoided_id = just(opponenet_characters.get_active_character_id())
            else:
                assert self.target_ref.pid is self.source.pid.other()
                assert self.target_ref.zone is ZONE.CHARACTERS
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
                        zone=ZONE.CHARACTERS,
                        id=char.get_id(),
                    ),
                    element=self.element,
                    damage=self.damage,
                    damage_type=self.damage_type,
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

    def execute(self, game_state: GameState) -> GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
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

    def execute(self, game_state: GameState) -> GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
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

    def execute(self, game_state: GameState) -> GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, chr.Character):
            return game_state
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
    pid: PID
    card: type[Card]

    def execute(self, game_state: GameState) -> GameState:
        pid = self.pid
        card = self.card
        hand_cards = game_state.get_player(pid).get_hand_cards()
        if not hand_cards.contains(card) or hand_cards[card] <= 0:
            return game_state
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().f_hand_cards(
                lambda cs: cs.remove(card)
            ).f_publicly_used_cards(
                lambda cs: cs.add(card)
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveAllCardEffect(Effect):
    pid: PID
    card: type[Card]

    def execute(self, game_state: GameState) -> GameState:
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
    pid: PID
    dices: ActualDices

    def execute(self, game_state: GameState) -> GameState:
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

    def execute(self, game_state: GameState) -> GameState:
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

    def execute(self, game_state: GameState) -> GameState:
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

    def execute(self, game_state: GameState) -> GameState:
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

    def execute(self, game_state: GameState) -> GameState:
        character = game_state.get_target(self.target)
        assert isinstance(character, chr.Character)
        if isinstance(self.status, stt.CharacterTalentStatus):
            character = character.factory().f_talents(
                lambda ts: ts.update_status(self.status, override=True)
            ).build()
        elif isinstance(self.status, stt.EquipmentStatus):
            character = character.factory().f_equipments(
                lambda es: es.update_status(self.status, override=True)
            ).build()
        elif isinstance(self.status, stt.CharacterStatus):
            character = character.factory().f_character_statuses(
                lambda cs: cs.update_status(self.status, override=True)
            ).build()
        return game_state.factory().f_player(
            self.target.pid,
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().character(character).build()
            ).build()
        ).build()


@dataclass(frozen=True)
class AddCombatStatusEffect(Effect):
    target_pid: PID
    status: type[stt.CombatStatus]

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(self.status())
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveCombatStatusEffect(Effect):
    target_pid: PID
    status: type[stt.CombatStatus]

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.remove(self.status)
            ).build()
        ).build()


@dataclass(frozen=True)
class UpdateCombatStatusEffect(Effect):
    target_pid: PID
    status: stt.CombatStatus

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(self.status)
            ).build()
        ).build()


@dataclass(frozen=True)
class OverrideCombatStatusEffect(Effect):
    target_pid: PID
    status: stt.CombatStatus

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_combat_statuses(
                lambda ss: ss.update_status(self.status, override=True)
            ).build()
        ).build()


@dataclass(frozen=True)
class AddSummonEffect(Effect):
    target_pid: PID
    summon: type[sm.Summon]

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(self.summon())
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveSummonEffect(Effect):
    target_pid: PID
    summon: type[sm.Summon]

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.remove_summon(self.summon)
            ).build()
        ).build()


@dataclass(frozen=True)
class UpdateSummonEffect(Effect):
    target_pid: PID
    summon: sm.Summon

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(self.summon)
            ).build()
        ).build()


@dataclass(frozen=True)
class OverrideSummonEffect(Effect):
    target_pid: PID
    summon: sm.Summon

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(self.summon, override=True)
            ).build()
        ).build()


@dataclass(frozen=True, kw_only=True)
class AllSummonIncreaseUsage(Effect):
    target_pid: PID
    d_usages: int = 1

    def execute(self, game_state: GameState) -> GameState:
        effects: list[Effect] = []
        summons = game_state.get_player(self.target_pid).get_summons()
        for summon in summons:
            effects.append(
                OverrideSummonEffect(
                    target_pid=self.target_pid,
                    summon=replace(summon, usages=summon.usages + self.d_usages),
                )
            )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True, kw_only=True)
class OneSummonIncreaseUsage(Effect):
    target_pid: PID
    summon_type: type[sm.Summon]
    d_usages: int = 1

    def execute(self, game_state: GameState) -> GameState:
        effects: list[Effect] = []
        summons = game_state.get_player(self.target_pid).get_summons()
        summon = summons.find(summon_type=self.summon_type)
        if summon is None:
            return game_state

        effects.append(
            OverrideSummonEffect(
                target_pid=self.target_pid,
                summon=replace(summon, usages=summon.usages + 1),
            )
        )
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).build()


@dataclass(frozen=True)
class AddSupportEffect(Effect):
    target_pid: PID
    support: type[sp.Support]

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_supports(
                lambda ss: ss.update_support(self.support(sid=ss.new_sid(self.support)))
            ).build()
        ).build()


@dataclass(frozen=True)
class RemoveSupportEffect(Effect):
    target_pid: PID
    sid: int

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_supports(
                lambda ss: ss.remove_by_sid(self.sid)
            ).build()
        ).build()


@dataclass(frozen=True)
class UpdateSupportEffect(Effect):
    target_pid: PID
    support: sp.Support

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_supports(
                lambda ss: ss.update_support(self.support)
            ).build()
        ).build()


@dataclass(frozen=True)
class OverrideSupportEffect(Effect):
    target_pid: PID
    support: sp.Support

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.target_pid,
            lambda p: p.factory().f_supports(
                lambda ss: ss.update_support(self.support, override=True)
            ).build()
        ).build()


@dataclass(frozen=True)
class AddCardEffect(Effect):
    pid: PID
    card: type[Card]

    def execute(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player(
            self.pid,
            lambda p: p.factory().f_hand_cards(
                lambda cs: cs.add(self.card)
            ).build()
        ).build()


@dataclass(frozen=True)
class CastSkillEffect(Effect):
    target: StaticTarget
    skill: CharacterSkill

    def execute(self, game_state: GameState) -> GameState:
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


@dataclass(frozen=True)
class BroadCastSkillInfoEffect(Effect):
    source: StaticTarget
    skill: CharacterSkill

    def execute(self, game_state: GameState) -> GameState:
        return StatusProcessing.inform_all_statuses(
            game_state,
            self.source.pid,
            self.skill,
            source=self.source,
        )
