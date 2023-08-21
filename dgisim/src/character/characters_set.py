from typing import FrozenSet, Type

from .character import *

__all__ = [
    "default_characters",
]

_DEFAULT_CHARACTERS: list[type[Character]] = [
    AratakiItto,
    Bennett,
    ElectroHypostasis,
    KaedeharaKazuha,
    Keqing,
    Kaeya,
    Klee,
    Mona,
    Nahida,
    Noelle,
    RhodeiaOfLoch,
    Shenhe,
    Tighnari,
    Venti,
    Xingqiu,
    YaeMiko,
]

_DEFAULT_CHARACTER_FSET = None


def default_characters() -> frozenset[type[Character]]:
    global _DEFAULT_CHARACTER_FSET
    if _DEFAULT_CHARACTER_FSET is None:
        _DEFAULT_CHARACTER_FSET = frozenset(_DEFAULT_CHARACTERS)
    return _DEFAULT_CHARACTER_FSET
