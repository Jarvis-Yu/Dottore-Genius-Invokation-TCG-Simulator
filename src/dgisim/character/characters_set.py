from typing import FrozenSet, Type

from .character import *

DEFAULT_CHARACTERS: FrozenSet[Type[Character]] = frozenset({
    Keqing,
    Kaeya,
    RhodeiaOfLoch,
})

_DEFAULT_CHARACTERS: list[type[Character]] = [
    Keqing,
    Kaeya,
    RhodeiaOfLoch,
]

_DEFAULT_CHARACTER_FSET = None


def default_characters() -> frozenset[type[Character]]:
    global _DEFAULT_CHARACTER_FSET
    if _DEFAULT_CHARACTER_FSET is None:
        _DEFAULT_CHARACTER_FSET = frozenset(_DEFAULT_CHARACTERS)
    return _DEFAULT_CHARACTER_FSET
