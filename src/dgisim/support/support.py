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
from dataclasses import dataclass, fields, replace
from enum import Enum
from itertools import chain
from typing import ClassVar, TYPE_CHECKING
from typing_extensions import Self, override

import random

from ..dice import AbstractDice, ActualDice
from ..effect import effect as eft
from ..event import *
from ..status import status as stt

from ..character.enums import CharacterSkillType
from ..effect.enums import TriggeringSignal, Zone
from ..effect.structs import StaticTarget
from ..element import Element, PURE_ELEMENTS
from ..helper.quality_of_life import BIG_INT, classproperty
from ..status.enums import Informables, Preprocessables

if TYPE_CHECKING:
    from ..card.card import Card
    from ..encoding.encoding_plan import EncodingPlan
    from ..state.game_state import GameState

__all__ = [
    # base
    "Support",

    # concrete implementations
    ## Companions ##
    "ChangTheNinthSupport",
    "ChefMaoSupport",
    "DunyarzadSupport",
    "LibenSupport",
    "LiuSuSupport",
    "MamereSupport",
    "MasterZhangSupport",
    "PaimonSupport",
    "RanaSupport",
    "SetariaSupport",
    "TimaeusSupport",
    "WagnerSupport",
    "XudongSupport",
    "YayoiNanatsukiSupport",

    ## Item ##
    "NRESupport",
    "ParametricTransformerSupport",
    "TreasureSeekingSeelieSupport",

    ## Locations ##
    "KnightsOfFavoniusLibrarySupport",
    "LiyueHarborWharfSupport",
    "SumeruCitySupport",
    "TenshukakuSupport",
    "VanaranaSupport",
]


@dataclass(frozen=True, kw_only=True)
class Support(stt.Status):
    #: a unique identifier for each support, used to distinguish supports of the same type.
    sid: int

    @override
    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: None | StaticTarget = None,
    ) -> bool:
        active_char = game_state.get_player(status_source.pid).get_active_character()
        if active_char is None:
            return False
        return StaticTarget(
            pid=status_source.pid,
            zone=Zone.CHARACTERS,
            id=active_char.id,
        ) == target

    def __str__(self) -> str:  # pragma: no cover
        return self.__class__.__name__.removesuffix("Support") \
            + f"<{str(self.sid)}>" \
            + self.content_str()

    def content_str(self) -> str:  # pragma: no cover
        return ""


@dataclass(frozen=True, kw_only=True)
class ChangTheNinthSupport(Support, stt._UsageLivingStatus):
    usages: int = 0  # this is the "Inspiration" of the card
    MAX_USAGES: ClassVar[int] = 3
    listening: bool = False
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.PRE_SKILL_USAGE:
            assert not self.listening
            return replace(self, listening=True)
        elif info_type is Informables.REACTION_TRIGGERED and self.listening and not self.activated:
            return replace(self, activated=True, listening=False)
        elif info_type is Informables.DMG_DEALT and self.listening and not self.activated:
            assert isinstance(information, DmgIEvent)
            if (
                    information.dmg.reaction is not None
                    or information.dmg.element is Element.PIERCING
                    or information.dmg.element is Element.PHYSICAL
            ):
                return replace(self, activated=True, listening=False)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            d_usages = 1 if self.activated else 0
            if self.usages + d_usages == self.MAX_USAGES:
                return [
                    eft.DrawRandomCardEffect(
                        pid=source.pid,
                        num=2,
                    ),
                ], None
            assert self.usages + d_usages < self.MAX_USAGES
            return [], replace(self, usages=d_usages, activated=False, listening=False)
        return [], self

    @override
    def content_str(self) -> str:
        return f"{self.usages}|{self.listening}|{self.activated}"


@dataclass(frozen=True, kw_only=True)
class ChefMaoSupport(Support, stt._UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    triggered: bool = False  # should draw on POST_CARD signal
    drawed: bool = False  # drawed this match
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_CARD,
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
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            from ..card.card import FoodCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, FoodCard)
            ):
                if (self.usages > 0 or not self.drawed) and not self.triggered:
                    return item, replace(self, triggered=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_CARD and self.triggered:
            from ..card.card import FoodCard
            assert self.usages > 0
            effects: list[eft.Effect] = [
                eft.AddDiceEffect(
                    pid=source.pid,
                    element=random.choice(tuple(PURE_ELEMENTS)),
                    num=1,
                ),
            ]
            if not self.drawed:
                effects.append(eft.DrawRandomCardOfTypeEffect(
                    pid=source.pid,
                    num=1,
                    card_type=FoodCard,
                ))
            return effects, replace(self, usages=-1, drawed=True, triggered=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            assert not self.triggered
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class DunyarzadSupport(Support, stt._UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    can_draw: bool = False  # should draw on POST_CARD signal
    drawed: bool = False  # drawed this match
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_CARD,
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
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            from ..card.card import CompanionCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, CompanionCard)
            ):
                new_item, new_self = item, self
                if self.usages > 0 and item.dice_cost.can_cost_less_elem():
                    new_item = new_item.with_new_cost(new_item.dice_cost.cost_less_elem(1))
                    new_self = replace(new_self, usages=new_self.usages - 1)
                if not self.drawed and not self.can_draw:
                    new_self = replace(new_self, can_draw=True)
                return new_item, new_self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_CARD and self.can_draw:
            from ..card.card import CompanionCard
            return [
                eft.DrawRandomCardOfTypeEffect(
                    pid=source.pid,
                    num=1,
                    card_type=CompanionCard,
                )
            ], replace(self, usages=0, can_draw=False, drawed=True)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class LibenSupport(Support, stt._UsageLivingStatus):
    usages: int = 0
    MAX_USAGES: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            this_player = game_state.get_player(source.pid)
            dice = this_player.dice
            if dice.is_empty():
                return [], self
            curr_size = 0
            ordered_dice = dice.readonly_dice_collection_ordered()
            used_dice: dict[Element, int] = {}
            for elem, num in ordered_dice.items():
                num_used = 1
                if elem is Element.OMNI:
                    num_used = min(self.MAX_USAGES - self.usages - curr_size, num)
                curr_size += num_used
                used_dice[elem] = num_used
                if curr_size + self.usages == self.MAX_USAGES:
                    break
                assert curr_size + self.usages < self.MAX_USAGES
            return [
                eft.RemoveDiceEffect(
                    pid=source.pid,
                    dice=ActualDice(used_dice),
                ),
            ], replace(self, usages=curr_size)
        elif signal is TriggeringSignal.ROUND_START and self.usages == self.MAX_USAGES:
            return [
                eft.DrawRandomCardEffect(
                    pid=source.pid,
                    num=2,
                ),
                eft.AddDiceEffect(
                    pid=source.pid,
                    element=Element.OMNI,
                    num=2,
                ),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class LiuSuSupport(Support, stt._UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = True
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.SELF_SWAP and self.activated:
            active_char = game_state.get_player(source.pid).get_active_character()
            if active_char is not None and active_char.energy == 0:
                return [
                    eft.EnergyRechargeEffect(
                        target=StaticTarget.from_char_id(source.pid, active_char.id),
                        recharge=1,
                    )
                ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and not self.activated:
            return [], replace(self, usages=0, activated=True)
        return [], self


@dataclass(frozen=True, kw_only=True)
class MamereSupport(Support, stt._UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    activated: bool = True  # whether the effect can be triggered this round
    triggered: bool = False  # whether the effect has been triggered by card playing
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_CARD,
        TriggeringSignal.ROUND_END,
    ))

    @classproperty
    def _card_categories(cls) -> tuple[type[Card], ...]:
        from ..card.card import FoodCard, LocationCard, CompanionCard, ItemCard
        return (
            FoodCard,
            LocationCard,
            CompanionCard,
            ItemCard,
        )

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.CARD1 and self.activated:
            from ..card.card import Mamere
            assert isinstance(item, CardPEvent)
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, self._card_categories)
                    and item.card_type is not Mamere
            ):
                return item, replace(self, triggered=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_CARD and self.triggered:
            from random import choice
            from ..card.card import Mamere
            assert self.activated
            card_pool = [
                card
                for card in game_state.mode.all_cards()
                if issubclass(card, self._card_categories) and card is not Mamere
            ]
            return [
                eft.PrivateAddCardEffect(
                    pid=source.pid,
                    card=choice(card_pool),
                )
            ], replace(self, usages=-1, triggered=False, activated=False)
        elif signal is TriggeringSignal.ROUND_END and not self.activated:
            assert not self.triggered
            return [], replace(self, usages=0, activated=True)
        return [], self


@dataclass(frozen=True, kw_only=True)
class MasterZhangSupport(Support, stt._UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    COST_DEDUCTION: ClassVar[int] = 1
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
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            from ..card.card import WeaponEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, WeaponEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
                    and self.usages > 0
            ):
                self_chars = game_state.get_player(status_source.pid).characters
                additional_deduction = sum([
                    1
                    for char in self_chars
                    if char.character_statuses.find_type(stt.WeaponEquipmentStatus) is not None
                ])
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(
                        self.COST_DEDUCTION + additional_deduction
                    )),
                    replace(self, usages=self.usages - 1),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self



@dataclass(frozen=True, kw_only=True)
class PaimonSupport(Support, stt._UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    NUM_GENERATED: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_START:
            return [
                eft.AddDiceEffect(
                    pid=source.pid,
                    element=Element.OMNI,
                    num=self.NUM_GENERATED,
                ),
            ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class RanaSupport(Support, stt._UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    AUTO_DESTROY: ClassVar[bool] = False
    triggered: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE and self.usages > 0 and not self.triggered:
            assert isinstance(information, SkillIEvent)
            if (
                    information.source.pid is status_source.pid
                    and information.skill_true_type is CharacterSkillType.ELEMENTAL_SKILL
            ):
                return replace(self, triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.triggered:
            next_char = game_state.get_player(
                source.pid
            ).characters.get_nth_next_alive_character_in_activity_order(1)
            return [
                eft.AddDiceEffect(
                    pid=source.pid,
                    element=next_char.ELEMENT,
                    num=1,
                ),
            ], replace(self, usages=-1, triggered=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            assert not self.triggered
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class SetariaSupport(Support, stt._UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_ANY,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_ANY:
            hand_cards = game_state.get_player(source.pid).hand_cards
            if hand_cards.num_cards() == 0:
                return [
                    eft.DrawRandomCardEffect(
                        pid=source.pid,
                        num=1,
                    ),
                ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TimaeusSupport(Support, stt._UsageLivingStatus):
    usages: int = 2
    used: bool = False
    MAX_USAGES: ClassVar[int] = BIG_INT
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
        if signal is Preprocessables.CARD2:
            assert isinstance(item, CardPEvent)
            from ..card.card import ArtifactEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, ArtifactEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
                    and item.dice_cost.num_dice() <= self.usages
                    and not self.used
            ):
                return (
                    item.with_new_cost(AbstractDice.from_empty()), 
                    replace(
                        self,
                        usages=self.usages - item.dice_cost.num_dice(),
                        used=True,
                    ),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=1, used=False)
        return [], self

    @override
    def content_str(self) -> str:
        return f"({self.usages}{'*' if not self.used else ''})"


@dataclass(frozen=True, kw_only=True)
class WagnerSupport(Support, stt._UsageLivingStatus):
    usages: int = 2
    used: bool = False
    MAX_USAGES: ClassVar[int] = BIG_INT
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
        if signal is Preprocessables.CARD2:
            assert isinstance(item, CardPEvent)
            from ..card.card import WeaponEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, WeaponEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
                    and item.dice_cost.num_dice() <= self.usages
                    and not self.used
            ):
                return (
                    item.with_new_cost(AbstractDice.from_empty()), 
                    replace(
                        self,
                        usages=self.usages - item.dice_cost.num_dice(),
                        used=True,
                    ),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=1, used=False)
        return [], self

    @override
    def content_str(self) -> str:
        return f"({self.usages}{'*' if not self.used else ''})"


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
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            from ..card.card import FoodCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, FoodCard)
                    and item.dice_cost.can_cost_less_elem()
                    and self.usages > 0
            ):
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(self.COST_DEDUCTION)), 
                    replace(self, usages=self.usages - 1),
                )
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
class YayoiNanatsukiSupport(Support, stt._UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    COST_DEDUCTION: ClassVar[int] = 1
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
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            from ..card.card import ArtifactEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, ArtifactEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
                    and self.usages > 0
            ):
                self_chars = game_state.get_player(status_source.pid).characters
                additional_deduction = sum([
                    1
                    for char in self_chars
                    if char.character_statuses.find_type(stt.ArtifactEquipmentStatus) is not None
                ])
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(
                        self.COST_DEDUCTION + additional_deduction
                    )),
                    replace(self, usages=self.usages - 1),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class NRESupport(Support, stt._UsageLivingStatus):
    # Game Test Result:
    #   If there's no food left in the deck, then it is still activated and got usages decrement
    #   (tested by using Sumeru Resonance with NRE)
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_CARD,
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
        from ..card.card import FoodCard
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            if (
                    not self.activated
                    and self.usages > 0
                    and item.pid is status_source.pid
                    and issubclass(item.card_type, FoodCard)
            ):
                return item, replace(self, activated=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        from ..card.card import FoodCard
        if signal is TriggeringSignal.POST_CARD and self.activated:
            return [
                eft.DrawRandomCardOfTypeEffect(
                    pid=source.pid,
                    num=1,
                    card_type=FoodCard,
                ),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            assert not self.activated
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ParametricTransformerSupport(Support, stt._UsageLivingStatus):
    usages: int = 0
    MAX_USAGES: ClassVar[int] = 3
    listening: bool = False
    activated: bool = False
    NUM_DICE_GENERATED: ClassVar[int] = 3

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.PRE_SKILL_USAGE:
            assert not self.listening
            return replace(self, listening=True)
        elif info_type is Informables.DMG_DEALT and self.listening and not self.activated:
            assert isinstance(information, DmgIEvent)
            from ..dice import _PURE_ELEMS
            if information.dmg.element in _PURE_ELEMS:
                return replace(self, activated=True, listening=False)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION:
            d_usages = 1 if self.activated else 0
            if self.usages + d_usages == self.MAX_USAGES:
                dice = ActualDice.from_random(
                    self.NUM_DICE_GENERATED,
                    excepted_elems={Element.OMNI},
                )
                return [
                    eft.AddDiceEffect(
                        pid=source.pid,
                        element=elem,
                        num=dice[elem],
                    )
                    for elem in dice
                ], None
            assert self.usages + d_usages < self.MAX_USAGES
            return [], replace(self, usages=d_usages, activated=False, listening=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TreasureSeekingSeelieSupport(Support, stt._UsageLivingStatus):
    usages: int = 0
    triggered: bool = False
    MAX_USAGES: ClassVar[int] = 3
    CARDS_DRAWN: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.COMBAT_ACTION,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source.pid is status_source.pid:
                return replace(self, triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.COMBAT_ACTION and self.triggered:
            if self.usages + 1 == self.MAX_USAGES:
                return [
                    eft.DrawRandomCardEffect(
                        pid=source.pid,
                        num=self.CARDS_DRAWN,
                    ),
                ], None
            assert self.usages < self.MAX_USAGES
            return [], replace(self, usages=1, triggered=False)
        return [], self


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
class LiyueHarborWharfSupport(Support, stt._UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            assert self.usages > 0
            return [
                eft.DrawRandomCardEffect(
                    pid=source.pid,
                    num=2,
                ),
            ], replace(self, usages=-1)
        return [], self

    @override
    def content_str(self) -> str:
        return f"{self.usages}"


@dataclass(frozen=True, kw_only=True)
class SumeruCitySupport(Support, stt._UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    COST_REDUCTION: ClassVar[int] = 1

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
        if signal is Preprocessables.SKILL:
            assert isinstance(item, ActionPEvent)
            if not (
                    self.usages > 0
                    and item.source.pid is status_source.pid
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item, self
            this_player = game_state.get_player(status_source.pid)
            if this_player.dice.num_dice() <= this_player.hand_cards.num_cards():
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(1)),
                    replace(self, usages=self.usages - 1),
                )
        elif signal is Preprocessables.CARD1:
            # though the part below is kinda a duplicate of the above block of code,
            # the CardPEvent may become more different with ActionPEvent in the future,
            # so leave it as it is.
            assert isinstance(item, CardPEvent)
            from ..card.card import TalentCard
            if not (
                    self.usages > 0
                    and issubclass(item.card_type, TalentCard)
                    and item.pid is status_source.pid
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item, self
            this_player = game_state.get_player(status_source.pid)
            if this_player.dice.num_dice() <= this_player.hand_cards.num_cards():
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(1)),
                    replace(self, usages=self.usages - 1),
                )
        return item, self


@dataclass(frozen=True, kw_only=True)
class TenshukakuSupport(Support):
    MINIMAL_KINDS: ClassVar[int] = 5
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_START:
            this_player_dice = game_state.get_player(source.pid).dice
            num_kinds = sum([
                1 if elem is not Element.OMNI else this_player_dice[elem]
                for elem in this_player_dice
            ])
            if num_kinds >= self.MINIMAL_KINDS:
                return [
                    eft.AddDiceEffect(
                        pid=source.pid,
                        element=Element.OMNI,
                        num=1,
                    ),
                ], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class VanaranaSupport(Support):
    saved_dice: ActualDice = ActualDice({})
    _CAPACITY: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            this_player = game_state.get_player(source.pid)
            dice = this_player.dice
            if dice.is_empty():
                return [], self
            curr_size = 0
            ordered_dice = dice.readonly_dice_collection_ordered()
            saved_dice: dict[Element, int] = {}
            for elem, num in ordered_dice.items():
                fitting_num = min(num, self._CAPACITY - curr_size)
                curr_size += fitting_num
                saved_dice[elem] = fitting_num
                if curr_size == self._CAPACITY:
                    break
            actual_saved_dice = ActualDice(saved_dice)
            return [
                eft.RemoveDiceEffect(
                    pid=source.pid,
                    dice=actual_saved_dice,
                )
            ], replace(self, saved_dice=actual_saved_dice)

        elif signal is TriggeringSignal.ROUND_START:
            if self.saved_dice.is_empty():
                return [], self
            effects: list[eft.Effect] = []
            for elem in self.saved_dice:
                effects.append(eft.AddDiceEffect(
                    pid=source.pid,
                    element=elem,
                    num=self.saved_dice[elem],
                ))
            return effects, type(self)(sid=self.sid)

        return [], self

    @override
    def perspective_view(self) -> Self:
        if self.saved_dice.num_dice() == 0:
            return self
        return replace(
            self,
            saved_dice=ActualDice.from_all(self.saved_dice.num_dice(), Element.ANY),
        )

    @override
    def content_str(self) -> str:
        return ','.join(
            f"{elem.name[:2]}:{self.saved_dice[elem]}"
            for elem in self.saved_dice
        )

    @override
    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of the content of the status. (excluding the type of status)
        """
        values = list(chain(*[
            [self.__getattribute__(field.name)]
            for field in fields(self)
        ]))
        ret_val = [encoding_plan.code_for(self)]
        for value in values:
            if isinstance(value, bool):
                ret_val.append(1 if value else 0)
            elif isinstance(value, int):
                ret_val.append(value)
            elif isinstance(value, Enum):
                assert isinstance(value.value, int), value
                ret_val.append(value.value)
            elif isinstance(value, ActualDice):
                fill_up = self._CAPACITY
                for elem in value.elems():
                    if value[elem] == 0:
                        continue
                    fill_up -= 1
                    ret_val.extend((elem.value, value[elem]))
                for _ in range(fill_up):
                    ret_val.extend((0, 0))
            else:
                raise Exception(f"unknown type {type(value)}")
        fillings = encoding_plan.STATUS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"status {self} has too many fields")
        for _ in range(fillings):
            ret_val.append(0)
        return ret_val
