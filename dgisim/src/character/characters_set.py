from typing import FrozenSet, Type

from dgisim.src.character.character import *

DEFAULT_CHARACTERS: FrozenSet[Type[Character]] = frozenset({
    Keqing,
    Kaeya,
    Oceanid,
})
