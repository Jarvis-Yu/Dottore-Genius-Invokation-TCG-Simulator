import unittest

from src.tests.test_characters.common_imports import *


class TestYaoyao(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Yaoyao,
        char_id=2,
        card=Beneficent,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.DENDRO: 1, Element.HYDRO: 1, Element.CRYO: 1}),
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
            dice=ActualDice({Element.DENDRO: 3}),
        )
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 0)
        self.assertIn(YueguiThrowingModeSummon, game_state.player1.summons)
        summon = game_state.player1.summons.just_find(YueguiThrowingModeSummon)
        self.assertEqual(summon.usages, 2)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.DENDRO: 4}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.DENDRO)
        self.assertIn(AdeptalLegacyStatus, game_state.player1.combat_statuses)
        status = game_state.player1.combat_statuses.just_find(AdeptalLegacyStatus)
        self.assertEqual(status.usages, 3)

    def test_yuegui_summon(self):
        game_state = AddSummonEffect(Pid.P1, YueguiThrowingModeSummon).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = replace_character(game_state, Pid.P1, ElectroHypostasis, char_id=1)
        game_state = simulate_status_dmg(game_state, 2, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 2, pid=Pid.P1, char_id=3)

        # check prioritize healing character with highest lost hp in activity order (# 3 > 1 > 2)
        game_state = next_round(game_state)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 2)
        self.assertEqual(p1c2.hp_lost(), 1)
        self.assertEqual(p1c3.hp_lost(), 1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.DENDRO)

        game_state = next_round(game_state)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 1)
        self.assertEqual(p1c2.hp_lost(), 1)
        self.assertEqual(p1c3.hp_lost(), 1)
        self.assertNotIn(YueguiThrowingModeSummon, game_state.player1.summons)

        game_state = AddSummonEffect(Pid.P1, YueguiThrowingModeSummon).execute(game_state)
        game_state = next_round(game_state)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 1)
        self.assertEqual(p1c2.hp_lost(), 0)
        self.assertEqual(p1c3.hp_lost(), 1)

    def test_adeptal_legacy_status(self):
        game_state = AddCombatStatusEffect(Pid.P1, AdeptalLegacyStatus).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=3)

        # check healing active character only and deals correct dmg
        game_state = step_swap(game_state, Pid.P1, 1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 4)
        self.assertEqual(p1c2.hp_lost(), 5)
        self.assertEqual(p1c3.hp_lost(), 5)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.DENDRO)

        game_state = step_swap(game_state, Pid.P1, 3)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 4)
        self.assertEqual(p1c2.hp_lost(), 5)
        self.assertEqual(p1c3.hp_lost(), 4)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.DENDRO)

        game_state = step_swap(game_state, Pid.P1, 1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 3)
        self.assertEqual(p1c2.hp_lost(), 5)
        self.assertEqual(p1c3.hp_lost(), 4)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.DENDRO)

        self.assertNotIn(AdeptalLegacyStatus, game_state.player1.combat_statuses)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1, char_id=3)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Beneficent,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 3})),
        ))

        # check not boosting when usages is not 1
        yuegui = game_state.player1.summons.just_find(YueguiThrowingModeSummon)
        self.assertGreater(yuegui.usages, 1)
        game_state = next_round(game_state)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 5)
        self.assertEqual(p1c2.hp_lost(), 4)
        self.assertEqual(p1c3.hp_lost(), 5)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.DENDRO)

        # check boosting when usages is 1
        yuegui = game_state.player1.summons.just_find(YueguiThrowingModeSummon)
        self.assertEqual(yuegui.usages, 1)
        game_state = next_round(game_state)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp_lost(), 5)
        self.assertEqual(p1c2.hp_lost(), 4)
        self.assertEqual(p1c3.hp_lost(), 3)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.DENDRO)
