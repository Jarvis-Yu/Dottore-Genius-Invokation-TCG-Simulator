from __future__ import annotations
from dataclasses import dataclass, replace
from typing import ClassVar, Optional, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft
from ..status import status as stt

from ..effect.enums import TRIGGERING_SIGNAL, DYNAMIC_CHARACTER_TARGET
from ..effect.structs import DamageType
from ..element.element import Element
from ..helper.quality_of_life import BIG_INT

if TYPE_CHECKING:
    from ..effect.structs import StaticTarget


@dataclass(frozen=True, kw_only=True)
class Summon(stt.Status):
    usages: int = -1

    def __str__(self) -> str:  # pragma: no cover
        return self.__class__.__name__.removesuffix("Summon") + f"({self.usages})"


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
            signal: TRIGGERING_SIGNAL,
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if new_status is None:
            return effects, new_status

        if signal is TRIGGERING_SIGNAL.END_ROUND_CHECK_OUT \
                and self.usages + new_status.usages <= 0:
            return effects, None

        return effects, new_status


@dataclass(frozen=True, kw_only=True)
class _DmgPerRoundSummon(_DestroyOnNumSummon):
    usages: int = -1
    MAX_USAGES: ClassVar[int] = BIG_INT
    DMG: ClassVar[int] = 0
    ELEMENT: ClassVar[Element] = Element.ANY  # should be overriden

    def _react_to_signal(
            self,
            source: StaticTarget,
            signal: TRIGGERING_SIGNAL
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is TRIGGERING_SIGNAL.END_ROUND_CHECK_OUT:
            d_usages = -1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DYNAMIC_CHARACTER_TARGET.OPPO_ACTIVE,
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
class BurningFlameSummon(_DmgPerRoundSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.PYRO


@dataclass(frozen=True, kw_only=True)
class OceanicMimicFrogSummon(_DestoryOnEndNumSummon, stt.FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DMG: ClassVar[int] = 2

    @override
    @staticmethod
    def _auto_destroy() -> bool:
        return False

    @override
    def _react_to_signal(
            self,
            source: StaticTarget,
            signal: TRIGGERING_SIGNAL
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        if signal is TRIGGERING_SIGNAL.END_ROUND_CHECK_OUT \
                and self.usages == 0:
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DYNAMIC_CHARACTER_TARGET.OPPO_ACTIVE,
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
