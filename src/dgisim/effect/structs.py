from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..state.enums import PID
from .enums import ZONE


@dataclass(frozen=True)
class StaticTarget:
    pid: PID
    zone: ZONE
    id: int

# TODO: postpone this until further tests are done
#       needs to investigate how Klee's burst and Mona's or Sucrose's Talent co-work
@dataclass(frozen=True, kw_only=True)
class DamageType:
    normal_attack: bool = False
    charged_attack: bool = False
    plunge_attack: bool = False
    elemental_skill: bool = False
    elemental_burst: bool = False
    status: bool = False  # any talent, equipmenet, character status, combat status.
    summon: bool = False
    no_boost: bool = False  # reaction secondary damage, Klee's burst status...