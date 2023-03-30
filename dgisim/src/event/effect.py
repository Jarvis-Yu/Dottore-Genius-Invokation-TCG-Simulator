from __future__ import annotations
from typing import FrozenSet, Optional, cast, Union
from enum import Enum
from dataclasses import InitVar, dataclass

from dgisim.src.element.element import Element
import dgisim.src.character.character as char
import dgisim.src.state.game_state as gs
import dgisim.src.state.player_state as ps


class Zone(Enum):
    CHARACTER = 0
    SUMMONS = 1
    SUPPORT = 2
    HAND = 3
    EFFECT = 4


class DynamicCharacterTarget(Enum):
    SELF_SELF = 0
    SELF_ACTIVE = 1
    SELF_OFF_FIELD = 2
    SELF_ALL = 3
    SELF_ABS = 4
    OPPO_ACTIVE = 5
    OPPO_OFF_FIELD = 6


@dataclass(frozen=True)
class StaticTarget:
    pid: gs.GameState.Pid
    zone: Zone
    id: int


class Effect:
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        raise Exception("Not Overriden or Implemented")


class TrigerrbleEffect(Effect):
    pass


class DirectEffect(Effect):
    pass


class CheckerEffect(Effect):
    pass


class PhaseEffect(Effect):
    pass


class SwapCharacterCheckerEffect(CheckerEffect):
    pass


@dataclass(frozen=True)
class DeathCheckCheckerEffect(CheckerEffect):
    def execute(self, game_state: gs.GameState) -> gs.GameState:
        # return game_state
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
            return game_state.factory().phase(game_state.get_mode().game_end_phase()).build()
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
    pass


@dataclass(frozen=True)
class DeathSwapPhaseStartEffect(PhaseEffect):
    def __str__(self) -> str:
        return self.__class__.__name__


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

    def __str__(self) -> str:
        return self.__class__.__name__


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
class SwapCharacterEffect(DirectEffect):
    source: StaticTarget
    target: StaticTarget

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        assert self.source.pid == self.target.pid \
            and self.source.zone == Zone.CHARACTER \
            and self.target.zone == Zone.CHARACTER \
            and self.source.id != self.target.id
        pid = self.source.pid
        player = game_state.get_player(pid)
        characters = player.get_characters()
        characters = characters.factory().active_character_id(self.target.id).build()
        player = player.factory().characters(characters).build()
        # TODO: Trigger swap event
        return game_state.factory().player(pid, player).build()


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
class DamageEffect(Effect):
    source: StaticTarget
    target: DynamicCharacterTarget
    element: Element
    damage: int

    def legal(self) -> bool:
        return self.element in _DAMAGE_ELEMENTS

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        pid = self.source.pid
        from dgisim.src.character.character import Character
        # Get damage target
        opponent: Character
        if self.target is DynamicCharacterTarget.OPPO_ACTIVE:
            optional_opponent = game_state.get_other_player(
                pid).get_characters().get_active_character()
            if optional_opponent is None:
                raise Exception("Not implemented yet")
            opponent = optional_opponent
        else:
            raise Exception("Not implemented yet")
        # TODO: Preprocess Damage
        # Damage Calculation
        hp = opponent.get_hp()
        hp = max(0, hp - self.damage)

        opponent = opponent.factory().hp(hp).build()
        other_player = game_state.get_other_player(pid)
        other_characters = other_player.get_characters().factory().character(opponent).build()
        other_player = other_player.factory().characters(other_characters).build()
        return game_state.factory().other_player(pid, other_player).build()


@dataclass(frozen=True)
class EnergyRechargeEffect(Effect):
    target: StaticTarget
    recharge: int

    def execute(self, game_state: gs.GameState) -> gs.GameState:
        character = game_state.get_target(self.target)
        if not isinstance(character, char.Character):
            return game_state
        character = cast(char.Character, character)
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
