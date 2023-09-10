
import unittest

from dgisim.tests.test_characters.common_imports import *


class TestKlee(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Klee.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(PoundingSurprise)
        ).dices(
            ActualDices({Element.OMNI: 100})  # even number
        ).build()
    ).build()

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.PYRO))
        self.assertFalse(gsm.get_game_state().get_player1().get_dices().is_even())

        # first normal attack
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
        ))
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        p1 = gsm.get_game_state().get_player1()
        p1ac = p1.just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.PYRO))
        self.assertTrue(p1.get_dices().is_even())
        self.assertEqual(
            p1ac.get_character_statuses().just_find(ExplosiveSparkStatus).usages,
            1
        )

        # second normal attack (charged)
        self.assertEqual(
            just(
                gsm.get_game_state().skill_checker().usable(Pid.P1, 2, CharacterSkill.SKILL1)
            )[1],
            AbstractDices({Element.ANY: 2})
        )
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 2})),
        ))
        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        p1 = gsm.get_game_state().get_player1()
        p1ac = p1.just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 4)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.PYRO))
        self.assertNotIn(ExplosiveSparkStatus, p1ac.get_character_statuses())

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.get_max_energy()
                    ).build()
                ).build()
            ).build()
        ).build()

        # burst
        gsm = GameStateMachine(base_game_state, a1, a2)
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.ELEMENTAL_BURST,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p2 = gsm.get_game_state().get_player2()
        p2ac = p2.just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.PYRO))
        self.assertEqual(p2.get_combat_statuses().just_find(SparksnSplashStatus).usages, 2)
        self.assertEqual(
            gsm.get_game_state().get_player1().just_get_active_character().get_energy(),
            0
        )

        # p2 skill
        game_state = remove_aura(gsm.get_game_state())
        gsm = GameStateMachine(game_state, a1, a2)
        a2.inject_action(
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p2 = gsm.get_game_state().get_player2()
        p2ac = p2.just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 5)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.PYRO))
        self.assertEqual(p2.get_combat_statuses().just_find(SparksnSplashStatus).usages, 1)

        # p1 end
        a1.inject_action(EndRoundAction())
        gsm.player_step()
        
        # test swap doesn't trigger
        a2.inject_action(
            SwapAction(
                char_id=2,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p2 = gsm.get_game_state().get_player2()
        p2ac = p2.just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertNotIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertEqual(p2.get_combat_statuses().just_find(SparksnSplashStatus).usages, 1)

        # p2 skill again
        a2.inject_action(
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p2 = gsm.get_game_state().get_player2()
        p2ac = p2.just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertNotIn(SparksnSplashStatus, p2.get_combat_statuses())

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            CardAction(
                card=PoundingSurprise,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 2})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 2})),
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3})),
            ),
            EndRoundAction(),
        ])
        gsm.step_until_next_phase()
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 1)
        self.assertIn(Element.PYRO, p2ac.get_elemental_aura())
        self.assertNotIn(ExplosiveSparkStatus, p1ac.get_character_statuses())