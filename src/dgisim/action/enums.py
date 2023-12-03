from enum import Enum

__all__ = [
    "ActionType",
]

class ActionType(Enum):
    SELECT_CARDS = 1
    SELECT_ACTIVE_CHARACTER = 2
    SELECT_DICE = 3
    PLAY_CARD = 4
    CAST_SKILL = 5
    SWAP_CHARACTER = 6
    ELEMENTAL_TUNING = 7
    END_ROUND = 8
    # SURRENDER = 8