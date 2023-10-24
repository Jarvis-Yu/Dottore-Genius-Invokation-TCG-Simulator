from typing import FrozenSet, Type

from .character import *

__all__ = [
    "default_characters",
]

_DEFAULT_CHARACTERS: list[type[Character]] = [
    Albedo,
    AratakiItto,
    Bennett,
    Collei,
    Dehya,
    ElectroHypostasis,
    FatuiPyroAgent,
    Fischl,
    Ganyu,
    HuTao,
    JadeplumeTerrorshroom,
    Jean,
    KaedeharaKazuha,
    Keqing,
    Kaeya,
    Klee,
    MaguuKenki,
    Mona,
    Nahida,
    Ningguang,
    Noelle,
    Qiqi,
    RhodeiaOfLoch,
    SangonomiyaKokomi,
    Shenhe,
    Tighnari,
    Venti,
    Xingqiu,
    YaeMiko,
    Yoimiya,
]

_DEFAULT_CHARACTER_FSET = None


def default_characters() -> frozenset[type[Character]]:
    global _DEFAULT_CHARACTER_FSET
    if _DEFAULT_CHARACTER_FSET is None:
        _DEFAULT_CHARACTER_FSET = frozenset(_DEFAULT_CHARACTERS)
    return _DEFAULT_CHARACTER_FSET
