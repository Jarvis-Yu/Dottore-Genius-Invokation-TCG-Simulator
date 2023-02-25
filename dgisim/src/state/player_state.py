from __future__ import annotations
from enum import Enum
from typing import Tuple

from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
from dgisim.src.card.cards import Cards
import dgisim.src.card.card as card
from dgisim.src.character.characters import Characters
from dgisim.src.dices import Dices
from dgisim.src.card.cards_set import DEFAULT_CARDS
from dgisim.src.character.characters_set import DEFAULT_CHARACTERS


class PlayerState:
    class act(Enum):
        ACTION_PHASE = "Action Phase"
        PASSIVE_WAIT_PHASE = "Passive Wait Phase"
        ACTIVE_WAIT_PHASE = "Aggressive Wait Phase"
        END_PHASE = "End Phase"

    def __init__(
        self,
        phase: act,
        characters: Characters,
        card_redraw_chances: int,
        dices: Dices,
        hand_cards: Cards,
        deck_cards: Cards,
        publicly_used_cards: Cards,
    ):
        # REMINDER: don't forget to update factory when adding new fields
        self._phase = phase
        self._card_redraw_chances = card_redraw_chances
        self._characters = characters
        self._dices = dices
        self._hand_cards = hand_cards
        self._deck_cards = deck_cards
        self._publicly_used_cards = publicly_used_cards

    def factory(self) -> PlayerStateFactory:
        return PlayerStateFactory(self)

    def get_phase(self) -> act:
        return self._phase

    def get_card_redraw_chances(self) -> int:
        return self._card_redraw_chances

    def get_characters(self) -> Characters:
        return self._characters

    def get_dices(self) -> Dices:
        return self._dices

    def get_hand_cards(self) -> Cards:
        return self._hand_cards

    def get_deck_cards(self) -> Cards:
        return self._deck_cards

    def get_publicly_used_cards(self) -> Cards:
        return self._publicly_used_cards

    def isEndPhase(self):
        return self._phase is self.act.END_PHASE

    @staticmethod
    def examplePlayer():
        return PlayerState(
            phase=PlayerState.act.PASSIVE_WAIT_PHASE,
            card_redraw_chances=0,
            characters=Characters.from_default(tuple([char() for char in DEFAULT_CHARACTERS][:3])),
            hand_cards=Cards(dict([(card, 0) for card in DEFAULT_CARDS])),
            dices=Dices({}),
            deck_cards=Cards(dict([(card, 2) for card in DEFAULT_CARDS])),
            publicly_used_cards=Cards(dict([(card, 0) for card in DEFAULT_CARDS])),
        )

    def _all_unique_data(self) -> Tuple:
        return (
            self._phase,
            self._card_redraw_chances,
            self._characters,
            self._dices,
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
            "Phase": level_print_single(self._phase.value, new_indent),
            "Card Redraw Chances": level_print_single(str(self._card_redraw_chances), new_indent),
            "Characters": self._characters.to_string(new_indent),
            "Dices": self._dices.to_string(new_indent),
            "Hand Cards": self._hand_cards.to_string(new_indent),
            "Deck Cards": self._deck_cards.to_string(new_indent),
            "Publicly Used Cards": self._publicly_used_cards.to_string(new_indent),
        }, indent)


class PlayerStateFactory:
    def __init__(self, player_state: PlayerState) -> None:
        self._phase = player_state.get_phase()
        self._card_redraw_chances = player_state.get_card_redraw_chances()
        self._characters = player_state.get_characters()
        self._hand_cards = player_state.get_hand_cards()
        self._dices = player_state.get_dices()
        self._deck_cards = player_state.get_deck_cards()
        self._publicly_used_cards = player_state.get_publicly_used_cards()

    def phase(self, phase: PlayerState.act) -> PlayerStateFactory:
        self._phase = phase
        return self

    def card_redraw_chances(self, chances: int) -> PlayerStateFactory:
        self._card_redraw_chances = chances
        return self

    def characters(self, characters: Characters) -> PlayerStateFactory:
        self._characters = characters
        return self

    def hand_cards(self, cards: Cards) -> PlayerStateFactory:
        self._hand_cards = cards
        return self

    def dices(self, dices: Dices) -> PlayerStateFactory:
        self._dices = dices
        return self

    def deck_cards(self, cards: Cards) -> PlayerStateFactory:
        self._deck_cards = cards
        return self

    def publicly_used_cards(self, cards: Cards) -> PlayerStateFactory:
        self._publicly_used_cards = cards
        return self

    def build(self) -> PlayerState:
        return PlayerState(
            phase=self._phase,
            card_redraw_chances=self._card_redraw_chances,
            characters=self._characters,
            hand_cards=self._hand_cards,
            dices=self._dices,
            deck_cards=self._deck_cards,
            publicly_used_cards=self._publicly_used_cards,
        )
