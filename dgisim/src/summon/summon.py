"""
This file contains the base class "Summon" for all summons,
and implementation of all summons.

Note that a summon is basically a Status.

The classes are divided into 3 sections ordered. Within each section, they are
ordered alphabetically.

- base class, which is Summon
- template classes, starting with an '_', are templates for other classes
- concrete classes, the implementation of summons that are actually in the game
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import ClassVar, Optional, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft
from ..status import status as stt

from ..character.enums import CharacterSkill
from ..effect.enums import TriggeringSignal, DynamicCharacterTarget, Zone
from ..effect.structs import DamageType, StaticTarget
from ..element import Element, Reaction
from ..event import *
from ..helper.quality_of_life import BIG_INT
from ..status.enums import Preprocessables, Informables

if TYPE_CHECKING:
    from ..card.card import Card
    from ..state.game_state import GameState

__all__ = [
    # base
    "Summon",

    # concrete implementations
    "AutumnWhirlwindSummon",
    "BurningFlameSummon",
    "ClusterbloomArrowSummon",
    "OceanicMimicFrogSummon",
    "OceanicMimicRaptorSummon",
    "OceanicMimicSquirrelSummon",
    "UshiSummon",
]


@dataclass(frozen=True, kw_only=True)
class Summon(stt.Status):
    usages: int = -1

    def __str__(self) -> str:  # pragma: no cover
        return self.__class__.__name__.removesuffix("Summon") + f"({self.usages})"

    def content_repr(self) -> str:
        return f"{self.usages}"


@dataclass(frozen=True, kw_only=True)
class _DestroyOnNumSummon(Summon):
    @override
    def _post_update(
            self,
            new_self: Optional[_DestroyOnNumSummon]
    ) -> Optional[_DestroyOnNumSummon]:
        """ remove the status if usages <= 0 """
        if new_self is not None and new_self.usages <= 0:
            new_self = None
        return super()._post_update(new_self)


@dataclass(frozen=True, kw_only=True)
class _DestoryOnEndNumSummon(Summon):
    @override
    def _post_react_to_signal(
            self,
            effects: list[eft.Effect],
            new_status: Optional[Self],
            source: StaticTarget,
            signal: TriggeringSignal,
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if new_status is None:
            return super()._post_react_to_signal(effects, new_status, source, signal)

        if signal is TriggeringSignal.END_ROUND_CHECK_OUT \
                and self.usages + new_status.usages <= 0:
            return super()._post_react_to_signal(effects, None, source, signal)

        return super()._post_react_to_signal(effects, new_status, source, signal)


@dataclass(frozen=True, kw_only=True)
class _DmgPerRoundSummon(_DestroyOnNumSummon):
    usages: int = -1
    MAX_USAGES: ClassVar[int] = BIG_INT
    DMG: ClassVar[int] = 0
    ELEMENT: ClassVar[Element]
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            d_usages = -1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
        return es, replace(self, usages=d_usages)

    def _update(self, other: Self) -> Optional[Self]:
        new_usages = min(max(self.usages, self.MAX_USAGES), self.usages + other.usages)
        return type(self)(usages=new_usages)


@dataclass(frozen=True, kw_only=True)
class _ConvertableAnemoSummon(_DestroyOnNumSummon):
    usages: int = -1
    MAX_USAGES: ClassVar[int] = BIG_INT
    curr_elem: Element = Element.ANEMO
    ready_elem: None | Element = None
    DMG: ClassVar[int]
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    def _convertable(self) -> bool:
        return self.curr_elem is Element.ANEMO

    def _to_be_converted(self) -> bool:
        return self._convertable() and self.ready_elem is not None

    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if isinstance(information, DmgIEvent):
            damage = information.dmg
            if (
                    self._convertable()
                    and damage.source.pid is status_source.pid
                    and (
                        damage.damage_type.from_character()
                        or damage.damage_type.from_summon()
                    )
                    and damage.reaction is not None
                    and damage.reaction.reaction_type is Reaction.SWIRL
            ):
                return replace(
                    self,
                    ready_elem=damage.reaction.first_elem,
                )
        return self

    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        new_self = self
        if signal is TriggeringSignal.COMBAT_ACTION:
            if self._to_be_converted():
                new_self = replace(
                    self,
                    usages=0,  # this is delta-usages
                    curr_elem=self.ready_elem,
                    ready_elem=None
                )
                return [], new_self

        elif signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            if self._to_be_converted():
                new_self = replace(
                    self,
                    usages=0,  # this is delta-usages
                    curr_elem=self.ready_elem,
                    ready_elem=None,
                )
                es.append(eft.UpdateSummonEffect(source.pid, new_self))
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=new_self.curr_elem,
                    damage=new_self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
            if new_self._convertable():
                opponent_aura = (
                    game_state
                    .get_player(source.pid.other())
                    .just_get_active_character()
                    .get_elemental_aura()
                )
                reaction = Reaction.consult_reaction_with_aura(opponent_aura, Element.ANEMO)
                if reaction is not None and reaction.first_elem in stt._MIDARE_RANZAN_MAP:
                    new_self = replace(
                        new_self,
                        curr_elem=reaction.first_elem,
                        ready_elem=None,
                    )
            new_self = replace(
                new_self,
                usages=-1,
            )

        return es, new_self

    def _update(self, other: Self) -> Self | None:
        new_usage = min(self.usages + other.usages, max(self.usages, self.MAX_USAGES))
        return replace(other, usages=new_usage)

    def __str__(self) -> str:  # pragma: no cover
        return super().__str__() + f"({self.curr_elem}|{self.ready_elem})"

    def content_repr(self) -> str:
        return f"{self.usages}, {self.curr_elem}|{self.ready_elem}"


@dataclass(frozen=True, kw_only=True)
class AutumnWhirlwindSummon(_ConvertableAnemoSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class BurningFlameSummon(_DmgPerRoundSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.PYRO


@dataclass(frozen=True, kw_only=True)
class ClusterbloomArrowSummon(_DmgPerRoundSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.DENDRO


@dataclass(frozen=True, kw_only=True)
class OceanicMimicFrogSummon(_DestoryOnEndNumSummon, stt.FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DMG: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    @staticmethod
    def _auto_destroy() -> bool:
        return False

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT \
                and self.usages == 0:
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.HYDRO,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
            return es, None

        return es, self


@dataclass(frozen=True, kw_only=True)
class OceanicMimicRaptorSummon(_DmgPerRoundSummon):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class OceanicMimicSquirrelSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class UshiSummon(_DestoryOnEndNumSummon, stt.FixedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    SHIELD_AMOUNT: ClassVar[int] = 1
    DMG: ClassVar[int] = 1
    status_gaining_usages: int = 1
    status_gaining_available: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
        TriggeringSignal.POST_DMG,
    ))

    @override
    @staticmethod
    def _auto_destroy() -> bool:
        return False

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DELT:
            assert isinstance(information, DmgIEvent)
            if (
                    self._is_target(game_state, status_source, information.dmg)
                    and self.status_gaining_usages > 0
                    and self.status_gaining_available is False
            ):
                return replace(self, status_gaining_available=True)
        elif info_type is Informables.CHARACTER_DEATH:
            """ This is a bug that currently exists in the official game """
            assert isinstance(information, CharacterDeathIEvent)
            if not self.status_gaining_available:
                return self
            my_active_character_ref = StaticTarget(
                pid=status_source.pid,
                zone=Zone.CHARACTERS,
                id=game_state.get_player(status_source.pid).just_get_active_character().get_id()
            )
            if information.target == my_active_character_ref:
                return replace(self, status_gaining_available=False)
        return self

    @override
    def _react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.GEO,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            ], None

        elif signal is TriggeringSignal.POST_DMG:
            if self.status_gaining_available is False:
                return [], self
            assert self.status_gaining_usages > 0
            from ..character.character import AratakiItto
            itto = game_state.get_player(
                source.pid).get_characters().find_first_character(AratakiItto)
            assert itto is not None
            return [
                eft.AddCharacterStatusEffect(
                    target=StaticTarget(
                        pid=source.pid,
                        zone=Zone.CHARACTERS,
                        id=itto.get_id(),
                    ),
                    status=stt.SuperlativeSuperstrengthStatus
                )
            ], replace(
                self,
                usages=0,
                status_gaining_usages=self.status_gaining_usages - 1,
                status_gaining_available=False,
            )

        return [], self
