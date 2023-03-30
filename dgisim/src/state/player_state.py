from __future__ import annotations
from enum import Enum
from typing import Tuple, Union, cast, Optional

from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
from dgisim.src.card.cards import Cards
import dgisim.src.card.card as card
from dgisim.src.character.characters import Characters
import dgisim.src.character.character as char
from dgisim.src.dices import ActualDices
import dgisim.src.character.character as char
from dgisim.src.event.event_pre import EventPre
# from dgisim.src.card.cards_set import DEFAULT_CARDS
# from dgisim.src.character.characters_set import DEFAULT_CHARACTERS


class PlayerState:
    class Act(Enum):
        ACTION_PHASE = "Action Phase"
        PASSIVE_WAIT_PHASE = "Passive Wait Phase"
        ACTIVE_WAIT_PHASE = "Aggressive Wait Phase"
        END_PHASE = "End Phase"

    def __init__(
        self,
        phase: Act,
        characters: Characters,
        card_redraw_chances: int,
        dices: ActualDices,
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

    def get_phase(self) -> Act:
        return self._phase

    def get_card_redraw_chances(self) -> int:
        return self._card_redraw_chances

    def get_characters(self) -> Characters:
        return self._characters

    def get_dices(self) -> ActualDices:
        return self._dices

    def get_hand_cards(self) -> Cards:
        return self._hand_cards

    def get_deck_cards(self) -> Cards:
        return self._deck_cards

    def get_publicly_used_cards(self) -> Cards:
        return self._publicly_used_cards

    def get_active_character(self) -> Optional[char.Character]:
        return self._characters.get_active_character()

    def is_action_phase(self):
        return self._phase is self.Act.ACTION_PHASE

    def is_passive_wait_phase(self):
        return self._phase is self.Act.PASSIVE_WAIT_PHASE

    def is_active_wait_phase(self):
        return self._phase is self.Act.ACTIVE_WAIT_PHASE

    def is_end_phase(self):
        return self._phase is self.Act.END_PHASE

    def is_mine(self, object: Union[char.Character, int]) -> bool:
        if isinstance(object, char.Character):
            character = cast(char.Character, object)
            return self._characters.get_id(character) is not None
        return False

    def get_possible_actions(self) -> Tuple[EventPre, ...]:
        character_skills = self._characters.get_skills()
        swaps = [
            # TypicalSwapCharacterEvent(id)
            # for id in self._characters.get_swappable_ids()
        ]
        return tuple([
            action
            for actions in [character_skills, swaps]
            for action in actions
        ])

    import dgisim.src.mode as md
    @staticmethod
    def examplePlayer(mode: md.Mode):
        cards = mode.all_cards()
        chars = mode.all_chars()
        return PlayerState(
            phase=PlayerState.Act.PASSIVE_WAIT_PHASE,
            card_redraw_chances=0,
            characters=Characters.from_default(
                tuple([char.from_default(i+1) for i, char in enumerate(chars)][:3])
            ),
            hand_cards=Cards(dict([(card, 0) for card in cards])),
            dices=ActualDices({}),
            deck_cards=Cards(dict([(card, 2) for card in cards])),
            publicly_used_cards=Cards(dict([(card, 0) for card in cards])),
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
            "Phase": self._phase.value,
            # "Card Redraw Chances": str(self._card_redraw_chances),
            "Characters": self._characters.to_string(new_indent),
            "Dices": self._dices.to_string(new_indent),
            # "Hand Cards": self._hand_cards.to_string(new_indent),
            # "Deck Cards": self._deck_cards.to_string(new_indent),
            # "Publicly Used Cards": self._publicly_used_cards.to_string(new_indent),
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

    def phase(self, phase: PlayerState.Act) -> PlayerStateFactory:
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

    def dices(self, dices: ActualDices) -> PlayerStateFactory:
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
