from __future__ import annotations
from typing import ClassVar, Optional
from typing_extensions import override
from dataclasses import dataclass, replace

import dgisim.src.status.status as stt
import dgisim.src.effect.effect as eft
from dgisim.src.element.element import Element


@dataclass(frozen=True, kw_only=True)
class Summon(stt.Status):
    num: int = -1
    
    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Summon")


@dataclass(frozen=True, kw_only=True)
class _DestroyOnNumSummon(Summon):
    @override
    def _preprocessed_react_to_signal(
            self, effects: list[eft.Effect], new_summon: Optional[_DestroyOnNumSummon]
    ) -> tuple[list[eft.Effect], Optional[_DestroyOnNumSummon]]:
        """ remove the status if num <= 0 """
        if new_summon is None or new_summon.num <= 0:
            new_summon = None
        return super()._preprocessed_react_to_signal(effects, new_summon)

    def __str__(self) -> str:
        return super().__str__() + f"({self.num})"



@dataclass(frozen=True)
class BurningFlameSummon(Summon):
    num: int = 1
    dmg: ClassVar[int] = 1

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[BurningFlameSummon]]:
        es: list[eft.Effect] = []
        new_num = self.num
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            new_num -= 1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.PYRO,
                    damage=self.dmg,
                )
            )
        return es, replace(self, num=new_num)
