from typing import TYPE_CHECKING

from ..character.characters_set import _DEFAULT_CHARACTERS
from ..card.cards_set import _DEFAULT_CARDS
from ..effect import effect
from ..mode import Mode, DefaultMode, AllOmniMode
from ..status import status
from ..summon import summon
from ..support import support

if TYPE_CHECKING:
    from ..character.character import Character
    from ..card.card import Card
    from ..effect.effect import Effect
    from ..status.status import Status
    from ..summon.summon import Summon
    from ..support.support import Support

__all__ = [
    "CHAR_MAPPING",
    "CARD_MAPPING",
    "EFFECT_MAPPING",
    "MODE_MAPPING",
    "STT_MAPPING",
    "SUMM_MAPPING",
    "SUPP_MAPPING",
]

CHAR_MAPPING: dict[type["Character"], int] = {
    char: 1000 + i
    for i, char in enumerate(_DEFAULT_CHARACTERS)
}

CARD_MAPPING: dict[type["Card"], int] = {
    card: 2000 + i
    for i, card in enumerate(_DEFAULT_CARDS)
}

EFFECT_MAPPING: dict[type["Effect"], int] = {
    getattr(effect, eft): 3000 + i
    for i, eft in enumerate(effect.__all__)
}

MODE_MAPPING: dict[type["Mode"], int] = {
    DefaultMode: 501,
    AllOmniMode: 502,
}

STT_MAPPING: dict[type["Status"], int] = {
    stt: 3000 + i
    for i, stt in enumerate([
        getattr(status, stt)
        for stt in status.__all__
    ])
}

SUMM_MAPPING: dict[type["Summon"], int] = {
    summ: 4000 + i
    for i, summ in enumerate([
        getattr(summon, summ)
        for summ in summon.__all__
    ])
}

SUPP_MAPPING: dict[type["Support"], int] = {
    supp: 5000 + i
    for i, supp in enumerate([
        getattr(support, supp)
        for supp in support.__all__
    ])
}
