import unittest

from src.tests.test_characters.common_imports import *


class TestNilou(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Nilou,
        char_id=2,
        card=TheStarrySkiesTheirFlowersRain,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.HYDRO: 1, Element.PYRO: 1, Element.DENDRO: 1}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL)

    def test_skill2(self):
        """ Check no status addition when not all self characters are dendro / hydro """
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = replace_character(game_state, Pid.P1, Klee, char_id=1)
        game_state = replace_character(game_state, Pid.P1, Xingqiu, char_id=3)
        game_state = RemoveCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=StoneForceStatus,
        ).execute(game_state)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.HYDRO: 3}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.HYDRO)
        self.assertNotIn(GoldenChalicesBountyStatus, game_state.player1.combat_statuses)

        """ Check status addition when all self characters are dendro / hydro """
        game_state = self.BASE_GAME
        game_state = replace_character(game_state, Pid.P1, RhodeiaOfLoch, char_id=1)
        game_state = replace_character(game_state, Pid.P1, Xingqiu, char_id=3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertIn(GoldenChalicesBountyStatus, game_state.player1.combat_statuses)

    def test_elemental_burst(self):
        game_state = self.BASE_GAME
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = add_dmg_listener(game_state, Pid.P2)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.HYDRO: 3}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.HYDRO)
        self.assertIn(LingeringAeonStatus, game_state.player2.just_get_active_character().character_statuses)
        game_state = next_round(game_state)
        self.assertNotIn(LingeringAeonStatus, game_state.player2.just_get_active_character().character_statuses)
        assert_last_dmg(
            self, game_state, Pid.P2, amount=3, elem=Element.HYDRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )

    def test_golden_chalices_bounty(self):
        base_state = self.BASE_GAME
        base_state = replace_character(base_state, Pid.P1, RhodeiaOfLoch, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Xingqiu, char_id=3)
        base_state = replace_character(base_state, Pid.P2, RhodeiaOfLoch, char_id=1)
        base_state = replace_character(base_state, Pid.P2, Nilou, char_id=2)
        base_state = replace_character(base_state, Pid.P2, Xingqiu, char_id=3)
        base_state = add_combat_status(base_state, Pid.P1, GoldenChalicesBountyStatus)

        """ Check self bloom doesn't trigger """
        game_state = base_state
        game_state = simulate_status_dmg(game_state, 1, Element.HYDRO, Pid.P1)
        game_state = simulate_status_dmg(game_state, 1, Element.DENDRO, Pid.P1)
        self.assertNotIn(BountifulCoreSummon, game_state.player1.summons)
        self.assertNotIn(BountifulCoreSummon, game_state.player2.summons)
        self.assertIn(DendroCoreStatus, game_state.player2.combat_statuses)

        game_state = base_state
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P1)
        game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P1)
        self.assertNotIn(BountifulCoreSummon, game_state.player1.summons)
        self.assertNotIn(BountifulCoreSummon, game_state.player2.summons)
        self.assertIn(DendroCoreStatus, game_state.player2.combat_statuses)

        """ Check oppo bloom triggers """
        game_state = base_state
        game_state = simulate_status_dmg(game_state, 1, Element.HYDRO, Pid.P2)
        game_state = simulate_status_dmg(game_state, 1, Element.DENDRO, Pid.P2)
        self.assertIn(BountifulCoreSummon, game_state.player1.summons)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)
        self.assertNotIn(BountifulCoreSummon, game_state.player2.summons)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)

        game_state = base_state
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        self.assertIn(BountifulCoreSummon, game_state.player1.summons)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)
        self.assertNotIn(BountifulCoreSummon, game_state.player2.summons)
        self.assertNotIn(DendroCoreStatus, game_state.player1.combat_statuses)

    def test_bountiful_core_summon(self):
        base_state = self.BASE_GAME
        base_state = replace_character(base_state, Pid.P1, RhodeiaOfLoch, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Xingqiu, char_id=3)
        base_state = add_combat_status(base_state, Pid.P1, GoldenChalicesBountyStatus)
        base_state = add_dmg_listener(base_state, Pid.P1)

        """ Check summon deals correct damage """
        # when usages == 1
        game_state = base_state
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)

        game_state = next_round(game_state)
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.DENDRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )
        self.assertNotIn(BountifulCoreSummon, game_state.player1.summons)

        # when usages == 2, additional damage on self end declaration
        game_state = base_state
        for _ in range(2):
            game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
            game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 2)

        game_state = end_round(game_state, Pid.P2)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 0)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 2)

        game_state = reactivate_player(game_state, Pid.P2)
        game_state = end_round(game_state, Pid.P1)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 1)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.DENDRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )

        game_state = next_round(game_state)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 2)
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.DENDRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )
        self.assertNotIn(BountifulCoreSummon, game_state.player1.summons)

        # when usages == 3
        game_state = base_state
        for _ in range(3):
            game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
            game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 3)

        game_state = next_round(game_state)
        assert_last_dmg(
            self, game_state, Pid.P1, last_index=1, amount=2, elem=Element.DENDRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, last_index=0, amount=2, elem=Element.DENDRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2),
        )
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)

        """ Check usages cap at 3 """
        game_state = base_state
        for _ in range(4):
            game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
            game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 3)

    def test_talent_card(self):
        game_state = self.BASE_GAME
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = replace_character(game_state, Pid.P1, RhodeiaOfLoch, char_id=1)
        game_state = replace_character(game_state, Pid.P1, Xingqiu, char_id=3)
        game_state = play_dice_only_card(game_state, Pid.P1, TheStarrySkiesTheirFlowersRain)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.HYDRO)
        self.assertIn(GoldenChalicesBountyStatus, game_state.player1.combat_statuses)
        self.assertIn(TheStarrySkiesTheirFlowersRainStatus, p1_active_char(game_state).character_statuses)

        game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        self.assertIn(BountifulCoreSummon, game_state.player1.summons)
        self.assertEqual(game_state.player1.summons.just_find(BountifulCoreSummon).usages, 1)

        game_state = next_round(game_state)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.DENDRO)
