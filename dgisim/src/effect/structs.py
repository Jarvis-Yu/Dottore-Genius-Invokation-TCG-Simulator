from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from ..helper.quality_of_life import dataclass_repr
from ..state.enums import Pid
from .enums import Zone

if TYPE_CHECKING:
    from ..summon.summon import Summon

__all__ = [
    "DamageType",
    "StaticTarget",
]


@dataclass(frozen=True, repr=False)
class StaticTarget:
    pid: Pid
    zone: Zone
    id: int | type["Summon"]

    def __repr__(self) -> str:
        return dataclass_repr(self)

# TODO: postpone this until further tests are done
#       needs to investigate how Klee's burst and Mona's or Sucrose's Talent co-work


@dataclass(frozen=True, kw_only=True, repr=False)
class DamageType:
    normal_attack: bool = False
    charged_attack: bool = False
    plunge_attack: bool = False
    elemental_skill: bool = False
    elemental_burst: bool = False
    status: bool = False  # any talent, equipmenet, character status, combat status.
    summon: bool = False
    no_boost: bool = False  # reaction secondary damage, Klee's burst status...

    def from_character(self) -> bool:
        return (
            self.normal_attack
            or self.elemental_skill
            or self.elemental_burst
            or self.charged_attack
            or self.plunge_attack
        )

    def from_summon(self) -> bool:
        return self.summon

    def from_status(self) -> bool:
        return self.status

    def can_boost(self) -> bool:
        return not self.no_boost

    def __repr__(self) -> str:
        cls_fields = fields(self)
        enabled_fields = [
            field.name
            for field in cls_fields
            if self.__getattribute__(field.name)
        ]
        return f'{self.__class__.__name__}({", ".join(enabled_fields)})'
