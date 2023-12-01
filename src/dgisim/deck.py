from __future__ import annotations
from abc import abstractmethod, ABC
from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, Sequence

from typing_extensions import override, Self

from .helper.hashable_dict import HashableDict

if TYPE_CHECKING:
    from .character.character import Character
    from .card.card import Card
    from .encoding.encoding_plan import EncodingPlan

__all__ = [
    "Deck",
    "MutableDeck",
    "FrozenDeck",
]


class Deck(ABC):
    """
    An abstract class representing a deck of cards.
    """
    chars: Sequence[type[Character]]
    cards: dict[type[Card], int]

    @property
    @abstractmethod
    def immutable(self) -> bool:
        """ :returns: `True` if the deck is immutable. """
        pass

    def to_frozen(self) -> FrozenDeck:
        """ :returns: An immutable copy of the deck. """
        return FrozenDeck(chars=tuple(self.chars), cards=HashableDict.from_dict(self.cards))

    def to_mutable(self) -> MutableDeck:
        """ :returns: A mutable copy of the deck. """
        return MutableDeck(chars=list(self.chars), cards=dict(self.cards))

    _JSON_CHARS = "chars"
    _JSON_CARDS = "cards"

    def to_json(self) -> str:
        """ :returns: A JSON string representing the deck. """
        chars: list[str] = [
            char.__name__
            for char in self.chars
        ]
        cards: dict[str, int] = {
            card.__name__: count
            for card, count in self.cards.items()
        }
        import json
        return json.dumps({
            self._JSON_CHARS: chars,
            self._JSON_CARDS: cards,
        })

    @classmethod
    @abstractmethod
    def from_json(cls, data: str) -> None | Self:
        """ :returns: A deck parsed from the given JSON string. """
        pass

    @classmethod
    def _from_json(cls, data: str) -> None | tuple[list[type[Character]], dict[type[Card], int]]:
        try:
            import json
            data_dict = json.loads(data)
            assert isinstance(data_dict, dict)
            chars_str_list = data_dict[cls._JSON_CHARS]
            assert isinstance(chars_str_list, list)
            cards_str_dict = data_dict[cls._JSON_CARDS]
            assert isinstance(cards_str_dict, dict)

            # chars
            from .character import character as chars
            chars_list = [
                chars.__dict__[char_str]
                for char_str in chars_str_list
            ]

            # cards
            from .card import card as cards
            cards_dict = {
                cards.__dict__[card_str]: count
                for card_str, count in cards_str_dict.items()
            }
            return chars_list, cards_dict
        except Exception as e:
            print(e)
            return None

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """ :returns: A list of integers representing the deck. """
        from .card.cards import Cards
        return list(chain(
            [encoding_plan.code_for(char) for char in self.chars],
            [0] * (3 - len(self.chars)),
            Cards(self.cards).encoding(encoding_plan),
        ))

    @classmethod
    @abstractmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | Self:
        """ :returns: A deck parsed from the given list of integers. """
        pass

    @classmethod
    def _decoding(
            cls,
            encoding: list[int],
            encoding_plan: EncodingPlan
    ) -> None | tuple[list[type[Character]], dict[type[Card], int]]:
        from .character.character import Character
        chars = [
            char
            for code in encoding[:3]
            if (char := encoding_plan.type_for(code)) is not None
        ]
        if not all(issubclass(char, Character) for char in chars):
            return None
        from .card.cards import Cards
        cards = Cards.decoding(encoding[3:], encoding_plan)
        if cards is None:
            return None
        return chars, cards._cards  # type: ignore

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Deck)
            and tuple(self.chars) == tuple(other.chars)
            and HashableDict(self.cards) == HashableDict(other.cards)
        )


@dataclass(eq=False)
class MutableDeck(Deck):
    chars: list[type[Character]]
    cards: dict[type[Card], int]

    @property
    @override
    def immutable(self) -> bool:
        return False

    @classmethod
    def from_json(cls, data: str) -> None | Self:
        ret_val = cls._from_json(data)
        if ret_val is None:
            return None
        return cls(
            chars=ret_val[0],
            cards=ret_val[1],
        )

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | Self:
        ret_val = cls._decoding(encoding, encoding_plan)
        if ret_val is None:
            return None
        return cls(
            chars=ret_val[0],
            cards=ret_val[1],
        )


@dataclass(frozen=True, eq=False)
class FrozenDeck(Deck):
    chars: tuple[type[Character], ...]
    cards: HashableDict[type[Card], int]

    def __post_init__(self):
        assert self.cards.frozen()

    @property
    @override
    def immutable(self) -> bool:
        return True

    @classmethod
    def from_json(cls, data: str) -> None | Self:
        mutable_deck = MutableDeck.from_json(data)
        if mutable_deck is None:
            return None
        return mutable_deck.to_frozen()  # type: ignore

    @classmethod
    def decoding(cls, encoding: list[int], encoding_plan: EncodingPlan) -> None | Self:
        mutable_deck = MutableDeck.decoding(encoding, encoding_plan)
        if mutable_deck is None:
            return None
        return mutable_deck.to_frozen()  # type: ignore
