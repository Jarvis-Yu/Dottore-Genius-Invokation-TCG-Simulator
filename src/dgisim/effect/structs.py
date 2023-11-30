from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from typing_extensions import Self

from ..helper.quality_of_life import dataclass_repr
from ..state.enums import Pid
from .enums import Zone

if TYPE_CHECKING:
    from ..encoding.encoding_plan import EncodingPlan
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

    def encoding(self, encoding_plan: "EncodingPlan") -> list[int]:
        return [
            self.pid.value,
            self.zone.value,
            self.id if isinstance(self.id, int) else encoding_plan.code_for(self.id),
        ]

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: "EncodingPlan") -> None | Self:
        pid_code = encoding[0]
        zone_code = encoding[1]
        if pid_code >= len(Pid) or zone_code >= len(Zone):
            return None
        zone = Zone(zone_code)
        id: int | type["Summon"]
        if zone is Zone.SUMMONS:
            tmp_id = encoding_plan.type_for(encoding[2])
            from ..summon.summon import Summon
            if tmp_id is None or not issubclass(tmp_id, Summon):
                return None
            id = tmp_id
        else:
            id = encoding[2]
        return cls(
            Pid(pid_code),
            zone,
            id,
        )

    def __repr__(self) -> str:
        return dataclass_repr(self)

    @classmethod
    def from_player_active(cls, game_state: "GameState", pid: Pid) -> Self:
        """
        :returns: the static target for the player `pid` in `game_state`.
        """
        return cls(
            pid,
            Zone.CHARACTERS,
            game_state.get_player(pid).just_get_active_character().get_id()
        )

    @classmethod
    def from_char_id(cls, pid: Pid, char_id: int) -> Self:
        """
        :returns: the static target for character with `char_id` of player `pid`.
        """
        return cls(pid, Zone.CHARACTERS, char_id)

    @classmethod
    def from_summon(cls, pid: Pid, summon: type["Summon"]) -> Self:
        """
        :returns: the static target for `summon` of player `pid`.
        """
        return cls(pid, Zone.SUMMONS, summon)

    @classmethod
    def from_support(cls, pid: Pid, sid: int) -> Self:
        """
        :returns: the static target for support with `sid` of player `pid`.
        """
        return cls(pid, Zone.SUPPORTS, sid)


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

    def encoding(self) -> list[int]:
        return [
            int(self.normal_attack),
            int(self.charged_attack),
            int(self.plunge_attack),
            int(self.elemental_skill),
            int(self.elemental_burst),
            int(self.status),
            int(self.summon),
            int(self.reaction),
            int(self.no_boost),
        ]

    def __repr__(self) -> str:
        cls_fields = fields(self)
        enabled_fields = [
            field.name
            for field in cls_fields
            if self.__getattribute__(field.name)
        ]
        return f'{self.__class__.__name__}({", ".join(enabled_fields)})'
