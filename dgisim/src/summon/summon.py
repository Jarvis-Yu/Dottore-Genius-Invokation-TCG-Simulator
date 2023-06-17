from __future__ import annotations
from typing import ClassVar, Optional
from typing_extensions import override, Self
from dataclasses import dataclass, replace
import dgisim.src.state.game_state as gs

import dgisim.src.status.status as stt
import dgisim.src.effect.effect as eft
from dgisim.src.element.element import Element
from dgisim.src.status.status import Status


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
            signal: eft.TriggeringSignal,
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if new_status is None:
            return effects, new_status

        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT \
                and self.usages + new_status.usages <= 0:
            return effects, None

        return effects, new_status


@dataclass(frozen=True)
class BurningFlameSummon(_DestroyOnNumSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            d_usages = -1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.PYRO,
                    damage=self.DMG,
                    damage_type=eft.DamageType(summon=True),
                )
            )
        return es, replace(self, usages=d_usages)

    def _update(self, other: Self) -> Optional[Self]:
        new_usages = min(max(self.usages, self.MAX_USAGES), self.usages + other.usages)
        return type(self)(usages=new_usages)


@dataclass(frozen=True)
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
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            if self.usages == 0:
                es.append(
                    eft.ReferredDamageEffect(
                        source=source,
                        target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                        element=Element.HYDRO,
                        damage=self.DMG,
                        damage_type=eft.DamageType(summon=True),
                    )
                )
                return es, None

        return es, self
