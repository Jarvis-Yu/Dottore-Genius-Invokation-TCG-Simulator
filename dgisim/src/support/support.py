"""
This file contains the base class "Support" for all supports,
and implementation of all supports.

Note that a summon is basically a Status.

The classes are divided into 3 sections ordered. Within each section, they are
ordered alphabetically.

- base class, which is Support
- template classes, starting with an '_', are templates for other classes
- concrete classes, the implementation of summons that are actually in the game
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import ClassVar, TYPE_CHECKING
from typing_extensions import Self, override

from ..card import card as cd
from ..dices import ActualDices
from ..effect import effect as eft
from ..event import *
from ..status import status as stt

from ..effect.enums import TriggeringSignal, Zone
from ..element import Element
from ..helper.quality_of_life import BIG_INT
from ..status.enums import Preprocessables

if TYPE_CHECKING:
    from ..state.game_state import GameState
    from ..effect.structs import StaticTarget

__all__ = [
    # base
    "Support",

    # concrete implementations
    ## Companions ##
    "XudongSupport",

    ## Locations ##
    "KnightsOfFavoniusLibrarySupport",
    "VanaranaSupport",
]


@dataclass(frozen=True, kw_only=True)
class Support(stt.Status):
    sid: int

    @override
    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: StaticTarget
    ) -> bool:
        active_char = game_state.get_player(status_source.pid).get_active_character()
        if active_char is None:
            return False
        return StaticTarget(
            pid=status_source.pid,
            zone=Zone.CHARACTERS,
            id=active_char.get_id(),
        ) == target

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
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.CARD:
            assert isinstance(item, CardPEvent)
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
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], type(self)(sid=self.sid)
        return [], self

    @override
    def content_str(self) -> str:
        return f"({self.usages})"


@dataclass(frozen=True, kw_only=True)
class KnightsOfFavoniusLibrarySupport(Support):
    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.ROLL_CHANCES:
            assert isinstance(item, RollChancePEvent)
            if item.pid is status_source.pid:
                return replace(item, chances=item.chances + 1), self
        return item, self


@dataclass(frozen=True, kw_only=True)
class VanaranaSupport(Support):
    saved_dices: ActualDices = ActualDices({})
    _CAPACITY: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            this_player = game_state.get_player(source.pid)
            dices = this_player.get_dices()
            if dices.is_empty():
                return [], self
            curr_size = 0
            ordered_dices = dices.readonly_dices_ordered(this_player)
            saved_dices: dict[Element, int] = {}
            for elem, num in ordered_dices.items():
                fitting_num = min(num, self._CAPACITY - curr_size)
                curr_size += fitting_num
                saved_dices[elem] = fitting_num
                if curr_size == self._CAPACITY:
                    break
            actual_saved_dices = ActualDices(saved_dices)
            return [
                eft.RemoveDiceEffect(
                    pid=source.pid,
                    dices=actual_saved_dices,
                )
            ], replace(self, saved_dices=actual_saved_dices)

        elif signal is TriggeringSignal.ROUND_START:
            if self.saved_dices.is_empty():
                return [], self
            effects: list[eft.Effect] = []
            for elem in self.saved_dices:
                effects.append(eft.AddDiceEffect(
                    pid=source.pid,
                    element=elem,
                    num=self.saved_dices[elem],
                ))
            return effects, type(self)(sid=self.sid)

        return [], self

    @override
    def content_str(self) -> str:
        return ','.join(
            f"{elem.name[:2]}:{self.saved_dices[elem]}"
            for elem in self.saved_dices
        )
