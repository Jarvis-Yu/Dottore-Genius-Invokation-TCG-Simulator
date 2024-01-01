import unittest

from src.tests.test_characters.common_imports import *


class TestXingqiu(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Xingqiu.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(TheScentRemained)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Xingqiu

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.elem_auras())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().player1
        p1ac = p1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.HYDRO, p2ac.elemental_aura)
        self.assertEqual(p1ac.hp, 10)
        self.assertIn(Element.HYDRO, p1ac.elemental_aura)
        self.assertIn(RainSwordStatus, p1.combat_statuses)
        self.assertEqual(
            p1.combat_statuses.just_find(RainSwordStatus).usages,
            2
        )

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.max_energy
                    ).build()
                ).build()
            ).build()
        ).build()

        # test burst base damage
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm = GameStateMachine(base_game, a1, a2)
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().player1
        p1ac = p1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.HYDRO, p2ac.elemental_aura)
        self.assertEqual(p1ac.hp, 10)
        self.assertIn(Element.HYDRO, p1ac.elemental_aura)
        self.assertIn(RainbowBladeworkStatus, p1.combat_statuses)
        self.assertEqual(
            p1.combat_statuses.just_find(RainbowBladeworkStatus).usages,
            3
        )

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(CardAction(
            card=TheScentRemained,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().player1
        p1ac = p1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.HYDRO, p2ac.elemental_aura)
        self.assertEqual(p1ac.hp, 10)
        self.assertIn(Element.HYDRO, p1ac.elemental_aura)
        self.assertIn(RainSwordStatus, p1.combat_statuses)
        self.assertEqual(
            p1.combat_statuses.just_find(RainSwordStatus).usages,
            3
        )

        # test dmg blocking
        game_state = gsm.get_game_state()
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = simulate_status_dmg(game_state, 1, Element.HYDRO, Pid.P1)
        self.assertEqual(get_dmg_listener_data(game_state, Pid.P1)[-1].damage, 1)
        game_state = simulate_status_dmg(game_state, 2, Element.HYDRO, Pid.P1)
        self.assertEqual(get_dmg_listener_data(game_state, Pid.P1)[-1].damage, 1)
        game_state = simulate_status_dmg(game_state, 3, Element.HYDRO, Pid.P1)
        self.assertEqual(get_dmg_listener_data(game_state, Pid.P1)[-1].damage, 2)

    def test_rain_sword_status(self):
        base_game = AddCombatStatusEffect(Pid.P1, RainSwordStatus).execute(self.BASE_GAME)
        for dmg in range(1, 5):
            with self.subTest(dmg=dmg):
                game_state = add_damage_effect(base_game, dmg, Element.ANEMO, Pid.P1, char_id=2)
                game_state = auto_step(game_state)
                p1 = game_state.player1
                p1ac = p1.just_get_active_character()
                if dmg <= 2:
                    self.assertEqual(p1ac.hp, 10 - dmg)
                    self.assertEqual(p1.combat_statuses.just_find(RainSwordStatus).usages, 2)
                else:
                    self.assertEqual(p1ac.hp, 10 - dmg + 1)
                    self.assertEqual(p1.combat_statuses.just_find(RainSwordStatus).usages, 1)

    def test_rainbow_bladework_status(self):
        base_game = AddCombatStatusEffect(Pid.P1, RainbowBladeworkStatus).execute(self.BASE_GAME)

        # p1 normal attack with Xingqiu
        game_state = step_skill(base_game, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertIn(RainbowBladeworkStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(RainbowBladeworkStatus).usages, 2)
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.HYDRO, p2ac.elemental_aura)

        # p2 normal attack doesn't trigger
        p2ac = game_state.player2.just_get_active_character()
        assert isinstance(p2ac, RhodeiaOfLoch)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p1ac = game_state.player1.just_get_active_character()
        self.assertIn(RainbowBladeworkStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(RainbowBladeworkStatus).usages, 2)
        self.assertEqual(p1ac.hp, 9)

        # p1 swap and normal attack with other character
        game_state = AddCombatStatusEffect(Pid.P1, LeaveItToMeStatus).execute(game_state)
        game_state = step_swap(game_state, Pid.P1, char_id=3)
        assert isinstance(game_state.player1.just_get_active_character(), Keqing)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertIn(RainbowBladeworkStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(RainbowBladeworkStatus).usages, 1)
        self.assertEqual(p2ac.hp, 4)
        self.assertIn(Element.HYDRO, p2ac.elemental_aura)
