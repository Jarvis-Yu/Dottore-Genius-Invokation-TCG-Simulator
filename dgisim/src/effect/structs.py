from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from typing_extensions import Self

from ..helper.quality_of_life import dataclass_repr
from ..state.enums import Pid
from .enums import Zone

if TYPE_CHECKING:
    from ..state.game_state import GameState
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

    @classmethod
    def from_player_active(cls, game_state: "GameState", pid: Pid) -> Self:
        return cls(
            pid,
            Zone.CHARACTERS,
            game_state.get_player(pid).just_get_active_character().get_id()
        )

    @classmethod
    def from_char_id(cls, pid: Pid, char_id: int) -> Self:
        return cls(pid, Zone.CHARACTERS, char_id)


@dataclass(frozen=True, kw_only=True, repr=False)
class DamageType:
    normal_attack: bool = False
    charged_attack: bool = False
    plunge_attack: bool = False
    elemental_skill: bool = False
    elemental_burst: bool = False
    status: bool = False  # any talent, equipmenet, character status, combat status.
    summon: bool = False
    reaction: bool = False  # reaction secondary damage
    no_boost: bool = False  # Klee's burst status...

    def directly_from_character(self) -> bool:
        return self.from_character() and not self.reaction

    def from_character(self) -> bool:
        return (
            self.normal_attack
            or self.elemental_skill
            or self.elemental_burst
            or self.charged_attack
            or self.plunge_attack
        )

    def direct_normal_attack(self) -> bool:
        return self.normal_attack and not self.reaction

    def direct_charged_attack(self) -> bool:
        return self.charged_attack and not self.reaction

    def direct_plunge_attack(self) -> bool:
        return self.plunge_attack and not self.reaction

    def direct_elemental_skill(self) -> bool:
        return self.elemental_skill and not self.reaction

    def direct_elemental_burst(self) -> bool:
        return self.elemental_burst and not self.reaction

    def directly_from_summon(self) -> bool:  # pragma: no cover
        return self.summon and not self.reaction

    def directly_from_status(self) -> bool:  # pragma: no cover
        return self.status and not self.reaction

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
