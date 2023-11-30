from __future__ import annotations
import random
from collections import Counter
from itertools import chain
from typing import Iterator, TYPE_CHECKING

from ..helper.hashable_dict import HashableDict

if TYPE_CHECKING:
    from .card import Card
    from ..encoding.encoding_plan import EncodingPlan

__all__ = [
    "Cards",
]


class Cards:
    """
    A container for easy management of cards.
    """
    def __init__(self, cards: dict[type[Card], int]) -> None:
        self._cards = HashableDict.from_dict(cards)

    @classmethod
    def from_empty(cls) -> Cards:
        """ :returns: an empty `Cards` object. """
        return Cards({})

    def __add__(self, other: Cards | dict[type[Card], int]) -> Cards:
        other_cards: dict[type[Card], int]
        if isinstance(other, Cards):
            other_cards = other._cards
        else:
            other_cards = other
        return Cards(self._cards + other_cards)

    def __sub__(self, other: Cards | dict[type[Card], int]) -> Cards:
        other_cards: dict[type[Card], int]
        if isinstance(other, Cards):
            other_cards = other._cards
        else:
            other_cards = other
        return Cards(self._cards - other_cards)

    def pick_random_cards(self, num: int) -> tuple[Cards, Cards]:
        """
        :returns: a tuple of [cards left, cards selected].

        `num` random cards are selected and returned with the left over cards.
        """
        num = min(self.num_cards(), num)
        if num == 0:
            return (self, Cards.from_empty())
        picked_cards: dict[type[Card], int] = dict(Counter(
            random.sample(list(self._cards.keys()), counts=self._cards.values(), k=num)
        ))
        return Cards(self._cards - picked_cards), Cards(picked_cards)

    def pick_random_cards_of_type(self, num: int, card_type: type[Card]) -> tuple[Cards, Cards]:
        """
        Similar to `.pick_random_cards()` but only select from cards of type `card_type`.
        """
        qualified_cards = dict(
            (c_type, c_num)
            for c_type, c_num in self._cards.items()
            if issubclass(c_type, card_type)
        )
        num = min(sum(qualified_cards.values()), num)
        if num == 0:
            return (self, Cards.from_empty())
        picked_cards: dict[type[Card], int] = dict(Counter(
            random.sample(list(qualified_cards.keys()), counts=qualified_cards.values(), k=num)
        ))
        return Cards(self._cards - picked_cards), Cards(picked_cards)

    def num_cards(self) -> int:
        """ :returns: the number of cards. """
        return sum(self._cards.values())

    def is_legal(self) -> bool:
        """ :returns: `True` if the current cards are legal (num >= 0 for each kind). """
        return all(val >= 0 for val in self._cards.values())

    def empty(self) -> bool:
        """ :returns: `True` if there's no cards. """
        return all(value == 0 for value in self._cards.values())

    def not_empty(self) -> bool:
        """ :returns: `True` if there's at least one card. """
        return any(value > 0 for value in self._cards.values())

    def contains(self, card: type[Card]) -> bool:
        """
        :returns: `True` if `card` can be found.

        Note if there's at least one `OmniCard`, then `True` is always returned.
        """
        from .card import OmniCard
        return self[card] > 0 or self[OmniCard] > 0

    def __contains__(self, card: type[Card]) -> bool:
        return self.contains(card)

    def add(self, card: type[Card]) -> Cards:
        """ :returns: new cards with addition of one `card`. """
        return self + {card: 1}

    def remove(self, card: type[Card]) -> Cards:
        """ :returns: new cards with removal of one `card`. """
        from .card import OmniCard
        if self[card] <= 0:
            assert self[OmniCard] > 0
            return self - {OmniCard: 1}  # type: ignore
        return self - {card: 1}

    def remove_all(self, card: type[Card]) -> Cards:
        """
        :returns: new cards with removal of all cards of exactly type `card`.

        If the card cannot be found, then no cards are removed no matter what.
        """
        if self[card] >= 1:
            return self - {card: self._cards[card]}
        else:
            # if the card doesn't exist, even though there might be OmniCards
            # but we don't know how many to remove, so nothing is removed
            return self

    def extend(self, cards: Cards | dict[type[Card], int], limit: None | int = None) -> Cards:
        """
        :returns: new cards with addition of `cards` discarding some if the
                  combined num exceeds limit.
        """
        if limit is not None:
            if not isinstance(cards, Cards):
                cards = Cards(cards)
            cards = cards.pick_random_cards(max(limit - self.num_cards(), 0))[1]
        return self + cards

    def hide_all(self) -> Cards:
        """
        :returns: the hidden version of cards. (replace all by `OmniCard`)
        """
        from .card import OmniCard
        return Cards({OmniCard: self.num_cards()})

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this `Cards` object.
        """
        ret_val: list[tuple[int, int]] = []
        for card, num in self._cards.items():
            if num == 0:
                continue
            ret_val.append((encoding_plan.code_for(card), num))
        ret_val.sort()
        fillings = encoding_plan.CARDS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"Too many cards: {len(self._cards)}")
        for _ in range(fillings):
            ret_val.append((0, 0))
        return list(chain.from_iterable(ret_val))

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | Cards:
        """
        :returns: the `Cards` object decoded from `encoding`.
        """
        from .card import Card
        cards: dict[type[Card], int] = {}
        for card_code, num in zip(encoding[::2], encoding[1::2]):
            if card_code == 0 or num == 0:
                break
            card = encoding_plan.type_for(card_code)
            if card is None or not issubclass(card, Card):
                return None
            cards[card] = num
        return cls(cards)

    def __getitem__(self, card: type[Card]) -> int:
        return self._cards.get(card, 0)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cards):
            return False
        return self is other or self._cards == other._cards

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._cards)

    def __repr__(self) -> str:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return (
            '{'
            + ", ".join(
                f"{key}: {val}"
                for key, val in existing_cards.items()
            )
            + '}'
        )

    def __iter__(self) -> Iterator[type[Card]]:
        return (  # type: ignore
            card
            for card in self._cards.keys()
            if self[card] > 0
        )

    def to_dict(self) -> dict[type[Card], int]:
        return dict(self._cards.items())

    def dict_str(self) -> dict:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return existing_cards
