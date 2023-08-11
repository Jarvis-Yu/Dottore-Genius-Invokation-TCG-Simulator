from .card import *

__all__ = [
    "default_cards",
]

_DEFAULT_CARDS: list[type[Card]] = [
    # Equipment Card
    ## Talents ##
    AbsorbingPrism,
    AratakiIchiban,
    ColdBloodedStrike,
    KeenSight,
    PoeticsOfFuubutsu,
    PoundingSurprise,
    ProphecyOfSubmersion,
    StreamingSurge,
    TheScentRemained,
    TheShrinesSacredShade,
    ThunderingPenance,
    ## Weapons ##
    ### Bow ###
    RavenBow,
    SacrificialBow,
    ### Catalyst ###
    MagicGuide,
    SacrificialFragments,
    ### Claymore ###
    SacrificialGreatsword,
    WhiteIronGreatsword,
    ### Polearm ###
    WhiteTassel,
    ### Sword ###
    SacrificialSword,
    TravelersHandySword,
    ## Artifact ##
    GamblersEarrings,

    # Event Card
    CalxsArts,
    ChangingShifts,
    IHaventLostYet,
    LeaveItToMe,
    QuickKnit,
    Starsigns,
    WindAndFreedom,

    ## Event Card / Food ##
    JueyunGuoba,
    LotusFlowerCrisp,
    MondstadtHashBrown,
    MushroomPizza,
    MintyMeatRolls,
    NorthernSmokedChicken,
    SweetMadame,
    TeyvatFriedEgg,

    # Support Card
    ## Support Card / Companion ##
    Xudong,
    ## Support Card / Location ##
    KnightsOfFavoniusLibrary,
    Vanarana,
]

_DEFAULT_CARDS_FSET = None


def default_cards() -> frozenset[type[Card]]:
    global _DEFAULT_CARDS_FSET
    if _DEFAULT_CARDS_FSET is None:
        _DEFAULT_CARDS_FSET = frozenset(_DEFAULT_CARDS)
    return _DEFAULT_CARDS_FSET
