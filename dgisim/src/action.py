from __future__ import annotations

from dgisim.src.card.cards import Cards

class Action:
    pass

class CardSelectAction(Action):
    def __init__(self, selected_cards: Cards):
        self._selected_cards = selected_cards

    def get_selected_cards(self) -> Cards:
        return self._selected_cards

    def num_cards(self) -> int:
        return self._selected_cards.num_cards()
