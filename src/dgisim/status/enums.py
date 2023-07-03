from __future__ import annotations
from enum import Enum

class PREPROCESSABLES(Enum):
    """ PreProcessType """
    # Swap
    SWAP = "Swap"                 # To determine if swap needs to cost more or less,
    #                             # if swap is fast action or combat action
    # Skill
    SKILL = "Skill"               # same as SWAP but for skill
    # Card
    CARD = "Card"                 # same as SWAP but for card
    # Damages
    DMG_ELEMENT = "DmgElement"    # To determine the element
    DMG_REACTION = "DmgReaction"  # To determine the reaction
    DMG_AMOUNT = "DmgNumber"      # To determine final amount of damage