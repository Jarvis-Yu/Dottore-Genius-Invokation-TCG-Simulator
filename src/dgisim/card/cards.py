from __future__ import annotations
import random
from collections import Counter, defaultdict
from functools import cached_property
from itertools import chain
from typing import Iterable, Iterator, Sequence, TYPE_CHECKING, TypeVar

from typing_extensions import override

from ..helper.hashable_dict import HashableDict

if TYPE_CHECKING:
    from .card import Card
    from ..encoding.encoding_plan import EncodingPlan

__all__ = [
    "Cards",
    "OrderedCards",
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

    def pick_random(self, num: int) -> tuple[Cards, Cards]:
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

    def pick_random_of_type(self, num: int, card_type: type[Card]) -> tuple[Cards, Cards]:
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

    def switch_random_different(self, cards_back: Cards) -> tuple[Cards, Cards]:
        """
        :returns: a tuple of [cards left, cards selected].

        `cards_back` is the cards to be put back into the pool,
        and `self` should be the pool.

        The selected cards try to be different from the cards in `cards_back`.
        """
        num_cards_to_pick = cards_back.num_cards()
        avoided_cards_in_pool: dict[type[Card], int] = {}
        for card in cards_back:
            avoided_cards_in_pool[card] = self[card]
        diff_pool = self - avoided_cards_in_pool
        same_pool = cards_back + avoided_cards_in_pool
        diff_pool_num = diff_pool.num_cards()

        if diff_pool_num < num_cards_to_pick:
            same_pick_num = num_cards_to_pick - diff_pool_num
            same_left, same_picked = same_pool.pick_random(
                same_pick_num
            )
            return same_left, diff_pool + same_picked
        else:
            diff_left, diff_picked = diff_pool.pick_random(num_cards_to_pick)
            return diff_left + same_pool, diff_picked

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
            cards = cards.pick_random(max(limit - self.num_cards(), 0))[1]
        return self + cards

    def hide_all(self) -> Cards:
        """
        :returns: the hidden version of cards. (replace all by `OmniCard`)
        """
        from .card import OmniCard
        return Cards({OmniCard: self.num_cards()})

    @cached_property
    def ordered_cards(self) -> tuple[type[Card], ...]:
        return tuple(Counter(self._cards).elements())  # type: ignore

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of this `Cards` object.
        """
        ret_val = [encoding_plan.encode_item(card) for card in self.ordered_cards]
        fillings = encoding_plan.CARDS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"Too many cards: {len(self._cards)}")
        for _ in range(fillings):
            ret_val.append(0)
        return ret_val

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | Cards:
        """
        :returns: the `Cards` object decoded from `encoding`.
        """
        from .card import Card
        cards: dict[type[Card], int] = defaultdict(int)
        for card_code in encoding:
            if card_code == 0:
                continue
            card = encoding_plan.type_for(card_code)
            if card is None or not issubclass(card, Card):
                return None
            cards[card] += 1
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

    def to_ordered_cards(self) -> OrderedCards:
        return OrderedCards(self.ordered_cards)

    def dict_str(self) -> dict:
        existing_cards = dict([
            (card.name(), str(num))
            for card, num in self._cards.items()
            if num != 0
        ])
        return existing_cards


class OrderedCards:
    """
    A container for easy management of cards with order.
    """
    def __init__(self, cards: Iterable[type[Card]]) -> None:
        """
        :param cards: the cards ordered from bottom to top.
        """
        self._cards = tuple(cards)

    @property
    def cards(self) -> tuple[type[Card], ...]:
        return self._cards

    def pick(self, n: int = 1) -> tuple[OrderedCards, OrderedCards]:
        """ :returns: cards left and top n cards. """
        n = min(len(self._cards), n)
        if n == 0:
            return (self, OrderedCards.from_empty())
        return (
            OrderedCards(self._cards[:-n]),
            OrderedCards(self._cards[-n:])
        )

    def pick_random_of_type(self, n: int, card_type: type[Card]) -> tuple[OrderedCards, OrderedCards]:
        """
        Similar to `.pick()` but only select from cards of type `card_type`.
        """
        qualified_indices = [
            i
            for i, card in enumerate(self._cards)
            if issubclass(card, card_type)
        ]
        n = min(len(qualified_indices), n)
        if n == 0:
            return (self, OrderedCards.from_empty())
        picked_indices = set(random.sample(qualified_indices, k=n))
        return (
            OrderedCards([card for i, card in enumerate(self._cards) if i not in picked_indices]),
            OrderedCards([card for i, card in enumerate(self._cards) if i in picked_indices]),
        )

    def switch_random_different(
            self, cards_back: OrderedCards | Iterable[type[Card]] | Cards | dict[type[Card], int]
    ) -> tuple[OrderedCards, OrderedCards]:
        """
        :returns: a tuple of [cards left, cards selected].

        `cards_back` will be put back to the pool, and `self` should be the pool.
        Put n cards back to the pool, and pick the same number of cards that are
        as different as possible back.

        As tested, cards back will be inserted back randomly, before picking
        cards (that appear not in cards back) from top to bottom. If there are
        insufficient cards, then pick from top to bottom the rest.
        (credit: https://www.bilibili.com/opus/930507267481010228)
        """
        if isinstance(cards_back, dict):
            cards_back = Cards(cards_back).to_ordered_cards()
        elif isinstance(cards_back, Cards):
            cards_back = cards_back.to_ordered_cards()
        elif not isinstance(cards_back, OrderedCards):
            cards_back = OrderedCards(cards_back)

        num_to_pick = len(cards_back)
        if num_to_pick == 0:
            return self, OrderedCards(())
        cards_to_avoid = set(cards_back._cards)
        mixed_cards = _standard_insertions(self._cards, cards_back._cards)
        indices_availabilities = [True] * len(mixed_cards)
        indiced_cards = list(enumerate(mixed_cards))
        # pick non-returned cards
        for i, card in reversed(indiced_cards):
            if card not in cards_to_avoid:
                num_to_pick -= 1
                indices_availabilities[i] = False
                if num_to_pick == 0:
                    break
        # pick any top cards left
        if num_to_pick > 0:
            for i, card in reversed(indiced_cards):
                if indices_availabilities[i]:
                    num_to_pick -= 1
                    indices_availabilities[i] = False
                    if num_to_pick == 0:
                        break
        left_ones = [card for i, card in enumerate(mixed_cards) if indices_availabilities[i]]
        picked_ones = [card for i, card in enumerate(mixed_cards) if not indices_availabilities[i]]
        return OrderedCards(left_ones), OrderedCards(picked_ones)

    def num_cards(self) -> int:
        """ :returns: the number of cards. """
        return len(self._cards)

    def empty(self) -> bool:
        """ :returns: ``True`` if there is no cards. """
        return len(self._cards) == 0
    
    def not_empty(self) -> bool:
        """ :returns: ``True`` if there are some cards. """
        return len(self._cards) > 0

    def contains(self, card: type[Card]) -> bool:
        """
        :returns: `True` if `card` can be found.

        Note if there's at least one `OmniCard`, then `True` is always returned.
        """
        from .card import OmniCard
        return any(
            c is card or c is OmniCard
            for c in self._cards
        )

    def __contains__(self, card: type[Card]) -> bool:
        return self.contains(card)

    def add(self, card: type[Card]) -> OrderedCards:
        """ :returns: new cards with this card at top. """
        return self + (card,)

    def random_add(self, cards: type[Card] | Sequence[type[Card]]) -> OrderedCards:
        """ :returns: new cards with input card(s) randomly inserted. """
        if not isinstance(cards, Sequence):
            cards = (cards,)
        return type(self)(_standard_insertions(self._cards, cards))

    def even_add(self, cards: type[Card] | Sequence[type[Card]]) -> OrderedCards:
        """
        :param cards: if it is a sequence, then it is ordered as LIFO.
        :returns: new cards with input card(s) evenly inserted.

        e.g. when 4 cards are inserted into 14 cards, the result will be:
        14 = 2 + 3 + 3 + 3 + 3; and then the 4 cards are insterted evenly.
        """
        if not isinstance(cards, Sequence):
            cards = (cards,)
        num_groups = len(cards) + 1
        remainder = len(self._cards) % num_groups
        group_len = len(self._cards) // num_groups
        group_lens = [group_len + (i <= remainder) for i in range(num_groups, 0, -1)]
        groups: list[Sequence[type[Card]]] = []
        j = 0
        for i, card in enumerate(cards):
            next_j = j + group_lens[i]
            groups.append(self._cards[j:next_j])
            j = next_j
            groups.append((card,))
        groups.append(self._cards[j:])
        return type(self)(list(chain(*groups)))

    def remove(self, card: type[Card]) -> OrderedCards:
        """ :returns: new cards with the top most card passed in removed. """
        for i, card in reversed(list(enumerate(self._cards))):
            if card is card:
                return OrderedCards(self._cards[:i] + self._cards[i + 1:])
        return self

    def remove_all(self, card: type[Card]) -> OrderedCards:
        """
        :returns: new cards with removal of all cards of exactly type `card`.
        """
        if card not in self._cards:
            return self
        return OrderedCards([c for c in self._cards if c is not card])

    def peek(self) -> None | type[Card]:
        """ :returns: the top card. """
        return self._cards[-1] if self._cards else None

    def pop(self) -> tuple[OrderedCards, None | type[Card]]:
        """ :returns: the rest of the cards and the top card. """
        if not self._cards:
            return self, None
        return OrderedCards(self._cards[:-1]), self._cards[-1]

    def extend(self, cards: OrderedCards | Iterable[type[Card]], limit: None | int = None) -> OrderedCards:
        """
        :returns: new cards with addition of `cards` at top, but discard some if exceeds limit.
        """
        if limit is not None:
            if not isinstance(cards, OrderedCards):
                cards = OrderedCards(cards)
            _, cards = cards.pick(max(limit - len(self._cards), 0))
        return self + cards

    def hide_all(self) -> OrderedCards:
        """
        :returns: the hidden version of cards. (replace all by `OmniCard`)
        """
        from .card import OmniCard
        return OrderedCards([OmniCard] * len(self._cards))

    @property
    def ordered_cards(self) -> tuple[type[Card], ...]:
        return self._cards

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        ret_val = [encoding_plan.encode_item(card) for card in self._cards]
        fillings = encoding_plan.CARDS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"Too many cards: {len(self._cards)}")
        for _ in range(fillings):
            ret_val.append(0)
        return ret_val

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | OrderedCards:
        cards: list[type[Card]] = []
        for card_code in encoding:
            if card_code == 0:
                continue
            card = encoding_plan.type_for(card_code)
            if card is None or not issubclass(card, Card):
                return None
            cards.append(card)
        return cls(cards)
    
    def __getitem__(self, card: type[Card]) -> int:
        if "__getitem_cache" not in self.__dict__:
            self.__getitem_cache = Counter(self._cards)
        return self.__getitem_cache.get(card, 0)
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, OrderedCards) and self._cards == other._cards

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._cards)

    def __repr__(self) -> str:
        return '{' + ", ".join(card.name() for card in self._cards) + '}'

    def __iter__(self) -> Iterator[type[Card]]:
        return iter(self._cards)

    def __reversed__(self) -> Iterator[type[Card]]:
        return reversed(self._cards)

    def to_dict(self) -> dict[type[Card], int]:
        return Counter(self._cards)

    def dict_str(self) -> list[str]:
        return [card.name() for card in self._cards]

    def to_cards(self) -> Cards:
        return Cards(self.to_dict())

    @classmethod
    def from_empty(cls) -> OrderedCards:
        return cls(())

    @classmethod
    def from_dict_unordered(cls, d: dict[type[Card], int]) -> OrderedCards:
        cards = list(Counter(d).elements())
        random.shuffle(cards)
        return cls(cards)

    @classmethod
    def from_dict_ordered(cls, d: dict[type[Card], int]) -> OrderedCards:
        return cls(Counter(d).elements())

    def __add__(self, other: OrderedCards | Iterable[type[Card]]) -> OrderedCards:
        if isinstance(other, OrderedCards):
            return OrderedCards(self._cards + other._cards)
        return OrderedCards(self._cards + tuple(other))

    def __radd__(self, other: OrderedCards | Iterable[type[Card]]) -> OrderedCards:
        if isinstance(other, OrderedCards):
            return OrderedCards(other._cards + self._cards)
        return OrderedCards(tuple(other) + self._cards)

    def __len__(self) -> int:
        return len(self._cards)


__T = TypeVar("__T")


def _ordered_random_mix(a: list[__T], b: list[__T]) -> list[__T]:
    """
    Achieves the effect of inserting each element of b into a randomly.
    It is unlikely to be faster when len(b) is not too big.
    """
    random.shuffle(b)

    i, j = 0, 0
    lena, lenb = len(a), len(b)
    c = []
    for _ in range(lena + lenb):
        if random.random() < lena / (lena + lenb):
            c.append(a[i])
            i += 1
            lena -= 1
        else:
            c.append(b[j])
            j += 1
            lenb -= 1
    return c


def _standard_insertions(a: Sequence[__T], b: Sequence[__T]) -> list[__T]:
    """
    Achieves the effect of inserting each element of b into a randomly.
    This performs the ordinary sequential random insertions. Faster when
    len(b) is small.
    """
    c = list(a)
    for n in b:
        c.insert(random.randint(0, len(c)), n)
    return c
