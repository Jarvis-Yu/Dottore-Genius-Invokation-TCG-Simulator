import unittest

from src.tests.test_characters.common_imports import *


def p1_burst_scan(game_state: GameState) -> BurstScanStatus:
    return game_state.player1.combat_statuses.just_find(BurstScanStatus)


class TestKaveh(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Kaveh,
        char_id=2,
        card=TheArtOfBudgeting,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.DENDRO: 1, Element.PYRO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.DENDRO: 3}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.DENDRO)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)

    def test_elemental_burst(self):
        game_state = self.BASE_GAME
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.DENDRO: 3}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.DENDRO)
        self.assertIn(MehraksAssistanceStatus, p1_active_char(game_state).character_statuses)
        self.assertEqual(
            p1_active_char(game_state).character_statuses.just_find(MehraksAssistanceStatus).usages,
            2,
        )
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 2)

    def test_burst_scan_status(self):
        base_state = self.BASE_GAME
        base_state = add_combat_status(base_state, Pid.P1, BurstScanStatus)
        base_state = add_combat_status(base_state, Pid.P1, BurstScanStatus)  # usages = 2
        base_state = add_combat_status(base_state, Pid.P1, DendroCoreStatus)
        base_state = add_dmg_listener(base_state, Pid.P1)

        self.assertEqual(p1_burst_scan(base_state).usages, 2)

        """ check damage depend upon top card dice cost (card removed), BurstScan & DendroCore usages - 1 """ 
        # damage = 0
        game_state = base_state
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            Paimon,  # 3
            Liben,  # top: 0
        )))
        assert Liben._DICE_COST.num_dice() == 0

        game_state = step_swap(game_state, Pid.P1, 3)
        assert_last_dmg(self, game_state, Pid.P1, amount=0, elem=Element.DENDRO)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)
        self.assertEqual(game_state.player1.deck_cards, OrderedCards((Paimon,)))

        # damage = 1
        game_state = base_state
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            Liben,  # 0
            Strategize,  # top: 1
        )))
        assert Strategize._DICE_COST.num_dice() == 1

        game_state = end_round(game_state, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=1, elem=Element.DENDRO)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)
        self.assertEqual(game_state.player1.deck_cards, OrderedCards((Liben,)))

        # damage = 2
        game_state = base_state
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            ThunderingPenance,  # 3
            TravelersHandySword,  # top: 2
        )))
        assert TravelersHandySword._DICE_COST.num_dice() == 2

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.DENDRO)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)
        self.assertEqual(game_state.player1.deck_cards, OrderedCards((ThunderingPenance,)))

        # damage = 3
        game_state = base_state
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            GuardiansOath,  # 4
            ChangTheNinth,  # 0
            TenacityOfTheMillelith,  # top: 3
        )))
        assert TenacityOfTheMillelith._DICE_COST.num_dice() == 3

        game_state = end_round(game_state, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.DENDRO)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)
        self.assertEqual(game_state.player1.deck_cards, OrderedCards((GuardiansOath, ChangTheNinth,)))

        # damage = 4
        game_state = base_state
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            GuardiansOath,  # top: 4
        )))
        assert GuardiansOath._DICE_COST.num_dice() == 4

        game_state = end_round(game_state, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=4, elem=Element.DENDRO)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)
        self.assertEqual(game_state.player1.deck_cards, OrderedCards(()))

        """ check bountiful core usages - 1 as well """
        base_state = self.BASE_GAME
        base_state = add_combat_status(base_state, Pid.P1, BurstScanStatus)
        base_state = add_combat_status(base_state, Pid.P1, BurstScanStatus)  # usages = 2
        base_state = add_summon(base_state, Pid.P1, BountifulCoreSummon)
        base_state = add_summon(base_state, Pid.P1, BountifulCoreSummon)  # usages = 2
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({Strategize: 30}))
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({TaroumarusSavings: 10}))

        self.assertEqual(p1_burst_scan(base_state).usages, 2)
        self.assertEqual(base_state.player1.summons.just_find(BountifulCoreSummon).usages, 2)

        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, TaroumarusSavings)
        assert_last_dmg(self, game_state, Pid.P1, amount=1, elem=Element.DENDRO)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)
        self.assertIn(BountifulCoreSummon, game_state.player1.summons)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)

        game_state = end_round(game_state, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=1, elem=Element.DENDRO, status=True)
        self.assertNotIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertNotIn(BountifulCoreSummon, game_state.player1.summons)

    def test_mehraks_assistance_status(self):
        base_state = self.BASE_GAME
        base_state = add_character_status(base_state, Pid.P1, MehraksAssistanceStatus)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = end_round(base_state, Pid.P2)

        self.assertIn(MehraksAssistanceStatus, p1_active_char(base_state).character_statuses)
        self.assertEqual(
            p1_active_char(base_state).character_statuses.just_find(MehraksAssistanceStatus).usages,
            2,
        )

        # check boosts normal attack
        game_state = base_state
        for i in range(5):
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
            assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.DENDRO, normal_attack=True)
            self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
            self.assertEqual(p1_burst_scan(game_state).usages, min(3, i + 1))

        game_state = remove_combat_status(game_state, Pid.P1, BurstScanStatus)

        # check same for other skills
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.DENDRO, elemental_skill=True)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 1)

        game_state = remove_combat_status(game_state, Pid.P1, BurstScanStatus)

        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.DENDRO, elemental_burst=True)
        self.assertIn(BurstScanStatus, game_state.player1.combat_statuses)
        self.assertEqual(p1_burst_scan(game_state).usages, 2)

        # check usages decrease each round
        game_state = next_round(game_state)
        self.assertIn(MehraksAssistanceStatus, p1_active_char(game_state).character_statuses)
        self.assertEqual(
            p1_active_char(game_state).character_statuses.just_find(MehraksAssistanceStatus).usages,
            1,
        )

        game_state = next_round(game_state)
        self.assertNotIn(MehraksAssistanceStatus, p1_active_char(game_state).character_statuses)
