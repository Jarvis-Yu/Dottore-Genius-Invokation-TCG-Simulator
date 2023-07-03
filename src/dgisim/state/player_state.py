from __future__ import annotations
from typing import Callable, Optional, Union, TYPE_CHECKING

from ..card import cards as cds
from ..character import character as chr
from ..status import statuses as sts
from ..support import support as sp

from ..character.characters import Characters
from ..dices import ActualDices
from ..helper.level_print import level_print, INDENT
from ..summon.summons import Summons
from ..support.supports import Supports

from .enums import ACT

if TYPE_CHECKING:
    from ..mode import Mode


class PlayerState:
    def __init__(
        self,
        phase: ACT,
        characters: Characters,
        combat_statuses: sts.Statuses,
        summons: Summons,
        supports: Supports,
        card_redraw_chances: int,
        dices: ActualDices,
        hand_cards: cds.Cards,
        deck_cards: cds.Cards,
        publicly_used_cards: cds.Cards,
    ):
        # REMINDER: don't forget to update factory when adding new fields
        self._phase = phase
        self._card_redraw_chances = card_redraw_chances
        self._characters = characters
        self._combat_statuses = combat_statuses
        self._summons = summons
        self._supports = supports
        self._dices = dices
        self._hand_cards = hand_cards
        self._deck_cards = deck_cards
        self._publicly_used_cards = publicly_used_cards

    def factory(self) -> PlayerStateFactory:
        return PlayerStateFactory(self)

    def get_phase(self) -> ACT:
        return self._phase

    def get_card_redraw_chances(self) -> int:
        return self._card_redraw_chances

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

    def get_hand_cards(self) -> cds.Cards:
        return self._hand_cards

    def get_deck_cards(self) -> cds.Cards:
        return self._deck_cards

    def get_publicly_used_cards(self) -> cds.Cards:
        return self._publicly_used_cards

    def get_active_character(self) -> Optional[chr.Character]:
        return self._characters.get_active_character()

    def just_get_active_character(self) -> chr.Character:
        return self._characters.just_get_active_character()

    def is_action_phase(self):
        return self._phase is ACT.ACTION_PHASE

    def is_passive_wait_phase(self):
        return self._phase is ACT.PASSIVE_WAIT_PHASE

    def is_active_wait_phase(self):
        return self._phase is ACT.ACTIVE_WAIT_PHASE

    def is_end_phase(self):
        return self._phase is ACT.END_PHASE

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

    @staticmethod
    def examplePlayer(mode: Mode):
        cards = mode.all_cards()
        chars = mode.all_chars()
        return PlayerState(
            phase=ACT.PASSIVE_WAIT_PHASE,
            card_redraw_chances=0,
            characters=Characters.from_default(
                tuple([char.from_default(i + 1) for i, char in enumerate(chars)][:3])
            ),
            combat_statuses=sts.Statuses(()),
            summons=Summons((), mode.summons_limit()),
            supports=Supports((), mode.supports_limit()),
            hand_cards=cds.Cards(dict([(card, 0) for card in cards])),
            dices=ActualDices({}),
            deck_cards=cds.Cards(dict([(card, 2) for card in cards])),
            publicly_used_cards=cds.Cards(dict([(card, 0) for card in cards])),
        )

    def _all_unique_data(self) -> tuple:
        return (
            self._phase,
            self._card_redraw_chances,
            self._characters,
            self._dices,
            self._summons,
            self._supports,
            self._hand_cards,
            self._deck_cards,
            self._publicly_used_cards,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlayerState):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0):
        new_indent = indent + INDENT
        return level_print({
            "Phase": self._phase.value,
            # "Card Redraw Chances": str(self._card_redraw_chances),
            "Characters": self._characters.to_string(new_indent),
            "Dices": self._dices.to_string(new_indent),
            # "Hand Cards": self._hand_cards.to_string(new_indent),
            # "Deck Cards": self._deck_cards.to_string(new_indent),
            # "Publicly Used Cards": self._publicly_used_cards.to_string(new_indent),
        }, indent)

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
        }


class PlayerStateFactory:
    def __init__(self, player_state: PlayerState) -> None:
        self._phase = player_state.get_phase()
        self._card_redraw_chances = player_state.get_card_redraw_chances()
        self._characters = player_state.get_characters()
        self._combat_statuses = player_state.get_combat_statuses()
        self._summons = player_state.get_summons()
        self._supports = player_state.get_supports()
        self._hand_cards = player_state.get_hand_cards()
        self._dices = player_state.get_dices()
        self._deck_cards = player_state.get_deck_cards()
        self._publicly_used_cards = player_state.get_publicly_used_cards()

    def phase(self, phase: ACT) -> PlayerStateFactory:
        self._phase = phase
        return self

    def card_redraw_chances(self, chances: int) -> PlayerStateFactory:
        self._card_redraw_chances = chances
        return self

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

    def hand_cards(self, cards: cds.Cards) -> PlayerStateFactory:
        self._hand_cards = cards
        return self

    def f_hand_cards(self, f: Callable[[cds.Cards], cds.Cards]) -> PlayerStateFactory:
        return self.hand_cards(f(self._hand_cards))

    def dices(self, dices: ActualDices) -> PlayerStateFactory:
        self._dices = dices
        return self

    def f_dices(self, f: Callable[[ActualDices], ActualDices]) -> PlayerStateFactory:
        return self.dices(f(self._dices))

    def deck_cards(self, cards: cds.Cards) -> PlayerStateFactory:
        self._deck_cards = cards
        return self

    def publicly_used_cards(self, cards: cds.Cards) -> PlayerStateFactory:
        self._publicly_used_cards = cards
        return self

    def f_publicly_used_cards(self, f: Callable[[cds.Cards], cds.Cards]) -> PlayerStateFactory:
        return self.publicly_used_cards(f(self._publicly_used_cards))

    def build(self) -> PlayerState:
        return PlayerState(
            phase=self._phase,
            card_redraw_chances=self._card_redraw_chances,
            characters=self._characters,
            combat_statuses=self._combat_statuses,
            summons=self._summons,
            supports=self._supports,
            hand_cards=self._hand_cards,
            dices=self._dices,
            deck_cards=self._deck_cards,
            publicly_used_cards=self._publicly_used_cards,
        )
