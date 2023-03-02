from __future__ import annotations

from dgisim.src.card.cards import Cards
from dgisim.src.character.characters import Characters

class PlayerAction:
    pass

class CardSelectAction(PlayerAction):
    def __init__(self, selected_cards: Cards):
        self._selected_cards = selected_cards

    def get_selected_cards(self) -> Cards:
        return self._selected_cards

    def num_cards(self) -> int:
        return self._selected_cards.num_cards()

class CharacterSelectAction(PlayerAction):
    def __init__(self, selected_character_id: Characters.CharId):
        self._selected_character_id = selected_character_id

    def get_selected_character_id(self) -> Characters.CharId:
        return self._selected_character_id

class EndRoundAction(PlayerAction):
    pass
