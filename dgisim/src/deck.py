from __future__ import annotations
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from typing_extensions import override

from .helper.hashable_dict import HashableDict

if TYPE_CHECKING:
    from .character.character import Character
    from .card.card import Card

__all__ = [
    "Deck",
    "MutableDeck",
    "FrozenDeck",
]


class Deck(ABC):
    chars: Sequence[type[Character]]
    cards: dict[type[Card], int]

    @property
    @abstractmethod
    def immutable(self) -> bool:
        pass

    def to_frozen(self) -> FrozenDeck:
        return FrozenDeck(chars=tuple(self.chars), cards=HashableDict.from_dict(self.cards))

    def to_mutable(self) -> MutableDeck:
        return MutableDeck(chars=list(self.chars), cards=dict(self.cards))


@dataclass
class MutableDeck(Deck):
    chars: list[type[Character]]
    cards: dict[type[Card], int]

    @property
    @override
    def immutable(self) -> bool:
        return False


@dataclass(frozen=True)
class FrozenDeck(Deck):
    chars: tuple[type[Character], ...]
    cards: HashableDict[type[Card], int]

    def __post_init__(self):
        assert self.cards.frozen()

    @property
    @override
    def immutable(self) -> bool:
        return True
