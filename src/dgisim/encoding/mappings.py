"""
This file contains the mappings for the encoding of the game's objects.
"""
# mypy: ignore-errors
from typing import TYPE_CHECKING

from ..card import card
from ..character import character as char
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

# min size: 700
CHAR_MAPPING: dict[type["Character"], int] = {
    c: 1000 + i
    for c, i in (
        #### Cryo 000 ####
        (char.Ganyu, 0),
        # (char.Diona, 1),
        (char.Kaeya, 2),
        # (char.Chongyun, 3),
        # (char.KamisatoAyaka, 4),
        # (char.Eula, 5),
        (char.Shenhe, 6),
        # (char.FatuiCryoCicinMage, 7),
        (char.Qiqi, 8),

        #### Hydro 100 ####
        # (char.Barbara, 100),
        (char.Xingqiu, 101),
        (char.Mona, 102),
        (char.RhodeiaOfLoch, 103),
        # (char.MirrorMaiden, 104),
        (char.SangonomiyaKokomi, 105),
        # (char.KamisatoAyato, 106),
        # (char.Tartaglia, 107),
        # (char.Candice, 108),
        # (char.Nilou, 109),

        #### Pyro 200 ####
        # (char.Diluc, 200),
        # (char.Xiangling, 201),
        (char.Bennett, 202),
        (char.Yoimiya, 203),
        (char.FatuiPyroAgent, 204),
        (char.Klee, 205),
        # (char.Amber, 206),
        (char.HuTao, 207),
        # (char.AbyssLectorFathomlessFlames, 208),
        # (char.Yanfei, 209),
        (char.Dehya, 210),

        #### Elctro 300 ####
        (char.Fischl, 300),
        (char.Keqing, 301),
        # (char.Razor, 302),
        # (char.Cyno, 303),
        # (char.Beidou, 304),
        # (char.KujouSara, 305),
        # (char.RaidenShogun, 306),
        (char.YaeMiko, 307),
        (char.ElectroHypostasis, 308),
        # (char.Lisa, 309),
        # (char.Dori, 310),

        #### Geo 400 ####
        (char.Ningguang, 400),
        (char.Noelle, 401),
        # (char.StonehideLawachurl, 402),
        (char.AratakiItto, 403),
        # (char.Zhongli, 404),
        (char.Albedo, 405),

        #### Dendro 500 ####
        (char.Collei, 500),
        (char.JadeplumeTerrorshroom, 501),
        (char.Tighnari, 502),
        (char.Nahida, 503),
        # (char.Yaoyao, 504),
        # (char.Baizhu, 505),

        #### Anemo 600 ####
        # (char.Sucrose, 600),
        (char.Jean, 601),
        (char.MaguuKenki, 602),
        (char.Venti, 603),
        # (char.Xiao, 604),
        (char.KaedeharaKazuha, 605),
        # (char.Wanderer, 606),

        #### End 700 ####
    )
}  # type: ignore

CARD_MAPPING: dict[type["Card"], int] = {
    card: 2000 + i
    for card, i in (
        #### 0 Weapon Card 0000 ####
        #### 0.1 Catalyst 0000 ####
        (card.MagicGuide, 0),
        (card.SacrificialFragments, 1),
        # (card.SkywardAtlas, 2),
        (card.AThousandFloatingDreams, 3),
        (card.FruitOfFulfillment, 4),

        #### 0.2 Bow 0025 ####
        (card.RavenBow, 25),
        (card.SacrificialBow, 26),
        # (card.SkywardHarp, 27),
        (card.AmosBow, 28),
        # (card.ElegyForTheEnd, 29),
        (card.KingsSquire, 30),

        #### 0.3 Claymore 0050 ####
        (card.WhiteIronGreatsword, 50),
        (card.SacrificialGreatsword, 51),
        # (card.SkywardPride, 52),
        (card.WolfsGravestone, 53),
        (card.TheBell, 54),

        #### 0.4 Polearm 0075 ####
        (card.WhiteTassel, 75),
        (card.LithicSpear, 76),
        # (card.SkywardSpine, 77),
        (card.VortexVanquisher, 78),
        # (card.EngulfingLightning, 79),
        # (card.Moonpiercer, 80),

        #### 0.5 Sword 0100 ####
        (card.TravelersHandySword, 100),
        (card.SacrificialSword, 101),
        # (card.SkywardBlade, 102),
        (card.AquilaFavonia, 103),
        # (card.FavoniusSword, 104),

        #### 1 Artifact Card 0125 ####
        # (card.AdventurersBandana, 125),
        # (card.LuckyDogsSilverCirclet, 126),
        # (card.TravellingDoctorsHandkerchief, 127),
        (card.GamblersEarrings, 128),
        (card.InstructorsCap, 129),
        # (card.ExilesCirclet, 130),
        # (card.BrokenRimesEcho, 131),
        # (card.BlizzardStrayer, 132),
        # (card.WineStainedTricorne, 133),
        # (card.HeartOfDepth, 134),
        # (card.WitchsScorchingHat, 135),
        # (card.CrimsonWitchOfFlames, 136),
        # (card.ThunderSummonersCrown, 137),
        # (card.ThunderingFury, 138),
        # (card.MaskOfSolitudeBasalt, 139),
        # (card.ArchaicPetra, 140),
        # (card.LaurelCoronet, 141),
        # (card.DeepwoodMemories, 142),
        # (card.ViridescentVenerersDiadem, 143),
        # (card.ViridescentVenerer, 144),
        (card.GeneralsAncientHelm, 145),
        (card.TenacityOfTheMillelith, 146),
        # (card.OrnateKabuto, 147),
        # (card.EmblemOfSeveredFate, 148),
        # (card.CapriciousVisage, 149),
        # (card.ShimenawasReminiscence, 150),
        # (card.ThunderingPoise, 151),
        # (card.VermillionHereafter, 152),
        # (card.CrownOfWatatsumi, 153),
        # (card.OceanHuedClam, 154),
        # (card.ShadowOfTheSandKing, 155),

        #### 2 Support Card 0250 ####
        #### 2.1 Location Card 0250 ####
        (card.LiyueHarborWharf, 250),
        (card.KnightsOfFavoniusLibrary, 251),
        # (card.JadeChamber, 252),
        # (card.DawnWinery, 253),
        # (card.WangshuInn, 254),
        # (card.FavoniusCathedral, 255),
        # (card.GrandNarukamiShrine, 256),
        (card.Tenshukaku, 257),
        # (card.SangonomiyaShrine, 258),
        (card.SumeruCity, 259),
        (card.Vanarana, 260),
        # (card.ChinjuForest, 261),
        # (card.GoldenHouse, 262),
        # (card.GandharvaVille, 263),
        # (card.StormterrorsLair, 264),

        #### 2.2 Companion Card 0350 ####
        (card.Paimon, 350),
        # (card.Katheryne, 351),
        # (card.Timaeus, 352),
        # (card.Wagner, 353),
        # (card.ChefMao, 354),
        # (card.Tubby, 355),
        # (card.Timmie, 356),
        (card.Liben, 357),
        (card.ChangTheNinth, 358),
        # (card.Ellin, 359),
        # (card.IronTongueTian, 360),
        # (card.LiuSu, 361),
        # (card.Hanachirusato, 362),
        # (card.KidKjirai, 363),
        (card.Xudong, 364),
        # (card.Dunyarzad, 365),
        # (card.Rana, 366),
        # (card.MasterZhang, 367),
        # (card.Setaria, 368),
        # (card.YayoiNanatsuki, 369),

        #### 2.3 Item Card 0450 ####
        (card.ParametricTransformer, 450),
        (card.NRE, 451),
        # (card.RedFeatherFan, 452),
        # (card.TreasureSeekingSeelie, 453),

        #### 3 Event Card 0550 ####
        #### 3.1 Arcane Legend Card 0550 ####
        # (card.AncientCourtyard, 550),
        # (card.CovenantOfRock, 551),
        # (card.JoyousCelebration, 552),
        (card.FreshWindOfFreedom, 553),
        # (card.InEveryHouseAStove, 554),

        #### 3.2 Elemental Resonance Card 0600 ####
        (card.ElementalResonanceShatteringIce, 600),
        (card.ElementalResonanceSoothingWater, 601),
        (card.ElementalResonanceFerventFlames, 602),
        (card.ElementalResonanceHighVoltage, 603),
        (card.ElementalResonanceEnduringRock, 604),
        (card.ElementalResonanceSprawlingGreenery, 605),
        (card.ElementalResonanceImpetuousWinds, 606),
        (card.ElementalResonanceWovenIce, 607),
        (card.ElementalResonanceWovenWaters, 608),
        (card.ElementalResonanceWovenFlames, 609),
        (card.ElementalResonanceWovenThunder, 610),
        (card.ElementalResonanceWovenStone, 611),
        (card.ElementalResonanceWovenWeeds, 612),
        (card.ElementalResonanceWovenWinds, 613),

        #### 3.3 General Event Card 0650 ####
        (card.TheBestestTravelCompanion, 650),
        (card.ChangingShifts, 651),
        # (card.TossUp, 652),
        # (card.Strategize, 653),
        (card.IHaventLostYet, 654),
        (card.LeaveItToMe, 655),
        (card.WhenTheCraneReturned, 656),
        (card.Starsigns, 657),
        (card.CalxsArts, 658),
        # (card.MasterOfWeaponry, 659),
        # (card.BlessingOfTheDivineRelicsInstallation, 660),
        (card.QuickKnit, 661),
        (card.SendOff, 662),
        # (card.GuardiansOath, 663),
        # (card.AbyssalSummons, 664),
        # (card.FatuiConspiracy, 665),
        # (card.FriendshipEternal, 666),
        # (card.HeavyStrike, 667),
        # (card.PlungingStrike, 668),
        (card.WindAndFreedom, 669),
        # (card.StoneAndContracts, 670),
        # (card.ThunderAndEternity, 671),
        # (card.NatureAndWisdom, 672),
        # (card.TheLegendOfVennessa, 673),
        # (card.RhythmOfTheGreatDream, 674),
        (card.WhereIsTheUnseenRazor, 675),
        # (card.Pankration, 676),
        # (card.Lyresong, 677),

        #### 3.4 Food Card 0800 ####
        (card.JueyunGuoba, 800),
        (card.NorthernSmokedChicken, 801),
        (card.MintyMeatRolls, 802),
        # (card.SashimiPlatter, 803),
        (card.SweetMadame, 804),
        (card.MondstadtHashBrown, 805),
        (card.MushroomPizza, 806),
        (card.LotusFlowerCrisp, 807),
        (card.TeyvatFriedEgg, 808),
        # (card.AdeptusTemptation, 809),
        (card.TandooriRoastChicken, 810),
        # (card.ButterCrab, 811),

        #### 3.5 Character Event Card 0900 ####
        (card.LightningStiletto, 900),

        #### 4 Talent Card 0925 ####
        #### 4.1 Cryo 0925 ####
        (card.UndividedHeart, 925),
        # Diona 926
        (card.ColdBloodedStrike, 927),
        # Chongyun 928
        # KamisatoAyaka 929
        # Eula 930
        (card.MysticalAbandon, 931),
        # FatuiCryoCicinMage 932
        (card.RiteOfResurrection, 933),

        #### 4.2 Hydro 1025 ####
        # Barbara 1025
        (card.TheScentRemained, 1026),
        (card.ProphecyOfSubmersion, 1027),
        (card.StreamingSurge, 1028),
        # MirrorMaiden 1029
        (card.TamakushiCasket, 1030),
        # KamisatoAyato 1031
        # Tartaglia 1032
        # Candice 1033
        # Nilou 1034

        #### 4.3 Pyro 1125 ####
        # Diluc 1125
        # Xiangling 1126
        (card.GrandExpectation, 1127),
        (card.NaganoharaMeteorSwarm, 1128),
        (card.PaidInFull, 1129),
        (card.PoundingSurprise, 1130),
        # Amber 1131
        (card.SanguineRouge, 1132),
        # AbyssLectorFathomlessFlames 1133
        # Yanfei 1134
        (card.StalwartAndTrue, 1135),

        #### 4.4 Electro 1225 ####
        (card.StellarPredator, 1225),
        (card.ThunderingPenance, 1226),
        # Razor 1227
        # Cyno 1228
        # Beidou 1229
        # KujouSara 1230
        # RaidenShogun 1231
        (card.TheShrinesSacredShade, 1232),
        (card.AbsorbingPrism, 1233),
        # Lisa 1234
        # Dori 1235

        #### 4.5 Geo 1325 ####
        (card.StrategicReserve, 1325),
        (card.IGotYourBack, 1326),
        # StonehideLawachurl 1327
        (card.AratakiIchiban, 1328),
        # Zhongli 1329
        (card.DescentOfDivinity, 1330),

        #### 4.6 Dendro 1425 ####
        (card.FloralSidewinder, 1425),
        (card.ProliferatingSpores, 1426),
        (card.KeenSight, 1427),
        (card.TheSeedOfStoredKnowledge, 1428),
        # Yaoyao 1429
        # Baizhu 1430

        #### 4.7 Anemo 1525 ####
        # Sucrose 1525
        (card.LandsOfDandelion, 1526),
        (card.TranscendentAutomaton, 1527),
        (card.EmbraceOfWinds, 1528),
        # Xiao 1529
        (card.PoeticsOfFuubutsu, 1530),
        # Wanderer 1531

        #### End 1625 ####
    )
}

EFFECT_MAPPING: dict[type["Effect"], int] = {
    getattr(effect, eft): 4000 + i
    for i, eft in enumerate(effect.__all__)
}

MODE_MAPPING: dict[type["Mode"], int] = {
    DefaultMode: 501,
    AllOmniMode: 502,
}

STT_MAPPING: dict[type["Status"], int] = {
    stt: 5000 + i
    for i, stt in enumerate([
        getattr(status, stt)
        for stt in status.__all__
    ])
}

SUMM_MAPPING: dict[type["Summon"], int] = {
    summ: 6000 + i
    for summ, i in (
        #### Cryo 0 ####
        (summon.SacredCryoPearlSummon, 0),
        # (summon.DrunkenMistSummon, 1),
        # (summon.FrostflakeSekiNoToSummon, 2),
        (summon.ShadowswordGallopingFrostSummon, 3),
        ##(summon.CryoHilichurlShooterSummon, 4),
        # (summon.LightfallSwordSummon, 5),
        (summon.TalismanSpiritSummon, 6),
        # (summon.CryoCicinsSummon, 7),
        (summon.HeraldOfFrostSummon, 8),

        #### Hydro 100 ####
        # (summon.MelodyLoopSummon, 100),
        (summon.ReflectionSummon, 101),
        (summon.OceanicMimicSquirrelSummon, 102),
        (summon.OceanicMimicRaptorSummon, 103),
        (summon.OceanicMimicFrogSummon, 104),
        ##(summon.HydroSamachurlSummon, 105),
        ##(summon.HealingRainSummon, 106),
        (summon.BakeKurageSummon, 107),
        # (summon.GardenOfPuritySummon, 108),

        #### Pyro 200 ####
        # (summon.GuobaSummon, 200),
        (summon.BurningFlameSummon, 201),
        ##(summon.HilichurlBerserkerSummon, 202),
        # (summon.BaronBunnySummon, 203),
        # (summon.DarkfireFurnaceSummon, 204),
        (summon.FierySanctumFieldSummon, 205),

        #### Electro 300 ####
        (summon.OzSummon, 300),
        ##(summon.ElectroHilichurlShooterSummon, 301),
        ##(summon.TangleboltRingSummon, 302),
        # (summon.TenguJuuraiAmbushSummon, 303),
        # (summon.TenguJuuraiStormclusterSummon, 304),
        # (summon.EyeOfStormyJudgmentSummon, 305),
        (summon.SesshouSakuraSummon, 306),
        (summon.ChainsOfWardingThunderSummon, 307),
        # (summon.LightningRoseSummon, 308),
        # (summon.AfterSalesServiceRoundsSummon, 309),
        # (summon.JinniSummon, 310),

        #### Geo 400 ####
        (summon.UshiSummon, 400),
        # (summon.StoneSteleSummon, 401),
        (summon.SolarIsotomaSummon, 402),

        #### Dendro 500 ####
        (summon.CuileinAnbarSummon, 500),
        ##(summon.BountifulCoreSummon, 501),
        (summon.ClusterbloomArrowSummon, 502),
        # (summon.YueguiThrowingModeSummon, 503),
        # (summon.GossamerSpriteSummon, 504),

        #### Anemo(convertible) 600 ####
        (summon.DandelionFieldSummon, 600),
        (summon.ShadowswordLoneGaleSummon, 601),
        ##(summon.WhirlwindSummon, 602),

        #### Anemo(inconvertible) 650 ####
        # (summon.LargeWindSpiritSummon, 650),
        (summon.StormEyeSummon, 651),
        (summon.AutumnWhirlwindSummon, 652),

        #### End 700 ####

    )
}



SUPP_MAPPING: dict[type["Support"], int] = {
    supp: 7000 + i
    for i, supp in enumerate([
        getattr(support, supp)
        for supp in support.__all__
    ])
}
