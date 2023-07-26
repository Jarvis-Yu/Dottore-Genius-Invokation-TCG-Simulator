from .card import *

__all__ = [
    "default_cards",
]

_DEFAULT_CARDS: list[type[Card]] = [
    # Equipment Card
    ## Weapons ##
    ### Bow ###
    RavenBow,
    ### Catalyst ###
    MagicGuide,
    ### Claymore ###
    WhiteIronGreatsword,
    ### Polearm ###
    WhiteTassel,
    ### Sword ###
    TravelersHandySword,
    ## Talents ##
    AratakiIchiban,
    ColdBloodedStrike,
    KeenSight,
    PoeticsOfFuubutsu,
    PoundingSurprise,
    StreamingSurge,
    ThunderingPenance,

    # Event Card
    CalxsArts,
    ChangingShifts,
    LeaveItToMe,
    QuickKnit,
    Starsigns,

    # Event Card / Food
    JueyunGuoba,
    LotusFlowerCrisp,
    MondstadtHashBrown,
    MushroomPizza,
    MintyMeatRolls,
    NorthernSmokedChicken,
    SweetMadame,

    # Support Card
    Xudong,
]

_DEFAULT_CARDS_FSET = None


def default_cards() -> frozenset[type[Card]]:
    global _DEFAULT_CARDS_FSET
    if _DEFAULT_CARDS_FSET is None:
        _DEFAULT_CARDS_FSET = frozenset(_DEFAULT_CARDS)
    return _DEFAULT_CARDS_FSET
