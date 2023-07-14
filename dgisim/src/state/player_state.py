from __future__ import annotations
from typing import Callable, Optional, Union, TYPE_CHECKING
from typing_extensions import Self

from ..character import character as chr
from ..status import statuses as sts
from ..support import support as sp

from ..card.cards import Cards
from ..character.characters import Characters
from ..dices import ActualDices
from ..summon.summons import Summons
from ..support.supports import Supports

from .enums import Act

if TYPE_CHECKING:
    from ..mode import Mode

__all__ = [
    "PlayerState",
]


class PlayerState:
    def __init__(
        self,
        phase: Act,
        characters: Characters,
        combat_statuses: sts.Statuses,
        summons: Summons,
        supports: Supports,
        card_redraw_chances: int,
        dice_reroll_chances: int,
        dices: ActualDices,
        hand_cards: Cards,
        deck_cards: Cards,
        publicly_used_cards: Cards,
        publicly_gained_cards: Cards,
    ):
        # REMINDER: don't forget to update factory when adding new fields
        self._phase = phase
        self._card_redraw_chances = card_redraw_chances
        self._dice_reroll_chances = dice_reroll_chances
        self._characters = characters
        self._combat_statuses = combat_statuses
        self._summons = summons
        self._supports = supports
        self._dices = dices
        self._hand_cards = hand_cards
        self._deck_cards = deck_cards
        self._publicly_used_cards = publicly_used_cards
        self._publicly_gained_cards = publicly_gained_cards

    def factory(self) -> PlayerStateFactory:
        return PlayerStateFactory(self)

    def get_phase(self) -> Act:
        return self._phase

    def get_card_redraw_chances(self) -> int:
        return self._card_redraw_chances

    def get_dice_reroll_chances(self) -> int:
        return self._dice_reroll_chances

    def get_characters(self) -> Characters:
        return self._characters

    def get_combat_statuses(self) -> sts.Statuses:
        return self._combat_statuses

    def get_summons(self) -> Summons:
        return self._summons

    def get_supports(self) -> Supports:
        return self._supports

    def get_dices(self) -> ActualDices:
        return self._dices

    def get_hand_cards(self) -> Cards:
        return self._hand_cards

    def get_deck_cards(self) -> Cards:
        return self._deck_cards

    def get_publicly_used_cards(self) -> Cards:
        return self._publicly_used_cards

    def get_publicly_gained_cards(self) -> Cards:
        return self._publicly_gained_cards

    def get_active_character(self) -> Optional[chr.Character]:
        return self._characters.get_active_character()

    def just_get_active_character(self) -> chr.Character:
        return self._characters.just_get_active_character()

    def is_action_phase(self) -> bool:
        return self._phase is Act.ACTION_PHASE

    def is_passive_wait_phase(self) -> bool:
        return self._phase is Act.PASSIVE_WAIT_PHASE

    def is_active_wait_phase(self) -> bool:
        return self._phase is Act.ACTIVE_WAIT_PHASE

    def is_end_phase(self) -> bool:
        return self._phase is Act.END_PHASE

    def is_mine(self, object: chr.Character | sp.Support) -> bool:
        if isinstance(object, chr.Character):
            return self._characters.get_id(object) is not None
        elif isinstance(object, sp.Support):
            support = self._supports.find(type(object), object.sid)
            return support == object
        else:
            raise NotImplementedError

    def defeated(self) -> bool:
        return self._characters.all_defeated()

    def hide_cards(self) -> PlayerState:
        return self.factory().f_hand_cards(
            lambda hcs: hcs.hide_all()
        ).f_deck_cards(
            lambda dcs: dcs.hide_all()
        ).build()

    @classmethod
    def example_player(cls, mode: Mode) -> Self:
        cards = mode.all_cards()
        chars = mode.all_chars()
        import random
        selected_cards = random.sample(list(cards), k=15)
        selected_chars = random.sample(list(chars), k=3)
        return cls(
            phase=Act.PASSIVE_WAIT_PHASE,
            card_redraw_chances=0,
            dice_reroll_chances=0,
            characters=Characters.from_default(
                tuple(char.from_default(i + 1) for i, char in enumerate(selected_chars))
            ),
            combat_statuses=sts.Statuses(()),
            summons=Summons((), mode.summons_limit()),
            supports=Supports((), mode.supports_limit()),
            dices=ActualDices({}),
            hand_cards=Cards({}),
            deck_cards=Cards(dict([(card, mode.max_cards_per_kind()) for card in selected_cards])),
            publicly_used_cards=Cards({}),
            publicly_gained_cards=Cards({}),
        )

    @classmethod
    def from_deck(cls, mode: Mode, characters: Characters, cards: Cards) -> Self:
        return cls(
            phase=Act.PASSIVE_WAIT_PHASE,
            card_redraw_chances=0,
            dice_reroll_chances=0,
            characters=characters,
            combat_statuses=sts.Statuses(()),
            summons=Summons((), mode.summons_limit()),
            supports=Supports((), mode.supports_limit()),
            dices=ActualDices({}),
            hand_cards=Cards({}),
            deck_cards=cards,
            publicly_used_cards=Cards({}),
            publicly_gained_cards=Cards({}),
        )

    def _all_unique_data(self) -> tuple:
        return (
            self._phase,
            self._card_redraw_chances,
            self._dice_reroll_chances,
            self._characters,
            self._combat_statuses,
            self._summons,
            self._supports,
            self._dices,
            self._hand_cards,
            self._deck_cards,
            self._publicly_used_cards,
            self._publicly_gained_cards,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlayerState):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def dict_str(self) -> dict[str, Union[dict, str]]:
        return {
            "Phase": self._phase.value,
            "Card Redraw Chances": str(self._card_redraw_chances),
            "Characters": self._characters.dict_str(),
            "Combat Statuses": str(self._combat_statuses),
            "Summons": self._summons.dict_str(),
            "Supports": self._supports.dict_str(),
            "Dices": self._dices.dict_str(),
            "Hand Cards": self._hand_cards.dict_str(),
            "Deck Cards": self._deck_cards.dict_str(),
            "Publicly Used Cards": self._publicly_used_cards.dict_str(),
            "Publicly Gained Cards": self._publicly_gained_cards.dict_str(),
        }


class PlayerStateFactory:
    def __init__(self, player_state: PlayerState) -> None:
        self._phase = player_state.get_phase()
        self._card_redraw_chances = player_state.get_card_redraw_chances()
        self._dice_reroll_chances = player_state.get_dice_reroll_chances()
        self._characters = player_state.get_characters()
        self._combat_statuses = player_state.get_combat_statuses()
        self._summons = player_state.get_summons()
        self._supports = player_state.get_supports()
        self._dices = player_state.get_dices()
        self._hand_cards = player_state.get_hand_cards()
        self._deck_cards = player_state.get_deck_cards()
        self._publicly_used_cards = player_state.get_publicly_used_cards()
        self._publicly_gained_cards = player_state.get_publicly_gained_cards()

    def phase(self, phase: Act) -> PlayerStateFactory:
        self._phase = phase
        return self

    def card_redraw_chances(self, chances: int) -> PlayerStateFactory:
        self._card_redraw_chances = chances
        return self

    def f_card_redraw_chances(self, f: Callable[[int], int]) -> PlayerStateFactory:  # pragma: no cover
        return self.card_redraw_chances(f(self._card_redraw_chances))

    def dice_reroll_chances(self, chances: int) -> PlayerStateFactory:
        self._dice_reroll_chances = chances
        return self

    def f_dice_reroll_chances(self, f: Callable[[int], int]) -> PlayerStateFactory:  # pragma: no cover
        return self.dice_reroll_chances(f(self._dice_reroll_chances))

    def characters(self, characters: Characters) -> PlayerStateFactory:
        self._characters = characters
        return self

    def f_characters(self, f: Callable[[Characters], Characters]) -> PlayerStateFactory:
        self._characters = f(self._characters)
        return self

    def combat_statuses(self, combat_statuses: sts.Statuses) -> PlayerStateFactory:
        self._combat_statuses = combat_statuses
        return self

    def f_combat_statuses(self, f: Callable[[sts.Statuses], sts.Statuses]) -> PlayerStateFactory:
        return self.combat_statuses(f(self._combat_statuses))

    def summons(self, summons: Summons) -> PlayerStateFactory:
        self._summons = summons
        return self

    def f_summons(self, f: Callable[[Summons], Summons]) -> PlayerStateFactory:
        return self.summons(f(self._summons))

    def supports(self, supports: Supports) -> PlayerStateFactory:
        self._supports = supports
        return self

    def f_supports(self, f: Callable[[Supports], Supports]) -> PlayerStateFactory:
        return self.supports(f(self._supports))

    def dices(self, dices: ActualDices) -> PlayerStateFactory:
        self._dices = dices
        return self

    def f_dices(self, f: Callable[[ActualDices], ActualDices]) -> PlayerStateFactory:
        return self.dices(f(self._dices))

    def hand_cards(self, cards: Cards) -> PlayerStateFactory:
        self._hand_cards = cards
        return self

    def f_hand_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.hand_cards(f(self._hand_cards))

    def deck_cards(self, cards: Cards) -> PlayerStateFactory:
        self._deck_cards = cards
        return self

    def f_deck_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.deck_cards(f(self._deck_cards))

    def publicly_used_cards(self, cards: Cards) -> PlayerStateFactory:
        self._publicly_used_cards = cards
        return self

    def f_publicly_used_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.publicly_used_cards(f(self._publicly_used_cards))

    def publicly_gained_cards(self, cards: Cards) -> PlayerStateFactory:
        self._publicly_gained_cards = cards
        return self

    def f_publicly_gained_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.publicly_gained_cards(f(self._publicly_gained_cards))

    def build(self) -> PlayerState:
        return PlayerState(
            phase=self._phase,
            card_redraw_chances=self._card_redraw_chances,
            dice_reroll_chances=self._dice_reroll_chances,
            characters=self._characters,
            combat_statuses=self._combat_statuses,
            summons=self._summons,
            supports=self._supports,
            dices=self._dices,
            hand_cards=self._hand_cards,
            deck_cards=self._deck_cards,
            publicly_used_cards=self._publicly_used_cards,
            publicly_gained_cards=self._publicly_gained_cards,
        )
