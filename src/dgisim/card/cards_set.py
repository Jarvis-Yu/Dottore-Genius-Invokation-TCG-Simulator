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
    DescentOfDivinity,
    EmbraceOfWinds,
    GrandExpectation,
    IGotYourBack,
    KeenSight,
    LandsOfDandelion,
    MysticalAbandon,
    NaganoharaMeteorSwarm,
    PaidInFull,
    PoeticsOfFuubutsu,
    PoundingSurprise,
    ProliferatingSpores,
    ProphecyOfSubmersion,
    RiteOfResurrection,
    SanguineRouge,
    StalwartAndTrue,
    StellarPredator,
    StrategicReserve,
    StreamingSurge,
    TamakushiCasket,
    TheScentRemained,
    TheSeedOfStoredKnowledge,
    TheShrinesSacredShade,
    ThunderingPenance,
    TranscendentAutomaton,
    UndividedHeart,
    ## Weapons ##
    ### Bow ###
    AmosBow,
    KingsSquire,
    RavenBow,
    SacrificialBow,
    ### Catalyst ###
    AThousandFloatingDreams,
    FruitOfFulfillment,
    MagicGuide,
    SacrificialFragments,
    ### Claymore ###
    SacrificialGreatsword,
    TheBell,
    WhiteIronGreatsword,
    WolfsGravestone,
    ### Polearm ###
    LithicSpear,
    VortexVanquisher,
    WhiteTassel,
    ### Sword ###
    AquilaFavonia,
    SacrificialSword,
    TravelersHandySword,
    ## Artifact ##
    GamblersEarrings,
    GeneralsAncientHelm,
    InstructorsCap,
    TenacityOfTheMillelith,

    # Event Card
    CalxsArts,
    ChangingShifts,
    ElementalResonanceEnduringRock,
    ElementalResonanceFerventFlames,
    ElementalResonanceHighVoltage,
    ElementalResonanceImpetuousWinds,
    ElementalResonanceShatteringIce,
    ElementalResonanceSoothingWater,
    ElementalResonanceSprawlingGreenery,
    ElementalResonanceWovenFlames,
    ElementalResonanceWovenIce,
    ElementalResonanceWovenStone,
    ElementalResonanceWovenThunder,
    ElementalResonanceWovenWaters,
    ElementalResonanceWovenWeeds,
    ElementalResonanceWovenWinds,
    FreshWindOfFreedom,
    IHaventLostYet,
    LeaveItToMe,
    QuickKnit,
    SendOff,
    Starsigns,
    TheBestestTravelCompanion,
    WhenTheCraneReturned,
    WhereIsTheUnseenRazor,
    WindAndFreedom,

    ## Event Card / Food ##
    JueyunGuoba,
    LotusFlowerCrisp,
    MondstadtHashBrown,
    MushroomPizza,
    MintyMeatRolls,
    NorthernSmokedChicken,
    SweetMadame,
    TandooriRoastChicken,
    TeyvatFriedEgg,

    # Support Card
    ## Support Card / Companion ##
    ChangTheNinth,
    Liben,
    Paimon,
    Xudong,
    ## Support Card / Item ##
    NRE,
    ParametricTransformer,
    ## Support Card / Location ##
    KnightsOfFavoniusLibrary,
    LiyueHarborWharf,
    SumeruCity,
    Tenshukaku,
    Vanarana,
]

_DEFAULT_CARDS_FSET = None


def default_cards() -> frozenset[type[Card]]:
    global _DEFAULT_CARDS_FSET
    if _DEFAULT_CARDS_FSET is None:
        _DEFAULT_CARDS_FSET = frozenset(_DEFAULT_CARDS)
    return _DEFAULT_CARDS_FSET
