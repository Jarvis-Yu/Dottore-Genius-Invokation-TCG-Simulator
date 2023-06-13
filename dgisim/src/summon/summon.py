from __future__ import annotations
from typing import ClassVar, Optional
from typing_extensions import override
from dataclasses import dataclass, replace

import dgisim.src.status.status as stt
import dgisim.src.effect.effect as eft
from dgisim.src.element.element import Element


@dataclass(frozen=True, kw_only=True)
class Summon(stt.Status):
    usages: int = -1

    def __str__(self) -> str:  # pragma: no cover
        return self.__class__.__name__.removesuffix("Summon")


@dataclass(frozen=True, kw_only=True)
class _DestroyOnNumSummon(Summon):
    @override
    def _pre_update(
            self,
            new_self: Optional[_DestroyOnNumSummon]
    ) -> Optional[_DestroyOnNumSummon]:
        """ remove the status if usages <= 0 """
        if new_self is not None and new_self.usages <= 0:
            new_self = None
        return super()._pre_update(new_self)

    def __str__(self) -> str:  # pragma: no cover
        return super().__str__() + f"({self.usages})"


@dataclass(frozen=True)
class BurningFlameSummon(_DestroyOnNumSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[BurningFlameSummon]]:
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
                )
            )
            es.append(eft.DeathCheckCheckerEffect())
        return es, replace(self, usages=d_usages)

    def _update(self, other: BurningFlameSummon) -> Optional[BurningFlameSummon]:
        new_usages = min(self.MAX_USAGES, self.usages + other.usages)
        return type(self)(usages=new_usages)
