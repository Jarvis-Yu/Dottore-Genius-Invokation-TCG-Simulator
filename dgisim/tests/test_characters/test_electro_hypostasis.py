import unittest

from dgisim.tests.test_characters.common_imports import *


class TestAratakiItto(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                ElectroHypostasis.from_default(2)
            ).build()
            # ).f_hand_cards(
            #     lambda hcs: hcs.add(AratakiIchiban)
        ).build()
    ).build()
    assert type(BASE_GAME.get_player1().just_get_active_character()) is ElectroHypostasis

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.ELECTRO, p2ac.get_elemental_aura())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 5})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        ## Normal Test ##
        # p1 skill
        gsm.player_step()
        gsm.auto_step()
        post_fst_skill_game_state = gsm.get_game_state()
        p1ac = post_fst_skill_game_state.get_player1().just_get_active_character()
        p2ac = post_fst_skill_game_state.get_player2().just_get_active_character()
        self.assertIn(RockPaperScissorsComboScissorsStatus, p1ac.get_character_statuses())
        self.assertNotIn(RockPaperScissorsComboPaperStatus, p1ac.get_character_statuses())
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertEqual(post_fst_skill_game_state.get_active_player_id(), Pid.P2)

        # p1 second skill (prepare skill)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertNotIn(RockPaperScissorsComboScissorsStatus, p1ac.get_character_statuses())
        self.assertIn(RockPaperScissorsComboPaperStatus, p1ac.get_character_statuses())
        self.assertEqual(p2ac.get_hp(), 6)
        self.assertEqual(post_fst_skill_game_state.get_active_player_id(), Pid.P2)

        # p1 third skill (prepare skill)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertNotIn(RockPaperScissorsComboScissorsStatus, p1ac.get_character_statuses())
        self.assertNotIn(RockPaperScissorsComboPaperStatus, p1ac.get_character_statuses())
        self.assertEqual(p2ac.get_hp(), 3)
        self.assertEqual(post_fst_skill_game_state.get_active_player_id(), Pid.P2)

        ## Frozen Test ##
        game_state = post_fst_skill_game_state.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().f_character_statuses(
                        lambda cstts: cstts.update_status(FrozenStatus())
                    ).build()
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertIn(RockPaperScissorsComboScissorsStatus, p1ac.get_character_statuses())
        self.assertNotIn(RockPaperScissorsComboPaperStatus, p1ac.get_character_statuses())
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertEqual(gsm.get_game_state().get_active_player_id(), Pid.P1)

        ## Overload Test ##
        game_state = post_fst_skill_game_state.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(Element.ELECTRO)
                    ).build()
                ).build()
            ).build()
        ).f_player2(
            lambda p2: p2.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: Klee.from_default(ac.get_id())
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_action(SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        ))
        gsm.player_step()
        gsm.auto_step()
        p1_electro_hypo = gsm.get_game_state().get_player1().get_characters().just_get_character(2)
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertNotIn(
            RockPaperScissorsComboScissorsStatus,
            p1_electro_hypo.get_character_statuses()
        )
        self.assertNotIn(
            RockPaperScissorsComboPaperStatus,
            p1_electro_hypo.get_character_statuses()
        )
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertEqual(gsm.get_game_state().get_active_player_id(), Pid.P1)
