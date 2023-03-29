from __future__ import annotations
from typing import FrozenSet, Optional, cast
from enum import Enum
from dataclasses import InitVar, dataclass

from dgisim.src.element.element import Element
import dgisim.src.state.game_state as gm


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
    pid: gm.GameState.Pid
    zone: Zone
    id: int


class Effect:
    def execute(self, game_state: gm.GameState) -> gm.GameState:
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


class DeathCheckCheckerEffect(CheckerEffect):
    pass


class DeathSwapPhaseEffect(PhaseEffect):
    pass


class SwapCharacterEffect(DirectEffect):

    def __init__(self, target: DynamicCharacterTarget, index: Optional[int] = None):
        assert target != DynamicCharacterTarget.SELF_ABS or index is not None
        self._target = target
        self._index = index


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

    def execute(self, game_state: gm.GameState) -> gm.GameState:
        pid = self.source.pid
        from dgisim.src.character.character import Character
        opponent: Character
        if self.target is DynamicCharacterTarget.OPPO_ACTIVE:
            optional_opponent = game_state.get_other_player(pid).get_characters().get_active_character()
            if optional_opponent is None:
                raise Exception("Not implemented yet")
            opponent = optional_opponent
        else:
            raise Exception("Not implemented yet")
        # TODO: Preprocessing
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
