"""
This file contains the mappings for the encoding of the game's objects.
"""
# mypy: ignore-errors
from typing import TYPE_CHECKING

from ..card import card
from ..character import character as char
from ..effect import effect
from ..helper.hashable_dict import HashableDict
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
CHAR_MAPPING: dict[type["Character"], int] = HashableDict({
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
})

CARD_MAPPING: dict[type["Card"], int] = HashableDict({
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

        #### 5 Special Card 1625 ####
        (card.OmniCard, 1625),

        #### End 1630 ####
    )
})

EFFECT_MAPPING: dict[type["Effect"], int] = HashableDict({
    eft: 4000 + i
    for eft, i in (
        #### 0 Phase Effect 000 ####
        (effect.DeathSwapPhaseStartEffect, 0),
        (effect.DeathSwapPhaseEndEffect, 1),
        (effect.EndPhaseCheckoutEffect, 2),
        (effect.EndRoundEffect, 3),
        (effect.RollPhaseStartEffect, 4),
        (effect.SetBothPlayerPhaseEffect, 5),
        (effect.TurnEndEffect, 6),
    
        #### 1 Checker Effect 050 ####
        (effect.AliveMarkCheckerEffect, 50),
        (effect.DefeatedMarkCheckerEffect, 51),
        (effect.SwapCharacterCheckerEffect, 52),
        (effect.DeathCheckCheckerEffect, 53),
        (effect.DefeatedCheckerEffect, 54),

        #### 2 Triggerrable Effect 075 ####
        #### 2.1 Triggerer Effect 075 ####
        (effect.AllStatusTriggererEffect, 75),
        (effect.PlayerStatusTriggererEffect, 76),
        (effect.PersonalStatusTriggererEffect, 77),

        #### 2.3 Trigger Effect 085
        (effect.TriggerStatusEffect, 85),
        (effect.TriggerHiddenStatusEffect, 86),
        (effect.TriggerCombatStatusEffect, 87),
        (effect.TriggerSummonEffect, 88),
        (effect.TriggerSupportEffect, 89),

        #### 3 Status Update Effect 100 ####
        #### 3.1 Character Status Update Effect 100 ####
        (effect.AddCharacterStatusEffect, 100),
        (effect.RemoveCharacterStatusEffect, 101),
        (effect.UpdateCharacterStatusEffect, 102),
        (effect.OverrideCharacterStatusEffect, 103),

        #### 3.2 Hidden Status Update Effect 125 ####
        (effect.AddHiddenStatusEffect, 125),
        (effect.RemoveHiddenStatusEffect, 126),
        (effect.UpdateHiddenStatusEffect, 127),
        (effect.OverrideHiddenStatusEffect, 128),

        #### 3.3 Combat Status Update Effect 150 ####
        (effect.AddCombatStatusEffect, 150),
        (effect.RemoveCombatStatusEffect, 151),
        (effect.UpdateCombatStatusEffect, 152),
        (effect.OverrideCombatStatusEffect, 153),

        #### 3.4 Summon Status Update Effect 175 ####
        (effect.AddSummonEffect, 175),
        (effect.RemoveSummonEffect, 176),
        (effect.UpdateSummonEffect, 177),
        (effect.OverrideSummonEffect, 178),
        (effect.AllSummonIncreaseUsageEffect, 179),
        (effect.OneSummonDecreaseUsageEffect, 180),
        (effect.OneSummonIncreaseUsageEffect, 181),

        #### 3.5 Support Status Update Effect 200 ####
        (effect.AddSupportEffect, 200),
        (effect.RemoveSupportEffect, 201),
        (effect.UpdateSupportEffect, 202),
        (effect.OverrideSupportEffect, 203),

        #### 4 Direct Effect 225 ####
        #### 4.1 Swap Character Effect 225 ####
        (effect.SwapCharacterEffect, 225),
        (effect.BackwardSwapCharacterEffect, 226),
        (effect.ForwardSwapCharacterEffect, 227),
        (effect.ForwardSwapCharacterCheckEffect, 228),

        #### 4.2 Damage Effect 250 ####
        (effect.SpecificDamageEffect, 250),
        (effect.ReferredDamageEffect, 251),

        #### 4.3 Recover Effect 260 ####
        (effect.RecoverHPEffect, 260),
        (effect.ReviveRecoverHPEffect, 261),

        #### 4.3 Energy Effect 270 ####
        (effect.EnergyRechargeEffect, 270),
        (effect.EnergyDrainEffect, 271),

        #### 4.4 Card Effect 280 ####
        (effect.DrawRandomCardEffect, 280),
        (effect.DrawRandomCardOfTypeEffect, 281),
        (effect.PublicAddCardEffect, 282),
        (effect.PublicRemoveCardEffect, 283),
        (effect.PublicRemoveAllCardEffect, 284),

        #### 4.5 Dice Effect 290 ####
        (effect.AddDiceEffect, 290),
        (effect.RemoveDiceEffect, 291),

        #### 4.5 Skill Effect 300 ####
        (effect.CastSkillEffect, 300),
        (effect.BroadcastPreSkillInfoEffect, 301),
        (effect.BroadcastPostSkillInfoEffect, 302),

        #### 4.6 Other Effect 310 ####
        (effect.ConsecutiveActionEffect, 310),
        (effect.ApplyElementalAuraEffect, 311),

        #### End 400 ####
    )
})

MODE_MAPPING: dict[type["Mode"], int] = HashableDict({
    DefaultMode: 501,
    AllOmniMode: 502,
})

STT_MAPPING: dict[type["Status"], int] = HashableDict({
    stt: 5000 + i
    for stt, i in (
        #### 0 Player Hidden Status 000 ####
        (status.ArcaneLegendUsedStatus, 0),
        (status.ChargedAttackStatus, 1),
        (status.PlungeAttackStatus, 2),
        (status.DeathThisRoundStatus, 3),

        #### 1 Equipment Status 050 ####
        #### 1.1 Weapon Status 050 ####
        #### 1.1.1 Catalyst Status 050 ####
        (status.MagicGuideStatus, 50),
        (status.SacrificialFragmentsStatus, 51),
        # (status.SkywardAtlasStatus, 52),
        (status.AThousandFloatingDreamsStatus, 53),
        (status.FruitOfFulfillmentStatus, 54),

        #### 1.1.2 Bow Status 075 ####
        (status.RavenBowStatus, 75),
        (status.SacrificialBowStatus, 76),
        # (status.SkywardHarpStatus, 77),
        (status.AmosBowStatus, 78),
        # (status.ElegyForTheEndStatus, 79),
        (status.KingsSquireStatus, 80),

        #### 1.1.3 Claymore Status 100 ####
        (status.WhiteIronGreatswordStatus, 100),
        (status.SacrificialGreatswordStatus, 101),
        # (status.SkywardPrideStatus, 102),
        (status.WolfsGravestoneStatus, 103),
        (status.TheBellStatus, 104),

        #### 1.1.4 Polearm Status 125 ####
        (status.WhiteTasselStatus, 125),
        (status.LithicSpearStatus, 126),
        # (status.SkywardSpineStatus, 127),
        (status.VortexVanquisherStatus, 128),
        # (status.EngulfingLightningStatus, 129),
        # (status.MoonpiercerStatus, 130),

        #### 1.1.5 Sword Status 150 ####
        (status.TravelersHandySwordStatus, 150),
        (status.SacrificialSwordStatus, 151),
        # (status.SkywardBladeStatus, 152),
        (status.AquilaFavoniaStatus, 153),
        # (status.FavoniusSwordStatus, 154),

        #### 1.2 Artifact Status 175 ####
        # (status.AdventurersBandanaStatus, 175),
        # (status.LuckyDogsSilverCircletStatus, 176),
        # (status.TravellingDoctorsHandkerchiefStatus, 177),
        (status.GamblersEarringsStatus, 178),
        (status.InstructorsCapStatus, 179),
        # (status.ExilesCircletStatus, 180),
        # (status.BrokenRimesEchoStatus, 181),
        # (status.BlizzardStrayerStatus, 182),
        # (status.WineStainedTricorneStatus, 183),
        # (status.HeartOfDepthStatus, 184),
        # (status.WitchsScorchingHatStatus, 185),
        # (status.CrimsonWitchOfFlamesStatus, 186),
        # (status.ThunderSummonersCrownStatus, 187),
        # (status.ThunderingFuryStatus, 188),
        # (status.MaskOfSolitudeBasaltStatus, 189),
        # (status.ArchaicPetraStatus, 190),
        # (status.LaurelCoronetStatus, 191),
        # (status.DeepwoodMemoriesStatus, 192),
        # (status.ViridescentVenerersDiademStatus, 193),
        # (status.ViridescentVenererStatus, 194),
        (status.GeneralsAncientHelmStatus, 195),
        (status.TenacityOfTheMillelithStatus, 196),
        # (status.OrnateKabutoStatus, 197),
        # (status.EmblemOfSeveredFateStatus, 198),
        # (status.CapriciousVisageStatus, 199),
        # (status.ShimenawasReminiscenceStatus, 200),
        # (status.ThunderingPoiseStatus, 201),
        # (status.VermillionHereafterStatus, 202),
        # (status.CrownOfWatatsumiStatus, 203),
        # (status.OceanHuedClamStatus, 204),
        # (status.ShadowOfTheSandKingStatus, 205),

        #### 2 Combat Status 300 ####
        #### 2.1 General Combat Status 300 ####
        (status.CatalyzingFieldStatus, 300),
        (status.DendroCoreStatus, 301),
        (status.ChangingShiftsStatus, 302),
        (status.ElementalResonanceEnduringRockStatus, 303),
        (status.ElementalResonanceFerventFlamesStatus, 304),
        (status.ElementalResonanceShatteringIceStatus, 305),
        (status.ElementalResonanceSprawlingGreeneryStatus, 306),
        (status.FreshWindOfFreedomStatus, 307),
        (status.KingsSquireEffectStatus, 308),
        (status.LeaveItToMeStatus, 309),
        (status.IHaventLostYetOnCooldownStatus, 310),
        (status.ReviveOnCooldownStatus, 311),
        (status.WhenTheCraneReturnedStatus, 312),
        (status.WhereIsTheUnseenRazorStatus, 313),
        (status.WindAndFreedomStatus, 314),

        #### 2.2 Shield Combat Status 375 ####
        (status.CrystallizeStatus, 375),
        (status.RebelliousShieldStatus, 376),

        #### 3 Character Status 450 ####
        #### 3.1 General Character Status 450 ####
        (status.FrozenStatus, 450),
        (status.JueyunGuobaStatus, 451),
        (status.MintyMeatRollsStatus, 452),
        (status.MushroomPizzaStatus, 453),
        (status.NorthernSmokedChickenStatus, 454),
        (status.SatiatedStatus, 455),
        (status.TandooriRoastChickenStatus, 456),
        (status.UnmovableMountainStatus, 457),

        #### 3.2 Shield Character Status 525 ####
        (status.LithicGuardStatus, 525),
        (status.LotusFlowerCrispStatus, 526),

        #### 4 Character Specific Status 600 ####
        #### 4.1 Cryo Character Status 600 ####
        ## Ganyu 600 ##
        (status.UndividedHeartStatus, 600),
        (status.GanyuTalentStatus, 601),
        (status.IceLotusStatus, 602),
        ## Diona 620 ##
        ## Kaeya 640 ##
        (status.ColdBloodedStrikeStatus, 640),
        (status.IcicleStatus, 641),
        ## Chongyun 660 ##
        ## KamisatoAyaka 680 ##
        ## Eula 700 ##
        ## Shenhe 720 ##
        (status.MysticalAbandonStatus, 720),
        (status.IcyQuillStatus, 721),
        ## FatuiCryoCicinMage 740 ##
        ## Qiqi 760 ##
        (status.RiteOfResurrectionStatus, 760),
        (status.FortunePreservingTalismanStatus, 761),
        (status.QiqiTalentStatus, 762),

        #### 4.2 Hydro Character Status 2600 ####
        ## Barbara 2600 ##
        ## Xingqiu 2620 ##
        (status.TheScentRemainedStatus, 2620),
        (status.RainSwordStatus, 2621),
        (status.RainbowBladeworkStatus, 2622),
        ## Mona 2640 ##
        (status.ProphecyOfSubmersionStatus, 2640),
        (status.IllusoryBubbleStatus, 2641),
        (status.IllusoryTorrentStatus, 2642),
        ## RhodeiaOfLoch 2660 ##
        (status.StreamingSurgeStatus, 2660),
        ## MirrorMaiden 2680 ##
        ## SangonomiyaKokomi 2700 ##
        (status.TamakushiCasketStatus, 2700),
        (status.CeremonialGarmentStatus, 2701),
        ## KamisatoAyato 2720 ##
        ## Tartaglia 2740 ##
        ## Candice 2760 ##
        ## Nilou 2780 ##

        #### 4.3 Pyro Character Status 4600 ####
        ## Diluc 4600 ##
        ## Xiangling 4620 ##
        ## Bennett 4640 ##
        (status.GrandExpectationStatus, 4640),
        (status.InspirationFieldStatus, 4641),
        (status.InspirationFieldEnhancedStatus, 4642),
        ## Yoimiya 4660 ##
        (status.NaganoharaMeteorSwarmStatus, 4660),
        (status.AurousBlazeStatus, 4661),
        (status.NiwabiEnshouStatus, 4662),
        ## FatuiPyroAgent 4680 ##
        (status.PaidInFullStatus, 4680),
        (status.StealthMasterStatus, 4681),
        (status.StealthStatus, 4682),
        ## Klee 4700 ##
        (status.PoundingSurpriseStatus, 4700),
        (status.ExplosiveSparkStatus, 4701),
        (status.SparksnSplashStatus, 4702),
        ## Amber 4720 ##
        ## HuTao 4740 ##
        (status.SanguineRougeStatus, 4740),
        (status.BloodBlossomStatus, 4741),
        (status.ParamitaPapilioStatus, 4742),
        ## AbyssLectorFathomlessFlames 4760 ##
        ## Yanfei 4780 ##
        ## Dehya 4800 ##
        (status.StalwartAndTrueStatus, 4800),
        (status.IncinerationDriveStatus, 4801),

        #### 4.4 Electro Character Status 6600 ####
        ## Fischl 6600 ##
        (status.StellarPredatorStatus, 6600),
        ## Keqing 6620 ##
        (status.ThunderingPenanceStatus, 6620),
        (status.KeqingElectroInfusionStatus, 6621),
        (status.KeqingTalentStatus, 6622),
        ## Razor 6640 ##
        ## Cyno 6660 ##
        ## Beidou 6680 ##
        ## KujouSara 6700 ##
        ## RaidenShogun 6720 ##
        ## YaeMiko 6740 ##
        (status.TheShrinesSacredShadeStatus, 6740),
        (status.RiteOfDispatchStatus, 6741),
        (status.TenkoThunderboltsStatus, 6742),
        ## ElectroHypostasis 6760 ##
        (status.ElectroCrystalCoreHiddenStatus, 6760),
        (status.ElectroCrystalCoreStatus, 6761),
        (status.RockPaperScissorsComboPaperStatus, 6762),
        (status.RockPaperScissorsComboScissorsStatus, 6763),
        ## Lisa 6780 ##
        ## Dori 6800 ##

        #### 4.5 Geo Character Status 8600 ####
        ## Ningguang 8600 ##
        (status.StrategicReserveStatus, 8600),
        (status.JadeScreenStatus, 8601),
        ## Noelle 8620 ##
        (status.IGotYourBackStatus, 8620),
        (status.FullPlateStatus, 8621),
        (status.SweepingTimeStatus, 8622),
        ## StonehideLawachurl 8640 ##
        ## AratakiItto 8660 ##
        (status.AratakiIchibanStatus, 8660),
        (status.RagingOniKingStatus, 8661),
        (status.SuperlativeSuperstrengthStatus, 8662),
        ## Zhongli 8680 ##
        ## Albedo 8700 ##
        (status.DescentOfDivinityStatus, 8700),

        #### 4.6 Dendro Character Status 10600 ####
        ## Collei 10600 ##
        (status.FloralSidewinderStatus, 10600),
        (status.ColleiTalentStatus, 10601),
        (status.FloralSidewinderStatus, 10602),
        ## JadeplumeTerrorshroom 10620 ##
        (status.ProliferatingSporesStatus, 10620),
        (status.RadicalVitalityHiddenStatus, 10621),
        (status.RadicalVitalityStatus, 10622),
        ## Tighnari 10640 ##
        (status.KeenSightStatus, 10640),
        (status.VijnanaSuffusionStatus, 10641),
        ## Nahida 10660 ##
        (status.TheSeedOfStoredKnowledgeStatus, 10660),
        (status.SeedOfSkandhaStatus, 10661),
        (status.ShrineOfMayaStatus, 10662),
        ## Yaoyao 10680 ##
        ## Baizhu 10700 ##

        #### 4.7 Anemo Character Status 12600 ####
        ## Sucrose 12600 ##
        ## Jean 12620 ##
        (status.LandsOfDandelionStatus, 12620),
        ## MaguuKenki 12640 ##
        (status.TranscendentAutomatonStatus, 12640),
        ## Venti 12660 ##
        (status.EmbraceOfWindsStatus, 12660),
        (status.StormzoneStatus, 12661),
        (status.WindsOfHarmonyStatus, 12662),
        ## Xiao 12680 ##
        ## KaedeharaKazuha 12700 ##
        (status.PoeticsOfFuubutsuStatus, 12700),
        (status.PoeticsOfFuubutsuCryoStatus, 12701),
        (status.PoeticsOfFuubutsuHydroStatus, 12702),
        (status.PoeticsOfFuubutsuPyroStatus, 12703),
        (status.PoeticsOfFuubutsuElectroStatus, 12704),
        (status.MidareRanzanStatus, 12705),
        (status.MidareRanzanCryoStatus, 12706),
        (status.MidareRanzanHydroStatus, 12707),
        (status.MidareRanzanPyroStatus, 12708),
        (status.MidareRanzanElectroStatus, 12709),
        ## Wanderer 12720 ##

        #### End 14600 ####
    )
})

SUMM_MAPPING: dict[type["Summon"], int] = HashableDict({
    summ: 15000 + i
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
})

SUPP_MAPPING: dict[type["Support"], int] = HashableDict({
    supp: 16000 + i
    for supp, i in (
        #### Location 000 ####
        (support.LiyueHarborWharfSupport, 0),
        (support.KnightsOfFavoniusLibrarySupport, 1),
        # (support.JadeChamberSupport, 2),
        # (support.DawnWinerySupport, 3),
        # (support.WangshuInnSupport, 4),
        # (support.FavoniusCathedralSupport, 5),
        # (support.GrandNarukamiShrineSupport, 6),
        (support.TenshukakuSupport, 7),
        # (support.SangonomiyaShrineSupport, 8),
        (support.SumeruCitySupport, 9),
        (support.VanaranaSupport, 10),
        # (support.ChinjuForestSupport, 11),
        # (support.GoldenHouseSupport, 12),
        # (support.GandharvaVilleSupport, 13),
        # (support.StormterrorsLairSupport, 14),

        #### Companion 100 ####
        (support.PaimonSupport, 100),
        # (support.KatheryneSupport, 101),
        # (support.TimaeusSupport, 102),
        # (support.WagnerSupport, 103),
        # (support.ChefMaoSupport, 104),
        # (support.TubbySupport, 105),
        # (support.TimmieSupport, 106),
        (support.LibenSupport, 107),
        (support.ChangTheNinthSupport, 108),
        # (support.EllinSupport, 109),
        # (support.IronTongueTianSupport, 110),
        # (support.LiuSuSupport, 111),
        # (support.HanachirusatoSupport, 112),
        # (support.KidKjiraiSupport, 113),
        (support.XudongSupport, 114),
        # (support.DunyarzadSupport, 115),
        # (support.RanaSupport, 116),
        # (support.MasterZhangSupport, 117),
        # (support.SetariaSupport, 118),
        # (support.YayoiNanatsukiSupport, 119),

        #### Item 200 ####
        (support.ParametricTransformerSupport, 200),
        (support.NRESupport, 201),
        # (support.RedFeatherFanSupport, 202),
        # (support.TreasureSeekingSeelieSupport, 203),

        #### End 300 ####
    )
})
