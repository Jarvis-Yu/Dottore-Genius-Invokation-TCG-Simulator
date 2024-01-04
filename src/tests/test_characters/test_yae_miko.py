import unittest

from src.tests.test_characters.common_imports import *


class TestYaeMiko(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                YaeMiko.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(TheShrinesSacredShade)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is YaeMiko

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
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), LazyAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
        ])
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()  # p1 skill
        p1 = gsm.get_game_state().player1
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(SesshouSakuraSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SesshouSakuraSummon).usages, 3)

        # second skill increases usage to 6
        gsm.player_step()
        gsm.auto_step()  # p1 skill
        p1 = gsm.get_game_state().player1
        self.assertIn(SesshouSakuraSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SesshouSakuraSummon).usages, 6)

        # summon usages cap at 6
        gsm.player_step()
        gsm.auto_step()  # p1 skill
        p1 = gsm.get_game_state().player1
        self.assertIn(SesshouSakuraSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SesshouSakuraSummon).usages, 6)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game_state = recharge_energy_for_all(self.BASE_GAME)

        # burst with no Sesshou Sakura
        gsm = GameStateMachine(base_game_state, a1, a2)
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.ELEMENTAL_BURST,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().player1
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertNotIn(TenkoThunderboltsStatus, p1.combat_statuses)
        self.assertEqual(p1.just_get_active_character().energy, 0)

        # burst with Sesshou Sakura
        game_state = AddSummonEffect(
            target_pid=Pid.P1, summon=SesshouSakuraSummon
        ).execute(base_game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1 = game_state.player1
        self.assertIn(TenkoThunderboltsStatus, p1.combat_statuses)
        self.assertNotIn(SesshouSakuraSummon, p1.summons)
        post_burst_state = game_state

        with self.subTest(condition="oppo end round"):
            game_state = step_action(post_burst_state, Pid.P2, EndRoundAction())
            p2ac = game_state.player2.just_get_active_character()
            self.assertEqual(p2ac.hp, 3)
            self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
            p1 = game_state.player1
            self.assertNotIn(TenkoThunderboltsStatus, p1.combat_statuses)
            self.assertNotIn(SesshouSakuraSummon, p1.summons)

        with self.subTest(condition="oppo take action"):
            game_state = step_skill(post_burst_state, Pid.P2, CharacterSkill.SKILL1)
            p2ac = game_state.player2.just_get_active_character()
            self.assertEqual(p2ac.hp, 3)
            self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
            p1 = game_state.player1
            self.assertNotIn(TenkoThunderboltsStatus, p1.combat_statuses)
            self.assertNotIn(SesshouSakuraSummon, p1.summons)

    def test_sesshou_sakura_summon(self):
        # p1 has the summon with usages <= 3 and ends the round
        base_game = OverrideSummonEffect(Pid.P1, SesshouSakuraSummon(usages=3)).execute(self.BASE_GAME)
        game_state = step_action(base_game, Pid.P1, EndRoundAction())
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertNotIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(SesshouSakuraSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SesshouSakuraSummon).usages, 3)

        # p1 has the summon with usages >= 4 and ends the round
        base_game = OverrideSummonEffect(Pid.P1, SesshouSakuraSummon(usages=4)).execute(self.BASE_GAME)
        game_state = step_action(base_game, Pid.P1, EndRoundAction())
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(SesshouSakuraSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SesshouSakuraSummon).usages, 3)

        # test that normal end round attack is working
        base_game = OverrideSummonEffect(Pid.P1, SesshouSakuraSummon(usages=3)).execute(self.BASE_GAME)
        game_state = step_action(base_game, Pid.P1, EndRoundAction())
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertIn(SesshouSakuraSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SesshouSakuraSummon).usages, 2)

        # test summon disappears on last attack
        base_game = OverrideSummonEffect(Pid.P1, SesshouSakuraSummon(usages=1)).execute(self.BASE_GAME)
        game_state = step_action(base_game, Pid.P1, EndRoundAction())
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.ELECTRO, p2ac.elemental_aura)
        self.assertNotIn(SesshouSakuraSummon, p1.summons)

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), LazyAgent()
        base_state = recharge_energy_for_all(self.BASE_GAME)

        # test burst generates no character status if no Sesshou Sakura destroyed
        gsm = GameStateMachine(base_state, a1, a2)
        a1.inject_action(CardAction(
            card=TheShrinesSacredShade,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()  # p1 burst
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertNotIn(RiteOfDispatchStatus, p1ac.character_statuses)

        # test burst generates Rite of Dispatch character status if Sesshou Sakura destroyed
        game_state = AddSummonEffect(Pid.P1, SesshouSakuraSummon).execute(base_state)
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(CardAction(
            card=TheShrinesSacredShade,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()  # p1 burst
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertIn(RiteOfDispatchStatus, p1ac.character_statuses)

        gsm.player_step()
        gsm.auto_step()  # p2 end round
        post_burst_state = gsm.get_game_state()

        # then next skill has cost deduction
        game_state = step_action(post_burst_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        p1ac = game_state.player1.just_get_active_character()
        self.assertNotIn(RiteOfDispatchStatus, p1ac.character_statuses)
        game_state = step_action(game_state, Pid.P1, SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))

        # status disappear the next round
        gsm = GameStateMachine(post_burst_state, LazyAgent(), LazyAgent())
        gsm.step_until_next_phase()
        gsm.step_until_phase(game_state.mode.action_phase)
        p1ac = game_state.player1.just_get_active_character()
        self.assertNotIn(RiteOfDispatchStatus, p1ac.character_statuses)
