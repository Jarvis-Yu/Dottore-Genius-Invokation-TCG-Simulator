import unittest

from src.tests.test_characters.common_imports import *


class TestDiona(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Diona,
        char_id=2,
        card=ShakenNotPurred,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(CatClawShieldStatus, game_state.player1.combat_statuses)
        status = game_state.player1.combat_statuses.just_find(CatClawShieldStatus)
        self.assertEqual(status.usages, 1)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = kill_character(game_state, char_id=2, pid=Pid.P1, hp=2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)
        p1ac = p1_active_char(game_state)
        self.assertEqual(p1ac.hp, 4)
        self.assertIn(DrunkenMistSummon, game_state.player1.summons)
        summon = game_state.player1.summons.just_find(DrunkenMistSummon)
        self.assertEqual(summon.usages, 2)

    def test_drunken_mist_summon(self):
        game_state = AddSummonEffect(Pid.P1, DrunkenMistSummon).execute(self.BASE_GAME)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = kill_character(game_state, char_id=1, pid=Pid.P1, hp=2)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)
        p1_ac = p1_active_char(game_state)
        self.assertEqual(p1_ac.hp, 4)
        self.assertIn(DrunkenMistSummon, game_state.player1.summons)
        summon = game_state.player1.summons.just_find(DrunkenMistSummon)
        self.assertEqual(summon.usages, 1)

    def test_talent_card(self):
        game_state = AddCombatStatusEffect(Pid.P1, CatClawShieldStatus).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ShakenNotPurred,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 3})),
        ))
        self.assertNotIn(CatClawShieldStatus, game_state.player1.combat_statuses)
        self.assertIn(CatClawShieldEnhancedStatus, game_state.player1.combat_statuses)
        status = game_state.player1.combat_statuses.just_find(CatClawShieldEnhancedStatus)
        self.assertEqual(status.usages, 2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.CRYO)
        self.assertEqual(dmg.damage, 2)

    def test_cat_claw_shield_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, CatClawShieldStatus).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertNotIn(CatClawShieldStatus, game_state.player1.combat_statuses)

    def test_cat_claw_shield_enhanced_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, CatClawShieldEnhancedStatus).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertNotIn(CatClawShieldEnhancedStatus, game_state.player1.combat_statuses)
