from __future__ import annotations
from dataclasses import dataclass, replace
from typing import ClassVar, TYPE_CHECKING
from typing_extensions import Self, override

import dgisim.src.card.card as cd
import dgisim.src.effect.effect as eft
import dgisim.src.event.event as evt
import dgisim.src.state.game_state as gs
import dgisim.src.status.status as stt
from dgisim.src.effect.enums import TRIGGERING_SIGNAL
from dgisim.src.element.element import Element
from dgisim.src.helper.quality_of_life import BIG_INT
from dgisim.src.status.enums import PREPROCESSABLES

if TYPE_CHECKING:
    from dgisim.src.effect.structs import StaticTarget


@dataclass(frozen=True, kw_only=True)
class Support(stt.Status):
    sid: int

    def __str__(self) -> str:  # pragma: no cover
        return self.__class__.__name__.removesuffix("Support") \
            + f"<{str(self.sid)}>" \
            + self.content_str()

    def content_str(self) -> str:  # pragma: no cover
        return ""


@dataclass(frozen=True, kw_only=True)
class XudongSupport(Support):
    usages: int = 1
    COST_DEDUCTION: ClassVar[int] = 2

    @override
    def _preprocess(
            self,
            game_state: gs.GameState,
            status_source: StaticTarget,
            item: eft.Preprocessable,
            signal: PREPROCESSABLES,
    ) -> tuple[eft.Preprocessable, None | Self]:
        if signal is PREPROCESSABLES.CARD:
            assert isinstance(item, evt.CardEvent)
            if item.pid is status_source.pid \
                    and issubclass(item.card_type, cd.FoodCard) \
                    and item.dices_cost.num_dices() > 0 \
                    and self.usages > 0:
                # note that this only handle cases when food requires only one kind of dices
                major_elem: Element
                if item.dices_cost[Element.OMNI] == item.dices_cost.num_dices():
                    major_elem = Element.OMNI
                elif item.dices_cost[Element.ANY] == item.dices_cost.num_dices():
                    major_elem = Element.ANY
                else:
                    raise NotImplementedError
                new_cost = (item.dices_cost - {major_elem: self.COST_DEDUCTION}).validify()
                return replace(item, dices_cost=new_cost), replace(self, usages=self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, source: StaticTarget, signal: TRIGGERING_SIGNAL
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TRIGGERING_SIGNAL.ROUND_END:
            return [], type(self)(sid=self.sid)
        return [], self

    @override
    def content_str(self) -> str:
        return f"({self.usages})"
