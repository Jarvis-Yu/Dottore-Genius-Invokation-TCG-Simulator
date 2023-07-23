from enum import Enum

__all__ = [
    "ActionType",
]

class ActionType(Enum):
    SELECT_CARDS = 0
    SELECT_ACTIVE_CHARACTER = 1
    SELECT_DICES = 2
    PLAY_CARD = 3
    CAST_SKILL = 4
    SWAP_CHARACTER = 5
    ELEMENTAL_TUNING = 6
    END_ROUND = 7
    # SURRENDER = 8