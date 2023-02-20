from enum import Enum
from typing import FrozenSet

from dgisim.src.card.card import *

DEFAULT_CARDS: FrozenSet[Card] = frozenset({
    SweetMadame(),
    MondstadtHashBrown(),
    JueyunGuoba(),
    LotusFlowerCrisp(),
    MintyMeatRolls(),
    MushroomPizza(),
    NorthernSmokedChicken(),
    Starsigns(),
})